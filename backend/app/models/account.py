from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.sql import func
from app.core.database import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True, index=True) # PaySim account string, e.g. C123456789 or M987654321
    node_type = Column(String, nullable=False, default="CUSTOMER") # CUSTOMER (C) or MERCHANT (M)
    phone = Column(String, nullable=True, index=True)
    email = Column(String, nullable=True, index=True)
    device_id = Column(String, nullable=True, index=True)
    card_id = Column(String, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

Index("idx_accounts_node_type", Account.node_type)
