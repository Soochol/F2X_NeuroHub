"""
Serial data model for PySide6 MES application.

This module provides Pydantic models for Serial entity validation and serialization,
mirroring the backend FastAPI schemas. Includes serial lifecycle management and
failure tracking.
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class SerialStatus(str, Enum):
    """
    Serial lifecycle status enumeration.

    Attributes:
        CREATED: Initial state after serial creation
        IN_PROGRESS: Serial is being processed
        PASSED: Serial passed all quality checks
        FAILED: Serial failed quality checks
    """
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    PASSED = "PASSED"
    FAILED = "FAILED"


class SerialBase(BaseModel):
    """
    Base schema for Serial with core fields and validation.

    Attributes:
        serial_number: Unique serial number identifier
        lot_id: Foreign key to lots table
        sequence_in_lot: Sequence position within LOT (1-100)
        status: Serial lifecycle status
        rework_count: Number of rework attempts (0-3)
        failure_reason: Reason for failure (required when status=FAILED)
    """
    serial_number: str
    lot_id: int = Field(..., gt=0)
    sequence_in_lot: int = Field(..., ge=1, le=100)
    status: SerialStatus = SerialStatus.CREATED
    rework_count: int = Field(default=0, ge=0, le=3)
    failure_reason: Optional[str] = None

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status is one of allowed values."""
        if isinstance(v, str):
            allowed = {'CREATED', 'IN_PROGRESS', 'PASSED', 'FAILED'}
            if v not in allowed:
                raise ValueError(f"status must be one of {allowed}, got '{v}'")
        return v

    @model_validator(mode='after')
    def validate_failure_reason(self) -> 'SerialBase':
        """Validate that failure_reason is required when status is FAILED."""
        if self.status == SerialStatus.FAILED and not self.failure_reason:
            raise ValueError("failure_reason is required when status is 'FAILED'")
        if self.status != SerialStatus.FAILED and self.failure_reason is not None:
            raise ValueError("failure_reason should only be provided when status is 'FAILED'")
        return self


class SerialCreate(SerialBase):
    """
    Schema for creating new Serial records.

    Inherits all validation from SerialBase.
    All required fields must be provided on creation.
    """
    pass


class SerialInDB(SerialBase):
    """
    Schema for Serial database response with all fields.

    Attributes:
        id: Primary key identifier
        created_at: Serial creation timestamp
        updated_at: Last modification timestamp
        completed_at: Completion timestamp when reaching terminal state
    """
    id: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
