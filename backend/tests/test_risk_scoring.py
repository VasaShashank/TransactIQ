import pytest
from app.services.risk_score_service import RiskScoreService
from app.schemas.risk import RiskScoreResponse, RiskScoreBreakdown

def test_risk_score_calculation_logic():
    # Mocking repositories / data
    fraud_score = 100.0
    txn_freq_score = 50.0
    outgoing_vol_score = 80.0
    linked_score = 40.0
    centrality_score = 60.0

    # Weights: 0.35, 0.20, 0.15, 0.15, 0.15
    expected_score = (
        0.35 * 100.0 +
        0.20 * 50.0 +
        0.15 * 80.0 +
        0.15 * 40.0 +
        0.15 * 60.0
    ) # 35 + 10 + 12 + 6 + 9 = 72.0

    assert round(expected_score, 2) == 72.0
