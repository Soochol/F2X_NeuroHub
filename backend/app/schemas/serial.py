"""
Pydantic schemas for Serial entity validation and serialization.

This module defines Pydantic schemas for handling Serial ORM model instances
across API operations (create, read, update). Includes comprehensive validation
for serial-specific constraints like rework count limits, sequence ranges, and
conditional failure reason requirements.

Schemas:
    SerialBase: Base schema with common fields for Serial entity
    SerialCreate: Schema for creating new Serial instances
    SerialUpdate: Schema for updating existing Serial instances
    SerialInDB: Complete schema with all fields including relationships and timestamps
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator, computed_field

from app.schemas.lot import LotInDB
from app.utils.serial_number import SerialNumber


class SerialBase(BaseModel):
    """
    Base schema for Serial entity with common fields.

    Includes core serial attributes with validation for ranges and constraints.
    Used as a base for Create, Update, and InDB schemas.

    Attributes:
        lot_id: Reference to parent Lot (required)
        sequence_in_lot: Sequence position within Lot (1-100, required)
        status: Serial lifecycle status (CREATED, IN_PROGRESS, PASSED, FAILED)
        rework_count: Number of rework attempts (0-3, default 0)
        failure_reason: Reason for failure (optional, required when status=FAILED)
    """

    lot_id: int = Field(
        ...,
        gt=0,
        description="Foreign key reference to parent Lot (must be positive integer)"
    )
    sequence_in_lot: int = Field(
        ...,
        ge=1,
        le=100,
        description="Sequence number within Lot (1-100 inclusive)"
    )
    status: str = Field(
        default="CREATED",
        description="Serial lifecycle status: CREATED, IN_PROGRESS, PASSED, FAILED"
    )
    rework_count: int = Field(
        default=0,
        ge=0,
        le=3,
        description="Number of rework attempts performed (0-3 maximum)"
    )
    failure_reason: Optional[str] = Field(
        default=None,
        description="Reason for failure (required only when status=FAILED)"
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        """
        Validate status is one of allowed values.

        Args:
            value: Status value to validate

        Returns:
            Validated status value

        Raises:
            ValueError: If status is not in allowed values
        """
        allowed_statuses = {"CREATED", "IN_PROGRESS", "PASSED", "FAILED"}
        if value not in allowed_statuses:
            raise ValueError(
                f"status must be one of {allowed_statuses}, got '{value}'"
            )
        return value

    @model_validator(mode="after")
    def validate_failure_reason_required(self) -> "SerialBase":
        """
        Validate that failure_reason is required when status is FAILED.

        Enforces the constraint that failed serials must have a failure reason
        provided for audit and analysis purposes.

        Returns:
            Validated instance

        Raises:
            ValueError: If status is FAILED but failure_reason is not provided
        """
        if self.status == "FAILED" and not self.failure_reason:
            raise ValueError(
                "failure_reason is required when status is 'FAILED'"
            )
        return self

    @model_validator(mode="after")
    def validate_failure_reason_not_provided(self) -> "SerialBase":
        """
        Validate that failure_reason is NOT provided for non-FAILED statuses.

        Ensures data integrity by preventing failure reasons from being set
        on serials that have not failed.

        Returns:
            Validated instance

        Raises:
            ValueError: If failure_reason is provided but status is not FAILED
        """
        if self.status != "FAILED" and self.failure_reason is not None:
            raise ValueError(
                "failure_reason should only be provided when status is 'FAILED'"
            )
        return self


class SerialCreate(SerialBase):
    """
    Schema for creating new Serial instances.

    Inherits all validation from SerialBase. All required fields from base
    must be provided. Optional fields use their defaults.

    Example:
        serial_create = SerialCreate(
            lot_id=1,
            sequence_in_lot=1,
            status="CREATED",
            rework_count=0
        )
    """

    pass


class SerialUpdate(BaseModel):
    """
    Schema for updating Serial instances.

    All fields are optional to allow partial updates. Only provided fields
    will be updated in the database.

    Attributes:
        status: Updated lifecycle status (optional)
        rework_count: Updated rework count (optional)
        failure_reason: Updated failure reason (optional)

    Note:
        lot_id and sequence_in_lot are immutable and cannot be updated.
    """

    status: Optional[str] = Field(
        default=None,
        description="Updated serial lifecycle status"
    )
    rework_count: Optional[int] = Field(
        default=None,
        ge=0,
        le=3,
        description="Updated rework count (0-3 maximum)"
    )
    failure_reason: Optional[str] = Field(
        default=None,
        description="Updated failure reason"
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> Optional[str]:
        """
        Validate status is one of allowed values if provided.

        Args:
            value: Status value to validate

        Returns:
            Validated status value or None

        Raises:
            ValueError: If status is provided but not in allowed values
        """
        if value is None:
            return value

        allowed_statuses = {"CREATED", "IN_PROGRESS", "PASSED", "FAILED"}
        if value not in allowed_statuses:
            raise ValueError(
                f"status must be one of {allowed_statuses}, got '{value}'"
            )
        return value

    @model_validator(mode="after")
    def validate_update_constraints(self) -> "SerialUpdate":
        """
        Validate update constraints for failure_reason.

        Ensures failure_reason is only provided when status is FAILED.

        Returns:
            Validated instance

        Raises:
            ValueError: If constraints are violated
        """
        # Only validate if both status and failure_reason are provided
        if self.status is not None and self.failure_reason is not None:
            if self.status != "FAILED":
                raise ValueError(
                    "failure_reason should only be provided when status is 'FAILED'"
                )

        # If status is FAILED but failure_reason is being cleared, validate
        if self.status == "FAILED" and self.failure_reason == "":
            raise ValueError(
                "failure_reason cannot be empty when status is 'FAILED'"
            )

        return self


class SerialInDB(SerialBase):
    """
    Complete schema for Serial instances with all database fields.

    Includes read-only fields populated by the database such as IDs,
    computed fields, and timestamps. Used for returning full serial
    details from API endpoints.

    Attributes:
        id: Primary key (auto-generated)
        serial_number: Auto-generated unique identifier (14 chars, format: KR01PSA2511001)
        created_at: Creation timestamp (UTC timezone-aware)
        updated_at: Last update timestamp (UTC timezone-aware)
        completed_at: Completion timestamp when reaching terminal state (optional)
        lot: Nested Lot object containing full lot details

    Configuration:
        from_attributes: Enables Pydantic to populate from ORM model instances
    """

    id: int = Field(
        ...,
        description="Primary key, auto-generated by database"
    )
    serial_number: str = Field(
        ...,
        min_length=16,
        max_length=16,
        pattern=r'^[A-Z0-9]{13}\d{3}$',
        description="Auto-generated unique serial number (16 chars: LOT number 13 chars + sequence 3 digits)"
    )
    created_at: datetime = Field(
        ...,
        description="Serial creation timestamp (UTC timezone-aware)"
    )
    updated_at: datetime = Field(
        ...,
        description="Last update timestamp (UTC timezone-aware)"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Completion timestamp when reaching terminal state (PASSED or FAILED)"
    )
    # lot: Optional[LotInDB] = Field(
    #     default=None,
    #     description="Nested Lot object containing full lot details"
    # )


    class Config:
        """Pydantic model configuration."""

        from_attributes = True


class SerialListItem(BaseModel):
    """
    Lightweight schema for serial list responses.
    
    Used in GET /serials/lot/{id} to avoid serialization issues
    with nested relationships. Contains only essential fields.
    """
    
    id: int
    serial_number: str
    lot_id: int
    sequence_in_lot: int
    status: str
    rework_count: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        """Pydantic model configuration."""
        from_attributes = True
