"""
BatchWorker subpackage for Station Service.

This package provides a modular BatchWorker implementation with separated concerns:

- core: Core worker logic, lifecycle management, IPC connection
- commands: Command handler mixin for IPC commands
- backend: Backend integration mixin for 착공/완공 operations
- execution: Sequence execution mixin for CLI worker callbacks
- hardware: Hardware integration mixin for drivers and barcode scanner
- state: Execution state management
- exceptions: Typed exception handling utilities

Usage:
    from station_service.batch.worker import BatchWorker

    worker = BatchWorker(
        batch_id="batch_1",
        config=batch_config,
        ipc_router_address="tcp://127.0.0.1:5555",
        ipc_sub_address="tcp://127.0.0.1:5557",
    )
    await worker.run()
"""

from station_service.batch.worker.core import BatchWorker
from station_service.batch.worker.state import ExecutionState, WorkerState
from station_service.batch.worker.exceptions import (
    WorkerError,
    CommandError,
    ExecutionError,
    BackendIntegrationError,
    HardwareIntegrationError,
)

__all__ = [
    "BatchWorker",
    "ExecutionState",
    "WorkerState",
    "WorkerError",
    "CommandError",
    "ExecutionError",
    "BackendIntegrationError",
    "HardwareIntegrationError",
]
