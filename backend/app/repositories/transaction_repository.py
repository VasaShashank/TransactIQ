from sqlalchemy.orm import Session
from sqlalchemy import or_
from statistics import mean, pstdev
from app.models.account import Account
from typing import List, Tuple
from app.models.transaction import Transaction

class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_timeline_for_account(
        self,
        account_id: str,
        page: int = 1,
        limit: int = 50
    ) -> Tuple[List[Transaction], int]:
        q = self.db.query(Transaction).filter(
            or_(
                Transaction.orig_account_id == account_id,
                Transaction.dest_account_id == account_id
            )
        ).order_by(Transaction.step.asc(), Transaction.id.asc())

        total = q.count()
        txns = q.offset((page - 1) * limit).limit(limit).all()
        return txns, total

    def get_account_transaction_stats(self, account_id: str) -> dict:
        outgoing = self.db.query(Transaction).filter(Transaction.orig_account_id == account_id).all()
        incoming = self.db.query(Transaction).filter(Transaction.dest_account_id == account_id).all()

        total_txns = len(outgoing) + len(incoming)
        fraud_txns = sum(1 for t in outgoing if t.is_fraud == 1) + sum(1 for t in incoming if t.is_fraud == 1)
        flagged_txns = sum(1 for t in outgoing if t.is_flagged_fraud == 1) + sum(1 for t in incoming if t.is_flagged_fraud == 1)
        outgoing_vol = sum(t.amount for t in outgoing)
        incoming_vol = sum(t.amount for t in incoming)

        return {
            "total_txns": total_txns,
            "fraud_txns": fraud_txns,
            "flagged_txns": flagged_txns,
            "outgoing_vol": outgoing_vol,
            "incoming_vol": incoming_vol,
            "outgoing_count": len(outgoing),
            "incoming_count": len(incoming)
        }

    def get_risk_queue(self, limit: int = 20) -> list[dict]:
        accounts = self.db.query(Account.id).all()
        ranked = []
        for (account_id,) in accounts:
            stats = self.get_account_transaction_stats(account_id)
            if stats["total_txns"] == 0:
                continue
            transactions = self.db.query(Transaction).filter(
                or_(Transaction.orig_account_id == account_id, Transaction.dest_account_id == account_id)
            ).all()
            step_counts = {}
            for transaction in transactions:
                step_counts[transaction.step] = step_counts.get(transaction.step, 0) + 1
            counts = list(step_counts.values())
            baseline_mean = mean(counts)
            baseline_std = pstdev(counts) or 1.0
            peak_velocity_z = (max(counts) - baseline_mean) / baseline_std
            velocity_score = min(100.0, max(0.0, peak_velocity_z * 20.0 + (stats["total_txns"] / 50.0) * 25.0))
            fraud_score = min(100.0, stats["fraud_txns"] * 100.0)
            volume_score = min(100.0, (stats["outgoing_vol"] / 500000.0) * 100.0)
            risk_score = round(0.65 * fraud_score + 0.20 * velocity_score + 0.15 * volume_score, 2)
            if stats["fraud_txns"] and risk_score >= 75:
                risk_level = "CRITICAL"
            elif stats["fraud_txns"] and risk_score >= 55:
                risk_level = "HIGH"
            elif risk_score >= 30:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
            reasons = []
            if stats["fraud_txns"]:
                reasons.append(f"{stats['fraud_txns']} fraud transaction(s)")
            if velocity_score >= 50:
                reasons.append(f"velocity z-score {peak_velocity_z:.1f}")
            if volume_score >= 50:
                reasons.append(f"${stats['outgoing_vol']:,.0f} outgoing volume")
            ranked.append({
                "account_id": account_id,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "transaction_count": stats["total_txns"],
                "fraud_count": stats["fraud_txns"],
                "outgoing_volume": round(stats["outgoing_vol"], 2),
                "velocity_score": round(velocity_score, 2),
                "reason": ", ".join(reasons) or "Elevated transaction activity"
            })
        return sorted(ranked, key=lambda item: item["risk_score"], reverse=True)[:limit]
