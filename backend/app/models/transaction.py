from sqlalchemy import Column, BigInteger, String, Float, Integer, ForeignKey, Index
from app.core.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    step = Column(Integer, nullable=False, index=True) # Time step in hours
    type = Column(String, nullable=False, index=True) # PAYMENT, TRANSFER, CASH_OUT, DEBIT, CASH_IN
    amount = Column(Float, nullable=False, index=True)
    orig_account_id = Column(String, ForeignKey("accounts.id"), nullable=False, index=True)
    dest_account_id = Column(String, ForeignKey("accounts.id"), nullable=False, index=True)
    old_balance_orig = Column(Float, nullable=False)
    new_balance_orig = Column(Float, nullable=False)
    old_balance_dest = Column(Float, nullable=False)
    new_balance_dest = Column(Float, nullable=False)
    is_fraud = Column(Integer, nullable=False, default=0, index=True)
    is_flagged_fraud = Column(Integer, nullable=False, default=0, index=True)

Index("idx_transactions_orig_dest", Transaction.orig_account_id, Transaction.dest_account_id)
Index("idx_transactions_fraud", Transaction.is_fraud)
