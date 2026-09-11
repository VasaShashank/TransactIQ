import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

logger = logging.getLogger(__name__)

def create_db_engine():
    url = settings.get_database_url()
    if "sqlite" in url:
        return create_engine(url, connect_args={"check_same_thread": False})
    
    try:
        eng = create_engine(
            url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
        with eng.connect() as conn:
            pass
        logger.info("Connected to PostgreSQL database successfully.")
        return eng
    except Exception as e:
        logger.warning(
            f"Could not connect to PostgreSQL ({e}). "
            "Falling back to embedded SQLite database (transactiq.db) so all features and authentication remain fully active."
        )
        return create_engine(
            "sqlite:///./transactiq.db",
            connect_args={"check_same_thread": False}
        )

engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
