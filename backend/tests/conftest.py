"""
Pytest configuration and global fixtures for F2X NeuroHub test suite.

Provides:
    - Test database setup/teardown
    - Test client for API testing
    - Authentication fixtures (tokens, users)
    - Database session fixtures
    - Factory fixtures for test data
"""

import os
import sys
import pytest
from typing import Generator
from unittest.mock import patch

# Mock the database configuration before importing the app
# CRITICAL: Must match TEST_DATABASE_URL to ensure app and tests use same DB
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.core import security
from app.models import User, UserRole
# Import all models to ensure tables are created
from app.models import (
    ProductModel,
    Process,
    Lot,
    Serial,
    ProcessData,
    AuditLog
)
from app.crud import user as user_crud
from app.schemas import UserCreate


# Test database URL (file-based SQLite for better isolation)
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Test session factory
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """
    Create test database schema once per test session.

    This fixture runs automatically before all tests and creates
    all tables in the in-memory SQLite database.
    """
    # Drop all tables first to ensure clean state
    Base.metadata.drop_all(bind=test_engine)
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    yield
    # Drop all tables after tests complete
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """
    Provide a clean database session for each test.

    Creates a new database session and clears data
    after the test completes, ensuring test isolation.

    Yields:
        SQLAlchemy session for testing
    """
    # Use a simple session without transaction
    session = TestSessionLocal()

    yield session

    session.close()

    # Clear all data from tables after each test
    # Use raw connection to bypass session
    from sqlalchemy import text
    with test_engine.begin() as conn:
        # Disable foreign key constraints temporarily for SQLite
        conn.execute(text("PRAGMA foreign_keys = OFF"))
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.execute(text("PRAGMA foreign_keys = ON"))


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """
    Provide FastAPI test client with database override.

    Args:
        db: Test database session

    Yields:
        TestClient for making API requests
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ============================================================================
# User Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def test_admin_user(db: Session) -> User:
    """
    Create and return a test ADMIN user.

    Args:
        db: Test database session

    Returns:
        User instance with ADMIN role
    """
    user_data = UserCreate(
        username="test_admin",
        email="admin@test.com",
        password="AdminPass123!",
        full_name="Test Admin",
        role=UserRole.ADMIN,
        department="IT",
        is_active=True,
    )
    user = user_crud.create(db, user_in=user_data)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_manager_user(db: Session) -> User:
    """
    Create and return a test MANAGER user.

    Args:
        db: Test database session

    Returns:
        User instance with MANAGER role
    """
    user_data = UserCreate(
        username="test_manager",
        email="manager@test.com",
        password="ManagerPass123!",
        full_name="Test Manager",
        role=UserRole.MANAGER,
        department="Production",
        is_active=True,
    )
    user = user_crud.create(db, user_in=user_data)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_operator_user(db: Session) -> User:
    """
    Create and return a test OPERATOR user.

    Args:
        db: Test database session

    Returns:
        User instance with OPERATOR role
    """
    user_data = UserCreate(
        username="test_operator",
        email="operator@test.com",
        password="OperatorPass123!",
        full_name="Test Operator",
        role=UserRole.OPERATOR,
        department="Manufacturing",
        is_active=True,
    )
    user = user_crud.create(db, user_in=user_data)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_inactive_user(db: Session) -> User:
    """
    Create and return an inactive user for testing access control.

    Args:
        db: Test database session

    Returns:
        User instance with is_active=False
    """
    user_data = UserCreate(
        username="test_inactive",
        email="inactive@test.com",
        password="InactivePass123!",
        full_name="Test Inactive",
        role=UserRole.OPERATOR,
        is_active=False,
    )
    user = user_crud.create(db, user_in=user_data)
    db.commit()
    db.refresh(user)
    return user


# ============================================================================
# Authentication Token Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def admin_token(test_admin_user: User) -> str:
    """
    Generate JWT token for admin user.

    Args:
        test_admin_user: Admin user fixture

    Returns:
        JWT access token string
    """
    return security.create_access_token(
        subject=test_admin_user.id,
        additional_claims={
            "role": test_admin_user.role.value,
            "username": test_admin_user.username,
        }
    )


@pytest.fixture(scope="function")
def manager_token(test_manager_user: User) -> str:
    """
    Generate JWT token for manager user.

    Args:
        test_manager_user: Manager user fixture

    Returns:
        JWT access token string
    """
    return security.create_access_token(
        subject=test_manager_user.id,
        additional_claims={
            "role": test_manager_user.role.value,
            "username": test_manager_user.username,
        }
    )


@pytest.fixture(scope="function")
def operator_token(test_operator_user: User) -> str:
    """
    Generate JWT token for operator user.

    Args:
        test_operator_user: Operator user fixture

    Returns:
        JWT access token string
    """
    return security.create_access_token(
        subject=test_operator_user.id,
        additional_claims={
            "role": test_operator_user.role.value,
            "username": test_operator_user.username,
        }
    )


@pytest.fixture(scope="function")
def inactive_token(test_inactive_user: User) -> str:
    """
    Generate JWT token for inactive user (for testing access denial).

    Args:
        test_inactive_user: Inactive user fixture

    Returns:
        JWT access token string
    """
    return security.create_access_token(
        subject=test_inactive_user.id,
        additional_claims={
            "role": test_inactive_user.role.value,
            "username": test_inactive_user.username,
        }
    )


# ============================================================================
# Helper Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def auth_headers_admin(admin_token: str) -> dict:
    """
    Generate authorization headers for admin user.

    Args:
        admin_token: Admin JWT token

    Returns:
        Headers dict with Bearer token
    """
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="function")
def auth_headers_manager(manager_token: str) -> dict:
    """
    Generate authorization headers for manager user.

    Args:
        manager_token: Manager JWT token

    Returns:
        Headers dict with Bearer token
    """
    return {"Authorization": f"Bearer {manager_token}"}


@pytest.fixture(scope="function")
def auth_headers_operator(operator_token: str) -> dict:
    """
    Generate authorization headers for operator user.

    Args:
        operator_token: Operator JWT token

    Returns:
        Headers dict with Bearer token
    """
    return {"Authorization": f"Bearer {operator_token}"}


@pytest.fixture(scope="function")
def auth_headers_inactive(inactive_token: str) -> dict:
    """
    Generate authorization headers for inactive user.

    Args:
        inactive_token: Inactive user JWT token

    Returns:
        Headers dict with Bearer token
    """
    return {"Authorization": f"Bearer {inactive_token}"}
