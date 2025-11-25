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
    - DataLevel enum validation (LOT, WIP, SERIAL)
    - ProcessResult enum validation (PASS, FAIL, REWORK)
    - JSONB fields for measurements and defects (dicts)
    - Conditional validation: serial_id required when data_level=SERIAL
    - Duration validation: completed_at >= started_at
    - Defect/result consistency: defects required for FAIL, empty for PASS
    - Nested schemas for Process and User relationships

Examples:
    Valid LOT-level data:
        {
            "lot_id": 1,
            "serial_id": null,
            "wip_id": null,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "result": "PASS",
            "measurements": {"temperature": 25.5},
            "defects": null,
            "started_at": "2024-01-01T10:00:00",
            "completed_at": "2024-01-01T10:15:00"
        }

    Valid SERIAL-level FAIL data:
        {
            "lot_id": 1,
            "serial_id": 100,
            "process_id": 2,
            "operator_id": 2,
            "data_level": "SERIAL",
            "result": "FAIL",
            "measurements": {"pressure": 2.8},
            "defects": {"type": "crack", "location": "edge", "severity": "critical"},
            "started_at": "2024-01-01T11:00:00",
            "completed_at": "2024-01-01T11:05:00",
            "notes": "Crack detected during visual inspection"
        }

    Invalid data (FAIL without defects):
        {
            "lot_id": 1,
            "serial_id": 101,
            "process_id": 3,
            "operator_id": 3,
            "data_level": "SERIAL",
            "result": "FAIL",
            "defects": null,  # ERROR: defects required for FAIL
            "started_at": "2024-01-01T12:00:00"
        }
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
import warnings

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


class DataLevel(str, Enum):
    """
    Data granularity level enumeration.

    Attributes:
        LOT: LOT-level process data (serial_id and wip_id are NULL)
        WIP: WIP-level process data (wip_id is NOT NULL, serial_id is NULL)
        SERIAL: Per-unit/serial-level process data (serial_id is NOT NULL)
    """
    LOT = "LOT"
    WIP = "WIP"
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


class EquipmentSchema(BaseModel):
    """
    Nested Equipment schema for relationship data.

    Attributes:
        id: Equipment identifier
        equipment_code: Unique equipment identifier
        equipment_name: Display name
        equipment_type: Type classification
        is_active: Whether equipment is currently operational
    """
    id: int
    equipment_code: str
    equipment_name: str
    equipment_type: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ProcessDataBase(BaseModel):
    """
    Base schema for ProcessData with core fields and validation.

    Attributes:
        lot_id: Foreign key to lots table (required)
        serial_id: Foreign key to serials table (optional for LOT-level)
        wip_id: Foreign key to wip_items table (optional for LOT/SERIAL-level)
        process_id: Foreign key to processes table (required)
        operator_id: Foreign key to users table (required)
        equipment_id: Foreign key to equipment table (optional)
        data_level: Data granularity level (LOT, WIP, or SERIAL)
        result: Process result (PASS, FAIL, REWORK)
        measurements: JSONB field with measurement data (dict, default empty)
        defects: JSONB field with defect information (required for FAIL)
        started_at: Process execution start timestamp
        completed_at: Process execution completion timestamp (optional)
        notes: Additional comments or observations from operator (optional)

    Validators:
        - validate_data_level: Ensures serial_id/wip_id consistency with data_level
        - validate_timestamps: Ensures completed_at >= started_at
        - validate_defects_result: Ensures defects consistency with result
        - validate_business_rules: Comprehensive business rules validation
    """

    lot_id: int = Field(..., gt=0, description="Lot identifier")
    serial_id: Optional[int] = Field(
        None, gt=0, description="Serial identifier (required for SERIAL data_level)"
    )
    wip_id: Optional[int] = Field(
        None, gt=0, description="WIP item identifier (required for WIP data_level)"
    )
    process_id: int = Field(..., gt=0, description="Process identifier")
    operator_id: int = Field(..., gt=0, description="Operator identifier")
    equipment_id: Optional[int] = Field(
        None, gt=0, description="Equipment identifier"
    )
    data_level: DataLevel = Field(..., description="Data granularity level: LOT, WIP, or SERIAL")
    result: ProcessResult = Field(
        default=ProcessResult.PASS, description="Process result: PASS, FAIL, or REWORK"
    )
    measurements: Dict[str, Any] = Field(
        default_factory=dict, description="JSONB field with process measurements"
    )
    defects: Optional[Dict[str, Any]] = Field(
        None, description="JSONB field with defect information (required if result=FAIL)"
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
                valid_values = [e.value for e in DataLevel]
                raise ValueError(
                    f"Invalid data_level '{v}'. Must be one of {valid_values}. "
                    f"Current value: '{v}'"
                )
        raise ValueError(
            f"data_level must be a string or DataLevel enum, got {type(v).__name__}"
        )

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
                valid_values = [e.value for e in ProcessResult]
                raise ValueError(
                    f"Invalid result '{v}'. Must be one of {valid_values}. "
                    f"Current value: '{v}'"
                )
        raise ValueError(
            f"result must be a string or ProcessResult enum, got {type(v).__name__}"
        )

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
            ValueError: If value is not a dict or has invalid structure
        """
        if v is None:
            return {}
        if not isinstance(v, dict):
            raise ValueError(
                f"measurements must be a dictionary, got {type(v).__name__}"
            )

        # Validate measurement structure
        for key, value in v.items():
            if not isinstance(key, str):
                raise ValueError(
                    f"measurement keys must be strings, got {type(key).__name__} for key {key}"
                )
            # Allow basic JSON-serializable types
            if not isinstance(value, (str, int, float, bool, list, dict, type(None))):
                raise ValueError(
                    f"measurement value for '{key}' must be JSON-serializable, "
                    f"got {type(value).__name__}"
                )

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
            ValueError: If value is not a dict or has invalid structure
        """
        if v is None:
            return None

        if not isinstance(v, dict):
            raise ValueError(
                f"defects must be a dictionary, got {type(v).__name__}"
            )

        # Empty dict is treated as None for consistency
        if not v:
            return None

        # Validate defect structure
        for key, value in v.items():
            if not isinstance(key, str):
                raise ValueError(
                    f"defect keys must be strings, got {type(key).__name__} for key {key}"
                )
            # Allow basic JSON-serializable types
            if not isinstance(value, (str, int, float, bool, list, dict, type(None))):
                raise ValueError(
                    f"defect value for '{key}' must be JSON-serializable, "
                    f"got {type(value).__name__}"
                )

        return v

    @model_validator(mode="after")
    def validate_data_level_consistency(self) -> "ProcessDataBase":
        """
        Validate serial_id and wip_id consistency with data_level.

        Rules:
            - If data_level=LOT: serial_id and wip_id MUST be None
            - If data_level=WIP: wip_id MUST be provided, serial_id MUST be None
            - If data_level=SERIAL: serial_id MUST be provided, wip_id is optional

        Returns:
            Self instance if valid

        Raises:
            ValueError: If serial_id/wip_id is inconsistent with data_level
        """
        if self.data_level == DataLevel.SERIAL:
            if self.serial_id is None:
                raise ValueError(
                    f"serial_id is required when data_level='SERIAL'. "
                    f"Current: serial_id={self.serial_id}, data_level={self.data_level.value}"
                )
        elif self.data_level == DataLevel.WIP:
            if self.wip_id is None:
                raise ValueError(
                    f"wip_id is required when data_level='WIP'. "
                    f"Current: wip_id={self.wip_id}, data_level={self.data_level.value}"
                )
            if self.serial_id is not None:
                raise ValueError(
                    f"serial_id must be None when data_level='WIP'. "
                    f"Current: serial_id={self.serial_id}, data_level={self.data_level.value}"
                )
        elif self.data_level == DataLevel.LOT:
            if self.serial_id is not None:
                raise ValueError(
                    f"serial_id must be None when data_level='LOT'. "
                    f"Current: serial_id={self.serial_id}, data_level={self.data_level.value}"
                )
            if self.wip_id is not None:
                raise ValueError(
                    f"wip_id must be None when data_level='LOT'. "
                    f"Current: wip_id={self.wip_id}, data_level={self.data_level.value}"
                )
        return self

    @model_validator(mode="after")
    def validate_defects_result_consistency(self) -> "ProcessDataBase":
        """
        Validate defects field consistency with result.

        Rules:
            - If result=FAIL: defects MUST be provided (non-empty dict)
            - If result=PASS: defects should be None or empty
            - If result=FAIL and no notes: recommend adding notes

        Returns:
            Self instance if valid

        Raises:
            ValueError: If defects/result are inconsistent
        """
        if self.result == ProcessResult.FAIL:
            if not self.defects:
                raise ValueError(
                    f"defects information is required when result='FAIL'. "
                    f"Current: result={self.result.value}, defects={self.defects}. "
                    f"Please provide defect details such as type, location, and severity."
                )

            # Recommend notes for FAIL results
            if not self.notes:
                warnings.warn(
                    f"Notes are recommended when result='FAIL' to provide additional context. "
                    f"Current: result={self.result.value}, notes={self.notes}",
                    UserWarning
                )

        elif self.result == ProcessResult.PASS:
            if self.defects:
                raise ValueError(
                    f"defects should be None or empty when result='PASS'. "
                    f"Current: result={self.result.value}, defects={self.defects}"
                )

        elif self.result == ProcessResult.REWORK:
            # REWORK can have defects (documenting the reason for rework) or not
            if self.defects and not self.notes:
                warnings.warn(
                    f"Notes are recommended when result='REWORK' with defects to explain the rework reason. "
                    f"Current: result={self.result.value}, defects={self.defects}, notes={self.notes}",
                    UserWarning
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
                duration = (self.started_at - self.completed_at).total_seconds()
                raise ValueError(
                    f"completed_at must be greater than or equal to started_at. "
                    f"Current: started_at={self.started_at.isoformat()}, "
                    f"completed_at={self.completed_at.isoformat()}, "
                    f"invalid duration={duration} seconds"
                )
        return self

    @model_validator(mode="after")
    def validate_comprehensive_business_rules(self) -> "ProcessDataBase":
        """
        Comprehensive business rules validation.

        This validator checks all business logic constraints at once to provide
        clear, actionable error messages with full context.

        Business Rules:
        1. Data consistency: lot_id, process_id, operator_id are always required
        2. Equipment tracking: Some processes may require equipment_id
        3. Result documentation: FAIL/REWORK results need proper documentation
        4. Timestamp logic: Process must have valid start time, completion is optional

        Returns:
            Self instance if valid

        Raises:
            ValueError: If any business rule is violated
        """
        errors = []
        warnings_list = []

        # Rule 1: Core fields validation
        if self.lot_id <= 0:
            errors.append(f"Invalid lot_id={self.lot_id}. Must be a positive integer.")

        if self.process_id <= 0:
            errors.append(f"Invalid process_id={self.process_id}. Must be a positive integer.")

        if self.operator_id <= 0:
            errors.append(f"Invalid operator_id={self.operator_id}. Must be a positive integer.")

        # Rule 2: Data level specific validation
        if self.data_level == DataLevel.SERIAL and self.serial_id and self.serial_id <= 0:
            errors.append(
                f"Invalid serial_id={self.serial_id} for data_level='SERIAL'. "
                f"Must be a positive integer."
            )

        if self.data_level == DataLevel.WIP and self.wip_id and self.wip_id <= 0:
            errors.append(
                f"Invalid wip_id={self.wip_id} for data_level='WIP'. "
                f"Must be a positive integer."
            )

        # Rule 3: Equipment validation
        if self.equipment_id is not None and self.equipment_id <= 0:
            errors.append(
                f"Invalid equipment_id={self.equipment_id}. "
                f"Must be a positive integer or None."
            )

        # Rule 4: Result documentation
        if self.result in [ProcessResult.FAIL, ProcessResult.REWORK]:
            if not self.defects and not self.notes:
                warnings_list.append(
                    f"Result '{self.result.value}' should have either defects or notes "
                    f"to document the reason."
                )

        # Rule 5: Measurement validation for specific processes
        # This is a placeholder for process-specific validation
        # Different processes may require different measurements
        if not self.measurements:
            warnings_list.append(
                f"No measurements provided for process_id={self.process_id}. "
                f"Consider adding relevant process measurements."
            )

        # Raise all errors at once with clear context
        if errors:
            error_msg = (
                "Business rules validation failed:\n" +
                "\n".join(f"  - {error}" for error in errors) +
                f"\n\nCurrent data state:" +
                f"\n  data_level: {self.data_level.value}" +
                f"\n  result: {self.result.value}" +
                f"\n  lot_id: {self.lot_id}" +
                f"\n  serial_id: {self.serial_id}" +
                f"\n  wip_id: {self.wip_id}" +
                f"\n  process_id: {self.process_id}" +
                f"\n  has_defects: {bool(self.defects)}" +
                f"\n  has_notes: {bool(self.notes)}" +
                f"\n  has_measurements: {bool(self.measurements)}"
            )
            raise ValueError(error_msg)

        # Issue warnings for non-critical issues
        for warning in warnings_list:
            warnings.warn(warning, UserWarning)

        return self


class ProcessDataCreate(ProcessDataBase):
    """
    Schema for creating new ProcessData records.

    Inherits all validation from ProcessDataBase.
    All required fields must be provided on creation.

    Example:
        Valid creation request:
        {
            "lot_id": 1,
            "serial_id": 100,
            "process_id": 5,
            "operator_id": 2,
            "equipment_id": 3,
            "data_level": "SERIAL",
            "result": "PASS",
            "measurements": {
                "temperature": 25.5,
                "pressure": 1.0,
                "humidity": 45
            },
            "started_at": "2024-01-01T10:00:00",
            "completed_at": "2024-01-01T10:15:00"
        }
    """
    pass


class ProcessDataUpdate(BaseModel):
    """
    Schema for updating ProcessData records.

    All fields are optional to allow partial updates.
    Validators ensure consistency when fields are provided.

    Attributes:
        equipment_id: Equipment identifier (optional)
        data_level: Data granularity level (optional)
        result: Process result (optional)
        measurements: Process measurements (optional)
        defects: Defect information (optional)
        completed_at: Process completion timestamp (optional)
        notes: Additional comments (optional)

    Note: lot_id, serial_id, wip_id, process_id, operator_id, and started_at
          cannot be updated after creation for data integrity.
    """

    equipment_id: Optional[int] = Field(
        None, gt=0, description="Equipment identifier"
    )
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
                valid_values = [e.value for e in DataLevel]
                raise ValueError(
                    f"Invalid data_level '{v}'. Must be one of {valid_values}. "
                    f"Current value: '{v}'"
                )
        raise ValueError(
            f"data_level must be a string or DataLevel enum, got {type(v).__name__}"
        )

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
                valid_values = [e.value for e in ProcessResult]
                raise ValueError(
                    f"Invalid result '{v}'. Must be one of {valid_values}. "
                    f"Current value: '{v}'"
                )
        raise ValueError(
            f"result must be a string or ProcessResult enum, got {type(v).__name__}"
        )

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
        if v is None:
            return None
        if not isinstance(v, dict):
            raise ValueError(
                f"measurements must be a dictionary, got {type(v).__name__}"
            )

        # Validate measurement structure
        for key, value in v.items():
            if not isinstance(key, str):
                raise ValueError(
                    f"measurement keys must be strings, got {type(key).__name__} for key {key}"
                )
            if not isinstance(value, (str, int, float, bool, list, dict, type(None))):
                raise ValueError(
                    f"measurement value for '{key}' must be JSON-serializable, "
                    f"got {type(value).__name__}"
                )

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
        if v is None:
            return None
        if not isinstance(v, dict):
            raise ValueError(
                f"defects must be a dictionary, got {type(v).__name__}"
            )

        # Empty dict is treated as None
        if not v:
            return None

        # Validate defect structure
        for key, value in v.items():
            if not isinstance(key, str):
                raise ValueError(
                    f"defect keys must be strings, got {type(key).__name__} for key {key}"
                )
            if not isinstance(value, (str, int, float, bool, list, dict, type(None))):
                raise ValueError(
                    f"defect value for '{key}' must be JSON-serializable, "
                    f"got {type(value).__name__}"
                )

        return v

    @model_validator(mode="after")
    def validate_update_consistency(self) -> "ProcessDataUpdate":
        """
        Validate update consistency for partial updates.

        When updating result to FAIL, defects should be provided.
        When updating result to PASS, defects should be cleared.

        Returns:
            Self instance if valid
        """
        # Only validate if result is being updated
        if self.result is not None:
            if self.result == ProcessResult.FAIL and self.defects is None:
                warnings.warn(
                    f"Updating result to 'FAIL' without providing defects. "
                    f"Consider adding defect information.",
                    UserWarning
                )
            elif self.result == ProcessResult.PASS and self.defects:
                warnings.warn(
                    f"Updating result to 'PASS' with defects present. "
                    f"Defects should be cleared for PASS results.",
                    UserWarning
                )

        return self


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
        equipment: Nested Equipment relationship data

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
    equipment: Optional[EquipmentSchema] = Field(
        None, description="Nested Equipment relationship data"
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


# =============================================================================
# Measurement History Response Schemas
# =============================================================================

class MeasurementSpec(BaseModel):
    """Specification limits for a measurement."""
    min: Optional[float] = Field(None, description="Minimum acceptable value")
    max: Optional[float] = Field(None, description="Maximum acceptable value")
    target: Optional[float] = Field(None, description="Target/nominal value")


class MeasurementHistoryItem(BaseModel):
    """Single measurement item in history response."""
    code: str = Field(..., description="Measurement code identifier")
    name: str = Field(..., description="Measurement display name")
    value: float = Field(..., description="Measured value")
    unit: Optional[str] = Field(None, description="Measurement unit (V, A, mm, etc.)")
    spec: Optional[MeasurementSpec] = Field(None, description="Specification limits")
    result: str = Field(default="PASS", description="Measurement result (PASS/FAIL)")


class MeasurementHistoryResponse(BaseModel):
    """Single measurement history record response."""
    id: int = Field(..., description="Process data record ID")
    lot_number: str = Field(..., description="LOT number")
    wip_id: Optional[str] = Field(None, description="WIP item ID")
    serial_number: Optional[str] = Field(None, description="Serial number")
    process_name: str = Field(..., description="Process name (Korean)")
    process_number: int = Field(..., description="Process sequence number (1-8)")
    result: str = Field(..., description="Overall process result (PASS/FAIL/REWORK)")
    operator_name: str = Field(..., description="Operator full name")
    measurements: List[MeasurementHistoryItem] = Field(
        default_factory=list, description="List of measurement items"
    )
    started_at: datetime = Field(..., description="Process start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Process completion timestamp")
    duration_seconds: Optional[int] = Field(None, description="Process duration in seconds")

    model_config = ConfigDict(from_attributes=True)


class MeasurementHistoryListResponse(BaseModel):
    """Paginated list response for measurement history."""
    items: List[MeasurementHistoryResponse] = Field(
        default_factory=list, description="List of measurement history records"
    )
    total: int = Field(..., description="Total number of records matching filters")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum records per page")


class ProcessMeasurementSummary(BaseModel):
    """Summary statistics for a specific process."""
    process_id: int = Field(..., description="Process ID")
    process_name: str = Field(..., description="Process name (Korean)")
    total: int = Field(..., description="Total records count")
    fail: int = Field(..., description="Failed records count")
    rate: float = Field(..., description="Failure rate percentage")


class MeasurementSummaryResponse(BaseModel):
    """Summary statistics response for measurement data."""
    total_count: int = Field(..., description="Total measurement records")
    pass_count: int = Field(..., description="PASS result count")
    fail_count: int = Field(..., description="FAIL result count")
    rework_count: int = Field(..., description="REWORK result count")
    pass_rate: float = Field(..., description="Pass rate percentage")
    by_process: List[ProcessMeasurementSummary] = Field(
        default_factory=list, description="Statistics grouped by process"
    )


# =============================================================================
# Measurement Code Schemas
# =============================================================================

class MeasurementCodeInfo(BaseModel):
    """Information about a unique measurement code found in the database."""
    code: str = Field(..., description="Measurement code identifier")
    name: str = Field(..., description="Measurement display name")
    unit: Optional[str] = Field(None, description="Measurement unit (V, A, mm, etc.)")
    count: int = Field(..., description="Number of records with this measurement")
    process_ids: List[int] = Field(default_factory=list, description="Process IDs where this measurement appears")


class MeasurementCodesResponse(BaseModel):
    """Response containing all unique measurement codes from the database."""
    codes: List[MeasurementCodeInfo] = Field(
        default_factory=list, description="List of unique measurement codes"
    )
    total_codes: int = Field(..., description="Total number of unique codes")


# =============================================================================
# Context Validation Helper
# =============================================================================

def validate_process_data_context(
    lot_id: int,
    serial_id: Optional[int],
    wip_id: Optional[int],
    process_id: int,
    operator_id: int,
    equipment_id: Optional[int],
    data_level: DataLevel,
    db_session: Any  # SQLAlchemy session
) -> Dict[str, Any]:
    """
    Validate process data context against database constraints.

    This function performs comprehensive validation of process data against
    the current database state to ensure referential integrity and business rules.

    Args:
        lot_id: Lot identifier to validate
        serial_id: Serial identifier to validate (if SERIAL level)
        wip_id: WIP item identifier to validate (if WIP level)
        process_id: Process identifier to validate
        operator_id: Operator identifier to validate
        equipment_id: Equipment identifier to validate (if provided)
        data_level: Data level (LOT, WIP, or SERIAL)
        db_session: Database session for validation queries

    Returns:
        Dict with validation results:
        {
            "valid": bool,
            "errors": List[str],
            "warnings": List[str],
            "context": {
                "lot": {...},
                "serial": {...},
                "wip": {...},
                "process": {...},
                "operator": {...},
                "equipment": {...},
                "duplicate_check": bool
            }
        }

    Example:
        result = validate_process_data_context(
            lot_id=1,
            serial_id=100,
            wip_id=None,
            process_id=5,
            operator_id=2,
            equipment_id=3,
            data_level=DataLevel.SERIAL,
            db_session=db
        )

        if not result["valid"]:
            raise ValueError("Validation failed: " + "; ".join(result["errors"]))
    """
    # This is a placeholder for the actual implementation
    # The actual implementation would query the database to validate:
    # 1. Lot exists and is active
    # 2. Serial exists and belongs to the lot (if SERIAL level)
    # 3. WIP item exists and is active (if WIP level)
    # 4. Process exists and is active
    # 5. Operator exists and has proper permissions
    # 6. Equipment exists and is active (if provided)
    # 7. No duplicate process execution for same entity

    errors = []
    warnings = []
    context = {}

    # Placeholder validation logic
    # In actual implementation, these would be database queries

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "context": context
    }