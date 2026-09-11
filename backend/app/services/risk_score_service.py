import json
from sqlalchemy.orm import Session
from neo4j import Session as Neo4jSession
from redis import Redis
from app.core.config import settings
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.graph_repository import GraphRepository
from app.schemas.risk import RiskScoreResponse, RiskScoreBreakdown

class RiskScoreService:
    def __init__(self, db: Session, neo4j_session: Neo4jSession | None, redis_client: Redis | None = None):
        self.txn_repo = TransactionRepository(db)
        # GraphRepository is optional — if neo4j_session is None, graph signals default to zero
        self.graph_repo = GraphRepository(neo4j_session) if neo4j_session is not None else None
        self.redis = redis_client

    def calculate_risk_score(self, account_id: str) -> RiskScoreResponse:
        cache_key = f"risk_score:{account_id}"
        if self.redis:
            try:
                cached = self.redis.get(cache_key)
                if cached:
                    return RiskScoreResponse(**json.loads(cached))
            except Exception:
                pass

        # 1. Fetch transaction statistics from Postgres
        stats = self.txn_repo.get_account_transaction_stats(account_id)

        # 2. Fetch graph signals from Neo4j (optional — falls back to SQL-derived values)
        if self.graph_repo is not None:
            fan = self.graph_repo.get_fan_analysis(account_id)
            centrality = self.graph_repo.get_degree_centrality(account_id)
        else:
            # Derive fan-in/fan-out from PostgreSQL transaction table
            fan = self.txn_repo.get_fan_analysis_from_sql(account_id)
            centrality = self.txn_repo.get_centrality_from_sql(account_id)

        # Factor 1: Known Fraud / Flagged Txn Flag (0 – 100)
        has_fraud = 1.0 if stats["fraud_txns"] > 0 or stats["flagged_txns"] > 0 else 0.0
        fraud_score = has_fraud * 100.0

        # Factor 2: Txn Frequency Score
        txn_freq_score = min(100.0, (stats["total_txns"] / 10.0) * 100.0)

        # Factor 3: Outgoing Volume Score (scaled: > 200,000 => 100 score)
        outgoing_vol_score = min(100.0, (stats["outgoing_vol"] / 200000.0) * 100.0)

        # Factor 4: Number of Linked Accounts (Fan-in + Fan-out)
        total_linked = fan["fan_in_count"] + fan["fan_out_count"]
        linked_score = min(100.0, (total_linked / 15.0) * 100.0)

        # Factor 5: Graph Centrality (Degree centrality: > 20 degree => 100 score)
        centrality_score = min(100.0, (centrality["degree_centrality"] / 20.0) * 100.0)

        # Calculate Weighted Composite Score
        total_score = (
            settings.WEIGHT_KNOWN_FRAUD * fraud_score +
            settings.WEIGHT_TXN_FREQ * txn_freq_score +
            settings.WEIGHT_OUTGOING_VOL * outgoing_vol_score +
            settings.WEIGHT_NUM_LINKED * linked_score +
            settings.WEIGHT_CENTRALITY * centrality_score
        )

        total_score = round(min(100.0, max(0.0, total_score)), 2)

        # Risk Classification Level
        if total_score >= 75.0:
            risk_level = "CRITICAL"
        elif total_score >= 50.0:
            risk_level = "HIGH"
        elif total_score >= 25.0:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        breakdown = RiskScoreBreakdown(
            known_fraud_flag_score=round(fraud_score, 2),
            txn_frequency_score=round(txn_freq_score, 2),
            outgoing_volume_score=round(outgoing_vol_score, 2),
            num_linked_accounts_score=round(linked_score, 2),
            graph_centrality_score=round(centrality_score, 2)
        )

        graph_note = "" if self.graph_repo is not None else " (derived from PostgreSQL — Neo4j offline)"
        explainable_factors = {
            "known_fraud": f"{stats['fraud_txns']} confirmed fraud transaction(s) associated.",
            "txn_frequency": f"{stats['total_txns']} total transaction(s) recorded for this account.",
            "outgoing_volume": f"${stats['outgoing_vol']:,.2f} total outgoing transaction volume.",
            "linked_accounts": f"{total_linked} distinct linked counterparty account(s){graph_note}.",
            "graph_centrality": f"Degree centrality score of {centrality['degree_centrality']} (In: {centrality['in_degree']}, Out: {centrality['out_degree']}){graph_note}."
        }

        res = RiskScoreResponse(
            account_id=account_id,
            risk_score=total_score,
            risk_level=risk_level,
            breakdown=breakdown,
            explainable_factors=explainable_factors
        )

        if self.redis:
            try:
                self.redis.setex(cache_key, 600, json.dumps(res.model_dump()))
            except Exception:
                pass

        return res
