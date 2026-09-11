from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String, nullable=False, index=True) # SEARCH, CASE_CREATE, CASE_UPDATE, CASE_EXPORT, GRAPH_VIEW
    target_type = Column(String, nullable=True) # ACCOUNT, CASE, SYSTEM
    target_id = Column(String, nullable=True) # account_id, case_id
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    metadata_json = Column(JSON, nullable=True)
