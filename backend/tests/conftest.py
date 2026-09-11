import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, get_db
from app.core.security import get_password_hash
from app.models.user import User, UserRole

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Seed admin & analyst users in sqlite test db
    admin = User(email="admin@test.com", hashed_password=get_password_hash("password"), role=UserRole.ADMIN.value)
    analyst = User(email="analyst@test.com", hashed_password=get_password_hash("password"), role=UserRole.ANALYST.value)
    db.add(admin)
    db.add(analyst)
    db.commit()
    db.close()

    yield
    Base.metadata.drop_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    return TestClient(app)
