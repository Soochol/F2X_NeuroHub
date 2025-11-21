"""
Pydantic schemas for the WIP Process History entity.

This module provides request/response schemas for WIP process execution history
in the F2X NeuroHub Manufacturing Execution System. It captures measurements,
test results, timing data, and defects for each process execution on WIP items.

Schemas:
    - ProcessResult: Enumeration of process execution results
    - WIPProcessHistoryBase: Base schema with core fields
    - WIPProcessHistoryCreate: Schema for creating new process history records
    - WIPProcessHistoryUpdate: Schema for updating process history records
    - WIPProcessHistoryInDB: Schema for database response with relationships

Key Features:
    - ProcessResult enum: PASS, FAIL
    - JSONB support for measurements and defects
    - Automatic duration calculation
    - Process number validation (1-6 only)
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


class ProcessResult(str, Enum):
    """
    Process execution result enumeration.

    Attributes:
        PASS: Process execution successful, quality criteria met
        FAIL: Process failed, quality check failure detected
        REWORK: Process failed but approved for rework attempt
    """
    PASS = "PASS"
    FAIL = "FAIL"
    REWORK = "REWORK"


class WIPProcessHistoryBase(BaseModel):
    """
    Base schema for WIP Process History with core fields.

    Attributes:
        wip_item_id: Foreign key to wip_items table
        process_id: Foreign key to processes table
        operator_id: Operator who performed the process
        equipment_id: Equipment used (optional)
        result: Process result (PASS or FAIL)
        measurements: Process-specific measurement data
        defects: Defect information if result=FAIL
        notes: Additional comments or observations
        started_at: Process start timestamp
        completed_at: Process completion timestamp
    """
    wip_item_id: int = Field(..., gt=0, description="WIP item identifier")
    process_id: int = Field(
        ...,
        ge=1,
        le=6,
        description="Process identifier (1-6 only)"
    )
    operator_id: int = Field(..., gt=0, description="Operator identifier")
    equipment_id: Optional[int] = Field(
        None,
        gt=0,
        description="Equipment identifier (optional)"
    )
    result: ProcessResult = Field(..., description="Process result: PASS or FAIL")
    measurements: Optional[dict] = Field(
        None,
        description="Process-specific measurement data in JSON format"
    )
    defects: Optional[list] = Field(
        None,
        description="Defect information array if result=FAIL"
    )
    notes: Optional[str] = Field(
        None,
        max_length=5000,
        description="Additional comments or observations"
    )
    started_at: datetime = Field(..., description="Process start timestamp")
    completed_at: Optional[datetime] = Field(
        None,
        description="Process completion timestamp"
    )

    @field_validator("process_id")
    @classmethod
    def validate_process_number(cls, v: int) -> int:
        """Validate process number is for WIP (1-6 only).

        Args:
            v: Process number value

        Returns:
            Validated process number

        Raises:
            ValueError: If process number is outside 1-6 range
        """
        if v < 1 or v > 6:
            raise ValueError("process_id must be between 1 and 6 (WIP processes only)")
        return v

    @model_validator(mode="after")
    def validate_timestamps(self) -> "WIPProcessHistoryBase":
        """Validate completed_at >= started_at.

        Returns:
            Self instance if valid

        Raises:
            ValueError: If completed_at is before started_at
        """
        if self.completed_at and self.started_at:
            if self.completed_at < self.started_at:
                raise ValueError("completed_at cannot be before started_at")
        return self

    @model_validator(mode="after")
    def validate_defects_on_fail(self) -> "WIPProcessHistoryBase":
        """Validate defects are provided when result=FAIL.

        Returns:
            Self instance if valid

        Raises:
            ValueError: If result is FAIL but defects are empty
        """
        if self.result == ProcessResult.FAIL:
            if not self.defects or len(self.defects) == 0:
                raise ValueError("defects must be provided when result=FAIL")
        return self


class WIPProcessHistoryCreate(BaseModel):
    """
    Schema for creating new WIP process history records.

    This is used when starting and completing processes on WIP items.
    Typically created via the WIP item process start/complete endpoints.

    Attributes:
        wip_item_id: WIP item identifier
        process_id: Process identifier (1-6)
        operator_id: Operator identifier
        equipment_id: Equipment identifier (optional)
        result: Process result (PASS or FAIL)
        measurements: Measurement data (optional)
        defects: Defect data (optional, required if result=FAIL)
        notes: Additional comments (optional)
        started_at: Process start timestamp
        completed_at: Process completion timestamp (optional)
    """
    wip_item_id: int = Field(..., gt=0, description="WIP item identifier")
    process_id: int = Field(
        ...,
        ge=1,
        le=6,
        description="Process identifier (1-6 only)"
    )
    operator_id: int = Field(..., gt=0, description="Operator identifier")
    equipment_id: Optional[int] = Field(
        None,
        gt=0,
        description="Equipment identifier (optional)"
    )
    result: ProcessResult = Field(..., description="Process result: PASS or FAIL")
    measurements: Optional[dict] = Field(
        None,
        description="Process-specific measurement data"
    )
    defects: Optional[list] = Field(
        None,
        description="Defect information if result=FAIL"
    )
    notes: Optional[str] = Field(
        None,
        max_length=5000,
        description="Additional comments"
    )
    started_at: datetime = Field(..., description="Process start timestamp")
    completed_at: Optional[datetime] = Field(
        None,
        description="Process completion timestamp"
    )

    @field_validator("process_id")
    @classmethod
    def validate_process_number(cls, v: int) -> int:
        """Validate process number."""
        if v < 1 or v > 6:
            raise ValueError("process_id must be between 1 and 6")
        return v

    @model_validator(mode="after")
    def validate_timestamps(self) -> "WIPProcessHistoryCreate":
        """Validate timestamp ordering."""
        if self.completed_at and self.started_at:
            if self.completed_at < self.started_at:
                raise ValueError("completed_at cannot be before started_at")
        return self

    @model_validator(mode="after")
    def validate_defects_on_fail(self) -> "WIPProcessHistoryCreate":
        """Validate defects when result=FAIL."""
        if self.result == ProcessResult.FAIL:
            if not self.defects or len(self.defects) == 0:
                raise ValueError("defects must be provided when result=FAIL")
        return self


class WIPProcessHistoryUpdate(BaseModel):
    """
    Schema for updating WIP process history records.

    All fields are optional to allow partial updates.
    Typically used to update completed_at, duration_seconds, or add notes.

    Attributes:
        result: Updated process result (optional)
        measurements: Updated measurements (optional)
        defects: Updated defects (optional)
        notes: Updated notes (optional)
        completed_at: Updated completion timestamp (optional)
        duration_seconds: Updated duration (optional)
    """
    result: Optional[ProcessResult] = Field(
        None,
        description="Process result: PASS or FAIL"
    )
    measurements: Optional[dict] = Field(
        None,
        description="Process-specific measurement data"
    )
    defects: Optional[list] = Field(
        None,
        description="Defect information"
    )
    notes: Optional[str] = Field(
        None,
        max_length=5000,
        description="Additional comments"
    )
    completed_at: Optional[datetime] = Field(
        None,
        description="Process completion timestamp"
    )
    duration_seconds: Optional[int] = Field(
        None,
        ge=0,
        description="Process duration in seconds"
    )

    model_config = ConfigDict(validate_assignment=True)


class WIPProcessHistoryInDB(WIPProcessHistoryBase):
    """
    Schema for WIP Process History database response.

    Extends WIPProcessHistoryBase with database-generated fields.

    Attributes:
        id: Primary key identifier
        duration_seconds: Calculated process duration in seconds
        created_at: Record creation timestamp
    """
    id: int = Field(..., description="Process history record identifier")
    duration_seconds: Optional[int] = Field(
        None,
        ge=0,
        description="Process duration in seconds (auto-calculated)"
    )
    created_at: datetime = Field(..., description="Record creation timestamp")

    model_config = ConfigDict(from_attributes=True)

    @field_validator("duration_seconds", mode="before")
    @classmethod
    def calculate_duration(cls, v: Optional[int], info) -> Optional[int]:
        """Calculate duration from timestamps if not provided.

        Args:
            v: Duration value
            info: Validation info with other field values

        Returns:
            Duration in seconds or None
        """
        if v is not None:
            return v

        # Try to calculate from timestamps
        data = info.data
        started_at = data.get("started_at")
        completed_at = data.get("completed_at")

        if started_at and completed_at:
            delta = completed_at - started_at
            return int(delta.total_seconds())

        return None
