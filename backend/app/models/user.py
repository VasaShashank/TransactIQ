import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from app.core.database import Base

class UserRole(str, enum.Enum):
    ANALYST = "analyst"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default=UserRole.ANALYST.value, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
