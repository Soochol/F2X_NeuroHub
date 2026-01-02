"""
Typed exception handling for BatchWorker.

Provides specific exception types for different worker domains,
enabling precise error handling and better debugging.
"""

from typing import Any, Dict, Optional

from station_service.core.exceptions import StationError


class WorkerError(StationError):
    """Base exception for BatchWorker errors."""

    def __init__(
        self,
        message: str,
        batch_id: Optional[str] = None,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize WorkerError.

        Args:
            message: Error message
            batch_id: Batch ID where error occurred
            code: Error code for categorization
            details: Additional error details
        """
        super().__init__(message, code, details)
        self.batch_id = batch_id
        if batch_id:
            self.details["batch_id"] = batch_id


class CommandError(WorkerError):
    """Exception for IPC command handling errors."""

    def __init__(
        self,
        message: str,
        command_type: str,
        batch_id: Optional[str] = None,
        request_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize CommandError.

        Args:
            message: Error message
            command_type: Type of command that failed
            batch_id: Batch ID
            request_id: IPC request ID
            details: Additional details
        """
        super().__init__(
            message=message,
            batch_id=batch_id,
            code="COMMAND_ERROR",
            details=details or {},
        )
        self.command_type = command_type
        self.request_id = request_id
        self.details.update({
            "command_type": command_type,
            "request_id": request_id,
        })


class SequenceAlreadyRunningError(CommandError):
    """Exception when trying to start a sequence that is already running."""

    def __init__(self, batch_id: str, execution_id: Optional[str] = None) -> None:
        super().__init__(
            message="Sequence already running",
            command_type="START_SEQUENCE",
            batch_id=batch_id,
            details={"execution_id": execution_id},
        )
        self.code = "SEQUENCE_ALREADY_RUNNING"


class SequenceNotRunningError(CommandError):
    """Exception when trying to stop a sequence that is not running."""

    def __init__(self, batch_id: str) -> None:
        super().__init__(
            message="Sequence is not running",
            command_type="STOP_SEQUENCE",
            batch_id=batch_id,
        )
        self.code = "SEQUENCE_NOT_RUNNING"


class ExecutionError(WorkerError):
    """Exception for sequence execution errors."""

    def __init__(
        self,
        message: str,
        batch_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        step_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize ExecutionError.

        Args:
            message: Error message
            batch_id: Batch ID
            execution_id: Execution ID
            step_name: Step that failed
            details: Additional details
        """
        super().__init__(
            message=message,
            batch_id=batch_id,
            code="EXECUTION_ERROR",
            details=details or {},
        )
        self.execution_id = execution_id
        self.step_name = step_name
        self.details.update({
            "execution_id": execution_id,
            "step_name": step_name,
        })


class CLIWorkerStartError(ExecutionError):
    """Exception when CLI worker fails to start."""

    def __init__(
        self,
        message: str,
        batch_id: str,
        sequence_name: Optional[str] = None,
    ) -> None:
        super().__init__(
            message=f"Failed to start CLI sequence: {message}",
            batch_id=batch_id,
            details={"sequence_name": sequence_name},
        )
        self.code = "CLI_WORKER_START_ERROR"


class SequenceLoadError(ExecutionError):
    """Exception when sequence package fails to load."""

    def __init__(
        self,
        message: str,
        batch_id: str,
        package_path: str,
    ) -> None:
        super().__init__(
            message=message,
            batch_id=batch_id,
            details={"package_path": package_path},
        )
        self.code = "SEQUENCE_LOAD_ERROR"


class BackendIntegrationError(WorkerError):
    """Exception for Backend integration errors (착공/완공)."""

    def __init__(
        self,
        message: str,
        operation: str,
        batch_id: Optional[str] = None,
        wip_id: Optional[str] = None,
        process_id: Optional[int] = None,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize BackendIntegrationError.

        Args:
            message: Error message
            operation: Operation that failed (start_process, complete_process, etc.)
            batch_id: Batch ID
            wip_id: WIP ID
            process_id: Process ID
            status_code: HTTP status code from backend
            details: Additional details
        """
        super().__init__(
            message=message,
            batch_id=batch_id,
            code="BACKEND_INTEGRATION_ERROR",
            details=details or {},
        )
        self.operation = operation
        self.wip_id = wip_id
        self.process_id = process_id
        self.status_code = status_code
        self.details.update({
            "operation": operation,
            "wip_id": wip_id,
            "process_id": process_id,
            "status_code": status_code,
        })

    @property
    def is_client_error(self) -> bool:
        """Check if this is a client error (4xx)."""
        return self.status_code is not None and 400 <= self.status_code < 500

    @property
    def is_server_error(self) -> bool:
        """Check if this is a server error (5xx)."""
        return self.status_code is not None and 500 <= self.status_code < 600

    @property
    def is_retryable(self) -> bool:
        """Check if this error is retryable (server error or connection issue)."""
        if self.is_server_error:
            return True
        # Connection errors are retryable
        return "connection" in self.message.lower()


class StartProcessError(BackendIntegrationError):
    """Exception for 착공 (start-process) failures."""

    def __init__(
        self,
        message: str,
        batch_id: str,
        wip_id: str,
        process_id: int,
        status_code: Optional[int] = None,
    ) -> None:
        super().__init__(
            message=message,
            operation="start_process",
            batch_id=batch_id,
            wip_id=wip_id,
            process_id=process_id,
            status_code=status_code,
        )
        self.code = "START_PROCESS_ERROR"


class CompleteProcessError(BackendIntegrationError):
    """Exception for 완공 (complete-process) failures."""

    def __init__(
        self,
        message: str,
        batch_id: str,
        wip_id: str,
        process_id: int,
        status_code: Optional[int] = None,
    ) -> None:
        super().__init__(
            message=message,
            operation="complete_process",
            batch_id=batch_id,
            wip_id=wip_id,
            process_id=process_id,
            status_code=status_code,
        )
        self.code = "COMPLETE_PROCESS_ERROR"


class HardwareIntegrationError(WorkerError):
    """Exception for hardware integration errors."""

    def __init__(
        self,
        message: str,
        hardware_name: str,
        batch_id: Optional[str] = None,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize HardwareIntegrationError.

        Args:
            message: Error message
            hardware_name: Name of hardware that failed
            batch_id: Batch ID
            operation: Operation that failed
            details: Additional details
        """
        super().__init__(
            message=message,
            batch_id=batch_id,
            code="HARDWARE_INTEGRATION_ERROR",
            details=details or {},
        )
        self.hardware_name = hardware_name
        self.operation = operation
        self.details.update({
            "hardware_name": hardware_name,
            "operation": operation,
        })


class DriverNotFoundError(HardwareIntegrationError):
    """Exception when hardware driver is not found."""

    def __init__(self, hardware_name: str, batch_id: Optional[str] = None) -> None:
        super().__init__(
            message=f"Hardware '{hardware_name}' not found",
            hardware_name=hardware_name,
            batch_id=batch_id,
        )
        self.code = "DRIVER_NOT_FOUND"


class DriverCommandError(HardwareIntegrationError):
    """Exception when hardware driver command fails."""

    def __init__(
        self,
        hardware_name: str,
        command: str,
        batch_id: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        super().__init__(
            message=f"Command '{command}' failed on hardware '{hardware_name}': {error}",
            hardware_name=hardware_name,
            batch_id=batch_id,
            operation=command,
            details={"error": error},
        )
        self.code = "DRIVER_COMMAND_ERROR"


class BarcodeScannerError(HardwareIntegrationError):
    """Exception for barcode scanner errors."""

    def __init__(
        self,
        message: str,
        batch_id: Optional[str] = None,
        operation: Optional[str] = None,
    ) -> None:
        super().__init__(
            message=message,
            hardware_name="barcode_scanner",
            batch_id=batch_id,
            operation=operation,
        )
        self.code = "BARCODE_SCANNER_ERROR"
