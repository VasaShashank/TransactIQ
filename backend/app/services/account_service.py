import json
from sqlalchemy.orm import Session
from redis import Redis
from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.account import AccountSearchQueryParams, AccountSearchResult, AccountResponse
from app.schemas.transaction import TimelineResponse, TransactionResponse

class AccountService:
    def __init__(self, db: Session, redis_client: Redis | None = None):
        self.account_repo = AccountRepository(db)
        self.txn_repo = TransactionRepository(db)
        self.redis = redis_client

    def search_accounts(self, params: AccountSearchQueryParams) -> AccountSearchResult:
        accounts, total = self.account_repo.search_accounts(
            query=params.query,
            node_type=params.type,
            min_amount=params.min_amount,
            max_amount=params.max_amount,
            is_fraud=params.is_fraud,
            page=params.page,
            limit=params.limit
        )
        items = [AccountResponse.model_validate(acc) for acc in accounts]
        return AccountSearchResult(
            accounts=items,
            total=total,
            page=params.page,
            limit=params.limit
        )

    def get_account_timeline(self, account_id: str, page: int = 1, limit: int = 50) -> TimelineResponse:
        cache_key = f"timeline:{account_id}:p{page}:l{limit}"
        
        # Check Redis Cache
        if self.redis:
            try:
                cached = self.redis.get(cache_key)
                if cached:
                    data = json.loads(cached)
                    return TimelineResponse(**data)
            except Exception:
                pass

        txns, total = self.txn_repo.get_timeline_for_account(account_id, page=page, limit=limit)
        items = [TransactionResponse.model_validate(t) for t in txns]
        res = TimelineResponse(
            account_id=account_id,
            transactions=items,
            total=total,
            page=page,
            limit=limit
        )

        # Cache in Redis with 300s TTL (PaySim is static data)
        if self.redis:
            try:
                self.redis.setex(cache_key, 300, json.dumps(res.model_dump()))
            except Exception:
                pass

        return res
