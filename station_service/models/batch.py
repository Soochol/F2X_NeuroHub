"""
Batch model definitions.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from station_service.models.execution import ExecutionStatus
    from station_service.models.hardware import HardwareStatus


class BatchStatus(str, Enum):
    """Batch execution status."""

    IDLE = "idle"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    COMPLETED = "completed"
    ERROR = "error"


class Batch(BaseModel):
    """Represents a batch configuration and runtime state."""

    id: str  # "batch_1"
    name: str  # "Batch 1"
    status: BatchStatus
    sequence_name: Optional[str] = None  # "PCB_Voltage_Test"
    sequence_version: Optional[str] = None
    sequence_package: str  # "sequences/pcb_voltage_test"

    # Execution state
    current_step: Optional[str] = None
    step_index: int = 0
    total_steps: int = 0
    progress: float = 0.0  # 0.0 ~ 1.0

    # Time
    started_at: Optional[datetime] = None
    elapsed: int = 0  # seconds

    # Configuration
    hardware_config: Dict[str, Dict[str, Any]] = {}
    auto_start: bool = False

    # Process information
    pid: Optional[int] = None


class BatchDetail(Batch):
    """Batch detailed information (for API responses)."""

    parameters: Dict[str, Any] = {}
    hardware_status: Dict[str, Any] = {}  # Dict[str, HardwareStatus] at runtime
    execution: Optional[Any] = None  # ExecutionStatus at runtime
