from typing import Generator

import pytest
from app.api.deps import get_db_session
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.test_config import (
    TestingSessionLocal,
    create_test_database,
    drop_test_database,
)

# ============================================================================
# Database Fixtures
# ===========================================================================


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Create test database tables before all tests
    and drop them after all tests complete.
    Runs once per test session.
    """
    create_test_database()
    yield
    drop_test_database()


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Create a new database session for each test.
    Automatically rolls back changes after each test.
    """
    session = TestingSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        # Clean up all data after each test
        session.close()
        # Create a new session to clean tables
        cleanup_session = TestingSessionLocal()
        try:
            from app.models.todo import Todo

            cleanup_session.query(Todo).delete()
            cleanup_session.commit()
        finally:
            cleanup_session.close()


# ============================================================================
# FastAPI Client Fixtures
# ============================================================================


@pytest.fixture(scope="function")
def client(db_session: Session):
    """
    Create a TestClient with overridden database dependency.
    Each test gets a fresh client with isolated database session.
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db_session] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ============================================================================
# Async Client Fixture (for async tests)
# ============================================================================


@pytest.fixture(scope="function")
async def async_client(db_session: Session):
    """
    Create an async HTTP client for testing async endpoints
    """
    from httpx import AsyncClient

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db_session] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
