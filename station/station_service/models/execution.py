"""
Execution result model definitions.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ExecutionStatus(str, Enum):
    """Execution status."""

    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


class StepResult(BaseModel):
    """Result of a single step execution."""

    model_config = ConfigDict(populate_by_name=True)

    name: str
    order: int
    status: str  # "pending", "running", "completed", "failed", "skipped"
    pass_: bool = Field(default=True, alias="pass")  # pass is reserved
    duration: Optional[float] = None  # seconds
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ExecutionResult(BaseModel):
    """Complete result of a sequence execution."""

    id: str  # "exec_20250120_123456"
    batch_id: str
    sequence_name: str
    sequence_version: str
    status: ExecutionStatus
    overall_pass: bool

    started_at: datetime
    completed_at: Optional[datetime] = None
    duration: Optional[int] = None  # seconds

    parameters: Dict[str, Any]
    steps: List[StepResult]

    synced_at: Optional[datetime] = None  # Backend sync time


class ExecutionSummary(BaseModel):
    """Execution result summary for list views."""

    id: str
    batch_id: str
    sequence_name: str
    sequence_version: str
    status: ExecutionStatus
    overall_pass: bool
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration: Optional[int] = None
    synced: bool
