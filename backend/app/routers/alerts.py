from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websockets import ws_manager
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Alerts"])

@router.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection open & receive optional messages/pings
            data = await websocket.receive_text()
            logger.debug(f"Received WS text: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)
