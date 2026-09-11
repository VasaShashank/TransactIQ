from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.routers import auth, accounts, graph, risk, cases, audit, alerts, export

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables if not present & seed default users
    logger.info("Initializing database schemas...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Seed Admin user
        admin = db.query(User).filter(User.email == "admin@fraud.intel").first()
        if not admin:
            admin = User(
                email="admin@fraud.intel",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN.value
            )
            db.add(admin)

        # Seed Analyst user
        analyst = db.query(User).filter(User.email == "analyst@fraud.intel").first()
        if not analyst:
            analyst = User(
                email="analyst@fraud.intel",
                hashed_password=get_password_hash("analyst123"),
                role=UserRole.ANALYST.value
            )
            db.add(analyst)

        db.commit()
        logger.info("Database initialized & default users seeded successfully.")
    except Exception as e:
        logger.error(f"Error seeding default users: {e}")
        db.rollback()
    finally:
        db.close()

    yield
    logger.info("Shutting down API server...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(accounts.router, prefix=settings.API_V1_STR)
app.include_router(graph.router, prefix=settings.API_V1_STR)
app.include_router(risk.router, prefix=settings.API_V1_STR)
app.include_router(cases.router, prefix=settings.API_V1_STR)
app.include_router(audit.router, prefix=settings.API_V1_STR)
app.include_router(export.router, prefix=settings.API_V1_STR)
app.include_router(alerts.router)

@app.get("/health")
def health_check():
    return {"status": "healthy", "project": settings.PROJECT_NAME}
