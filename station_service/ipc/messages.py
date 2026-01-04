"""
IPC message definitions for Station Service.

Defines the message types and serialization for ZeroMQ communication
between the master process and batch worker processes.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class CommandType(str, Enum):
    """IPC command types from master to worker."""

    START_SEQUENCE = "START_SEQUENCE"
    STOP_SEQUENCE = "STOP_SEQUENCE"
    GET_STATUS = "GET_STATUS"
    MANUAL_CONTROL = "MANUAL_CONTROL"
    SHUTDOWN = "SHUTDOWN"
    PING = "PING"


class EventType(str, Enum):
    """IPC event types from worker to master."""

    STEP_START = "STEP_START"
    STEP_COMPLETE = "STEP_COMPLETE"
    SEQUENCE_COMPLETE = "SEQUENCE_COMPLETE"
    LOG = "LOG"
    ERROR = "ERROR"
    STATUS_UPDATE = "STATUS_UPDATE"
    PONG = "PONG"
    BARCODE_SCANNED = "BARCODE_SCANNED"
    WIP_PROCESS_COMPLETE = "WIP_PROCESS_COMPLETE"


@dataclass
class IPCCommand:
    """
    Command message from master to worker.

    Commands use the REQ/REP pattern for synchronous request/response.
    """

    type: CommandType
    batch_id: str
    params: Dict[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: datetime.now().isoformat())

    def serialize(self) -> str:
        """Serialize command to JSON string."""
        return json.dumps({
            "type": self.type.value,
            "batch_id": self.batch_id,
            "params": self.params,
            "request_id": self.request_id,
        })

    @classmethod
    def deserialize(cls, data: str) -> "IPCCommand":
        """Deserialize command from JSON string."""
        obj = json.loads(data)
        return cls(
            type=CommandType(obj["type"]),
            batch_id=obj["batch_id"],
            params=obj.get("params", {}),
            request_id=obj.get("request_id", ""),
        )


@dataclass
class IPCResponse:
    """
    Response message from worker to master.

    Sent in response to IPCCommand via REQ/REP pattern.
    """

    status: str  # "ok", "error"
    request_id: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def serialize(self) -> str:
        """Serialize response to JSON string."""
        return json.dumps({
            "status": self.status,
            "request_id": self.request_id,
            "data": self.data,
            "error": self.error,
        })

    @classmethod
    def deserialize(cls, data: str) -> "IPCResponse":
        """Deserialize response from JSON string."""
        obj = json.loads(data)
        return cls(
            status=obj["status"],
            request_id=obj["request_id"],
            data=obj.get("data"),
            error=obj.get("error"),
        )

    @classmethod
    def ok(cls, request_id: str, data: Optional[Dict[str, Any]] = None) -> "IPCResponse":
        """Create success response."""
        return cls(status="ok", request_id=request_id, data=data, error=None)

    @classmethod
    def error(cls, request_id: str, error_msg: str) -> "IPCResponse":
        """Create error response."""
        return cls(status="error", request_id=request_id, error=error_msg)


@dataclass
class IPCEvent:
    """
    Event message from worker to master.

    Events use the PUB/SUB pattern for asynchronous broadcast.
    """

    type: EventType
    batch_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def serialize(self) -> str:
        """Serialize event to JSON string."""
        return json.dumps({
            "type": self.type.value,
            "batch_id": self.batch_id,
            "data": self.data,
            "timestamp": self.timestamp,
        })

    @classmethod
    def deserialize(cls, data: str) -> "IPCEvent":
        """Deserialize event from JSON string."""
        obj = json.loads(data)
        return cls(
            type=EventType(obj["type"]),
            batch_id=obj["batch_id"],
            data=obj.get("data", {}),
            timestamp=obj.get("timestamp", ""),
        )

    @classmethod
    def step_start(
        cls,
        batch_id: str,
        step_name: str,
        step_index: int,
        total_steps: int,
        execution_id: str = "",
        step_names: Optional[list] = None,
    ) -> "IPCEvent":
        """Create step start event.

        Args:
            step_names: List of all step names from manifest (sent on first step only)
        """
        data: Dict[str, Any] = {
            "step": step_name,
            "index": step_index,
            "total": total_steps,
            "execution_id": execution_id,
        }
        # Include step_names on first step for UI to display skipped steps
        if step_names is not None:
            data["step_names"] = step_names
        return cls(
            type=EventType.STEP_START,
            batch_id=batch_id,
            data=data,
        )

    @classmethod
    def step_complete(
        cls,
        batch_id: str,
        step_name: str,
        step_index: int,
        duration: float,
        passed: bool,
        result: Optional[Dict[str, Any]] = None,
        execution_id: str = "",
    ) -> "IPCEvent":
        """Create step complete event."""
        return cls(
            type=EventType.STEP_COMPLETE,
            batch_id=batch_id,
            data={
                "step": step_name,
                "index": step_index,
                "duration": duration,
                "pass": passed,
                "result": result or {},
                "execution_id": execution_id,
            },
        )

    @classmethod
    def sequence_complete(
        cls,
        batch_id: str,
        execution_id: str,
        overall_pass: bool,
        duration: float,
        result: Optional[Dict[str, Any]] = None,
    ) -> "IPCEvent":
        """Create sequence complete event."""
        return cls(
            type=EventType.SEQUENCE_COMPLETE,
            batch_id=batch_id,
            data={
                "execution_id": execution_id,
                "overall_pass": overall_pass,
                "duration": duration,
                "result": result or {},
            },
        )

    @classmethod
    def log(cls, batch_id: str, level: str, message: str) -> "IPCEvent":
        """Create log event."""
        return cls(
            type=EventType.LOG,
            batch_id=batch_id,
            data={
                "level": level,
                "message": message,
            },
        )

    @classmethod
    def error(cls, batch_id: str, code: str, message: str, step: Optional[str] = None) -> "IPCEvent":
        """Create error event."""
        return cls(
            type=EventType.ERROR,
            batch_id=batch_id,
            data={
                "code": code,
                "message": message,
                "step": step,
            },
        )

    @classmethod
    def status_update(cls, batch_id: str, status: Dict[str, Any]) -> "IPCEvent":
        """Create status update event."""
        return cls(
            type=EventType.STATUS_UPDATE,
            batch_id=batch_id,
            data=status,
        )

    @classmethod
    def barcode_scanned(cls, batch_id: str, barcode: str, scanner_id: str = "") -> "IPCEvent":
        """Create barcode scanned event."""
        return cls(
            type=EventType.BARCODE_SCANNED,
            batch_id=batch_id,
            data={
                "barcode": barcode,
                "scanner_id": scanner_id,
            },
        )

    @classmethod
    def wip_process_complete(
        cls,
        batch_id: str,
        wip_id: str,
        process_id: int,
        result: str,
        wip_status: Optional[str] = None,
        can_convert: bool = False,
    ) -> "IPCEvent":
        """Create WIP process complete event."""
        return cls(
            type=EventType.WIP_PROCESS_COMPLETE,
            batch_id=batch_id,
            data={
                "wip_id": wip_id,
                "process_id": process_id,
                "result": result,
                "wip_status": wip_status,
                "can_convert": can_convert,
            },
        )
