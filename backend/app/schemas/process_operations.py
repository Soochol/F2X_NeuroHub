from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ProcessStartRequest(BaseModel):
    """Request schema for starting a process (착공 등록)."""
    wip_id: str = Field(..., description="WIP ID (e.g., WIP-KR01PSA2511-001)")
    lot_number: Optional[str] = Field(None, description="LOT number (optional, auto-resolved from wip_id)")
    serial_number: Optional[str] = Field(None, description="Serial number (optional for LOT-level)")
    process_id: str = Field(..., description="Process ID (e.g., PROC-001 or 1)")
    header_id: Optional[int] = Field(None, description="Process header ID for station/batch tracking")
    worker_id: str = Field(..., description="Worker ID (e.g., W001)")
    equipment_id: Optional[str] = Field(None, description="Equipment ID (e.g., EQ-001)")
    # Additional fields from PySide app
    line_id: Optional[str] = Field(None, description="Production line ID")
    process_name: Optional[str] = Field(None, description="Process name")
    start_time: Optional[str] = Field(None, description="Start time ISO format")


class ProcessStartResponse(BaseModel):
    """Response schema for process start."""
    success: bool
    message: str
    process_data_id: int
    started_at: datetime
    wip_id: Optional[int] = None
    wip_id_str: Optional[str] = None


class ProcessCompleteRequest(BaseModel):
    """Request schema for completing a process (완공 등록)."""
    wip_id: str = Field(..., description="WIP ID (e.g., WIP-KR01PSA2511-001)")
    lot_number: Optional[str] = Field(None, description="LOT number (optional, auto-resolved from wip_id)")
    serial_number: Optional[str] = Field(None, description="Serial number")
    process_id: str = Field(..., description="Process ID, code, or name")
    header_id: Optional[int] = Field(None, description="Process header ID for station/batch tracking")
    worker_id: str = Field(..., description="Worker ID (e.g., W001)")
    result: str = Field(..., description="Result: PASS, FAIL, or REWORK")
    measurements: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Measurement data"
    )
    defect_data: Optional[Dict[str, Any]] = Field(
        None, description="Defect information if result=FAIL"
    )


class ProcessCompleteResponse(BaseModel):
    """Response schema for process complete."""
    success: bool
    message: str
    process_data_id: int
    completed_at: datetime
    duration_seconds: int
    result: Optional[str] = None
    label_printed: Optional[bool] = False
    label_type: Optional[str] = None


class ProcessHistoryItem(BaseModel):
    """Schema for a single process history item."""
    process_number: int
    process_name: str
    result: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]
    operator_name: Optional[str]
    measurements: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class ProcessHistoryResponse(BaseModel):
    """Response schema for process history."""
    serial_number: str
    lot_number: str
    total_processes: int
    completed_processes: int
    history: List[ProcessHistoryItem]
