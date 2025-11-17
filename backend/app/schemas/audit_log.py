"""
Pydantic schemas for the AuditLog entity.

This module provides read-only schemas for audit log data in the F2X NeuroHub
Manufacturing Execution System. Audit logs are immutable and created automatically
by database triggers on entity changes. No Create/Update schemas exist as logs
cannot be modified via API.

Schemas:
    - AuditAction: Enumeration for audit action types (CREATE, UPDATE, DELETE)
    - UserSchema: Nested User schema for relationship data
    - AuditLogBase: Base schema with core audit log fields
    - AuditLogInDB: Schema for database response with user relationship

Key Features:
    - AuditAction enum validation (CREATE, UPDATE, DELETE)
    - JSONB fields for snapshots: old_values, new_values
    - Entity tracking: entity_type, entity_id
    - Client tracking: ip_address, user_agent
    - User accountability: user_id with nested User relationship
    - Immutable (no Create/Update schemas - logs are read-only)
    - Partitioned by created_at for performance
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator


class AuditAction(str, Enum):
    """
    Enumeration of audit action types.

    Attributes:
        CREATE: Record was created
        UPDATE: Record was updated
        DELETE: Record was deleted
    """
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class UserSchema(BaseModel):
    """
    Nested User schema for relationship data in audit logs.

    Attributes:
        id: User identifier
        username: Unique login username
        email: User email address
        full_name: User's full name
        role: User role (ADMIN, MANAGER, OPERATOR)
        is_active: Account active status
    """
    id: int = Field(..., description="User identifier")
    username: str = Field(..., description="Unique login username")
    email: str = Field(..., description="User email address")
    full_name: str = Field(..., description="User's full name")
    role: str = Field(..., description="User role: ADMIN, MANAGER, or OPERATOR")
    is_active: bool = Field(..., description="Account active status")

    model_config = ConfigDict(from_attributes=True)


class AuditLogBase(BaseModel):
    """
    Base schema for audit logs (read-only).

    Represents immutable audit trail entries documenting system changes for
    compliance, security, and change tracking. Audit logs are created automatically
    by database triggers and cannot be modified or deleted via API.

    Attributes:
        entity_type: Name of the table/entity being audited
        entity_id: Primary key of the affected record in entity_type table
        action: Type of operation (CREATE, UPDATE, or DELETE)
        old_values: Complete record snapshot before change (NULL for CREATE)
        new_values: Complete record snapshot after change (NULL for DELETE)
        ip_address: Client IP address (IPv4 or IPv6 format)
        user_agent: Client user agent string for security analysis

    Validators:
        - validate_action: Ensures action is a valid AuditAction enum value
        - validate_old_values: Validates old_values as a dict
        - validate_new_values: Validates new_values as a dict
    """

    entity_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Name of the table/entity being audited"
    )
    entity_id: int = Field(
        ...,
        gt=0,
        description="Primary key of the affected record in entity_type table"
    )
    action: AuditAction = Field(
        ...,
        description="Type of operation: CREATE, UPDATE, or DELETE"
    )
    old_values: Optional[Dict[str, Any]] = Field(
        None,
        description="Complete record snapshot before change (NULL for CREATE)"
    )
    new_values: Optional[Dict[str, Any]] = Field(
        None,
        description="Complete record snapshot after change (NULL for DELETE)"
    )
    ip_address: Optional[str] = Field(
        None,
        max_length=45,
        description="Client IP address (IPv4 or IPv6 format)"
    )
    user_agent: Optional[str] = Field(
        None,
        description="Client user agent string for security analysis"
    )

    @field_validator("action", mode="before")
    @classmethod
    def validate_action(cls, v: Any) -> AuditAction:
        """
        Validate and convert action to AuditAction enum.

        Args:
            v: Input value for action

        Returns:
            AuditAction enum value

        Raises:
            ValueError: If value is not a valid AuditAction
        """
        if isinstance(v, AuditAction):
            return v
        if isinstance(v, str):
            try:
                return AuditAction(v.upper())
            except ValueError:
                raise ValueError(
                    f"action must be one of {[e.value for e in AuditAction]}, got '{v}'"
                )
        raise ValueError(f"action must be a string or AuditAction enum, got {type(v)}")

    @field_validator("old_values")
    @classmethod
    def validate_old_values(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Validate old_values field as JSONB dict.

        Args:
            v: old_values dictionary

        Returns:
            Validated old_values dict or None

        Raises:
            ValueError: If value is not a dict
        """
        if v is not None and not isinstance(v, dict):
            raise ValueError("old_values must be a dictionary")
        return v

    @field_validator("new_values")
    @classmethod
    def validate_new_values(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Validate new_values field as JSONB dict.

        Args:
            v: new_values dictionary

        Returns:
            Validated new_values dict or None

        Raises:
            ValueError: If value is not a dict
        """
        if v is not None and not isinstance(v, dict):
            raise ValueError("new_values must be a dictionary")
        return v


class AuditLogInDB(AuditLogBase):
    """
    Schema for audit log responses from database.

    Extends AuditLogBase with database-generated fields and nested user relationship.
    Audit logs are immutable and created automatically by database triggers.

    Note: Audit logs are immutable. No Create/Update schemas exist as logs cannot
    be modified or deleted via API. They represent an immutable audit trail for
    compliance and security purposes.

    Attributes:
        id: Unique identifier for audit log entry
        user_id: ID of user who performed the action
        created_at: Timestamp when audit entry was created (partitioning key)
        user: Nested User relationship data for the user who performed the action

    Configuration:
        - Uses from_attributes=True for SQLAlchemy ORM compatibility
        - All fields are read-only at API level
        - No Create/Update schemas - audit logs are append-only
    """

    id: int = Field(..., description="Unique identifier for audit log entry")
    user_id: int = Field(
        ...,
        gt=0,
        description="ID of user who performed the action (FK to users table)"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when audit entry was created (partitioning key)"
    )
    user: Optional[UserSchema] = Field(
        None,
        description="Nested User relationship data for the user who performed the action"
    )

    model_config = ConfigDict(from_attributes=True)


# Note: No AuditLogCreate or AuditLogUpdate schemas exist
# Audit logs are immutable and created automatically by database triggers.
# They cannot be created or modified via API - only read/queried.
