from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Any
from app.models.case import CaseStatus, CaseSeverity, CaseVerdict

class CaseNote(BaseModel):
    user_id: int
    user_email: Optional[str] = None
    note: str
    timestamp: str

class CaseEvidenceInput(BaseModel):
    account_id: Optional[str] = None
    transaction_id: Optional[int] = None
    note: Optional[str] = None

class CaseEvidence(CaseEvidenceInput):
    added_by: int
    added_at: datetime

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
    evidence: Optional[CaseEvidenceInput] = None
    verdict: Optional[CaseVerdict] = None

class CaseResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: CaseStatus
    severity: CaseSeverity
    assigned_to: Optional[int] = None
    related_account_ids: List[str]
    notes: List[dict]
    evidence: List[dict]
    verdict: Optional[CaseVerdict] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    closed_by: Optional[int] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
