from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
import logging
import json
from typing import Dict, List

logger = logging.getLogger(__name__)
router = APIRouter()

class ConnectionManager:
    def __init__(self):
        # match_id -> list of websockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, match_id: str):
        await websocket.accept()
        if match_id not in self.active_connections:
            self.active_connections[match_id] = []
        self.active_connections[match_id].append(websocket)
        logger.info(f"New connection to match {match_id}. Total: {len(self.active_connections[match_id])}")

    def disconnect(self, websocket: WebSocket, match_id: str):
        if match_id in self.active_connections:
            if websocket in self.active_connections[match_id]:
                self.active_connections[match_id].remove(websocket)
            if not self.active_connections[match_id]:
                del self.active_connections[match_id]
        logger.info(f"Disconnected from match {match_id}")

    async def broadcast(self, message: str, match_id: str, exclude: WebSocket = None):
        if match_id in self.active_connections:
            for connection in self.active_connections[match_id]:
                if connection != exclude:
                    try:
                        await connection.send_text(message)
                    except Exception as e:
                        logger.error(f"Error broadcasting to client in match {match_id}: {e}")

manager = ConnectionManager()

@router.websocket("/{match_id}")
async def websocket_endpoint(websocket: WebSocket, match_id: str):
    """WebSocket endpoint for real-time match updates."""
    await manager.connect(websocket, match_id)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                # Broadcast code updates to other players in the room
                if message.get("type") == "CODE_SYNC":
                    await manager.broadcast(data, match_id, exclude=websocket)
                elif message.get("type") == "CHAT":
                    await manager.broadcast(data, match_id, exclude=websocket)
                else:
                    # Echo or handle other types
                    await websocket.send_text(f"ACK: {message.get('type')}")
            except json.JSONDecodeError:
                # Fallback for plain text
                await websocket.send_text(f"Echo: {data}")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, match_id)
    except Exception as e:
        logger.error(f"WebSocket error in match {match_id}: {e}")
        manager.disconnect(websocket, match_id)