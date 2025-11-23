"""
Database connection and session management using SQLAlchemy 2.0.

Provides:
    - Engine creation with connection pooling
    - Session factory for dependency injection
    - Base class for ORM models
    - Database initialization utilities
    - Cross-database JSONB type support
"""

from typing import Generator, Any, Optional, Type as TypingType, Union
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from sqlalchemy.pool import Pool, StaticPool
from sqlalchemy.types import JSON, TypeDecorator
from sqlalchemy.dialects.postgresql import JSONB as PostgreSQL_JSONB

from app.config import settings


class JSONBType(TypeDecorator):
    """
    Cross-database JSONB type that uses the appropriate JSON storage for each dialect.

    - PostgreSQL: Uses native JSONB type for efficient binary JSON storage
    - SQLite: Falls back to TEXT-based JSON storage
    - Other databases: Uses their native JSON type if available

    This TypeDecorator ensures consistent behavior across different database backends
    while leveraging database-specific optimizations where available.

    Example usage:
        class MyModel(Base):
            __tablename__ = 'my_table'
            data: Mapped[dict] = mapped_column(JSONBType, nullable=True)
            items: Mapped[list] = mapped_column(JSONBType, nullable=True)
    """

    impl = JSON
    cache_ok = True  # Safe for SQLAlchemy's statement cache

    def load_dialect_impl(self, dialect):
        """Return the appropriate JSON type implementation for the current dialect."""
        if dialect.name == 'postgresql':
            # Use native JSONB for PostgreSQL
            return dialect.type_descriptor(PostgreSQL_JSONB())
        else:
            # Use standard JSON for other databases (including SQLite)
            return dialect.type_descriptor(JSON())

    def process_bind_param(self, value, dialect):
        """Process value before sending to database."""
        if value is None:
            return value
        # Ensure we're working with dict or list
        if not isinstance(value, (dict, list)):
            raise TypeError(f"JSONBType expects dict or list, got {type(value).__name__}")
        return value

    def process_result_value(self, value, dialect):
        """Process value when loading from database."""
        # The underlying JSON/JSONB type handles deserialization
        return value


class JSONBDict(JSONBType):
    """
    JSONB type specifically for dictionary/object storage.

    Provides better type hints and validation for dictionary data.

    Example usage:
        class MyModel(Base):
            __tablename__ = 'my_table'
            settings: Mapped[Optional[dict]] = mapped_column(JSONBDict, nullable=True)
            metadata: Mapped[dict] = mapped_column(JSONBDict, default=dict)
    """

    def process_bind_param(self, value, dialect):
        """Validate that value is a dictionary before storage."""
        if value is None:
            return value
        if not isinstance(value, dict):
            raise TypeError(f"JSONBDict expects dict, got {type(value).__name__}")
        return value


class JSONBList(JSONBType):
    """
    JSONB type specifically for list/array storage.

    Provides better type hints and validation for list data.

    Example usage:
        class MyModel(Base):
            __tablename__ = 'my_table'
            tags: Mapped[Optional[list]] = mapped_column(JSONBList, nullable=True)
            items: Mapped[list] = mapped_column(JSONBList, default=list)
    """

    def process_bind_param(self, value, dialect):
        """Validate that value is a list before storage."""
        if value is None:
            return value
        if not isinstance(value, list):
            raise TypeError(f"JSONBList expects list, got {type(value).__name__}")
        return value


# Legacy function - kept for backward compatibility
def get_json_type():
    """
    Return appropriate JSON type based on database dialect.

    DEPRECATED: Use JSONBType, JSONBDict, or JSONBList instead.
    This function is kept for backward compatibility with existing code.
    """
    if "sqlite" in settings.DATABASE_URL:
        return JSON
    return PostgreSQL_JSONB


# Legacy alias - kept for backward compatibility
JSONB = get_json_type()

# Export new types for convenience
__all__ = [
    'Base',
    'engine',
    'SessionLocal',
    'get_db',
    'set_audit_context',
    'JSONBType',
    'JSONBDict',
    'JSONBList',
    'JSONB',  # Legacy
    'get_json_type',  # Legacy
    'is_sqlite',
    'is_postgresql',
]


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
        connect_args={
            "check_same_thread": False,  # SQLite specific
            "timeout": 30,  # Connection timeout in seconds
        },
        poolclass=StaticPool,  # Use static pool for SQLite
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


# Database dialect-specific event handlers
if "sqlite" in settings.DATABASE_URL:
    @event.listens_for(Pool, "connect")
    def set_sqlite_pragmas(dbapi_conn, _):
        """
        Configure SQLite pragmas for better concurrency and performance.

        WAL mode (Write-Ahead Logging) improves concurrent access by allowing
        reads to proceed during writes. NORMAL synchronous mode balances
        performance with safety.
        """
        cursor = dbapi_conn.cursor()
        # Enable WAL mode for better concurrent access
        cursor.execute("PRAGMA journal_mode=WAL")
        # NORMAL synchronous mode (instead of FULL) for better performance
        cursor.execute("PRAGMA synchronous=NORMAL")
        # Increase cache size for better performance
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
        # Enable foreign key constraint checking
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

elif "postgresql" in settings.DATABASE_URL:
    @event.listens_for(Pool, "connect")
    def set_session_variables(dbapi_conn, _):
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


def set_audit_context(
    db: Session,
    user_id: int,
    client_ip: str = "",
    user_agent: str = ""
) -> None:
    """
    Set audit context for current session.

    Uses parameterized queries to prevent SQL injection.

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
        db.execute(
            text("SET app.current_user_id = :user_id"),
            {"user_id": user_id}
        )
        db.execute(
            text("SET app.client_ip = :client_ip"),
            {"client_ip": client_ip}
        )
        db.execute(
            text("SET app.user_agent = :user_agent"),
            {"user_agent": user_agent}
        )
