"""
User model for authentication and authorization.

This module defines the User ORM model that represents the users table in the
F2X NeuroHub database. It includes user credentials, profile information, role-based
access control, and audit timestamps.

Provides:
    - User: SQLAlchemy ORM model for the users table
    - UserRole: Enumeration for user roles (ADMIN, MANAGER, OPERATOR)

Database Table: users
    - Primary Key: id (BIGSERIAL)
    - Unique Constraints: username, email
    - Role Enum: ADMIN, MANAGER, OPERATOR
    - Audit Fields: created_at, updated_at
"""

from datetime import datetime, timezone
from typing import Optional, List
import enum

from sqlalchemy import (
    Index,
    String,
    Boolean,
    DateTime,
    Enum,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(str, enum.Enum):
    """
    User role enumeration for role-based access control.

    Roles:
        ADMIN: Full system access, user management, master data modification
        MANAGER: Production management, approval authority, report generation
        OPERATOR: Process execution, data recording, limited access
    """
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    OPERATOR = "OPERATOR"


class User(Base):
    """
    User model for authentication and authorization.

    Represents a system user with credentials, profile information, and role-based
    access control. Includes audit timestamps for tracking account changes.

    Attributes:
        id: Unique identifier (auto-incrementing primary key)
        username: Unique login username (3-50 characters)
        email: Unique email address with format validation
        password_hash: Bcrypt hashed password (cost factor 12)
        full_name: User's full name (Korean or English)
        role: User role (ADMIN, MANAGER, OPERATOR)
        department: Department or team assignment
        is_active: Account active status (True/False)
        last_login_at: Timestamp of last successful login
        created_at: Account creation timestamp
        updated_at: Last update timestamp

    Table Name: users

    Constraints:
        - PK: pk_users on id
        - UK: uk_users_username on username
        - UK: uk_users_email on email
        - CHK: chk_users_role (role IN ['ADMIN', 'MANAGER', 'OPERATOR'])
        - CHK: chk_users_email_format (valid email format)
        - CHK: chk_users_username_length (username >= 3 characters)

    Indexes:
        - idx_users_active: (is_active, role) WHERE is_active = TRUE
        - idx_users_role: (role)
        - idx_users_department: (department) WHERE department IS NOT NULL
        - idx_users_last_login: (last_login_at DESC) WHERE last_login_at IS NOT NULL
    """

    __tablename__ = "users"

    # Primary key
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    # Core columns
    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False, length=20),
        nullable=False,
        default=UserRole.OPERATOR
    )

    department: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        default=None
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    # Activity tracking
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP")
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP")
    )

    # Relationships
    process_data_records: Mapped[List["ProcessData"]] = relationship(
        "ProcessData",
        back_populates="operator",
        cascade="all, delete-orphan"
    )

    error_logs: Mapped[List["ErrorLog"]] = relationship(
        "ErrorLog",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    saved_filters: Mapped[List["SavedFilter"]] = relationship(
        "SavedFilter",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index(
            "idx_users_active",
            "is_active",
            "role"),
        Index(
            "idx_users_role",
            "role"
        ),
        Index(
            "idx_users_department",
            "department"),
        Index(
            "idx_users_last_login",
            "last_login_at"
        ),
    )

    def __repr__(self) -> str:
        """Return string representation of User instance."""
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', role={self.role.value})>"

    def to_dict(self) -> dict:
        """
        Convert User instance to dictionary.

        Returns:
            Dictionary representation of user (password_hash excluded)
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role.value,
            "department": self.department,
            "is_active": self.is_active,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# Type hint imports for forward references
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.process_data import ProcessData
    from app.models.error_log import ErrorLog
    from app.models.saved_filter import SavedFilter
