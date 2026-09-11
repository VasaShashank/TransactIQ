from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, UserResponse, Token, RefreshTokenRequest
from app.routers.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.register_user(user_in)

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.authenticate_user(form_data.username, form_data.password)

@router.post("/refresh", response_model=Token)
def refresh_token(body: RefreshTokenRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.refresh_access_token(body.refresh_token)

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
