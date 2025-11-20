"""
ErrorLog model for centralized error logging and monitoring.

This module defines the ErrorLog ORM model that represents the error_logs table in the
F2X NeuroHub database. It provides error logging functionality for monitoring, debugging,
and analytics of all API errors.

Provides:
    - ErrorLog: SQLAlchemy ORM model for the error_logs table

Database Table: error_logs
    - Primary Key: id (BIGSERIAL)
    - Unique Key: trace_id (UUID)
    - Foreign Keys: user_id (optional)
    - Indexes: timestamp, error_code, trace_id, user_id, path, status_code
    - Partitioning: Monthly partitions by timestamp for performance
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    Index,
    String,
    Text,
    DateTime,
    Integer,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID, JSONB

from app.database import Base


class ErrorLog(Base):
    """
    ErrorLog model for centralized error logging.

    Represents an API error in the MES system that has been logged for monitoring,
    debugging, and analytics purposes. Automatically captured by ErrorLoggingMiddleware
    for all 4xx and 5xx HTTP responses.

    Attributes:
        id: Unique identifier (auto-incrementing primary key)
        trace_id: Unique trace ID for frontend-backend correlation (UUID)
        error_code: Standardized error code from ErrorCode enum (e.g., RES_001, VAL_002)
        message: Human-readable error message
        path: API endpoint path where error occurred
        method: HTTP method (GET, POST, PUT, DELETE, PATCH)
        status_code: HTTP status code (4xx or 5xx)
        user_id: Optional reference to user who triggered the error
        details: Additional error details in JSONB format
        timestamp: Timestamp when error occurred

    Table Name: error_logs

    Constraints:
        - PK: pk_error_logs on (id, timestamp) - for partitioning
        - UNIQUE: trace_id - each error has unique trace ID
        - FK: fk_error_logs_user on user_id → users.id
        - CHECK: chk_error_logs_status_code - status_code BETWEEN 400 AND 599
        - CHECK: chk_error_logs_method - method IN ('GET', 'POST', 'PUT', 'DELETE', 'PATCH', etc.)

    Indexes:
        - idx_error_logs_timestamp: (timestamp DESC)
        - idx_error_logs_error_code: (error_code, timestamp DESC)
        - idx_error_logs_trace_id: (trace_id) UNIQUE
        - idx_error_logs_user_id: (user_id, timestamp DESC) WHERE user_id IS NOT NULL
        - idx_error_logs_path: (path, timestamp DESC) WHERE path IS NOT NULL
        - idx_error_logs_status_code: (status_code, timestamp DESC)
        - idx_error_logs_details: GIN index on details JSONB

    Partitioning:
        - Monthly partitions by timestamp (error_logs_y2025m11, error_logs_y2025m12, etc.)
        - Automatic partition management via create_monthly_error_log_partition() function
        - 6-month retention policy (configurable)
    """

    __tablename__ = "error_logs"

    # Primary key (partitioned by timestamp)
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    # Trace correlation (unique)
    trace_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        nullable=False,
        unique=True
    )

    # Error classification
    error_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    # Request context
    path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        default=None
    )

    method: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        default=None
    )

    status_code: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    # User tracking (nullable for unauthenticated requests)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        default=None
    )

    # Additional details (flexible JSONB for stack traces, field errors, etc.)
    details: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=None
    )

    # Timestamp (partition key)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        primary_key=True  # Part of composite primary key for partitioning
    )

    # Relationship to User
    user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="error_logs"
    )

    # Indexes (defined in SQL schema for partitioned table)
    __table_args__ = (
        Index(
            "idx_error_logs_timestamp",
            "timestamp",
            postgresql_ops={"timestamp": "DESC"}
        ),
        Index(
            "idx_error_logs_error_code_timestamp",
            "error_code",
            "timestamp",
            postgresql_ops={"timestamp": "DESC"}
        ),
        Index(
            "idx_error_logs_trace_id",
            "trace_id",
            unique=True
        ),
        Index(
            "idx_error_logs_user_id_timestamp",
            "user_id",
            "timestamp",
            postgresql_ops={"timestamp": "DESC"},
            postgresql_where=user_id.isnot(None)
        ),
        Index(
            "idx_error_logs_path_timestamp",
            "path",
            "timestamp",
            postgresql_ops={"timestamp": "DESC"},
            postgresql_where=path.isnot(None)
        ),
        Index(
            "idx_error_logs_status_code_timestamp",
            "status_code",
            "timestamp",
            postgresql_ops={"timestamp": "DESC"}
        ),
        Index(
            "idx_error_logs_details_gin",
            "details",
            postgresql_using="gin"
        ),
    )

    def __repr__(self) -> str:
        """Return string representation of ErrorLog instance."""
        return (
            f"<ErrorLog(id={self.id}, trace_id={self.trace_id}, "
            f"error_code={self.error_code}, status_code={self.status_code})>"
        )

    def to_dict(self) -> dict:
        """
        Convert ErrorLog instance to dictionary.

        Returns:
            Dictionary representation of error log with all fields
        """
        return {
            "id": self.id,
            "trace_id": str(self.trace_id),
            "error_code": self.error_code,
            "message": self.message,
            "path": self.path,
            "method": self.method,
            "status_code": self.status_code,
            "user_id": self.user_id,
            "details": self.details,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
