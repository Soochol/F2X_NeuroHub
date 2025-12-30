"""
Core module for Station Service.

Provides exceptions, events, and utility classes.
"""

from station_service.core.exceptions import (
    StationError,
    BatchError,
    BatchNotFoundError,
    BatchAlreadyRunningError,
    SequenceError,
    HardwareError,
    IPCError,
    SyncError,
    ConfigurationError,
)
from station_service.core.events import (
    Event,
    EventType,
    EventEmitter,
)
from station_service.core.container import (
    ServiceContainer,
    get_container,
    set_container,
    initialize_container,
    shutdown_container,
)

__all__ = [
    # Exceptions
    "StationError",
    "BatchError",
    "BatchNotFoundError",
    "BatchAlreadyRunningError",
    "SequenceError",
    "HardwareError",
    "IPCError",
    "SyncError",
    "ConfigurationError",
    # Events
    "Event",
    "EventType",
    "EventEmitter",
    # Container
    "ServiceContainer",
    "get_container",
    "set_container",
    "initialize_container",
    "shutdown_container",
]
