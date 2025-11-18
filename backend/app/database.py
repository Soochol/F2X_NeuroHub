"""
Database connection and session management using SQLAlchemy 2.0.

Provides:
    - Engine creation with connection pooling
    - Session factory for dependency injection
    - Base class for ORM models
    - Database initialization utilities
"""

from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from sqlalchemy.pool import Pool
from sqlalchemy.types import JSON
from sqlalchemy.dialects.postgresql import JSONB as PostgreSQL_JSONB

from app.config import settings


# JSONB compatibility: Use JSON for SQLite, JSONB for PostgreSQL
def get_json_type():
    """Return appropriate JSON type based on database dialect."""
    if "sqlite" in settings.DATABASE_URL:
        return JSON
    return PostgreSQL_JSONB


# Alias for easier imports
JSONB = get_json_type()


# Database dialect helpers
def is_sqlite() -> bool:
    """Check if current database is SQLite."""
    return "sqlite" in settings.DATABASE_URL


def is_postgresql() -> bool:
    """Check if current database is PostgreSQL."""
    return "postgresql" in settings.DATABASE_URL


# Create SQLAlchemy engine
# SQLite doesn't support pool_size and max_overflow, so we check the dialect
if "sqlite" in settings.DATABASE_URL:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DB_ECHO,
        connect_args={"check_same_thread": False},  # SQLite specific
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DB_ECHO,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,
        max_overflow=20,
    )


# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# Base class for ORM models
class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# Set PostgreSQL session variables for audit logging
# (Only for PostgreSQL, not SQLite)
if "postgresql" in settings.DATABASE_URL:
    @event.listens_for(Pool, "connect")
    def set_session_variables(dbapi_conn, connection_record):
        """
        Set PostgreSQL session variables on connection.
        These are used by audit triggers to log user actions.
        """
        cursor = dbapi_conn.cursor()
        # Set default values - will be overridden by application
        cursor.execute("SET app.current_user_id = '0'")
        cursor.execute("SET app.client_ip = 'unknown'")
        cursor.execute("SET app.user_agent = 'unknown'")
        cursor.close()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.

    Usage in FastAPI:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()

    Yields:
        Session: SQLAlchemy session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def set_audit_context(db: Session, user_id: int, client_ip: str = "", user_agent: str = ""):
    """
    Set audit context for current session.

    Args:
        db: Database session
        user_id: Current user ID
        client_ip: Client IP address
        user_agent: User agent string

    Note:
        Only works with PostgreSQL. SQLite does not support session variables.
    """
    # Only execute for PostgreSQL
    if "postgresql" in settings.DATABASE_URL:
        db.execute(f"SET app.current_user_id = '{user_id}'")
        db.execute(f"SET app.client_ip = '{client_ip}'")
        db.execute(f"SET app.user_agent = '{user_agent}'")
