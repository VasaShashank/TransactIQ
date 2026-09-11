from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.audit_service import AuditService
from app.schemas.audit import AuditLogListResponse
from app.routers.deps import require_role
from app.models.user import User, UserRole

router = APIRouter(prefix="/audit-logs", tags=["Audit Log"])

@router.get("", response_model=AuditLogListResponse)
def get_audit_logs(
    user_id: int | None = Query(None),
    action: str | None = Query(None),
    target_type: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(UserRole.ADMIN))
):
    service = AuditService(db)
    return service.get_audit_logs(
        user_id=user_id,
        action=action,
        target_type=target_type,
        page=page,
        limit=limit
    )
