from sqlalchemy.orm import Session
from typing import Dict, Any
from app.repositories.audit_repository import AuditRepository
from app.schemas.audit import AuditLogListResponse, AuditLogResponse

class AuditService:
    def __init__(self, db: Session):
        self.audit_repo = AuditRepository(db)

    def log_action(
        self,
        user_id: int,
        action: str,
        target_type: str | None = None,
        target_id: str | None = None,
        metadata_json: Dict[str, Any] | None = None
    ):
        return self.audit_repo.log(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            metadata_json=metadata_json
        )

    def get_audit_logs(
        self,
        user_id: int | None = None,
        action: str | None = None,
        target_type: str | None = None,
        page: int = 1,
        limit: int = 50
    ) -> AuditLogListResponse:
        logs_data, total = self.audit_repo.get_logs(
            user_id=user_id,
            action=action,
            target_type=target_type,
            page=page,
            limit=limit
        )
        logs = [AuditLogResponse(**l) for l in logs_data]
        return AuditLogListResponse(
            logs=logs,
            total=total,
            page=page,
            limit=limit
        )
