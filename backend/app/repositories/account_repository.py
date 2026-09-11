from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Tuple
from app.models.account import Account
from app.models.transaction import Transaction

class AccountRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, account_id: str) -> Account | None:
        return self.db.query(Account).filter(Account.id == account_id).first()

    def search_accounts(
        self,
        query: str | None = None,
        node_type: str | None = None,
        min_amount: float | None = None,
        max_amount: float | None = None,
        is_fraud: int | None = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Account], int]:
        q = self.db.query(Account)

        if query:
            q = q.filter(Account.id.ilike(f"%{query}%"))
        
        if node_type:
            q = q.filter(Account.node_type == node_type.upper())

        # If transaction-level filters are specified, join with transactions
        if min_amount is not None or max_amount is not None or is_fraud is not None:
            txn_subq = self.db.query(Transaction.orig_account_id).union(
                self.db.query(Transaction.dest_account_id)
            )
            txn_filter = self.db.query(Transaction)
            if min_amount is not None:
                txn_filter = txn_filter.filter(Transaction.amount >= min_amount)
            if max_amount is not None:
                txn_filter = txn_filter.filter(Transaction.amount <= max_amount)
            if is_fraud is not None:
                txn_filter = txn_filter.filter(Transaction.is_fraud == is_fraud)
            
            matching_txn_accounts = self.db.query(Transaction.orig_account_id).filter(
                Transaction.id.in_(txn_filter.with_entities(Transaction.id))
            ).union(
                self.db.query(Transaction.dest_account_id).filter(
                    Transaction.id.in_(txn_filter.with_entities(Transaction.id))
                )
            ).subquery()

            q = q.filter(Account.id.in_(matching_txn_accounts))

        total = q.count()
        accounts = q.offset((page - 1) * limit).limit(limit).all()
        return accounts, total
