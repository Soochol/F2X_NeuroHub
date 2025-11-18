"""
ProcessData data model for PySide6 MES application.

This module provides Pydantic models for ProcessData entity validation and serialization,
mirroring the backend FastAPI schemas. Includes data level tracking and result validation.
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class DataLevel(str, Enum):
    """
    Data granularity level enumeration.

    Attributes:
        LOT: LOT-level process data (serial_id is NULL)
        SERIAL: Per-unit/serial-level process data (serial_id is NOT NULL)
    """
    LOT = "LOT"
    SERIAL = "SERIAL"


class ProcessResult(str, Enum):
    """
    Process execution result enumeration.

    Attributes:
        PASS: Process successful, quality criteria met
        FAIL: Process failed, quality check failure
        REWORK: Retry after failure
    """
    PASS = "PASS"
    FAIL = "FAIL"
    REWORK = "REWORK"


class ProcessDataCreate(BaseModel):
    """
    Schema for creating new ProcessData records.

    Attributes:
        lot_id: Foreign key to lots table
        serial_id: Foreign key to serials table (required for SERIAL level)
        process_id: Foreign key to processes table
        operator_id: Foreign key to users table
        data_level: Data granularity level (LOT or SERIAL)
        result: Process result (PASS, FAIL, REWORK)
        measurements: JSONB field with measurement data
        defects: JSONB field with defect information (optional)
        started_at: Process execution start timestamp
        completed_at: Process execution completion timestamp (optional)
        notes: Additional comments from operator (optional)
    """
    lot_id: int = Field(..., gt=0)
    serial_id: Optional[int] = Field(None, gt=0)
    process_id: int = Field(..., gt=0)
    operator_id: int = Field(..., gt=0)
    data_level: DataLevel
    result: ProcessResult = ProcessResult.PASS
    measurements: Dict[str, Any] = Field(default_factory=dict)
    defects: Optional[Dict[str, Any]] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=1000)

    @field_validator('data_level', mode='before')
    @classmethod
    def validate_data_level(cls, v):
        """Convert string to DataLevel enum if needed."""
        if isinstance(v, str):
            try:
                return DataLevel(v.upper())
            except ValueError:
                raise ValueError(f"data_level must be one of {[e.value for e in DataLevel]}, got '{v}'")
        return v

    @field_validator('result', mode='before')
    @classmethod
    def validate_result(cls, v):
        """Convert string to ProcessResult enum if needed."""
        if isinstance(v, str):
            try:
                return ProcessResult(v.upper())
            except ValueError:
                raise ValueError(f"result must be one of {[e.value for e in ProcessResult]}, got '{v}'")
        return v

    @model_validator(mode='after')
    def validate_serial_id(self) -> 'ProcessDataCreate':
        """Validate serial_id consistency with data_level."""
        if self.data_level == DataLevel.SERIAL and self.serial_id is None:
            raise ValueError('serial_id is required when data_level is SERIAL')
        if self.data_level == DataLevel.LOT and self.serial_id is not None:
            raise ValueError('serial_id must be None when data_level is LOT')
        return self

    @model_validator(mode='after')
    def validate_timestamps(self) -> 'ProcessDataCreate':
        """Validate timestamp consistency."""
        if self.completed_at is not None:
            if self.completed_at < self.started_at:
                raise ValueError('completed_at must be greater than or equal to started_at')
        return self


class ProcessDataInDB(ProcessDataCreate):
    """
    Schema for ProcessData database response with all fields.

    Attributes:
        id: Primary key identifier
        duration_seconds: Calculated process duration
        created_at: Record creation timestamp
    """
    id: int
    duration_seconds: Optional[int] = None
    created_at: datetime

    @field_validator('duration_seconds', mode='before')
    @classmethod
    def calculate_duration(cls, v: Optional[int], info) -> Optional[int]:
        """Calculate duration from timestamps if not provided."""
        if v is not None:
            return v

        data = info.data
        started_at = data.get('started_at')
        completed_at = data.get('completed_at')

        if started_at and completed_at:
            delta = completed_at - started_at
            return int(delta.total_seconds())

        return None

    class Config:
        from_attributes = True
