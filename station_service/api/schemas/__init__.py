"""
Station Service API Schemas.

This module exports all Pydantic schemas used for API request/response validation.
"""

from station_service.api.schemas.responses import (
    ApiResponse,
    ErrorDetail,
    ErrorResponse,
    PaginatedData,
    PaginatedResponse,
    PaginationMeta,
)
from station_service.api.schemas.batch import (
    BatchDetail,
    BatchExecution,
    BatchSequenceInfo,
    BatchStartResponse,
    BatchStopResponse,
    BatchSummary,
    HardwareStatus,
    ManualControlRequest,
    ManualControlResponse,
    SequenceStartRequest,
    SequenceStartResponse,
    SequenceStopResponse,
    StepResult,
)
from station_service.api.schemas.sequence import (
    HardwareConfigSchema,
    HardwareDefinition,
    ParameterDefinition,
    ParameterUpdate,
    SequenceDetail,
    SequenceSummary,
    SequenceUpdateRequest,
    SequenceUpdateResponse,
    StepDefinition,
    StepUpdate,
)
from station_service.api.schemas.result import (
    HealthStatus,
    LogEntry,
    ResultDetail,
    ResultSummary,
    StepResultDetail,
    SystemInfo,
)

__all__ = [
    # Common responses
    "ApiResponse",
    "ErrorDetail",
    "ErrorResponse",
    "PaginatedData",
    "PaginatedResponse",
    "PaginationMeta",
    # Batch schemas
    "BatchDetail",
    "BatchExecution",
    "BatchSequenceInfo",
    "BatchStartResponse",
    "BatchStopResponse",
    "BatchSummary",
    "HardwareStatus",
    "ManualControlRequest",
    "ManualControlResponse",
    "SequenceStartRequest",
    "SequenceStartResponse",
    "SequenceStopResponse",
    "StepResult",
    # Sequence schemas
    "HardwareConfigSchema",
    "HardwareDefinition",
    "ParameterDefinition",
    "ParameterUpdate",
    "SequenceDetail",
    "SequenceSummary",
    "SequenceUpdateRequest",
    "SequenceUpdateResponse",
    "StepDefinition",
    "StepUpdate",
    # Result schemas
    "HealthStatus",
    "LogEntry",
    "ResultDetail",
    "ResultSummary",
    "StepResultDetail",
    "SystemInfo",
]
