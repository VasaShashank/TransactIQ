from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from neo4j import Session as Neo4jSession
from redis import Redis
from app.core.database import get_db
from app.core.neo4j import get_neo4j_session
from app.core.redis import get_redis
from app.services.risk_score_service import RiskScoreService
from app.schemas.risk import RiskScoreResponse
from app.routers.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/accounts", tags=["Risk Score"])

@router.get("/{id}/risk-score", response_model=RiskScoreResponse)
def get_risk_score(
    id: str,
    db: Session = Depends(get_db),
    neo4j_session: Neo4jSession = Depends(get_neo4j_session),
    redis_client: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    if neo4j_session is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Neo4j graph database is not available. Risk scoring requires graph data."
        )
    service = RiskScoreService(db, neo4j_session, redis_client)
    return service.calculate_risk_score(account_id=id)

