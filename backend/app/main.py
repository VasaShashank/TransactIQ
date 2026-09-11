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
from app.models.account import Account
from app.models.transaction import Transaction
from app.routers import auth, accounts, graph, risk, cases, audit, alerts, export

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_sample_data(db):
    import random
    random.seed(42)
    customers = [f"C{random.randint(1000000, 9999999)}" for _ in range(50)]
    merchants = [f"M{random.randint(1000000, 9999999)}" for _ in range(20)]
    for cid in customers:
        db.add(Account(id=cid, node_type="CUSTOMER"))
    for mid in merchants:
        db.add(Account(id=mid, node_type="MERCHANT"))
    db.flush()

    txn_types = ["PAYMENT", "TRANSFER", "CASH_OUT", "DEBIT", "CASH_IN"]
    for step in range(1, 25):
        for _ in range(10):
            ttype = random.choices(txn_types, weights=[0.4, 0.25, 0.25, 0.05, 0.05])[0]
            orig = random.choice(customers)
            dest = random.choice(merchants if ttype in ["PAYMENT", "CASH_OUT"] else customers)
            amount = round(random.uniform(50.0, 15000.0), 2)
            is_fraud = 1 if (ttype in ["TRANSFER", "CASH_OUT"] and amount > 7000.0 and random.random() < 0.25) else 0

            db.add(Transaction(
                step=step,
                type=ttype,
                amount=amount,
                orig_account_id=orig,
                dest_account_id=dest,
                old_balance_orig=amount + 5000.0,
                new_balance_orig=5000.0,
                old_balance_dest=1000.0,
                new_balance_dest=1000.0 + amount,
                is_fraud=is_fraud,
                is_flagged_fraud=is_fraud
            ))
    db.commit()
    logger.info("Sample PaySim accounts and transactions seeded successfully.")

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

            # Seed sample accounts and transactions if empty
            if db.query(Account).count() == 0:
                logger.info("No transaction data detected in database. Auto-seeding initial PaySim dataset...")
                seed_sample_data(db)

            db.commit()
            logger.info("Database initialized & default users seeded successfully.")
        except Exception as e:
            logger.error(f"Error seeding default users: {e}")
            db.rollback()
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

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

@app.api_route("/health", methods=["GET", "HEAD"])
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

    @app.api_route("/{full_path:path}", methods=["GET", "HEAD"], include_in_schema=False)
    async def serve_spa(full_path: str):
        if full_path.startswith("api") or full_path.startswith("ws") or full_path in ("docs", "redoc", "openapi.json", "health"):
            raise HTTPException(status_code=404, detail="Not Found")
        target_file = os.path.join(static_dir, full_path)
        if full_path and os.path.isfile(target_file):
            return FileResponse(target_file)
        return FileResponse(os.path.join(static_dir, "index.html"))
else:
    @app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
    def root():
        return RedirectResponse(url="/docs")

