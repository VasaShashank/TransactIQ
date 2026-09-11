from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, Token
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token

class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def register_user(self, user_in: UserCreate):
        existing = self.user_repo.get_by_email(user_in.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        hashed_password = get_password_hash(user_in.password)
        return self.user_repo.create(user_in, hashed_password)

    def authenticate_user(self, email: str, password: str) -> Token:
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = create_access_token(subject=user.id, role=user.role)
        refresh_token = create_refresh_token(subject=user.id, role=user.role)
        return Token(access_token=access_token, refresh_token=refresh_token)

    def refresh_access_token(self, refresh_token: str) -> Token:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        user_id = payload.get("sub")
        user = self.user_repo.get_by_id(int(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        new_access = create_access_token(subject=user.id, role=user.role)
        new_refresh = create_refresh_token(subject=user.id, role=user.role)
        return Token(access_token=new_access, refresh_token=new_refresh)
