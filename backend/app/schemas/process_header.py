"""
Pydantic schemas for the ProcessHeader entity.

This module provides request/response schemas for process header (execution session)
management in the F2X NeuroHub Manufacturing Execution System.

ProcessHeader tracks execution sessions at the station/batch level, enabling:
- Station/batch-level process tracking
- Parameter and hardware configuration snapshots
- Aggregated statistics (pass/fail counts)

Schemas:
    - HeaderStatus: Enum for header status
    - ProcessHeaderBase: Base schema with core fields
    - ProcessHeaderCreate: Schema for creating new headers
    - ProcessHeaderUpdate: Schema for updating headers
    - ProcessHeaderOpen: Schema for opening a new header
    - ProcessHeaderClose: Schema for closing a header
    - ProcessHeaderInDB: Schema for database response
    - ProcessHeaderSummary: Summary schema for list views
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


class HeaderStatus(str, Enum):
    """
    Process header status enumeration.

    Attributes:
        OPEN: Header is active, accepting new process executions
        CLOSED: Header is closed, batch execution completed normally
        CANCELLED: Header was cancelled before completion
    """
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class ProcessSchema(BaseModel):
    """Nested Process schema for relationship data."""
    id: int
    process_number: int
    process_code: str
    process_name_en: str
    process_name_ko: str

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Base Schema
# =============================================================================

class ProcessHeaderBase(BaseModel):
    """
    Base schema for ProcessHeader with core fields.

    Attributes:
        station_id: Station identifier from station config
        batch_id: Batch identifier from station_service
        process_id: Foreign key to processes table
        sequence_package: Sequence package name (optional)
        sequence_version: Sequence version at execution time (optional)
        parameters: Batch parameters snapshot (JSONB)
        hardware_config: Hardware configuration snapshot (JSONB)
    """
    station_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Station identifier from station config"
    )
    batch_id: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Batch identifier from station_service"
    )
    process_id: int = Field(
        ...,
        gt=0,
        description="Process identifier (1-100)"
    )
    sequence_package: Optional[str] = Field(
        None,
        max_length=255,
        description="Sequence package name (e.g., sensor_inspection)"
    )
    sequence_version: Optional[str] = Field(
        None,
        max_length=50,
        description="Sequence version at execution time"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Batch parameters snapshot"
    )
    hardware_config: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Hardware configuration snapshot"
    )

    @field_validator("parameters", "hardware_config", mode="before")
    @classmethod
    def validate_jsonb_dict(cls, v: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate JSONB dict fields."""
        if v is None:
            return {}
        if not isinstance(v, dict):
            raise ValueError(f"Expected dict, got {type(v).__name__}")
        return v


# =============================================================================
# Create/Update Schemas
# =============================================================================

class ProcessHeaderCreate(ProcessHeaderBase):
    """
    Schema for creating new ProcessHeader records.

    Inherits all fields from ProcessHeaderBase.
    Status defaults to OPEN and opened_at is set automatically.
    """
    pass


class ProcessHeaderOpen(BaseModel):
    """
    Schema for opening a new process header.

    This is the primary way to create a header when a batch starts processing.
    If a header already exists for the same station+batch+process and is OPEN,
    the existing header will be returned instead of creating a new one.
    """
    station_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Station identifier"
    )
    batch_id: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Batch identifier"
    )
    process_id: int = Field(
        ...,
        gt=0,
        description="Process identifier"
    )
    slot_id: Optional[int] = Field(
        None,
        ge=1,
        le=12,
        description="Slot ID for UI display order (1-12, auto-assigned if not provided)"
    )
    sequence_package: Optional[str] = Field(
        None,
        max_length=255,
        description="Sequence package name"
    )
    sequence_version: Optional[str] = Field(
        None,
        max_length=50,
        description="Sequence version"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Batch parameters snapshot"
    )
    hardware_config: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Hardware configuration snapshot"
    )

    @field_validator("parameters", "hardware_config", mode="before")
    @classmethod
    def validate_jsonb_dict(cls, v: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate JSONB dict fields."""
        if v is None:
            return {}
        if not isinstance(v, dict):
            raise ValueError(f"Expected dict, got {type(v).__name__}")
        return v


class ProcessHeaderClose(BaseModel):
    """
    Schema for closing an open header.

    Only OPEN headers can be closed. The status will be set to CLOSED
    and closed_at will be set to current timestamp.
    """
    notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional notes about the closure"
    )


class ProcessHeaderCancel(BaseModel):
    """
    Schema for cancelling an open header.

    Only OPEN headers can be cancelled. The status will be set to CANCELLED
    and closed_at will be set to current timestamp.
    """
    reason: Optional[str] = Field(
        None,
        max_length=1000,
        description="Reason for cancellation"
    )


class ProcessHeaderUpdate(BaseModel):
    """
    Schema for updating ProcessHeader records.

    Only parameters and hardware_config can be updated.
    Status changes should use close/cancel endpoints.
    """
    parameters: Optional[Dict[str, Any]] = Field(
        None,
        description="Updated batch parameters"
    )
    hardware_config: Optional[Dict[str, Any]] = Field(
        None,
        description="Updated hardware configuration"
    )

    @field_validator("parameters", "hardware_config", mode="before")
    @classmethod
    def validate_jsonb_dict(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Validate JSONB dict fields."""
        if v is None:
            return None
        if not isinstance(v, dict):
            raise ValueError(f"Expected dict, got {type(v).__name__}")
        return v

    model_config = ConfigDict(validate_assignment=True)


# =============================================================================
# Response Schemas
# =============================================================================

class ProcessHeaderInDB(ProcessHeaderBase):
    """
    Schema for ProcessHeader database response.

    Extends ProcessHeaderBase with database-generated fields
    and calculated properties.
    """
    id: int = Field(..., description="Header identifier")
    slot_id: Optional[int] = Field(None, description="Slot ID for UI display order (1-12)")
    status: HeaderStatus = Field(..., description="Header status")
    opened_at: datetime = Field(..., description="When header was opened")
    closed_at: Optional[datetime] = Field(None, description="When header was closed")
    total_count: int = Field(default=0, description="Total items processed")
    pass_count: int = Field(default=0, description="Number of PASS results")
    fail_count: int = Field(default=0, description="Number of FAIL results")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    # Nested relationships
    process: Optional[ProcessSchema] = Field(
        None,
        description="Nested Process relationship data"
    )

    # Calculated properties
    pass_rate: Optional[float] = Field(
        None,
        description="Pass rate percentage"
    )
    fail_rate: Optional[float] = Field(
        None,
        description="Fail rate percentage"
    )
    duration_seconds: Optional[int] = Field(
        None,
        description="Duration in seconds (if closed)"
    )

    model_config = ConfigDict(from_attributes=True)

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, v: Any) -> HeaderStatus:
        """Validate and convert status to HeaderStatus enum."""
        if isinstance(v, HeaderStatus):
            return v
        if isinstance(v, str):
            try:
                return HeaderStatus(v.upper())
            except ValueError:
                valid_values = [e.value for e in HeaderStatus]
                raise ValueError(f"Invalid status '{v}'. Must be one of {valid_values}")
        raise ValueError(f"status must be a string or HeaderStatus enum, got {type(v).__name__}")

    @model_validator(mode="after")
    def calculate_rates(self) -> "ProcessHeaderInDB":
        """Calculate pass/fail rates from counts."""
        if self.total_count > 0:
            self.pass_rate = round((self.pass_count / self.total_count) * 100, 2)
            self.fail_rate = round((self.fail_count / self.total_count) * 100, 2)
        else:
            self.pass_rate = 0.0
            self.fail_rate = 0.0

        # Calculate duration if closed
        if self.opened_at and self.closed_at:
            delta = self.closed_at - self.opened_at
            self.duration_seconds = int(delta.total_seconds())

        return self


class ProcessHeaderSummary(BaseModel):
    """
    Summary schema for list views (less detail).

    Used for list endpoints and dashboard displays.
    """
    id: int = Field(..., description="Header identifier")
    station_id: str = Field(..., description="Station identifier")
    batch_id: str = Field(..., description="Batch identifier")
    slot_id: Optional[int] = Field(None, description="Slot ID for UI display order (1-12)")
    process_id: int = Field(..., description="Process identifier")
    status: HeaderStatus = Field(..., description="Header status")
    total_count: int = Field(default=0, description="Total items processed")
    pass_count: int = Field(default=0, description="PASS count")
    fail_count: int = Field(default=0, description="FAIL count")
    pass_rate: float = Field(default=0.0, description="Pass rate percentage")
    opened_at: datetime = Field(..., description="When opened")
    closed_at: Optional[datetime] = Field(None, description="When closed")

    # Optional nested process info
    process_name: Optional[str] = Field(None, description="Process name (Korean)")
    process_code: Optional[str] = Field(None, description="Process code")

    model_config = ConfigDict(from_attributes=True)

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, v: Any) -> HeaderStatus:
        """Validate and convert status to HeaderStatus enum."""
        if isinstance(v, HeaderStatus):
            return v
        if isinstance(v, str):
            try:
                return HeaderStatus(v.upper())
            except ValueError:
                valid_values = [e.value for e in HeaderStatus]
                raise ValueError(f"Invalid status '{v}'. Must be one of {valid_values}")
        raise ValueError(f"status must be a string or HeaderStatus enum")

    @model_validator(mode="after")
    def calculate_pass_rate(self) -> "ProcessHeaderSummary":
        """Calculate pass rate from counts."""
        if self.total_count > 0:
            self.pass_rate = round((self.pass_count / self.total_count) * 100, 2)
        else:
            self.pass_rate = 0.0
        return self


# =============================================================================
# List Response Schemas
# =============================================================================

class ProcessHeaderListResponse(BaseModel):
    """Paginated list response for process headers."""
    items: List[ProcessHeaderSummary] = Field(
        default_factory=list,
        description="List of process header summaries"
    )
    total: int = Field(..., description="Total count matching filters")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum records per page")


class ProcessHeaderStatsResponse(BaseModel):
    """Statistics response for process headers."""
    total_headers: int = Field(..., description="Total number of headers")
    open_headers: int = Field(..., description="Currently open headers")
    closed_headers: int = Field(..., description="Closed headers")
    cancelled_headers: int = Field(..., description="Cancelled headers")
    total_items_processed: int = Field(..., description="Total items across all headers")
    total_pass: int = Field(..., description="Total PASS results")
    total_fail: int = Field(..., description="Total FAIL results")
    overall_pass_rate: float = Field(..., description="Overall pass rate percentage")

    # Breakdown by station
    by_station: Optional[Dict[str, Dict[str, Any]]] = Field(
        None,
        description="Statistics grouped by station_id"
    )

    # Breakdown by process
    by_process: Optional[Dict[int, Dict[str, Any]]] = Field(
        None,
        description="Statistics grouped by process_id"
    )


# =============================================================================
# Filter Schema
# =============================================================================

class ProcessHeaderFilter(BaseModel):
    """Filter schema for querying process headers."""
    station_id: Optional[str] = Field(None, description="Filter by station ID")
    batch_id: Optional[str] = Field(None, description="Filter by batch ID")
    process_id: Optional[int] = Field(None, gt=0, description="Filter by process ID")
    status: Optional[HeaderStatus] = Field(None, description="Filter by status")
    opened_after: Optional[datetime] = Field(None, description="Filter headers opened after this time")
    opened_before: Optional[datetime] = Field(None, description="Filter headers opened before this time")
    closed_after: Optional[datetime] = Field(None, description="Filter headers closed after this time")
    closed_before: Optional[datetime] = Field(None, description="Filter headers closed before this time")

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, v: Any) -> Optional[HeaderStatus]:
        """Validate and convert status to HeaderStatus enum."""
        if v is None:
            return None
        if isinstance(v, HeaderStatus):
            return v
        if isinstance(v, str):
            try:
                return HeaderStatus(v.upper())
            except ValueError:
                valid_values = [e.value for e in HeaderStatus]
                raise ValueError(f"Invalid status '{v}'. Must be one of {valid_values}")
        raise ValueError(f"status must be a string or HeaderStatus enum")

    @model_validator(mode="after")
    def validate_date_ranges(self) -> "ProcessHeaderFilter":
        """Validate that date ranges are valid."""
        if self.opened_after and self.opened_before:
            if self.opened_after > self.opened_before:
                raise ValueError("opened_after must be before opened_before")
        if self.closed_after and self.closed_before:
            if self.closed_after > self.closed_before:
                raise ValueError("closed_after must be before closed_before")
        return self
