from sqlalchemy.orm import Session
from typing import List, Tuple, Dict, Any
from app.models.audit import AuditLog
from app.models.user import User

class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        user_id: int,
        action: str,
        target_type: str | None = None,
        target_id: str | None = None,
        metadata_json: Dict[str, Any] | None = None
    ) -> AuditLog:
        audit = AuditLog(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=str(target_id) if target_id else None,
            metadata_json=metadata_json or {}
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(audit)
        return audit

    def get_logs(
        self,
        user_id: int | None = None,
        action: str | None = None,
        target_type: str | None = None,
        page: int = 1,
        limit: int = 50
    ) -> Tuple[List[Dict[str, Any]], int]:
        q = self.db.query(AuditLog, User.email).outerjoin(User, AuditLog.user_id == User.id)

        if user_id:
            q = q.filter(AuditLog.user_id == user_id)
        if action:
            q = q.filter(AuditLog.action == action)
        if target_type:
            q = q.filter(AuditLog.target_type == target_type)

        total = q.count()
        results = q.order_by(AuditLog.timestamp.desc()).offset((page - 1) * limit).limit(limit).all()

        formatted_logs = []
        for log, email in results:
            formatted_logs.append({
                "id": log.id,
                "user_id": log.user_id,
                "user_email": email,
                "action": log.action,
                "target_type": log.target_type,
                "target_id": log.target_id,
                "timestamp": log.timestamp,
                "metadata_json": log.metadata_json
            })

        return formatted_logs, total
