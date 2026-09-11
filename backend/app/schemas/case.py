from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Any
from app.models.case import CaseStatus, CaseSeverity

class CaseNote(BaseModel):
    user_id: int
    user_email: Optional[str] = None
    note: str
    timestamp: str

class CaseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    severity: CaseSeverity = CaseSeverity.MEDIUM
    assigned_to: Optional[int] = None
    related_account_ids: List[str] = []

class CaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CaseStatus] = None
    severity: Optional[CaseSeverity] = None
    assigned_to: Optional[int] = None
    related_account_ids: Optional[List[str]] = None
    new_note: Optional[str] = None

class CaseResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: CaseStatus
    severity: CaseSeverity
    assigned_to: Optional[int] = None
    related_account_ids: List[str]
    notes: List[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
