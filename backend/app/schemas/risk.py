from pydantic import BaseModel
from typing import Dict

class RiskScoreBreakdown(BaseModel):
    known_fraud_flag_score: float
    txn_frequency_score: float
    outgoing_volume_score: float
    num_linked_accounts_score: float
    graph_centrality_score: float

class RiskScoreResponse(BaseModel):
    account_id: str
    risk_score: float
    risk_level: str # LOW, MEDIUM, HIGH, CRITICAL
    breakdown: RiskScoreBreakdown
    explainable_factors: Dict[str, str]

class RiskQueueItem(BaseModel):
    account_id: str
    risk_score: float
    risk_level: str
    transaction_count: int
    fraud_count: int
    outgoing_volume: float
    velocity_score: float
    reason: str

class RiskQueueResponse(BaseModel):
    items: list[RiskQueueItem]
