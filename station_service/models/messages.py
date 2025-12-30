"""
WebSocket and IPC message model definitions.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# WebSocket Client Messages
# ============================================================


class SubscribeMessage(BaseModel):
    """Client message to subscribe to batch updates."""

    type: Literal["subscribe"] = "subscribe"
    batch_ids: List[str]


class UnsubscribeMessage(BaseModel):
    """Client message to unsubscribe from batch updates."""

    type: Literal["unsubscribe"] = "unsubscribe"
    batch_ids: List[str]


# ============================================================
# WebSocket Server Messages
# ============================================================


class BatchStatusMessage(BaseModel):
    """Server message for batch status updates."""

    type: Literal["batch_status"] = "batch_status"
    batch_id: str
    data: Dict[str, Any]


class StepStartMessage(BaseModel):
    """Server message when a step starts."""

    type: Literal["step_start"] = "step_start"
    batch_id: str
    data: Dict[str, Any]  # step, index, total


class StepCompleteMessage(BaseModel):
    """Server message when a step completes."""

    type: Literal["step_complete"] = "step_complete"
    batch_id: str
    data: Dict[str, Any]  # step, index, duration, pass, result


class SequenceCompleteMessage(BaseModel):
    """Server message when a sequence completes."""

    type: Literal["sequence_complete"] = "sequence_complete"
    batch_id: str
    data: Dict[str, Any]  # execution_id, overall_pass, duration, steps


class LogMessage(BaseModel):
    """Server message for log entries."""

    type: Literal["log"] = "log"
    batch_id: str
    data: Dict[str, Any]  # level, message, timestamp


class ErrorMessage(BaseModel):
    """Server message for errors."""

    type: Literal["error"] = "error"
    batch_id: str
    data: Dict[str, Any]  # code, message, step, timestamp


# ============================================================
# IPC Commands (Master → Worker)
# ============================================================


class StartSequenceCommand(BaseModel):
    """Command to start sequence execution."""

    type: Literal["START_SEQUENCE"] = "START_SEQUENCE"
    parameters: Dict[str, Any] = {}


class StopSequenceCommand(BaseModel):
    """Command to stop sequence execution."""

    type: Literal["STOP_SEQUENCE"] = "STOP_SEQUENCE"


class GetStatusCommand(BaseModel):
    """Command to get current status."""

    type: Literal["GET_STATUS"] = "GET_STATUS"


class ManualControlCommand(BaseModel):
    """Command for manual hardware control."""

    type: Literal["MANUAL_CONTROL"] = "MANUAL_CONTROL"
    hardware: str
    command: str
    params: Dict[str, Any] = {}


class ShutdownCommand(BaseModel):
    """Command to shutdown the worker process."""

    type: Literal["SHUTDOWN"] = "SHUTDOWN"


# ============================================================
# IPC Response (Worker → Master)
# ============================================================


class CommandResponse(BaseModel):
    """Response to IPC commands."""

    status: str  # "ok", "error"
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# ============================================================
# IPC Events (Worker → Master via PUB/SUB)
# ============================================================


class StepStartEvent(BaseModel):
    """Event when a step starts."""

    model_config = ConfigDict(populate_by_name=True)

    type: Literal["STEP_START"] = "STEP_START"
    batch_id: str
    step: str
    index: int
    timestamp: datetime


class StepCompleteEvent(BaseModel):
    """Event when a step completes."""

    model_config = ConfigDict(populate_by_name=True)

    type: Literal["STEP_COMPLETE"] = "STEP_COMPLETE"
    batch_id: str
    step: str
    index: int
    duration: float
    pass_: bool = Field(alias="pass")
    result: Dict[str, Any] = {}
    timestamp: datetime


class SequenceCompleteEvent(BaseModel):
    """Event when a sequence completes."""

    type: Literal["SEQUENCE_COMPLETE"] = "SEQUENCE_COMPLETE"
    batch_id: str
    execution_id: str
    overall_pass: bool
    duration: int
    result: Dict[str, Any] = {}
    timestamp: datetime


class LogEvent(BaseModel):
    """Log event from worker."""

    type: Literal["LOG"] = "LOG"
    batch_id: str
    level: str
    message: str
    timestamp: datetime


class ErrorEvent(BaseModel):
    """Error event from worker."""

    type: Literal["ERROR"] = "ERROR"
    batch_id: str
    code: str
    message: str
    step: Optional[str] = None
    timestamp: datetime
