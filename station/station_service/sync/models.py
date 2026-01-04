"""
Pydantic models for Backend API communication.

Defines request/response models for WIP process operations:
- Process Start (착공)
- Process Complete (완공)
- Serial Convert (시리얼 변환)
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ============================================================
# Request Models
# ============================================================


class ProcessStartRequest(BaseModel):
    """Request model for starting a process (착공)."""

    process_id: int = Field(..., ge=1, le=8, description="Process number (1-8)")
    header_id: Optional[int] = Field(None, description="Process header ID for station/batch tracking")
    operator_id: int = Field(..., gt=0, description="Operator ID")
    equipment_id: Optional[int] = Field(None, gt=0, description="Equipment ID (optional)")
    started_at: Optional[datetime] = Field(None, description="Start time (defaults to now)")


class ProcessCompleteRequest(BaseModel):
    """Request model for completing a process (완공)."""

    result: str = Field(..., pattern="^(PASS|FAIL|REWORK)$", description="Process result")
    header_id: Optional[int] = Field(None, description="Process header ID for station/batch tracking")
    measurements: Dict[str, Any] = Field(
        default_factory=dict,
        description="Measurement data from sequence execution",
    )
    defects: List[str] = Field(
        default_factory=list,
        description="Defect codes if result is FAIL",
    )
    notes: Optional[str] = Field(None, description="Operator notes")
    started_at: Optional[datetime] = Field(None, description="Start time from 착공")
    completed_at: Optional[datetime] = Field(None, description="Completion time (defaults to now)")


class SerialConvertRequest(BaseModel):
    """Request model for converting WIP to serial."""

    operator_id: int = Field(..., gt=0, description="Operator ID")
    notes: Optional[str] = Field(None, description="Conversion notes")


# ============================================================
# Response/Lookup Models
# ============================================================


class WIPLookupResult(BaseModel):
    """Result model from WIP lookup (scan) operation."""

    id: int = Field(..., description="Integer ID for API calls")
    wip_id: str = Field(..., description="String WIP ID from barcode")
    status: str = Field(..., description="Current WIP status")
    lot_id: int = Field(..., description="Associated LOT ID")
    sequence_in_lot: int = Field(..., description="Sequence number within LOT")
    current_process_id: Optional[int] = Field(None, description="Current process ID if in progress")
    has_pass_for_process: Optional[bool] = Field(
        None, description="True if WIP already has PASS result for the requested process"
    )
    pass_warning_message: Optional[str] = Field(
        None, description="Warning message if has_pass_for_process is True"
    )

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "WIPLookupResult":
        """Create WIPLookupResult from Backend API response."""
        return cls(
            id=data["id"],
            wip_id=data["wip_id"],
            status=data["status"],
            lot_id=data["lot_id"],
            sequence_in_lot=data.get("sequence_in_lot", 0),
            current_process_id=data.get("current_process_id"),
            has_pass_for_process=data.get("has_pass_for_process"),
            pass_warning_message=data.get("pass_warning_message"),
        )


class ProcessStartResponse(BaseModel):
    """Response model from start-process API."""

    wip_item: Dict[str, Any] = Field(..., description="Updated WIP item data")
    message: str = Field(..., description="Success message")


class ProcessCompleteResponse(BaseModel):
    """Response model from complete-process API."""

    process_history: Dict[str, Any] = Field(..., description="Process history record")
    wip_item: Dict[str, Any] = Field(..., description="Updated WIP item data")


class SerialConvertResponse(BaseModel):
    """Response model from convert-to-serial API."""

    serial: Dict[str, Any] = Field(..., description="Created serial data")
    wip_item: Dict[str, Any] = Field(..., description="Updated WIP item data")


class BackendErrorResponse(BaseModel):
    """Error response from Backend API."""

    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error info")


# ============================================================
# Process Header Models (Station/Batch tracking)
# ============================================================


class ProcessHeaderOpenRequest(BaseModel):
    """Request model for opening a process header (batch start)."""

    station_id: str = Field(..., description="Station identifier")
    batch_id: str = Field(..., description="Batch identifier")
    process_id: int = Field(..., description="Process ID (foreign key)")
    sequence_package: Optional[str] = Field(None, description="Sequence package name")
    sequence_version: Optional[str] = Field(None, description="Sequence version")
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Batch parameters snapshot",
    )
    hardware_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Hardware configuration snapshot",
    )


class ProcessHeaderCloseRequest(BaseModel):
    """Request model for closing a process header (batch end)."""

    status: str = Field(
        default="CLOSED",
        pattern="^(CLOSED|CANCELLED)$",
        description="Final status: CLOSED or CANCELLED",
    )


class ProcessHeaderSummary(BaseModel):
    """Summary model for process header (for list views)."""

    id: int = Field(..., description="Header ID")
    station_id: str = Field(..., description="Station identifier")
    batch_id: str = Field(..., description="Batch identifier")
    process_id: int = Field(..., description="Process ID")
    status: str = Field(..., description="Header status: OPEN, CLOSED, CANCELLED")
    total_count: int = Field(default=0, description="Total WIP items processed")
    pass_count: int = Field(default=0, description="Number of PASS results")
    fail_count: int = Field(default=0, description="Number of FAIL results")
    opened_at: datetime = Field(..., description="When header was opened")
    closed_at: Optional[datetime] = Field(None, description="When header was closed")
    process_name: Optional[str] = Field(None, description="Process name (from relation)")
    process_code: Optional[str] = Field(None, description="Process code (from relation)")

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "ProcessHeaderSummary":
        """Create ProcessHeaderSummary from Backend API response."""
        opened_at_str = data.get("opened_at", data.get("openedAt", ""))
        closed_at_str = data.get("closed_at", data.get("closedAt"))

        return cls(
            id=data["id"],
            station_id=data.get("station_id", data.get("stationId", "")),
            batch_id=data.get("batch_id", data.get("batchId", "")),
            process_id=data.get("process_id", data.get("processId", 0)),
            status=data["status"],
            total_count=data.get("total_count", data.get("totalCount", 0)),
            pass_count=data.get("pass_count", data.get("passCount", 0)),
            fail_count=data.get("fail_count", data.get("failCount", 0)),
            opened_at=datetime.fromisoformat(opened_at_str.replace("Z", "+00:00")) if opened_at_str else datetime.now(),
            closed_at=(
                datetime.fromisoformat(closed_at_str.replace("Z", "+00:00"))
                if closed_at_str
                else None
            ),
            process_name=data.get("process_name", data.get("processName")),
            process_code=data.get("process_code", data.get("processCode")),
        )


class ProcessHeaderResponse(BaseModel):
    """Response model for process header operations."""

    id: int = Field(..., description="Header ID")
    station_id: str = Field(..., description="Station identifier")
    batch_id: str = Field(..., description="Batch identifier")
    process_id: int = Field(..., description="Process ID")
    status: str = Field(..., description="Header status: OPEN, CLOSED, CANCELLED")
    opened_at: datetime = Field(..., description="When header was opened")
    closed_at: Optional[datetime] = Field(None, description="When header was closed")
    total_count: int = Field(default=0, description="Total WIP items processed")
    pass_count: int = Field(default=0, description="Number of PASS results")
    fail_count: int = Field(default=0, description="Number of FAIL results")
    sequence_package: Optional[str] = Field(None, description="Sequence package name")
    sequence_version: Optional[str] = Field(None, description="Sequence version")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters snapshot")
    hardware_config: Dict[str, Any] = Field(default_factory=dict, description="Hardware snapshot")

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "ProcessHeaderResponse":
        """Create ProcessHeaderResponse from Backend API response."""
        return cls(
            id=data["id"],
            station_id=data["station_id"],
            batch_id=data["batch_id"],
            process_id=data["process_id"],
            status=data["status"],
            opened_at=datetime.fromisoformat(data["opened_at"].replace("Z", "+00:00")),
            closed_at=(
                datetime.fromisoformat(data["closed_at"].replace("Z", "+00:00"))
                if data.get("closed_at")
                else None
            ),
            total_count=data.get("total_count", 0),
            pass_count=data.get("pass_count", 0),
            fail_count=data.get("fail_count", 0),
            sequence_package=data.get("sequence_package"),
            sequence_version=data.get("sequence_version"),
            parameters=data.get("parameters", {}),
            hardware_config=data.get("hardware_config", {}),
        )


# ============================================================
# Sequence Pull Models (CLI-based sequence deployment)
# ============================================================


class SequencePullRequest(BaseModel):
    """Request model for pulling sequence from Backend."""

    station_id: str = Field(..., description="Station identifier for authentication")
    batch_id: Optional[str] = Field(None, description="Target batch ID (optional)")
    current_version: Optional[str] = Field(
        None, description="Currently installed version (for update check)"
    )


class SequencePullResponse(BaseModel):
    """Response model from sequence pull operation."""

    name: str = Field(..., description="Sequence name")
    version: str = Field(..., description="Latest version")
    checksum: str = Field(..., description="SHA-256 checksum of package")
    package_size: int = Field(..., description="Package size in bytes")
    needs_update: bool = Field(..., description="Whether station needs to update")
    package_data: Optional[str] = Field(
        None, description="Base64-encoded ZIP package (only if needs_update)"
    )

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "SequencePullResponse":
        """Create SequencePullResponse from Backend API response."""
        return cls(
            name=data["name"],
            version=data["version"],
            checksum=data["checksum"],
            package_size=data["package_size"],
            needs_update=data["needs_update"],
            package_data=data.get("package_data"),
        )
