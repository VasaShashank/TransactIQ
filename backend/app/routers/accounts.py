from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from redis import Redis
from app.core.database import get_db
from app.core.redis import get_redis
from app.services.account_service import AccountService
from app.services.audit_service import AuditService
from app.schemas.account import AccountSearchResult, AccountSearchQueryParams
from app.schemas.transaction import TimelineResponse
from app.routers.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/accounts", tags=["Accounts"])

@router.get("/search", response_model=AccountSearchResult)
def search_accounts(
    query: str | None = Query(None, description="Account string ID search query"),
    type: str | None = Query(None, description="CUSTOMER or MERCHANT"),
    min_amount: float | None = Query(None),
    max_amount: float | None = Query(None),
    is_fraud: int | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    redis_client: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    params = AccountSearchQueryParams(
        query=query,
        type=type,
        min_amount=min_amount,
        max_amount=max_amount,
        is_fraud=is_fraud,
        page=page,
        limit=limit
    )
    service = AccountService(db, redis_client)
    res = service.search_accounts(params)

    # Audit logging
    audit = AuditService(db)
    audit.log_action(
        user_id=current_user.id,
        action="SEARCH",
        target_type="ACCOUNT",
        metadata_json={"query": query, "type": type, "min_amount": min_amount, "max_amount": max_amount, "is_fraud": is_fraud}
    )

    return res

@router.get("/{id}/timeline", response_model=TimelineResponse)
def get_account_timeline(
    id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    redis_client: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    service = AccountService(db, redis_client)
    return service.get_account_timeline(account_id=id, page=page, limit=limit)
