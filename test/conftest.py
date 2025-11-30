import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.database import Base, get_db
from main import app
from dao import UserDAO, MovieDAO, LinkDAO, RatingDAO, TagDAO

# Test database in the test root folder
TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_integration.db")
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
    """Test client with clean database for each test"""
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def db_session():
    """Database session for fixtures"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


# ============================================================================
# AUTH FIXTURES
# ============================================================================

@pytest.fixture
def admin_user(db_session):
    """Create admin user for testing"""
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
    """Create regular user for testing"""
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
    """Get JWT token for admin user"""
    response = client.post(
        "/login",
        json={"username": "admin", "password": "admin123"}
    )
    return response.json()["access_token"]


@pytest.fixture
def user_token(client, regular_user):
    """Get JWT token for regular user"""
    response = client.post(
        "/login",
        json={"username": "user", "password": "user123"}
    )
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(user_token):
    """Get authorization headers with user token"""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_headers(admin_token):
    """Get authorization headers with admin token"""
    return {"Authorization": f"Bearer {admin_token}"}


# ============================================================================
# MOVIE FIXTURES
# ============================================================================

@pytest.fixture
def sample_movies(db_session):
    """Create sample movies for testing"""
    movies = [
        MovieDAO.create(db_session, movie_id=1, title="The Matrix", genres="Action|Sci-Fi"),
        MovieDAO.create(db_session, movie_id=2, title="Inception", genres="Action|Thriller|Sci-Fi"),
        MovieDAO.create(db_session, movie_id=3, title="The Godfather", genres="Crime|Drama"),
    ]
    db_session.commit()
    return movies


@pytest.fixture
def single_movie(db_session):
    """Create a single movie for testing"""
    movie = MovieDAO.create(db_session, movie_id=100, title="Test Movie", genres="Drama")
    db_session.commit()
    return movie


# ============================================================================
# LINK FIXTURES
# ============================================================================

@pytest.fixture
def sample_links(db_session, sample_movies):
    """Create sample links for testing"""
    links = [
        LinkDAO.create(db_session, movie_id=1, imdb_id="tt0133093", tmdb_id="603"),
        LinkDAO.create(db_session, movie_id=2, imdb_id="tt1375666", tmdb_id="27205"),
        LinkDAO.create(db_session, movie_id=3, imdb_id="tt0068646", tmdb_id="238"),
    ]
    db_session.commit()
    return links


@pytest.fixture
def single_link(db_session, single_movie):
    """Create a single link for testing"""
    link = LinkDAO.create(db_session, movie_id=100, imdb_id="tt9999999", tmdb_id="99999")
    db_session.commit()
    return link


# ============================================================================
# RATING FIXTURES
# ============================================================================

@pytest.fixture
def sample_ratings(db_session, sample_movies):
    """Create sample ratings for testing"""
    ratings = [
        RatingDAO.create(db_session, user_id=1, movie_id=1, rating=5.0, timestamp=1609459200),
        RatingDAO.create(db_session, user_id=1, movie_id=2, rating=4.5, timestamp=1609459300),
        RatingDAO.create(db_session, user_id=2, movie_id=1, rating=4.0, timestamp=1609459400),
        RatingDAO.create(db_session, user_id=2, movie_id=3, rating=5.0, timestamp=1609459500),
    ]
    db_session.commit()
    return ratings


@pytest.fixture
def single_rating(db_session, single_movie):
    """Create a single rating for testing"""
    rating = RatingDAO.create(db_session, user_id=10, movie_id=100, rating=3.5, timestamp=1609459600)
    db_session.commit()
    return rating


# ============================================================================
# TAG FIXTURES
# ============================================================================

@pytest.fixture
def sample_tags(db_session, sample_movies):
    """Create sample tags for testing"""
    tags = [
        TagDAO.create(db_session, user_id=1, movie_id=1, tag="mind-bending", timestamp=1609459200),
        TagDAO.create(db_session, user_id=1, movie_id=2, tag="complex", timestamp=1609459300),
        TagDAO.create(db_session, user_id=2, movie_id=1, tag="classic", timestamp=1609459400),
        TagDAO.create(db_session, user_id=2, movie_id=3, tag="masterpiece", timestamp=1609459500),
        TagDAO.create(db_session, user_id=3, movie_id=2, tag="confusing", timestamp=1609459600),
    ]
    db_session.commit()
    return tags


@pytest.fixture
def single_tag(db_session, single_movie):
    """Create a single tag for testing"""
    tag = TagDAO.create(db_session, user_id=10, movie_id=100, tag="test-tag", timestamp=1609459700)
    db_session.commit()
    return tag

