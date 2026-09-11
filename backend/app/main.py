import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

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
    try:
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
    except Exception as e:
        logger.error(f"Database initialization failed (PostgreSQL connection error): {e}")
        logger.warning(
            "Application started, but PostgreSQL is currently unreachable. "
            "Please ensure the DATABASE_URL environment variable is set to a valid PostgreSQL connection string in your deployment environment."
        )

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

# Frontend SPA Static Files serving
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if not os.path.exists(static_dir):
    static_dir = os.path.abspath("static")

if os.path.exists(static_dir) and os.path.isfile(os.path.join(static_dir, "index.html")):
    assets_dir = os.path.join(static_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        if full_path.startswith("api") or full_path.startswith("ws") or full_path in ("docs", "redoc", "openapi.json", "health"):
            raise HTTPException(status_code=404, detail="Not Found")
        target_file = os.path.join(static_dir, full_path)
        if full_path and os.path.isfile(target_file):
            return FileResponse(target_file)
        return FileResponse(os.path.join(static_dir, "index.html"))
else:
    @app.get("/", include_in_schema=False)
    def root():
        return RedirectResponse(url="/docs")

