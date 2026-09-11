from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.case_service import CaseService
from app.services.audit_service import AuditService
from app.schemas.case import CaseCreate, CaseUpdate, CaseResponse
from app.routers.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/cases", tags=["Cases"])

@router.get("", response_model=dict)
def list_cases(
    status: str | None = Query(None),
    assigned_to: int | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = CaseService(db)
    return service.list_cases(status=status, assigned_to=assigned_to, page=page, limit=limit)

@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(
    case_in: CaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = CaseService(db)
    case_res = service.create_case(case_in, current_user)

    # Audit Log
    audit = AuditService(db)
    audit.log_action(
        user_id=current_user.id,
        action="CASE_CREATE",
        target_type="CASE",
        target_id=str(case_res.id),
        metadata_json={"title": case_in.title, "severity": case_in.severity}
    )
    return case_res

@router.get("/{id}", response_model=CaseResponse)
def get_case(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = CaseService(db)
    return service.get_case(id)

@router.patch("/{id}", response_model=CaseResponse)
def update_case(
    id: int,
    case_in: CaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = CaseService(db)
    case_res = service.update_case(id, case_in, current_user)

    # Audit Log
    audit = AuditService(db)
    audit.log_action(
        user_id=current_user.id,
        action="CASE_UPDATE",
        target_type="CASE",
        target_id=str(id),
        metadata_json={"status": case_in.status, "assigned_to": case_in.assigned_to}
    )
    return case_res
