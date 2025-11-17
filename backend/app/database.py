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

from app.config import settings


# Create SQLAlchemy engine
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
    """
    db.execute(f"SET app.current_user_id = '{user_id}'")
    db.execute(f"SET app.client_ip = '{client_ip}'")
    db.execute(f"SET app.user_agent = '{user_agent}'")
