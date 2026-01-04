"""
State management for BatchWorker.

Provides structured state classes for worker and execution lifecycle,
replacing scattered instance variables with organized, type-safe state objects.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from station_service.models.batch import BatchStatus


class WorkerPhase(Enum):
    """Worker lifecycle phases."""

    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class ExecutionState:
    """
    State for a single sequence execution.

    Tracks all state related to an active execution including
    step progress, results, and WIP context.
    """

    execution_id: str
    started_at: datetime
    sequence_name: Optional[str] = None
    sequence_version: Optional[str] = None

    # Step tracking
    current_step: Optional[str] = None
    step_index: int = 0
    total_steps: int = 0
    progress: float = 0.0
    step_names: List[str] = field(default_factory=list)  # All step names from manifest

    # Results tracking
    step_results: List[Dict[str, Any]] = field(default_factory=list)

    # WIP context (Backend integration)
    wip_id: Optional[str] = None
    wip_int_id: Optional[int] = None
    process_id: Optional[int] = None
    operator_id: Optional[int] = None
    process_start_time: Optional[datetime] = None

    def update_step(
        self,
        step_name: str,
        index: int,
        total: int,
    ) -> None:
        """Update step progress."""
        self.current_step = step_name
        self.step_index = index
        self.total_steps = total
        if total > 0:
            self.progress = index / total

    def add_step_result(
        self,
        name: str,
        status: str = "running",
        duration: Optional[float] = None,
        result: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a new step result entry."""
        self.step_results.append({
            "name": name,
            "status": status,
            "duration": duration,
            "result": result,
        })

    def update_step_result(
        self,
        name: str,
        status: str,
        duration: float,
        result: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Update an existing step result."""
        for step in self.step_results:
            if step.get("name") == name:
                step.update({
                    "status": status,
                    "duration": duration,
                    "result": result,
                })
                break

    def complete_step(self, index: int) -> None:
        """Mark step as complete and update progress."""
        self.step_index = index + 1
        if self.total_steps > 0:
            self.progress = self.step_index / self.total_steps

    @property
    def has_wip_context(self) -> bool:
        """Check if WIP context is available for Backend integration."""
        return (
            self.wip_id is not None
            and self.process_id is not None
            and self.operator_id is not None
        )

    def to_status_dict(self) -> Dict[str, Any]:
        """Convert to status dictionary for IPC response."""
        return {
            "execution_id": self.execution_id,
            "current_step": self.current_step,
            "step_index": self.step_index,
            "total_steps": self.total_steps,
            "progress": self.progress,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "steps": self.step_results,
        }


@dataclass
class LastRunState:
    """
    State preserved from last completed execution.

    Used to display results in UI after execution completes.
    """

    passed: Optional[bool] = None
    progress: float = 0.0
    step_results: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_execution(cls, execution: ExecutionState) -> "LastRunState":
        """Create from completed execution state."""
        # Determine pass/fail from step results
        passed = None
        if execution.step_results:
            passed = all(
                step.get("status") == "completed"
                for step in execution.step_results
            )

        return cls(
            passed=passed,
            progress=1.0,  # 완료된 실행은 항상 100%
            step_results=execution.step_results.copy(),
        )

    def to_status_dict(self) -> Dict[str, Any]:
        """Convert to status dictionary for IPC response."""
        return {
            "last_run_passed": self.passed,
            "progress": self.progress,
            "step_index": len(self.step_results),
            "total_steps": len(self.step_results),
            "steps": self.step_results,
        }


@dataclass
class BackendState:
    """
    State for Backend integration.

    Tracks connection status, process headers, and sync state.
    """

    is_online: bool = False
    station_id: Optional[str] = None
    current_header_id: Optional[int] = None

    def reset_header(self) -> None:
        """Reset process header state."""
        self.current_header_id = None


@dataclass
class WorkerState:
    """
    Complete state for a BatchWorker.

    Aggregates all state components for easy management and serialization.
    """

    batch_id: str
    phase: WorkerPhase = WorkerPhase.INITIALIZING
    status: BatchStatus = BatchStatus.IDLE
    is_running: bool = True

    # Sequence info
    sequence_name: Optional[str] = None
    sequence_version: Optional[str] = None
    manifest: Optional[Dict[str, Any]] = None

    # Current execution (None when idle)
    execution: Optional[ExecutionState] = None

    # Last run (preserved after completion)
    last_run: Optional[LastRunState] = None

    # Backend state
    backend: BackendState = field(default_factory=BackendState)

    def start_execution(
        self,
        execution_id: str,
        wip_id: Optional[str] = None,
        wip_int_id: Optional[int] = None,
        process_id: Optional[int] = None,
        operator_id: Optional[int] = None,
        step_names: Optional[List[str]] = None,
    ) -> ExecutionState:
        """Start a new execution.

        Args:
            step_names: All step names from manifest (for UI to display skipped steps)
        """
        from datetime import timezone

        self.execution = ExecutionState(
            execution_id=execution_id,
            started_at=datetime.now(timezone.utc),
            sequence_name=self.sequence_name,
            sequence_version=self.sequence_version,
            wip_id=wip_id,
            wip_int_id=wip_int_id,
            process_id=process_id,
            operator_id=operator_id,
            process_start_time=datetime.now(timezone.utc) if wip_id else None,
            step_names=step_names or [],
        )
        self.status = BatchStatus.RUNNING
        self.phase = WorkerPhase.RUNNING
        return self.execution

    def complete_execution(self) -> Optional[LastRunState]:
        """Complete current execution and save to last_run."""
        if self.execution:
            self.last_run = LastRunState.from_execution(self.execution)
            self.execution = None
        self.status = BatchStatus.IDLE
        self.phase = WorkerPhase.READY
        return self.last_run

    def cancel_execution(self) -> None:
        """Cancel current execution without saving to last_run."""
        self.execution = None
        self.status = BatchStatus.IDLE
        self.phase = WorkerPhase.READY

    @property
    def is_executing(self) -> bool:
        """Check if an execution is in progress."""
        return self.execution is not None and self.status == BatchStatus.RUNNING

    def to_status_dict(self) -> Dict[str, Any]:
        """Convert to complete status dictionary."""
        result: Dict[str, Any] = {
            "batch_id": self.batch_id,
            "status": self.status.value,
            "sequence_name": self.sequence_name,
            "sequence_version": self.sequence_version,
        }

        if self.is_executing and self.execution:
            result.update(self.execution.to_status_dict())
        elif self.last_run:
            result.update(self.last_run.to_status_dict())
        else:
            result.update({
                "execution_id": None,
                "current_step": None,
                "step_index": 0,
                "total_steps": 0,
                "progress": 0.0,
                "steps": [],
                "last_run_passed": None,
            })

        return result
