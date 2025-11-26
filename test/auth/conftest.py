import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.database import Base, get_db
from main import app
from dao import UserDAO

# Test database in the test folder
TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():

    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():

    Base.metadata.create_all(bind=engine)

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def admin_user(db_session):
    user = UserDAO.create_user(
        db=db_session,
        username="admin",
        email="admin@test.com",
        password="admin123",
        roles=["ROLE_ADMIN", "ROLE_USER"]
    )
    return user


@pytest.fixture
def regular_user(db_session):

    user = UserDAO.create_user(
        db=db_session,
        username="user",
        email="user@test.com",
        password="user123",
        roles=["ROLE_USER"]
    )
    return user


@pytest.fixture
def admin_token(client, admin_user):

    response = client.post(
        "/login",
        json={"username": "admin", "password": "admin123"}
    )
    return response.json()["access_token"]


@pytest.fixture
def user_token(client, regular_user):

    response = client.post(
        "/login",
        json={"username": "user", "password": "user123"}
    )
    return response.json()["access_token"]
