from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ProcessStartRequest(BaseModel):
    """Request schema for starting a process (착공 등록)."""
    lot_number: str = Field(..., description="LOT number (e.g., WF-KR-251110D-001)")
    serial_number: Optional[str] = Field(None, description="Serial number (optional for LOT-level)")
    wip_id: Optional[str] = Field(None, description="WIP ID (e.g., WIP-KR01PSA2511-001)")
    process_id: str = Field(..., description="Process ID (e.g., PROC-001 or 1)")
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
    lot_number: str = Field(..., description="LOT number")
    serial_number: Optional[str] = Field(None, description="Serial number")
    process_id: int = Field(..., gt=0, description="Process ID")
    result: str = Field(..., description="Result: PASS, FAIL, or REWORK")
    measurement_data: Optional[Dict[str, Any]] = Field(
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
