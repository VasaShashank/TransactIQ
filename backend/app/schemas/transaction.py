from pydantic import BaseModel
from typing import List

class TransactionResponse(BaseModel):
    id: int
    step: int
    type: str
    amount: float
    orig_account_id: str
    dest_account_id: str
    old_balance_orig: float
    new_balance_orig: float
    old_balance_dest: float
    new_balance_dest: float
    is_fraud: int
    is_flagged_fraud: int

    class Config:
        from_attributes = True

class TimelineResponse(BaseModel):
    account_id: str
    transactions: List[TransactionResponse]
    total: int
    page: int
    limit: int
