from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.case_repository import CaseRepository
from app.schemas.case import CaseCreate, CaseUpdate, CaseResponse
from app.models.user import User, UserRole

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

        # RBAC Check: Admins can update any case; Analysts can only update cases assigned to them
        if current_user.role != UserRole.ADMIN.value and case.assigned_to != current_user.id:
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

        if case_in.status is not None and case_in.status == "closed" and current_user.role != UserRole.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can close investigation cases"
            )

        new_note_entry = None
        if case_in.new_note:
            new_note_entry = {
                "user_id": current_user.id,
                "user_email": current_user.email,
                "note": case_in.new_note,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        updated_case = self.case_repo.update(case, case_in, new_note_entry=new_note_entry)
        return CaseResponse.model_validate(updated_case)
