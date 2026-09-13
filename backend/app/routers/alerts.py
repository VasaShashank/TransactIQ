from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.routers.deps import get_current_user
from app.models.user import User
from app.services.risk_score_service import RiskScoreService
from app.core.websockets import ws_manager
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Alerts"])

@router.post("/api/v1/alerts/scan")
async def scan_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    queue = RiskScoreService(db, None, None).get_risk_queue(limit=20)
    published = 0
    for item in queue.items:
        if item.risk_level in {"HIGH", "CRITICAL"}:
            await ws_manager.broadcast({
                "type": "suspicious_cluster_detected",
                "account_id": item.account_id,
                "risk_score": item.risk_score,
                "message": item.reason
            })
            published += 1
    return {"scanned": len(queue.items), "published": published}

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
