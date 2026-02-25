from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/{match_id}")
async def websocket_endpoint(websocket: WebSocket, match_id: str):
    """WebSocket endpoint for real-time match updates."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        logger.info(f"Client disconnected from match {match_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")