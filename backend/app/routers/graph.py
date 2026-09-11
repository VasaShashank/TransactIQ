from fastapi import APIRouter, Depends, Query, HTTPException, status
from neo4j import Session as Neo4jSession
from sqlalchemy.orm import Session
from redis import Redis
from app.core.database import get_db
from app.core.neo4j import get_neo4j_session
from app.core.redis import get_redis
from app.services.graph_service import GraphService
from app.services.audit_service import AuditService
from app.schemas.graph import GraphResponse, FanAnalysisResponse, CentralityResponse
from app.routers.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/accounts", tags=["Graph"])

def _require_neo4j(neo4j_session):
    if neo4j_session is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Neo4j graph database is not available. Graph features are disabled."
        )

@router.get("/{id}/graph", response_model=GraphResponse)
def get_account_graph(
    id: str,
    hops: int = Query(1, ge=1, le=3),
    neo4j_session: Neo4jSession = Depends(get_neo4j_session),
    redis_client: Redis = Depends(get_redis),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    _require_neo4j(neo4j_session)
    service = GraphService(neo4j_session, redis_client)
    res = service.get_graph(account_id=id, hops=hops)

    # Audit log
    audit = AuditService(db)
    audit.log_action(
        user_id=current_user.id,
        action="GRAPH_VIEW",
        target_type="ACCOUNT",
        target_id=id,
        metadata_json={"hops": hops}
    )
    return res

@router.get("/{id}/fan-analysis", response_model=FanAnalysisResponse)
def get_fan_analysis(
    id: str,
    neo4j_session: Neo4jSession = Depends(get_neo4j_session),
    redis_client: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    _require_neo4j(neo4j_session)
    service = GraphService(neo4j_session, redis_client)
    return service.get_fan_analysis(account_id=id)

@router.get("/{id}/centrality", response_model=CentralityResponse)
def get_centrality(
    id: str,
    neo4j_session: Neo4jSession = Depends(get_neo4j_session),
    redis_client: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    _require_neo4j(neo4j_session)
    service = GraphService(neo4j_session, redis_client)
    return service.get_centrality(account_id=id)
