from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List

class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    user_email: Optional[str] = None
    action: str
    target_type: Optional[str] = None
    target_id: Optional[str] = None
    timestamp: datetime
    metadata_json: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class AuditLogFilter(BaseModel):
    user_id: Optional[int] = None
    action: Optional[str] = None
    target_type: Optional[str] = None
    page: int = 1
    limit: int = 50

class AuditLogListResponse(BaseModel):
    logs: List[AuditLogResponse]
    total: int
    page: int
    limit: int
