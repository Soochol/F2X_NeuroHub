"""
User schemas for request/response validation.

This module defines Pydantic schemas for user-related operations,
including user creation, updates, and authentication.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRole(str, Enum):
    """User role enumeration."""

    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    OPERATOR = "OPERATOR"


class UserBase(BaseModel):
    """Base user schema with common fields."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username (3-50 characters, alphanumeric and underscore)",
    )
    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User full name",
    )
    role: UserRole = Field(..., description="User role")
    department: Optional[str] = Field(
        None,
        max_length=100,
        description="Department name",
    )
    is_active: bool = Field(
        True,
        description="User active status",
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format (alphanumeric and underscore only)."""
        if not v.replace("_", "").isalnum():
            raise ValueError(
                "Username must contain only alphanumeric characters and underscores"
            )
        return v.lower()


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User password (min 8 chars, must contain upper, lower, and digit)",
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password meets security requirements.

        Password must:
        - Be at least 8 characters long
        - Contain at least one uppercase letter
        - Contain at least one lowercase letter
        - Contain at least one digit
        """
        if not any(c.isupper() for c in v):
            raise ValueError(
                "Password must contain at least one uppercase letter"
            )
        if not any(c.islower() for c in v):
            raise ValueError(
                "Password must contain at least one lowercase letter"
            )
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information."""

    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        description="Username",
    )
    email: Optional[EmailStr] = Field(
        None,
        description="User email address",
    )
    full_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="User full name",
    )
    role: Optional[UserRole] = Field(
        None,
        description="User role",
    )
    department: Optional[str] = Field(
        None,
        max_length=100,
        description="Department name",
    )
    is_active: Optional[bool] = Field(
        None,
        description="User active status",
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        """Validate username format if provided."""
        if v is None:
            return v
        if not v.replace("_", "").isalnum():
            raise ValueError(
                "Username must contain only alphanumeric characters and underscores"
            )
        return v.lower()


class UserInDB(UserBase):
    """Schema for user data retrieved from database.

    Security: password_hash is intentionally excluded from this schema
    to prevent accidental exposure of sensitive data in API responses.
    """

    id: int = Field(..., description="User ID")
    created_at: datetime = Field(..., description="User creation timestamp")
    updated_at: datetime = Field(..., description="User last update timestamp")
    last_login_at: Optional[datetime] = Field(
        None,
        description="User last login timestamp",
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "role": "OPERATOR",
                "department": "Engineering",
                "is_active": True,
                "created_at": "2024-11-18T10:00:00Z",
                "updated_at": "2024-11-18T10:00:00Z",
                "last_login_at": "2024-11-18T12:30:00Z",
            }
        },
    )


class UserLogin(BaseModel):
    """Schema for user login request."""

    username: str = Field(
        ...,
        min_length=1,
        description="Username or email",
    )
    password: str = Field(
        ...,
        min_length=1,
        description="User password",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "john_doe",
                "password": "SecurePassword123",
            }
        }
    )
