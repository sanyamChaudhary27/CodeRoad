"""Authenticated, match-scoped WebSocket relay."""

from __future__ import annotations

import json
import logging
from typing import Dict, List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..core.database import SessionLocal
from ..core.security import validate_player_token
from ..models import Match

logger = logging.getLogger(__name__)
router = APIRouter()

AUTH_PROTOCOL_PREFIX = "coderoad-auth."
MAX_MESSAGE_BYTES = 60_000
MAX_CODE_CHARS = 50_000
MAX_CHAT_CHARS = 1_000


def token_from_protocol_header(header: str) -> str | None:
    """Extract a JWT sent as a WebSocket subprotocol token.

    Browsers cannot set an Authorization header on a native WebSocket. The
    client therefore offers `coderoad` and `coderoad-auth.<JWT>` protocols. The
    server selects only the non-secret `coderoad` protocol in its response.
    """

    for raw_protocol in header.split(","):
        protocol = raw_protocol.strip()
        if protocol.startswith(AUTH_PROTOCOL_PREFIX):
            token = protocol.removeprefix(AUTH_PROTOCOL_PREFIX)
            return token or None
    return None


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, match_id: str) -> None:
        await websocket.accept(subprotocol="coderoad")
        self.active_connections.setdefault(match_id, []).append(websocket)
        logger.info(
            "Authenticated WebSocket joined match %s; connections=%s",
            match_id,
            len(self.active_connections[match_id]),
        )

    def disconnect(self, websocket: WebSocket, match_id: str) -> None:
        connections = self.active_connections.get(match_id)
        if connections and websocket in connections:
            connections.remove(websocket)
            if not connections:
                del self.active_connections[match_id]
        logger.info("WebSocket disconnected from match %s", match_id)

    async def broadcast(self, message: str, match_id: str, exclude: WebSocket) -> None:
        for connection in list(self.active_connections.get(match_id, [])):
            if connection == exclude:
                continue
            try:
                await connection.send_text(message)
            except Exception:
                logger.warning("Removing failed WebSocket from match %s", match_id)
                self.disconnect(connection, match_id)


manager = ConnectionManager()


@router.websocket("/{match_id}")
async def websocket_endpoint(websocket: WebSocket, match_id: str) -> None:
    """Relay bounded code/chat updates only between authenticated participants."""

    token = token_from_protocol_header(websocket.headers.get("sec-websocket-protocol", ""))
    player = validate_player_token(token) if token else None
    if player is None:
        await websocket.close(code=1008, reason="Authentication required")
        return

    db = SessionLocal()
    try:
        match = db.query(Match).filter(Match.id == match_id).first()
        is_participant = bool(
            match
            and player["id"] in {match.player1_id, match.player2_id}
        )
    finally:
        db.close()

    if not is_participant:
        await websocket.close(code=1008, reason="Match access denied")
        return

    await manager.connect(websocket, match_id)
    try:
        while True:
            data = await websocket.receive_text()
            if len(data.encode("utf-8")) > MAX_MESSAGE_BYTES:
                await websocket.close(code=1009, reason="Message too large")
                return

            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "ERROR", "detail": "Invalid JSON"})
                continue

            message_type = message.get("type") if isinstance(message, dict) else None
            if message_type == "CODE_SYNC":
                code = message.get("code")
                if not isinstance(code, str) or len(code) > MAX_CODE_CHARS:
                    await websocket.send_json({"type": "ERROR", "detail": "Invalid code update"})
                    continue
                outgoing = {
                    "type": "CODE_SYNC",
                    "code": code,
                    "player_id": player["id"],
                }
            elif message_type == "CHAT":
                text = message.get("text")
                if not isinstance(text, str) or not text.strip() or len(text) > MAX_CHAT_CHARS:
                    await websocket.send_json({"type": "ERROR", "detail": "Invalid chat message"})
                    continue
                outgoing = {
                    "type": "CHAT",
                    "text": text.strip(),
                    "player_id": player["id"],
                    "username": player["username"],
                }
            else:
                await websocket.send_json({"type": "ERROR", "detail": "Unsupported message type"})
                continue

            await manager.broadcast(
                json.dumps(outgoing, separators=(",", ":")),
                match_id,
                exclude=websocket,
            )
    except WebSocketDisconnect:
        pass
    except Exception:
        logger.exception("WebSocket failure in match %s", match_id)
    finally:
        manager.disconnect(websocket, match_id)
