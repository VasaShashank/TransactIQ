from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.ANALYST

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str | None = None
    role: str | None = None
    type: str | None = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str
