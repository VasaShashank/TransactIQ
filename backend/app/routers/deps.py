from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from neo4j import Session as Neo4jSession
from redis import Redis
from app.core.database import get_db
from app.core.neo4j import get_neo4j_session
from app.core.redis import get_redis
from app.core.security import decode_token
from app.repositories.user_repository import UserRepository
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate access credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

def require_role(allowed_role: UserRole):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        role_order = {
            UserRole.ANALYST.value: 1,
            UserRole.SENIOR_ANALYST.value: 2,
            UserRole.ADMIN.value: 3,
        }
        if role_order.get(current_user.role, 0) < role_order[allowed_role.value]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires {allowed_role.value} privilege"
            )
        return current_user
    return role_checker
