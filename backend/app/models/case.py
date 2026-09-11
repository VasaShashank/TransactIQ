import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class CaseStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"

class CaseSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default=CaseStatus.OPEN.value, nullable=False, index=True)
    severity = Column(String, default=CaseSeverity.MEDIUM.value, nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    related_account_ids = Column(JSON, default=list, nullable=False) # List of account string IDs
    notes = Column(JSON, default=list, nullable=False) # List of dicts: [{user_id, note, timestamp}]
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
