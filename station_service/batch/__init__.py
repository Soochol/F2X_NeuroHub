"""
Batch module for Station Service.

Provides batch process management including lifecycle control,
process isolation, and IPC communication.

Note: Use lazy imports to avoid circular import issues when
BatchWorker is imported in subprocess context.
"""


def __getattr__(name: str):
    """Lazy import to avoid circular imports in subprocess context."""
    if name == "BatchManager":
        from station_service.batch.manager import BatchManager
        return BatchManager
    elif name == "BatchProcess":
        from station_service.batch.process import BatchProcess
        return BatchProcess
    elif name == "BatchWorker":
        from station_service.batch.worker import BatchWorker
        return BatchWorker
    elif name == "CLISequenceWorker":
        from station_service.batch.cli_worker import CLISequenceWorker
        return CLISequenceWorker
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "BatchManager",
    "BatchProcess",
    "BatchWorker",
    "CLISequenceWorker",
]
