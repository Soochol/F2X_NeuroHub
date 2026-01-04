"""
Station Service Data Models

This module provides Pydantic models for the Station Service.
"""

from station_service.models.batch import Batch, BatchDetail, BatchStatus
from station_service.models.config import (
    BackendConfig,
    BatchConfig,
    LoggingConfig,
    ServerConfig,
    StationConfig,
    StationInfo,
)
from station_service.models.execution import (
    ExecutionResult,
    ExecutionStatus,
    ExecutionSummary,
    StepResult,
)
from station_service.models.hardware import HardwareStatus
from station_service.models.log import LogEntry, LogLevel
from station_service.models.messages import (
    # WebSocket Client Messages
    SubscribeMessage,
    UnsubscribeMessage,
    # WebSocket Server Messages
    BatchStatusMessage,
    StepStartMessage,
    StepCompleteMessage,
    SequenceCompleteMessage,
    LogMessage,
    ErrorMessage,
    # IPC Commands
    StartSequenceCommand,
    StopSequenceCommand,
    GetStatusCommand,
    ManualControlCommand,
    ShutdownCommand,
    # IPC Response
    CommandResponse,
    # IPC Events
    StepStartEvent,
    StepCompleteEvent,
    SequenceCompleteEvent,
    LogEvent,
    ErrorEvent,
)
from station_service.models.sequence import (
    ConfigField,
    EntryPoint,
    HardwareDefinition,
    HardwareSchema,
    ParameterDefinition,
    ParameterSchema,
    SequenceManifest,
    SequencePackage,
    StepSchema,
)
from station_service.models.station import Station

__all__ = [
    # Station
    "Station",
    # Batch
    "Batch",
    "BatchDetail",
    "BatchStatus",
    # Execution
    "ExecutionResult",
    "ExecutionStatus",
    "ExecutionSummary",
    "StepResult",
    # Hardware
    "HardwareStatus",
    # Log
    "LogEntry",
    "LogLevel",
    # Config
    "BackendConfig",
    "BatchConfig",
    "LoggingConfig",
    "ServerConfig",
    "StationConfig",
    "StationInfo",
    # Sequence
    "ConfigField",
    "EntryPoint",
    "HardwareDefinition",
    "HardwareSchema",
    "ParameterDefinition",
    "ParameterSchema",
    "SequenceManifest",
    "SequencePackage",
    "StepSchema",
    # WebSocket Client Messages
    "SubscribeMessage",
    "UnsubscribeMessage",
    # WebSocket Server Messages
    "BatchStatusMessage",
    "StepStartMessage",
    "StepCompleteMessage",
    "SequenceCompleteMessage",
    "LogMessage",
    "ErrorMessage",
    # IPC Commands
    "StartSequenceCommand",
    "StopSequenceCommand",
    "GetStatusCommand",
    "ManualControlCommand",
    "ShutdownCommand",
    # IPC Response
    "CommandResponse",
    # IPC Events
    "StepStartEvent",
    "StepCompleteEvent",
    "SequenceCompleteEvent",
    "LogEvent",
    "ErrorEvent",
]
