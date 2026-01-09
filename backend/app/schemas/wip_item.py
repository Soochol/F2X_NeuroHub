"""
Pydantic schemas for the WIP Item entity.

This module provides request/response schemas for WIP (Work-In-Progress) item
management in the F2X NeuroHub Manufacturing Execution System. It includes
validation for WIP ID format, status lifecycle, and relationships to LOT,
processes, and serial numbers.

Schemas:
    - WIPStatus: Enumeration of WIP lifecycle statuses
    - WIPItemBase: Base schema with core fields and validators
    - WIPItemCreate: Schema for creating new WIP items (batch generation)
    - WIPItemUpdate: Schema for updating existing WIP items
    - WIPItemInDB: Schema for database response with relationships
    - WIPItemScan: Schema for barcode scan operations
    - WIPItemProcessStart: Schema for starting a process
    - WIPItemProcessComplete: Schema for completing a process
    - WIPItemConvert: Schema for converting WIP to serial

Key Features:
    - WIPStatus enum: CREATED, IN_PROGRESS, COMPLETED, FAILED, CONVERTED
    - WIP ID format validation: WIP-{LOT 11}-{SEQ 3} = 19 chars
    - Sequence validation: 1-100 units per LOT
    - Process number validation: 1-6 (processes before serial conversion)
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class WIPStatus(str, Enum):
    """
    WIP lifecycle status enumeration.

    Attributes:
        CREATED: Initial state after WIP creation
        IN_PROGRESS: Currently being processed
        COMPLETED: All processes (1-6) completed, ready for serial conversion
        FAILED: Failed quality check
        CONVERTED: Successfully converted to serial number (terminal state)
    """
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CONVERTED = "CONVERTED"


class WIPItemBase(BaseModel):
    """
    Base schema for WIP Item with core fields and validation.

    Attributes:
        wip_id: Unique WIP identifier (format: WIP-{LOT}-{SEQ})
        lot_id: Foreign key to lots table
        sequence_in_lot: Sequence number within LOT (1-100)
        status: WIP lifecycle status
    """
    lot_id: int = Field(..., gt=0, description="LOT identifier")
    sequence_in_lot: int = Field(
        ...,
        ge=1,
        le=100,
        description="Sequence number within LOT (1-100)"
    )

    @field_validator("sequence_in_lot")
    @classmethod
    def validate_sequence(cls, v: int) -> int:
        """Validate sequence is within valid range.

        Args:
            v: Sequence number value

        Returns:
            Validated sequence number

        Raises:
            ValueError: If sequence is outside 1-100 range
        """
        if v < 1 or v > 100:
            raise ValueError("sequence_in_lot must be between 1 and 100")
        return v


class WIPItemCreate(BaseModel):
    """
    Schema for creating WIP items in batch.

    This schema is used for batch generation of WIP IDs when starting
    LOT production. Quantity determines how many WIP IDs are generated.

    Attributes:
        lot_id: LOT identifier for which to generate WIP IDs
        quantity: Number of WIP IDs to generate (1-100)
    """
    lot_id: int = Field(..., gt=0, description="LOT identifier")
    quantity: int = Field(
        ...,
        ge=1,
        le=100,
        description="Number of WIP IDs to generate (1-100)"
    )

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        """Validate quantity is within valid range.

        Args:
            v: Quantity value

        Returns:
            Validated quantity

        Raises:
            ValueError: If quantity is outside 1-100 range
        """
        if v < 1 or v > 100:
            raise ValueError("quantity must be between 1 and 100")
        return v


class WIPItemUpdate(BaseModel):
    """
    Schema for updating WIP items.

    All fields are optional to allow partial updates.

    Attributes:
        status: Updated WIP status (optional)
        current_process_id: Updated current process (optional)
        serial_id: Serial number after conversion (optional)
        completed_at: Completion timestamp (optional)
        converted_at: Conversion timestamp (optional)
    """
    status: Optional[WIPStatus] = Field(
        None,
        description="WIP lifecycle status"
    )
    current_process_id: Optional[int] = Field(
        None,
        description="Current process identifier"
    )
    serial_id: Optional[int] = Field(
        None,
        description="Serial number after conversion"
    )
    completed_at: Optional[datetime] = Field(
        None,
        description="All processes completed timestamp"
    )
    converted_at: Optional[datetime] = Field(
        None,
        description="Serial conversion timestamp"
    )

    model_config = ConfigDict(validate_assignment=True)


class WIPItemInDB(WIPItemBase):
    """
    Schema for WIP Item database response with relationships.

    Extends WIPItemBase with database-generated fields and relationships.

    Attributes:
        id: Primary key identifier
        wip_id: Unique WIP identifier (WIP-{LOT}-{SEQ})
        status: WIP lifecycle status
        current_process_id: Current process (nullable)
        serial_id: Serial number after conversion (nullable)
        created_at: WIP creation timestamp
        updated_at: Last modification timestamp
        completed_at: All processes completed timestamp (optional)
        converted_at: Serial conversion timestamp (optional)
    """
    id: int = Field(..., description="WIP item identifier")
    wip_id: str = Field(
        ...,
        min_length=19,
        max_length=50,
        description="Unique WIP identifier (WIP-{LOT}-{SEQ})"
    )
    status: WIPStatus = Field(..., description="WIP lifecycle status")
    current_process_id: Optional[int] = Field(
        None,
        description="Current process identifier"
    )
    serial_id: Optional[int] = Field(
        None,
        description="Serial number after conversion"
    )
    created_at: datetime = Field(..., description="WIP creation timestamp")
    updated_at: datetime = Field(..., description="Last modification timestamp")
    completed_at: Optional[datetime] = Field(
        None,
        description="All processes completed timestamp"
    )
    converted_at: Optional[datetime] = Field(
        None,
        description="Serial conversion timestamp"
    )

    model_config = ConfigDict(from_attributes=True)


class WIPItemScan(BaseModel):
    """
    Schema for WIP barcode scan operations.

    Attributes:
        wip_id: Scanned WIP identifier
        process_id: Process for which WIP is being scanned (optional)
    """
    wip_id: str = Field(
        ...,
        min_length=19,
        max_length=50,
        pattern=r"^WIP-[A-Z0-9]{11}-[0-9]{3}$",
        description="Scanned WIP identifier (format: WIP-{LOT}-{SEQ})"
    )
    process_id: Optional[int] = Field(
        None,
        gt=0,
        description="Process identifier (optional)"
    )

    @field_validator("wip_id")
    @classmethod
    def validate_wip_id_format(cls, v: str) -> str:
        """Validate WIP ID format.

        Args:
            v: WIP ID string

        Returns:
            Validated WIP ID

        Raises:
            ValueError: If WIP ID format is invalid
        """
        if not v.startswith("WIP-"):
            raise ValueError("WIP ID must start with 'WIP-'")
        if len(v) != 19:
            raise ValueError("WIP ID must be 19 characters (WIP-{11 chars}-{3 digits})")
        return v.upper()


class WIPItemProcessStart(BaseModel):
    """
    Schema for starting a process on a WIP item.

    Attributes:
        process_id: Process identifier (1-6)
        operator_id: Operator performing the process
        equipment_id: Equipment used (optional)
        process_session_id: Process session ID for station/batch tracking (optional)
        started_at: Process start timestamp (optional, defaults to current time)
    """
    process_id: int = Field(
        ...,
        ge=1,
        le=6,
        description="Process identifier (1-6 only, process 7 is serial conversion)"
    )
    operator_id: int = Field(..., gt=0, description="Operator identifier")
    equipment_id: Optional[int] = Field(
        None,
        gt=0,
        description="Equipment identifier (optional)"
    )
    process_session_id: Optional[int] = Field(
        None,
        description="Process session ID for station/batch tracking (optional)"
    )
    started_at: Optional[datetime] = Field(
        None,
        description="Process start timestamp (optional, defaults to current time)"
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
            raise ValueError("process_id must be between 1 and 6 (process 7 is serial conversion)")
        return v


class WIPItemProcessComplete(BaseModel):
    """
    Schema for completing a process on a WIP item.

    Attributes:
        result: Process result (PASS or FAIL)
        measurements: Process-specific measurement data (optional)
        defects: Defect information if result=FAIL (optional)
        notes: Additional comments (optional)
        completed_at: Process completion timestamp (optional, defaults to current time)
    """
    result: str = Field(
        ...,
        pattern="^(PASS|FAIL|REWORK)$",
        description="Process result: PASS, FAIL, or REWORK"
    )
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
    started_at: Optional[datetime] = Field(
        None,
        description="Process start timestamp from 착공 (optional)"
    )
    completed_at: Optional[datetime] = Field(
        None,
        description="Process completion timestamp (optional, defaults to current time)"
    )

    @field_validator("result", mode="before")
    @classmethod
    def validate_result(cls, v: str) -> str:
        """Validate and normalize result value.

        Args:
            v: Result value

        Returns:
            Normalized result value (uppercase)

        Raises:
            ValueError: If result is not PASS, FAIL, or REWORK
        """
        if isinstance(v, str):
            v_upper = v.upper()
            if v_upper not in ("PASS", "FAIL", "REWORK"):
                raise ValueError("result must be 'PASS', 'FAIL', or 'REWORK'")
            return v_upper
        raise ValueError("result must be a string")


class WIPItemConvert(BaseModel):
    """
    Schema for converting WIP to serial number (process 7).

    Attributes:
        operator_id: Operator performing the conversion
        notes: Additional comments (optional)
    """
    operator_id: int = Field(..., gt=0, description="Operator identifier")
    notes: Optional[str] = Field(
        None,
        max_length=5000,
        description="Additional comments"
    )


class WIPScanResponse(WIPItemInDB):
    """
    Schema for WIP barcode scan response with process validation.

    Extends WIPItemInDB with additional fields for pre-validation:
    - has_pass_for_process: Whether WIP already PASS for the requested process
    - pass_warning_message: Warning message if already passed

    This allows UI to show warnings before starting a sequence,
    preventing the error from occurring only at completion time.
    """
    has_pass_for_process: Optional[bool] = Field(
        None,
        description="True if WIP already has PASS result for the requested process"
    )
    pass_warning_message: Optional[str] = Field(
        None,
        description="Warning message if has_pass_for_process is True"
    )


class WIPStatistics(BaseModel):
    """
    Schema for WIP statistics response.

    Attributes:
        total: Total number of WIP items
        created: Number of WIP items in CREATED status
        in_progress: Number of WIP items in IN_PROGRESS status
        completed: Number of WIP items in COMPLETED status
        failed: Number of WIP items in FAILED status
        converted: Number of WIP items in CONVERTED status
        by_lot: Statistics grouped by LOT (optional)
        by_process: Statistics grouped by current process (optional)
    """
    total: int = Field(..., ge=0, description="Total number of WIP items")
    created: int = Field(..., ge=0, description="WIP items in CREATED status")
    in_progress: int = Field(..., ge=0, description="WIP items in IN_PROGRESS status")
    completed: int = Field(..., ge=0, description="WIP items in COMPLETED status")
    failed: int = Field(..., ge=0, description="WIP items in FAILED status")
    converted: int = Field(..., ge=0, description="WIP items in CONVERTED status")
    by_lot: Optional[dict] = Field(
        None,
        description="Statistics grouped by LOT identifier"
    )
    by_process: Optional[dict] = Field(
        None,
        description="Statistics grouped by current process identifier"
    )

    model_config = ConfigDict(from_attributes=True)
