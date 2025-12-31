"""
Batch-related API schemas for Station Service.

This module defines request and response schemas for batch operations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ============================================================================
# Nested Models for Batch Detail
# ============================================================================


class BatchSequenceInfo(BaseModel):
    """Sequence information associated with a batch.

    Attributes:
        name: Sequence package name
        version: Sequence version
        package_path: Path to the sequence package
    """
    name: str = Field(..., description="Sequence package name")
    version: str = Field(..., description="Sequence version")
    package_path: str = Field(..., description="Path to the sequence package")


class HardwareStatus(BaseModel):
    """Hardware device status information.

    Attributes:
        status: Connection status (connected, disconnected, error)
        driver: Driver class name
        port: Serial port or IP address
    """
    status: str = Field(..., description="Connection status")
    driver: str = Field(..., description="Driver class name")
    port: Optional[str] = Field(None, description="Serial port path")
    ip: Optional[str] = Field(None, description="IP address for network devices")


class StepResult(BaseModel):
    """Execution result for a single step.

    Attributes:
        name: Step name
        status: Execution status (pending, running, completed, failed, skipped)
        duration: Execution duration in seconds (null if not completed)
        result: Step result data (null if not completed)
    """
    name: str = Field(..., description="Step name")
    status: str = Field(..., description="Execution status")
    duration: Optional[float] = Field(None, description="Execution duration in seconds")
    result: Optional[Dict[str, Any]] = Field(None, description="Step result data")


class BatchExecution(BaseModel):
    """Current execution state of a batch.

    Attributes:
        status: Execution status (idle, running, paused, completed, failed)
        current_step: Name of the currently executing step
        step_index: Index of the current step (0-based)
        total_steps: Total number of steps
        progress: Execution progress (0.0 to 1.0)
        started_at: Execution start time
        elapsed: Elapsed time in seconds
        steps: List of step execution results
    """
    status: str = Field(..., description="Execution status")
    current_step: Optional[str] = Field(None, description="Currently executing step name")
    step_index: int = Field(..., description="Current step index (0-based)", ge=0)
    total_steps: int = Field(..., description="Total number of steps", ge=0)
    progress: float = Field(..., description="Execution progress (0.0 to 1.0)", ge=0.0, le=1.0)
    started_at: Optional[datetime] = Field(None, description="Execution start time")
    elapsed: float = Field(default=0.0, description="Elapsed time in seconds", ge=0.0)
    steps: List[StepResult] = Field(default_factory=list, description="Step execution results")


# ============================================================================
# Batch Response Models
# ============================================================================


class BatchSummary(BaseModel):
    """Summary information for a batch in list view.

    Attributes:
        id: Unique batch identifier
        name: Display name of the batch
        status: Current status (idle, running, completed, failed)
        sequence_name: Name of the assigned sequence
        sequence_version: Version of the assigned sequence
        current_step: Name of the currently executing step
        step_index: Index of the current step
        total_steps: Total number of steps
        progress: Execution progress (0.0 to 1.0)
        started_at: Execution start time
        elapsed: Elapsed time in seconds
    """
    id: str = Field(..., description="Unique batch identifier")
    name: str = Field(..., description="Display name of the batch")
    status: str = Field(..., description="Current status")
    sequence_name: str = Field(..., description="Assigned sequence name")
    sequence_version: str = Field(..., description="Assigned sequence version")
    current_step: Optional[str] = Field(None, description="Currently executing step")
    step_index: int = Field(default=0, description="Current step index", ge=0)
    total_steps: int = Field(default=0, description="Total number of steps", ge=0)
    progress: float = Field(default=0.0, description="Execution progress", ge=0.0, le=1.0)
    started_at: Optional[datetime] = Field(None, description="Execution start time")
    elapsed: float = Field(default=0.0, description="Elapsed time in seconds", ge=0.0)


class BatchDetail(BaseModel):
    """Detailed information for a single batch.

    Attributes:
        id: Unique batch identifier
        name: Display name of the batch
        status: Current status
        sequence: Sequence information
        parameters: Runtime parameters
        hardware: Hardware device statuses
        execution: Current execution state
    """
    id: str = Field(..., description="Unique batch identifier")
    name: str = Field(..., description="Display name of the batch")
    status: str = Field(..., description="Current status")
    sequence: BatchSequenceInfo = Field(..., description="Sequence information")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Runtime parameters")
    hardware: Dict[str, HardwareStatus] = Field(default_factory=dict, description="Hardware statuses")
    execution: BatchExecution = Field(..., description="Current execution state")


# ============================================================================
# Batch Action Request/Response Models
# ============================================================================


class BatchStartResponse(BaseModel):
    """Response for batch process start action.

    Attributes:
        batch_id: ID of the started batch
        status: New status ('started')
        pid: Process ID of the batch process
    """
    batch_id: str = Field(..., description="Batch identifier")
    status: str = Field(..., description="New status")
    pid: int = Field(..., description="Process ID")


class BatchStopResponse(BaseModel):
    """Response for batch process stop action.

    Attributes:
        batch_id: ID of the stopped batch
        status: New status ('stopped')
    """
    batch_id: str = Field(..., description="Batch identifier")
    status: str = Field(..., description="New status")


class SequenceStartRequest(BaseModel):
    """Request body for starting sequence execution.

    Attributes:
        parameters: Runtime parameters for the sequence
    """
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Runtime parameters for the sequence execution"
    )


class SequenceStartResponse(BaseModel):
    """Response for sequence start action.

    Attributes:
        batch_id: ID of the batch
        execution_id: Unique identifier for this execution
        status: New status ('started')
    """
    batch_id: str = Field(..., description="Batch identifier")
    execution_id: str = Field(..., description="Execution identifier")
    status: str = Field(..., description="New status")


class SequenceStopResponse(BaseModel):
    """Response for sequence stop action.

    Attributes:
        batch_id: ID of the batch
        status: New status ('stopped')
    """
    batch_id: str = Field(..., description="Batch identifier")
    status: str = Field(..., description="New status")


class ManualControlRequest(BaseModel):
    """Request body for manual hardware control.

    Attributes:
        hardware: Hardware device ID to control
        command: Command to execute
        params: Command parameters
    """
    hardware: str = Field(..., description="Hardware device ID")
    command: str = Field(..., description="Command to execute")
    params: Dict[str, Any] = Field(default_factory=dict, description="Command parameters")


class ManualControlResponse(BaseModel):
    """Response for manual control command.

    Attributes:
        hardware: Hardware device ID
        command: Executed command
        result: Command execution result
    """
    hardware: str = Field(..., description="Hardware device ID")
    command: str = Field(..., description="Executed command")
    result: Dict[str, Any] = Field(..., description="Command result")


class BatchStatistics(BaseModel):
    """Statistics for a batch's execution history.

    Attributes:
        total: Total number of executions
        pass_count: Number of passed executions
        fail: Number of failed executions
        pass_rate: Pass rate (0.0 to 1.0)
    """
    total: int = Field(default=0, description="Total number of executions", ge=0)
    pass_count: int = Field(default=0, alias="pass", description="Number of passed executions", ge=0)
    fail: int = Field(default=0, description="Number of failed executions", ge=0)
    pass_rate: float = Field(default=0.0, alias="passRate", description="Pass rate (0.0 to 1.0)", ge=0.0, le=1.0)

    model_config = {"populate_by_name": True}
