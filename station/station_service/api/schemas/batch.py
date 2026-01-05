"""
Batch-related API schemas for Station Service.

This module defines request and response schemas for batch operations.
All responses use camelCase field names in JSON output via APIBaseModel.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from station_service.api.schemas.base import APIBaseModel


# ============================================================================
# Nested Models for Batch Detail
# ============================================================================


class BatchSequenceInfo(APIBaseModel):
    """Sequence information associated with a batch.

    Attributes:
        name: Sequence package name
        version: Sequence version
        package_path: Path to the sequence package
    """
    name: str = Field(..., description="Sequence package name")
    version: str = Field(..., description="Sequence version")
    package_path: str = Field(..., description="Path to the sequence package")


class HardwareStatus(APIBaseModel):
    """Hardware device status information.

    Attributes:
        name: Hardware device name
        type: Hardware type
        status: Connection status (connected, disconnected, error)
        configured: Whether the hardware is configured
        connected: Whether the hardware is connected
        driver: Driver class name
        port: Serial port or IP address
        details: Additional hardware details
    """
    name: str = Field(default="", description="Hardware device name")
    type: str = Field(default="unknown", description="Hardware type")
    status: str = Field(default="unknown", description="Connection status")
    configured: bool = Field(default=True, description="Whether hardware is configured")
    connected: bool = Field(default=False, description="Whether hardware is connected")
    driver: Optional[str] = Field(None, description="Driver class name")
    port: Optional[str] = Field(None, description="Serial port path")
    ip: Optional[str] = Field(None, description="IP address for network devices")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional hardware details")


class StepResult(APIBaseModel):
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


class BatchExecution(APIBaseModel):
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
        step_names: Ordered list of all step names from manifest (for displaying skipped steps)
    """
    status: str = Field(..., description="Execution status")
    current_step: Optional[str] = Field(None, description="Currently executing step name")
    step_index: int = Field(..., description="Current step index (0-based)", ge=0)
    total_steps: int = Field(..., description="Total number of steps", ge=0)
    progress: float = Field(..., description="Execution progress (0.0 to 1.0)", ge=0.0, le=1.0)
    started_at: Optional[datetime] = Field(None, description="Execution start time")
    elapsed: float = Field(default=0.0, description="Elapsed time in seconds", ge=0.0)
    steps: List[StepResult] = Field(default_factory=list, description="Step execution results")
    step_names: List[str] = Field(default_factory=list, description="Ordered list of all step names from manifest")


# ============================================================================
# Batch Response Models
# ============================================================================


class BatchSummary(APIBaseModel):
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


class BatchDetail(APIBaseModel):
    """Detailed information for a single batch.

    Attributes:
        id: Unique batch identifier
        name: Display name of the batch
        status: Current status
        sequence: Sequence information
        parameters: Runtime parameters
        config: Dynamic batch configuration (processId, headerId, etc.)
        hardware: Hardware device statuses
        execution: Current execution state
        last_run_passed: Result of last completed execution (True=pass, False=fail, None=no execution)
        process_id: [Deprecated] Use config.processId instead
        header_id: [Deprecated] Use config.headerId instead
    """
    id: str = Field(..., description="Unique batch identifier")
    name: str = Field(..., description="Display name of the batch")
    status: str = Field(..., description="Current status")
    sequence: BatchSequenceInfo = Field(..., description="Sequence information")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Runtime parameters")
    config: Dict[str, Any] = Field(default_factory=dict, description="Dynamic batch configuration")
    hardware: Dict[str, HardwareStatus] = Field(default_factory=dict, description="Hardware statuses")
    execution: BatchExecution = Field(..., description="Current execution state")
    last_run_passed: Optional[bool] = Field(None, description="Result of last completed execution (True=pass, False=fail, None=no execution)")
    # Legacy fields for backward compatibility
    process_id: Optional[int] = Field(None, description="[Deprecated] Use config.processId instead")
    header_id: Optional[int] = Field(None, description="[Deprecated] Use config.headerId instead")


# ============================================================================
# Batch Action Request/Response Models
# ============================================================================


class BatchStartResponse(APIBaseModel):
    """Response for batch process start action.

    Attributes:
        batch_id: ID of the started batch
        status: New status ('started')
        pid: Process ID of the batch process
    """
    batch_id: str = Field(..., description="Batch identifier")
    status: str = Field(..., description="New status")
    pid: int = Field(..., description="Process ID")


class BatchStopResponse(APIBaseModel):
    """Response for batch process stop action.

    Attributes:
        batch_id: ID of the stopped batch
        status: New status ('stopped')
    """
    batch_id: str = Field(..., description="Batch identifier")
    status: str = Field(..., description="New status")


class SequenceStartRequest(APIBaseModel):
    """Request body for starting sequence execution.

    Attributes:
        parameters: Runtime parameters for the sequence
        wip_int_id: Pre-validated WIP integer ID (skip lookup if provided)
    """
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Runtime parameters for the sequence execution"
    )
    wip_int_id: Optional[int] = Field(
        None,
        description="Pre-validated WIP integer ID to skip lookup in worker"
    )


class SequenceStartResponse(APIBaseModel):
    """Response for sequence start action.

    Attributes:
        batch_id: ID of the batch
        execution_id: Unique identifier for this execution
        status: New status ('started')
    """
    batch_id: str = Field(..., description="Batch identifier")
    execution_id: str = Field(..., description="Execution identifier")
    status: str = Field(..., description="New status")


class SequenceStopResponse(APIBaseModel):
    """Response for sequence stop action.

    Attributes:
        batch_id: ID of the batch
        status: New status ('stopped')
    """
    batch_id: str = Field(..., description="Batch identifier")
    status: str = Field(..., description="New status")


class ManualControlRequest(APIBaseModel):
    """Request body for manual hardware control.

    Attributes:
        hardware: Hardware device ID to control
        command: Command to execute
        params: Command parameters
    """
    hardware: str = Field(..., description="Hardware device ID")
    command: str = Field(..., description="Command to execute")
    params: Dict[str, Any] = Field(default_factory=dict, description="Command parameters")


class ManualControlResponse(APIBaseModel):
    """Response for manual control command.

    Attributes:
        hardware: Hardware device ID
        command: Executed command
        result: Command execution result
    """
    hardware: str = Field(..., description="Hardware device ID")
    command: str = Field(..., description="Executed command")
    result: Dict[str, Any] = Field(..., description="Command result")


class BatchStatistics(APIBaseModel):
    """Statistics for a batch's execution history.

    Attributes:
        total: Total number of executions
        pass_count: Number of passed executions (JSON: passCount)
        fail: Number of failed executions
        pass_rate: Pass rate (0.0 to 1.0) (JSON: passRate)
        avg_duration: Average execution duration in seconds (JSON: avgDuration)
        last_duration: Last execution duration in seconds (JSON: lastDuration)
    """
    total: int = Field(default=0, description="Total number of executions", ge=0)
    pass_count: int = Field(default=0, description="Number of passed executions", ge=0)
    fail: int = Field(default=0, description="Number of failed executions", ge=0)
    pass_rate: float = Field(default=0.0, description="Pass rate (0.0 to 1.0)", ge=0.0, le=1.0)
    avg_duration: float = Field(default=0.0, description="Average execution duration in seconds", ge=0.0)
    last_duration: float = Field(default=0.0, description="Last execution duration in seconds", ge=0.0)


# ============================================================================
# Batch CRUD Request/Response Models
# ============================================================================


class BatchCreateRequest(APIBaseModel):
    """Request body for creating a new batch.

    Attributes:
        id: Unique batch identifier
        name: Display name of the batch
        sequence_package: Sequence package path to use
        hardware: Hardware configuration (device_id -> config)
        auto_start: Whether to start automatically on station startup
        config: Dynamic batch configuration (processId, headerId, etc.)
        parameters: Batch parameters for sequence execution
        process_id: [Deprecated] Use config.processId instead
        header_id: [Deprecated] Use config.headerId instead
    """
    id: str = Field(..., description="Unique batch identifier", min_length=1)
    name: str = Field(..., description="Display name of the batch", min_length=1)
    sequence_package: str = Field(..., description="Sequence package path", min_length=1)
    hardware: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Hardware configuration"
    )
    auto_start: bool = Field(default=False, description="Auto-start on station startup")
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Dynamic batch configuration (processId, headerId, etc.)"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Batch parameters for sequence execution"
    )
    # Legacy fields for backward compatibility
    process_id: Optional[int] = Field(
        None,
        description="[Deprecated] Use config.processId instead",
        ge=1,
        le=8
    )
    header_id: Optional[int] = Field(
        None,
        description="[Deprecated] Use config.headerId instead"
    )


class BatchCreateResponse(APIBaseModel):
    """Response for batch creation.

    Attributes:
        batch_id: ID of the created batch
        name: Name of the created batch
        status: Creation status ('created')
    """
    batch_id: str = Field(..., description="Batch identifier")
    name: str = Field(..., description="Batch name")
    status: str = Field(..., description="Creation status")


class BatchDeleteResponse(APIBaseModel):
    """Response for batch deletion.

    Attributes:
        batch_id: ID of the deleted batch
        status: Deletion status ('deleted')
    """
    batch_id: str = Field(..., description="Batch identifier")
    status: str = Field(..., description="Deletion status")


class BatchUpdateRequest(APIBaseModel):
    """Request body for updating a batch configuration.

    All fields are optional - only provided fields will be updated.

    Attributes:
        name: New display name for the batch
        sequence_package: New sequence package path
        hardware: Updated hardware configuration
        auto_start: Whether to auto-start on station startup
        config: Dynamic batch configuration (processId, headerId, etc.)
        parameters: Batch parameters for sequence execution
        process_id: [Deprecated] Use config.processId instead
        header_id: [Deprecated] Use config.headerId instead
    """
    name: Optional[str] = Field(None, description="Display name of the batch", min_length=1)
    sequence_package: Optional[str] = Field(None, description="Sequence package path", min_length=1)
    hardware: Optional[Dict[str, Dict[str, Any]]] = Field(
        None,
        description="Hardware configuration (device_id -> config)"
    )
    auto_start: Optional[bool] = Field(None, description="Auto-start on station startup")
    config: Optional[Dict[str, Any]] = Field(
        None,
        description="Dynamic batch configuration (processId, headerId, etc.)"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        None,
        description="Batch parameters for sequence execution"
    )
    # Legacy fields for backward compatibility
    process_id: Optional[int] = Field(
        None,
        description="[Deprecated] Use config.processId instead",
        ge=1,
        le=8
    )
    header_id: Optional[int] = Field(
        None,
        description="[Deprecated] Use config.headerId instead"
    )


class BatchUpdateResponse(APIBaseModel):
    """Response for batch update.

    Attributes:
        batch_id: ID of the updated batch
        status: Update status ('updated')
    """
    batch_id: str = Field(..., description="Batch identifier")
    status: str = Field(default="updated", description="Update status")
