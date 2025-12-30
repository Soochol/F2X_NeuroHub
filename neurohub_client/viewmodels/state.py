"""
State Management for Production Tracker App.

Provides explicit state classes for:
- Clear state definition and documentation
- Type-safe state access
- State change notifications
- State persistence (optional)

Usage:
    from viewmodels.state import WorkState, AppState

    state = WorkState()
    state.set_current_wip("WIP-KR01PSA2511-001", "홍길동")

    if state.has_active_work:
        print(f"Working on: {state.current_wip_id}")
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from PySide6.QtCore import QObject, Signal


class ConnectionStatus(Enum):
    """Connection status enumeration."""
    UNKNOWN = "unknown"
    CONNECTING = "connecting"
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"


class WorkStatus(Enum):
    """Work operation status enumeration."""
    IDLE = "idle"
    STARTING = "starting"
    IN_PROGRESS = "in_progress"
    COMPLETING = "completing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class MeasurementData:
    """
    Equipment measurement data from TCP server.

    Stores measurement results received from equipment
    for work completion.
    """
    result: str = "PASS"
    measurements: List[Dict[str, Any]] = field(default_factory=list)
    defects: List[Dict[str, Any]] = field(default_factory=list)
    received_at: Optional[datetime] = None

    def has_data(self) -> bool:
        """Check if measurement data is available."""
        return len(self.measurements) > 0 or self.result != "PASS"

    def to_api_format(self) -> Dict[str, Any]:
        """Convert to format suitable for API transmission."""
        return {
            "items": [
                {
                    "code": m.get("code", ""),
                    "name": m.get("name", ""),
                    "value": m.get("value"),
                    "unit": m.get("unit"),
                    "spec": m.get("spec"),
                    "result": m.get("result", "PASS"),
                }
                for m in self.measurements
            ]
        }


@dataclass
class WorkState:
    """
    State for current work operation.

    Tracks the lifecycle of a single work operation from
    start to completion.
    """
    # Core identifiers
    current_wip_id: Optional[str] = None
    current_worker: Optional[str] = None

    # Timestamps
    start_time: Optional[datetime] = None
    complete_time: Optional[datetime] = None

    # Status
    status: WorkStatus = WorkStatus.IDLE

    # Measurement data (from equipment via TCP)
    pending_measurement: Optional[MeasurementData] = None

    # Error tracking
    last_error: Optional[str] = None

    @property
    def has_active_work(self) -> bool:
        """Check if there's active work in progress."""
        return (
            self.current_wip_id is not None and
            self.status in (WorkStatus.STARTING, WorkStatus.IN_PROGRESS)
        )

    @property
    def is_idle(self) -> bool:
        """Check if ready for new work."""
        return self.status == WorkStatus.IDLE

    @property
    def elapsed_seconds(self) -> Optional[int]:
        """Get elapsed time since work started in seconds."""
        if self.start_time is None:
            return None
        end = self.complete_time or datetime.now()
        return int((end - self.start_time).total_seconds())

    @property
    def elapsed_formatted(self) -> str:
        """Get elapsed time as HH:MM:SS string."""
        seconds = self.elapsed_seconds
        if seconds is None:
            return "00:00:00"
        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def start(self, wip_id: str, worker: str) -> None:
        """
        Record work start.

        Args:
            wip_id: WIP ID being worked on
            worker: Worker identifier
        """
        self.current_wip_id = wip_id
        self.current_worker = worker
        self.start_time = datetime.now()
        self.complete_time = None
        self.status = WorkStatus.IN_PROGRESS
        self.pending_measurement = None
        self.last_error = None

    def complete(self, result: str = "PASS") -> None:
        """
        Record work completion.

        Args:
            result: Work result (PASS/FAIL)
        """
        self.complete_time = datetime.now()
        self.status = WorkStatus.COMPLETED

    def fail(self, error: str) -> None:
        """
        Record work failure.

        Args:
            error: Error message
        """
        self.status = WorkStatus.FAILED
        self.last_error = error

    def reset(self) -> None:
        """Reset to idle state."""
        self.current_wip_id = None
        self.current_worker = None
        self.start_time = None
        self.complete_time = None
        self.status = WorkStatus.IDLE
        self.pending_measurement = None
        self.last_error = None

    def set_measurement(self, measurement: MeasurementData) -> None:
        """
        Store pending measurement data.

        Args:
            measurement: Measurement data from equipment
        """
        measurement.received_at = datetime.now()
        self.pending_measurement = measurement

    def clear_measurement(self) -> None:
        """Clear pending measurement data."""
        self.pending_measurement = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging or persistence."""
        return {
            "current_wip_id": self.current_wip_id,
            "current_worker": self.current_worker,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "complete_time": self.complete_time.isoformat() if self.complete_time else None,
            "status": self.status.value,
            "has_measurement": self.pending_measurement is not None,
            "last_error": self.last_error,
        }


@dataclass
class ConnectionState:
    """
    State for external connections.

    Tracks backend API and equipment connection status.
    """
    backend_status: ConnectionStatus = ConnectionStatus.UNKNOWN
    backend_last_error: Optional[str] = None
    backend_last_success: Optional[datetime] = None

    equipment_status: ConnectionStatus = ConnectionStatus.UNKNOWN
    equipment_address: Optional[str] = None
    equipment_last_seen: Optional[datetime] = None

    @property
    def is_backend_online(self) -> bool:
        """Check if backend is online."""
        return self.backend_status == ConnectionStatus.ONLINE

    @property
    def is_equipment_connected(self) -> bool:
        """Check if equipment is connected."""
        return self.equipment_status == ConnectionStatus.ONLINE

    def set_backend_online(self) -> None:
        """Mark backend as online."""
        self.backend_status = ConnectionStatus.ONLINE
        self.backend_last_success = datetime.now()
        self.backend_last_error = None

    def set_backend_offline(self, error: Optional[str] = None) -> None:
        """Mark backend as offline."""
        self.backend_status = ConnectionStatus.OFFLINE
        self.backend_last_error = error

    def set_equipment_connected(self, address: str) -> None:
        """Mark equipment as connected."""
        self.equipment_status = ConnectionStatus.ONLINE
        self.equipment_address = address
        self.equipment_last_seen = datetime.now()

    def set_equipment_disconnected(self) -> None:
        """Mark equipment as disconnected."""
        self.equipment_status = ConnectionStatus.OFFLINE
        self.equipment_address = None


class AppState(QObject):
    """
    Central application state manager.

    Combines all state objects and emits signals on changes.
    This provides a single source of truth for application state.
    """

    # State change signals
    work_state_changed = Signal(object)  # WorkState
    connection_state_changed = Signal(object)  # ConnectionState

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._work = WorkState()
        self._connection = ConnectionState()

    @property
    def work(self) -> WorkState:
        """Get current work state."""
        return self._work

    @property
    def connection(self) -> ConnectionState:
        """Get current connection state."""
        return self._connection

    # Work state methods
    def start_work(self, wip_id: str, worker: str) -> None:
        """Start work and emit signal."""
        self._work.start(wip_id, worker)
        self.work_state_changed.emit(self._work)

    def complete_work(self, result: str = "PASS") -> None:
        """Complete work and emit signal."""
        self._work.complete(result)
        self.work_state_changed.emit(self._work)

    def fail_work(self, error: str) -> None:
        """Fail work and emit signal."""
        self._work.fail(error)
        self.work_state_changed.emit(self._work)

    def reset_work(self) -> None:
        """Reset work state and emit signal."""
        self._work.reset()
        self.work_state_changed.emit(self._work)

    def set_measurement(self, result: str, measurements: List[Dict], defects: List[Dict] = None) -> None:
        """Set measurement data and emit signal."""
        measurement = MeasurementData(
            result=result,
            measurements=measurements,
            defects=defects or []
        )
        self._work.set_measurement(measurement)
        self.work_state_changed.emit(self._work)

    def clear_measurement(self) -> None:
        """Clear measurement data and emit signal."""
        self._work.clear_measurement()
        self.work_state_changed.emit(self._work)

    # Connection state methods
    def set_backend_online(self) -> None:
        """Set backend online and emit signal."""
        self._connection.set_backend_online()
        self.connection_state_changed.emit(self._connection)

    def set_backend_offline(self, error: Optional[str] = None) -> None:
        """Set backend offline and emit signal."""
        self._connection.set_backend_offline(error)
        self.connection_state_changed.emit(self._connection)

    def set_equipment_connected(self, address: str) -> None:
        """Set equipment connected and emit signal."""
        self._connection.set_equipment_connected(address)
        self.connection_state_changed.emit(self._connection)

    def set_equipment_disconnected(self) -> None:
        """Set equipment disconnected and emit signal."""
        self._connection.set_equipment_disconnected()
        self.connection_state_changed.emit(self._connection)

    def to_dict(self) -> Dict[str, Any]:
        """Convert all state to dictionary."""
        return {
            "work": self._work.to_dict(),
            "connection": {
                "backend_status": self._connection.backend_status.value,
                "equipment_status": self._connection.equipment_status.value,
            }
        }
