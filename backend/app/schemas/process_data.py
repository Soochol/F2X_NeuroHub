"""
Pydantic schemas for the ProcessData entity.

This module provides request/response schemas for process data management in the F2X NeuroHub
Manufacturing Execution System. It includes validation for data levels, process results, JSONB
fields, conditional serial_id validation, and duration calculations.

Schemas:
    - ProcessDataBase: Base schema with core fields and validators
    - ProcessDataCreate: Schema for creating new process data records
    - ProcessDataUpdate: Schema for updating existing process data records
    - ProcessDataInDB: Schema for database response with relationships

Key Features:
    - DataLevel enum validation (LOT, SERIAL)
    - ProcessResult enum validation (PASS, FAIL, REWORK)
    - JSONB fields for measurements and defects (dicts)
    - Conditional validation: serial_id required when data_level=SERIAL
    - Duration validation: completed_at >= started_at
    - Nested schemas for Process and User relationships
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


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
        PASS: Process execution successful, quality criteria met
        FAIL: Process failed, quality check failure detected
        REWORK: Retry after failure
    """
    PASS = "PASS"
    FAIL = "FAIL"
    REWORK = "REWORK"


class ProcessSchema(BaseModel):
    """
    Nested Process schema for relationship data.

    Attributes:
        id: Process identifier
        process_number: Process sequence number (1-8)
        process_code: Unique process code (e.g., 'LASER_MARKING')
        process_name_en: English process name
        process_name_ko: Korean process name
    """
    id: int
    process_number: int
    process_code: str
    process_name_en: str
    process_name_ko: str

    model_config = ConfigDict(from_attributes=True)


class UserSchema(BaseModel):
    """
    Nested User schema for relationship data.

    Attributes:
        id: User identifier
        username: Unique login username
        full_name: User's full name
        role: User role (ADMIN, MANAGER, OPERATOR)
    """
    id: int
    username: str
    full_name: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class ProcessDataBase(BaseModel):
    """
    Base schema for ProcessData with core fields and validation.

    Attributes:
        lot_id: Foreign key to lots table (required)
        serial_id: Foreign key to serials table (optional for LOT-level)
        process_id: Foreign key to processes table (required)
        operator_id: Foreign key to users table (required)
        data_level: Data granularity level (LOT or SERIAL)
        result: Process result (PASS, FAIL, REWORK)
        measurements: JSONB field with measurement data (dict, default empty)
        defects: JSONB field with defect information (optional dict)
        started_at: Process execution start timestamp
        completed_at: Process execution completion timestamp (optional)
        notes: Additional comments or observations from operator (optional)

    Validators:
        - validate_data_level: Ensures serial_id consistency with data_level
        - validate_timestamps: Ensures completed_at >= started_at
    """

    lot_id: int = Field(..., gt=0, description="Lot identifier")
    serial_id: Optional[int] = Field(
        None, gt=0, description="Serial identifier (required for SERIAL data_level)"
    )
    process_id: int = Field(..., gt=0, description="Process identifier")
    operator_id: int = Field(..., gt=0, description="Operator identifier")
    data_level: DataLevel = Field(..., description="Data granularity level: LOT or SERIAL")
    result: ProcessResult = Field(
        default=ProcessResult.PASS, description="Process result: PASS, FAIL, or REWORK"
    )
    measurements: Dict[str, Any] = Field(
        default_factory=dict, description="JSONB field with process measurements"
    )
    defects: Optional[Dict[str, Any]] = Field(
        None, description="JSONB field with defect information if result=FAIL"
    )
    started_at: datetime = Field(..., description="Process execution start timestamp")
    completed_at: Optional[datetime] = Field(
        None, description="Process execution completion timestamp"
    )
    notes: Optional[str] = Field(
        None, max_length=1000, description="Additional comments or observations"
    )

    @field_validator("data_level", mode="before")
    @classmethod
    def validate_data_level_enum(cls, v: Any) -> DataLevel:
        """
        Validate and convert data_level to DataLevel enum.

        Args:
            v: Input value for data_level

        Returns:
            DataLevel enum value

        Raises:
            ValueError: If value is not a valid DataLevel
        """
        if isinstance(v, DataLevel):
            return v
        if isinstance(v, str):
            try:
                return DataLevel(v.upper())
            except ValueError:
                raise ValueError(
                    f"data_level must be one of {[e.value for e in DataLevel]}, got '{v}'"
                )
        raise ValueError(f"data_level must be a string or DataLevel enum, got {type(v)}")

    @field_validator("result", mode="before")
    @classmethod
    def validate_result_enum(cls, v: Any) -> ProcessResult:
        """
        Validate and convert result to ProcessResult enum.

        Args:
            v: Input value for result

        Returns:
            ProcessResult enum value

        Raises:
            ValueError: If value is not a valid ProcessResult
        """
        if isinstance(v, ProcessResult):
            return v
        if isinstance(v, str):
            try:
                return ProcessResult(v.upper())
            except ValueError:
                raise ValueError(
                    f"result must be one of {[e.value for e in ProcessResult]}, got '{v}'"
                )
        raise ValueError(f"result must be a string or ProcessResult enum, got {type(v)}")

    @field_validator("measurements")
    @classmethod
    def validate_measurements(cls, v: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate measurements field as JSONB dict.

        Args:
            v: Measurements dictionary

        Returns:
            Validated measurements dict (empty dict if None)

        Raises:
            ValueError: If value is not a dict
        """
        if v is None:
            return {}
        if not isinstance(v, dict):
            raise ValueError("measurements must be a dictionary")
        return v

    @field_validator("defects")
    @classmethod
    def validate_defects(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Validate defects field as JSONB dict.

        Args:
            v: Defects dictionary

        Returns:
            Validated defects dict or None

        Raises:
            ValueError: If value is not a dict
        """
        if v is not None and not isinstance(v, dict):
            raise ValueError("defects must be a dictionary")
        return v

    @model_validator(mode="after")
    def validate_data_level_serial_consistency(self) -> "ProcessDataBase":
        """
        Validate serial_id consistency with data_level.

        Rules:
            - If data_level=SERIAL: serial_id MUST be provided (not None)
            - If data_level=LOT: serial_id MUST be None

        Returns:
            Self instance if valid

        Raises:
            ValueError: If serial_id is inconsistent with data_level
        """
        if self.data_level == DataLevel.SERIAL:
            if self.serial_id is None:
                raise ValueError(
                    "serial_id is required when data_level='SERIAL'"
                )
        elif self.data_level == DataLevel.LOT:
            if self.serial_id is not None:
                raise ValueError(
                    "serial_id must be None when data_level='LOT'"
                )
        return self

    @model_validator(mode="after")
    def validate_duration_timestamps(self) -> "ProcessDataBase":
        """
        Validate timestamp consistency: completed_at >= started_at.

        Returns:
            Self instance if valid

        Raises:
            ValueError: If completed_at is before started_at
        """
        if self.completed_at is not None:
            if self.completed_at < self.started_at:
                raise ValueError(
                    "completed_at must be greater than or equal to started_at"
                )
        return self


class ProcessDataCreate(ProcessDataBase):
    """
    Schema for creating new ProcessData records.

    Inherits all validation from ProcessDataBase.
    All required fields must be provided on creation.
    """
    pass


class ProcessDataUpdate(BaseModel):
    """
    Schema for updating ProcessData records.

    All fields are optional to allow partial updates.
    Validators ensure consistency when fields are provided.

    Attributes:
        data_level: Data granularity level (optional)
        result: Process result (optional)
        measurements: Process measurements (optional)
        defects: Defect information (optional)
        completed_at: Process completion timestamp (optional)
        notes: Additional comments (optional)
    """

    data_level: Optional[DataLevel] = Field(None, description="Data granularity level")
    result: Optional[ProcessResult] = Field(None, description="Process result")
    measurements: Optional[Dict[str, Any]] = Field(
        None, description="Process measurements"
    )
    defects: Optional[Dict[str, Any]] = Field(None, description="Defect information")
    completed_at: Optional[datetime] = Field(
        None, description="Process completion timestamp"
    )
    notes: Optional[str] = Field(None, max_length=1000, description="Additional comments")

    model_config = ConfigDict(validate_assignment=True)

    @field_validator("data_level", mode="before")
    @classmethod
    def validate_data_level_enum(cls, v: Any) -> Optional[DataLevel]:
        """
        Validate and convert data_level to DataLevel enum.

        Args:
            v: Input value for data_level

        Returns:
            DataLevel enum value or None
        """
        if v is None:
            return None
        if isinstance(v, DataLevel):
            return v
        if isinstance(v, str):
            try:
                return DataLevel(v.upper())
            except ValueError:
                raise ValueError(
                    f"data_level must be one of {[e.value for e in DataLevel]}, got '{v}'"
                )
        raise ValueError(f"data_level must be a string or DataLevel enum, got {type(v)}")

    @field_validator("result", mode="before")
    @classmethod
    def validate_result_enum(cls, v: Any) -> Optional[ProcessResult]:
        """
        Validate and convert result to ProcessResult enum.

        Args:
            v: Input value for result

        Returns:
            ProcessResult enum value or None
        """
        if v is None:
            return None
        if isinstance(v, ProcessResult):
            return v
        if isinstance(v, str):
            try:
                return ProcessResult(v.upper())
            except ValueError:
                raise ValueError(
                    f"result must be one of {[e.value for e in ProcessResult]}, got '{v}'"
                )
        raise ValueError(f"result must be a string or ProcessResult enum, got {type(v)}")

    @field_validator("measurements")
    @classmethod
    def validate_measurements(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Validate measurements field as JSONB dict.

        Args:
            v: Measurements dictionary

        Returns:
            Validated measurements dict or None
        """
        if v is not None and not isinstance(v, dict):
            raise ValueError("measurements must be a dictionary")
        return v

    @field_validator("defects")
    @classmethod
    def validate_defects(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Validate defects field as JSONB dict.

        Args:
            v: Defects dictionary

        Returns:
            Validated defects dict or None
        """
        if v is not None and not isinstance(v, dict):
            raise ValueError("defects must be a dictionary")
        return v


class ProcessDataInDB(ProcessDataBase):
    """
    Schema for ProcessData database response with relationships.

    Extends ProcessDataBase with database-generated fields and nested relationship objects.

    Attributes:
        id: Primary key identifier
        duration_seconds: Calculated process duration in seconds (completed_at - started_at)
        created_at: Record creation timestamp
        process: Nested Process relationship data
        operator: Nested User relationship data for the operator

    Configuration:
        - Uses from_attributes=True for SQLAlchemy ORM compatibility
        - All fields are read-only at API level
    """

    id: int = Field(..., description="Process data record identifier")
    duration_seconds: Optional[int] = Field(
        None,
        ge=0,
        description="Calculated process duration in seconds (auto-calculated from timestamps)"
    )
    created_at: datetime = Field(..., description="Record creation timestamp")
    process: Optional[ProcessSchema] = Field(
        None, description="Nested Process relationship data"
    )
    operator: Optional[UserSchema] = Field(
        None, description="Nested Operator (User) relationship data"
    )

    model_config = ConfigDict(from_attributes=True)

    @field_validator("duration_seconds", mode="before")
    @classmethod
    def calculate_duration(cls, v: Optional[int], info) -> Optional[int]:
        """
        Calculate duration_seconds from completed_at and started_at if not provided.

        If duration_seconds is already provided, use it. Otherwise, calculate from timestamps.

        Args:
            v: duration_seconds value
            info: Validation info with other field values

        Returns:
            Duration in seconds or None if not completed
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
