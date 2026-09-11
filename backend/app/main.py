import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

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
    existing_acc_ids = set(r[0] for r in db.query(Account.id).all())
    customers = [f"C{9000000 + i}" for i in range(50) if f"C{9000000 + i}" not in existing_acc_ids]
    merchants = [f"M{9000000 + i}" for i in range(20) if f"M{9000000 + i}" not in existing_acc_ids]
    for cid in customers:
        db.add(Account(id=cid, node_type="CUSTOMER"))
    for mid in merchants:
        db.add(Account(id=mid, node_type="MERCHANT"))
    db.commit()

    all_customers = [r[0] for r in db.query(Account.id).filter(Account.node_type == "CUSTOMER").all()]
    all_merchants = [r[0] for r in db.query(Account.id).filter(Account.node_type == "MERCHANT").all()]
    if not all_customers:
        return

    txn_types = ["PAYMENT", "TRANSFER", "CASH_OUT", "DEBIT", "CASH_IN"]
    for step in range(1, 25):
        for _ in range(8):
            ttype = random.choices(txn_types, weights=[0.4, 0.25, 0.25, 0.05, 0.05])[0]
            orig = random.choice(all_customers)
            dest = random.choice(all_merchants if (ttype in ["PAYMENT", "CASH_OUT"] and all_merchants) else all_customers)
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
            # 1. Seed Admin user
            admin = db.query(User).filter(User.email == "admin@fraud.intel").first()
            if not admin:
                admin = User(
                    email="admin@fraud.intel",
                    hashed_password=get_password_hash("admin123"),
                    role=UserRole.ADMIN.value
                )
                db.add(admin)
            else:
                admin.hashed_password = get_password_hash("admin123")
            db.commit()

            # 2. Seed Analyst user
            analyst = db.query(User).filter(User.email == "analyst@fraud.intel").first()
            if not analyst:
                analyst = User(
                    email="analyst@fraud.intel",
                    hashed_password=get_password_hash("analyst123"),
                    role=UserRole.ANALYST.value
                )
                db.add(analyst)
            else:
                analyst.hashed_password = get_password_hash("analyst123")
            db.commit()
            logger.info("Default users seeded and verified successfully.")

            # 3. Seed sample accounts and transactions in separate block
            try:
                if db.query(Account).count() == 0:
                    logger.info("No transaction data detected in database. Auto-seeding initial PaySim dataset...")
                    seed_sample_data(db)
            except Exception as seed_err:
                logger.warning(f"Auto-seeding sample dataset failed (non-fatal): {seed_err}")
                db.rollback()

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

@app.get("/health")
def health_check():
    return {"status": "healthy", "project": settings.PROJECT_NAME}

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

