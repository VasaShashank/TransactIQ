from sqlalchemy.orm import Session
from sqlalchemy import or_
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
