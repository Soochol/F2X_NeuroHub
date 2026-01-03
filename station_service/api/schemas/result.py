"""
Result-related API schemas for Station Service.

This module defines request and response schemas for execution result operations.
All responses use camelCase field names in JSON output via APIBaseModel.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from station_service.api.schemas.base import APIBaseModel


# ============================================================================
# Nested Models for Result Detail
# ============================================================================


class StepResultDetail(APIBaseModel):
    """Detailed result for a single step execution.

    Attributes:
        name: Step name
        order: Step execution order
        status: Execution status (completed, failed, skipped)
        passed: Whether the step passed
        duration: Execution duration in seconds
        started_at: Step start timestamp
        completed_at: Step completion timestamp
        result: Step result data
    """
    name: str = Field(..., description="Step name")
    order: int = Field(..., description="Step execution order", ge=1)
    status: str = Field(..., description="Execution status")
    passed: bool = Field(..., serialization_alias="pass", description="Whether the step passed")
    duration: float = Field(..., description="Execution duration in seconds", ge=0.0)
    started_at: datetime = Field(..., description="Step start timestamp")
    completed_at: datetime = Field(..., description="Step completion timestamp")
    result: Dict[str, Any] = Field(default_factory=dict, description="Step result data")


# ============================================================================
# Result Response Models
# ============================================================================


class ResultSummary(APIBaseModel):
    """Summary information for an execution result in list view.

    Attributes:
        id: Unique execution identifier
        batch_id: ID of the batch that ran the execution
        sequence_name: Name of the executed sequence
        sequence_version: Version of the executed sequence
        status: Execution status (completed, failed)
        overall_pass: Whether all steps passed
        started_at: Execution start timestamp
        completed_at: Execution completion timestamp
        duration: Total execution duration in seconds
        synced: Whether the result has been synced to backend
    """
    id: str = Field(..., description="Unique execution identifier")
    batch_id: str = Field(..., description="Batch identifier")
    sequence_name: str = Field(..., description="Executed sequence name")
    sequence_version: str = Field(..., description="Executed sequence version")
    status: str = Field(..., description="Execution status")
    overall_pass: bool = Field(..., description="Whether all steps passed")
    started_at: datetime = Field(..., description="Execution start timestamp")
    completed_at: datetime = Field(..., description="Execution completion timestamp")
    duration: float = Field(..., description="Total duration in seconds", ge=0.0)
    synced: bool = Field(default=False, description="Whether synced to backend")


class ResultDetail(APIBaseModel):
    """Detailed information for a single execution result.

    Attributes:
        id: Unique execution identifier
        batch_id: ID of the batch that ran the execution
        sequence_name: Name of the executed sequence
        sequence_version: Version of the executed sequence
        status: Execution status
        overall_pass: Whether all steps passed
        started_at: Execution start timestamp
        completed_at: Execution completion timestamp
        duration: Total execution duration in seconds
        parameters: Runtime parameters used for execution
        steps: List of step execution results
    """
    id: str = Field(..., description="Unique execution identifier")
    batch_id: str = Field(..., description="Batch identifier")
    sequence_name: str = Field(..., description="Executed sequence name")
    sequence_version: str = Field(..., description="Executed sequence version")
    status: str = Field(..., description="Execution status")
    overall_pass: bool = Field(..., description="Whether all steps passed")
    started_at: datetime = Field(..., description="Execution start timestamp")
    completed_at: datetime = Field(..., description="Execution completion timestamp")
    duration: float = Field(..., description="Total duration in seconds", ge=0.0)
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Runtime parameters")
    steps: List[StepResultDetail] = Field(default_factory=list, description="Step results")


# ============================================================================
# System Info and Health Models
# ============================================================================


class SystemInfo(APIBaseModel):
    """Station system information.

    Attributes:
        station_id: Unique station identifier
        station_name: Display name of the station
        description: Station description
        version: Service version
        uptime: Service uptime in seconds
        backend_connected: Whether connected to NeuroHub backend
        sequences_dir: Directory for sequence packages
        data_dir: Directory for data files
    """
    station_id: str = Field(..., description="Unique station identifier")
    station_name: str = Field(..., description="Display name of the station")
    description: Optional[str] = Field(None, description="Station description")
    version: str = Field(..., description="Service version")
    uptime: int = Field(..., description="Service uptime in seconds", ge=0)
    backend_connected: bool = Field(..., description="Whether connected to backend")
    sequences_dir: str = Field(..., description="Directory for sequence packages")
    data_dir: str = Field(..., description="Directory for data files")


class HealthStatus(APIBaseModel):
    """Health check response.

    Attributes:
        status: Overall health status (healthy, degraded, unhealthy)
        batches_running: Number of currently running batches
        backend_status: Backend connection status
        disk_usage: Disk usage percentage
    """
    status: str = Field(..., description="Overall health status")
    batches_running: int = Field(..., description="Number of running batches", ge=0)
    backend_status: str = Field(..., description="Backend connection status")
    disk_usage: float = Field(..., description="Disk usage percentage", ge=0.0, le=100.0)


# ============================================================================
# Log Models
# ============================================================================


class LogEntry(APIBaseModel):
    """Single log entry.

    Attributes:
        id: Log entry ID
        batch_id: Associated batch ID (optional)
        execution_id: Associated execution ID (optional)
        level: Log level (debug, info, warning, error)
        message: Log message
        timestamp: Log timestamp
    """
    id: int = Field(..., description="Log entry ID")
    batch_id: Optional[str] = Field(None, description="Associated batch ID")
    execution_id: Optional[str] = Field(None, description="Associated execution ID")
    level: str = Field(..., description="Log level")
    message: str = Field(..., description="Log message")
    timestamp: datetime = Field(..., description="Log timestamp")
