from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class AccountResponse(BaseModel):
    id: str
    node_type: str
    phone: Optional[str] = None
    email: Optional[str] = None
    device_id: Optional[str] = None
    card_id: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AccountSearchQueryParams(BaseModel):
    query: Optional[str] = None
    type: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    is_fraud: Optional[int] = None
    page: int = 1
    limit: int = 20

class AccountSearchResult(BaseModel):
    accounts: List[AccountResponse]
    total: int
    page: int
    limit: int
