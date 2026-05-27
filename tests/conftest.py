"""Shared pytest fixtures."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

# Use in-memory SQLite for tests — no MySQL needed
TEST_DB_URL = "sqlite:///./test_hiresense.db"

from database import Base, get_db
from main import app

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def recruiter_token(client):
    client.post("/auth/register", json={
        "full_name": "Test Recruiter",
        "email": "recruiter@test.com",
        "password": "testpass123",
        "role": "recruiter",
    })
    resp = client.post("/auth/login", json={
        "email": "recruiter@test.com",
        "password": "testpass123",
    })
    return resp.json()["access_token"]


@pytest.fixture
def candidate_token(client):
    client.post("/auth/register", json={
        "full_name": "Test Candidate",
        "email": "candidate@test.com",
        "password": "testpass123",
        "role": "candidate",
    })
    resp = client.post("/auth/login", json={
        "email": "candidate@test.com",
        "password": "testpass123",
    })
    return resp.json()["access_token"]
