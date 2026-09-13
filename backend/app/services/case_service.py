from datetime import datetime, timezone

from app.models.case import CaseStatus
from app.models.user import User, UserRole
from app.repositories.case_repository import CaseRepository
from app.schemas.case import CaseCreate, CaseResponse, CaseUpdate
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


class CaseService:
    def __init__(self, db: Session):
        self.case_repo = CaseRepository(db)

    def get_case(self, case_id: int) -> CaseResponse:
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
        return CaseResponse.model_validate(case)

    def list_cases(self, status: str | None = None, assigned_to: int | None = None, page: int = 1, limit: int = 20):
        cases, total = self.case_repo.get_all(status=status, assigned_to=assigned_to, page=page, limit=limit)
        items = [CaseResponse.model_validate(c) for c in cases]
        return {"cases": items, "total": total, "page": page, "limit": limit}

    def create_case(self, case_in: CaseCreate, current_user: User) -> CaseResponse:
        case = self.case_repo.create(case_in, current_user.id)
        return CaseResponse.model_validate(case)

    def update_case(self, case_id: int, case_in: CaseUpdate, current_user: User) -> CaseResponse:
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

        elevated_roles = {UserRole.SENIOR_ANALYST.value, UserRole.ADMIN.value}
        if current_user.role not in elevated_roles and case.assigned_to != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Analysts can only modify cases assigned to them"
            )

        # RBAC Check: Only Admin can reassign or close cases
        if case_in.assigned_to is not None and case_in.assigned_to != case.assigned_to and current_user.role != UserRole.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can reassign case ownership"
            )

        if case_in.status is not None and case_in.status == CaseStatus.CLOSED and current_user.role not in elevated_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only senior analysts or administrators can approve case closure"
            )

        if case_in.status == CaseStatus.CLOSED and not case_in.verdict:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="A closure verdict is required")

        new_note_entry = None
        if case_in.new_note:
            new_note_entry = {
                "user_id": current_user.id,
                "user_email": current_user.email,
                "note": case_in.new_note,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        evidence_entry = None
        if case_in.evidence:
            evidence_entry = {
                **case_in.evidence.model_dump(),
                "added_by": current_user.id,
                "added_at": datetime.now(timezone.utc).isoformat()
            }

        updated_case = self.case_repo.update(case, case_in, new_note_entry=new_note_entry, evidence_entry=evidence_entry)
        if case_in.status == CaseStatus.CLOSED:
            now = datetime.now(timezone.utc)
            case.approved_by = current_user.id
            case.approved_at = now
            case.closed_by = current_user.id
            case.closed_at = now
            self.case_repo.db.commit()
            self.case_repo.db.refresh(case)
        return CaseResponse.model_validate(updated_case)

    def delete_case(self, case_id: int) -> None:
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
        self.case_repo.db.delete(case)
        self.case_repo.db.commit()
