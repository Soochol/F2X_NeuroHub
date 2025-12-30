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
    operator_id: int = Field(..., gt=0, description="Operator ID")
    equipment_id: Optional[int] = Field(None, gt=0, description="Equipment ID (optional)")
    started_at: Optional[datetime] = Field(None, description="Start time (defaults to now)")


class ProcessCompleteRequest(BaseModel):
    """Request model for completing a process (완공)."""

    result: str = Field(..., pattern="^(PASS|FAIL|REWORK)$", description="Process result")
    measurements: Dict[str, Any] = Field(
        default_factory=dict,
        description="Measurement data from sequence execution",
    )
    defects: List[str] = Field(
        default_factory=list,
        description="Defect codes if result is FAIL",
    )
    notes: Optional[str] = Field(None, description="Operator notes")
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
