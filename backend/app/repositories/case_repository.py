from sqlalchemy.orm import Session
from typing import List, Tuple
from app.models.case import Case, CaseStatus, CaseSeverity
from app.schemas.case import CaseCreate, CaseUpdate

class CaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, case_id: int) -> Case | None:
        return self.db.query(Case).filter(Case.id == case_id).first()

    def get_all(
        self,
        status: str | None = None,
        assigned_to: int | None = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Case], int]:
        q = self.db.query(Case)

        if status:
            q = q.filter(Case.status == status)
        if assigned_to:
            q = q.filter(Case.assigned_to == assigned_to)

        total = q.count()
        cases = q.order_by(Case.updated_at.desc()).offset((page - 1) * limit).limit(limit).all()
        return cases, total

    def create(self, case_in: CaseCreate, user_id: int) -> Case:
        case = Case(
            title=case_in.title,
            description=case_in.description,
            severity=case_in.severity.value if hasattr(case_in.severity, "value") else str(case_in.severity),
            status=CaseStatus.OPEN.value,
            assigned_to=case_in.assigned_to or user_id,
            related_account_ids=case_in.related_account_ids,
            notes=[]
        )
        self.db.add(case)
        self.db.commit()
        self.db.refresh(case)
        return case

    def update(self, case: Case, case_in: CaseUpdate, new_note_entry: dict | None = None) -> Case:
        if case_in.title is not None:
            case.title = case_in.title
        if case_in.description is not None:
            case.description = case_in.description
        if case_in.status is not None:
            case.status = case_in.status.value if hasattr(case_in.status, "value") else str(case_in.status)
        if case_in.severity is not None:
            case.severity = case_in.severity.value if hasattr(case_in.severity, "value") else str(case_in.severity)
        if case_in.assigned_to is not None:
            case.assigned_to = case_in.assigned_to
        if case_in.related_account_ids is not None:
            case.related_account_ids = case_in.related_account_ids
        
        if new_note_entry:
            current_notes = list(case.notes or [])
            current_notes.append(new_note_entry)
            case.notes = current_notes

        self.db.commit()
        self.db.refresh(case)
        return case
