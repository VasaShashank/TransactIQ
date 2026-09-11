from fastapi import APIRouter, Depends, Response, HTTPException, status
from sqlalchemy.orm import Session
from neo4j import Session as Neo4jSession
from redis import Redis
from app.core.database import get_db
from app.core.neo4j import get_neo4j_session
from app.core.redis import get_redis
from app.repositories.case_repository import CaseRepository
from app.services.risk_score_service import RiskScoreService
from app.services.pdf_service import PDFService
from app.services.audit_service import AuditService
from app.routers.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/cases", tags=["Export"])

@router.get("/{id}/export")
def export_case_pdf(
    id: int,
    db: Session = Depends(get_db),
    neo4j_session: Neo4jSession = Depends(get_neo4j_session),
    redis_client: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    case_repo = CaseRepository(db)
    case = case_repo.get_by_id(id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    if neo4j_session is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Neo4j graph database is not available. PDF export requires graph data."
        )

    risk_service = RiskScoreService(db, neo4j_session, redis_client)
    pdf_bytes = PDFService.generate_case_pdf(case, risk_service)

    # Audit log
    audit = AuditService(db)
    audit.log_action(
        user_id=current_user.id,
        action="CASE_EXPORT",
        target_type="CASE",
        target_id=str(id),
        metadata_json={"format": "PDF"}
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=case_{id}_summary.pdf"}
    )
