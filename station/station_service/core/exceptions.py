"""
Exception definitions for Station Service.

All custom exceptions inherit from StationError for consistent error handling.
"""

from typing import Any, Dict, Optional


class StationError(Exception):
    """Base exception for all Station Service errors."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize exception.

        Args:
            message: Error message
            code: Optional error code for categorization
            details: Optional additional details
        """
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for serialization."""
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details,
        }


# ============================================================
# Batch Exceptions
# ============================================================


class BatchError(StationError):
    """Base exception for batch-related errors."""

    pass


class BatchNotFoundError(BatchError):
    """Exception raised when a batch cannot be found."""

    def __init__(self, batch_id: str) -> None:
        """
        Initialize exception.

        Args:
            batch_id: The ID of the batch that was not found
        """
        super().__init__(
            message=f"Batch '{batch_id}' not found",
            code="BATCH_NOT_FOUND",
            details={"batch_id": batch_id},
        )
        self.batch_id = batch_id


class BatchAlreadyRunningError(BatchError):
    """Exception raised when trying to start a batch that is already running."""

    def __init__(self, batch_id: str) -> None:
        """
        Initialize exception.

        Args:
            batch_id: The ID of the batch that is already running
        """
        super().__init__(
            message=f"Batch '{batch_id}' is already running",
            code="BATCH_ALREADY_RUNNING",
            details={"batch_id": batch_id},
        )
        self.batch_id = batch_id


class BatchNotRunningError(BatchError):
    """Exception raised when trying to stop a batch that is not running."""

    def __init__(self, batch_id: str) -> None:
        """
        Initialize exception.

        Args:
            batch_id: The ID of the batch that is not running
        """
        super().__init__(
            message=f"Batch '{batch_id}' is not running",
            code="BATCH_NOT_RUNNING",
            details={"batch_id": batch_id},
        )
        self.batch_id = batch_id


class BatchProcessError(BatchError):
    """Exception raised when a batch process encounters an error."""

    def __init__(self, batch_id: str, error: str, exit_code: Optional[int] = None) -> None:
        """
        Initialize exception.

        Args:
            batch_id: The ID of the batch
            error: Error description
            exit_code: Process exit code if available
        """
        super().__init__(
            message=f"Batch '{batch_id}' process error: {error}",
            code="BATCH_PROCESS_ERROR",
            details={"batch_id": batch_id, "exit_code": exit_code},
        )
        self.batch_id = batch_id
        self.exit_code = exit_code


class BatchAlreadyExistsError(BatchError):
    """Exception raised when trying to create a batch that already exists."""

    def __init__(self, batch_id: str) -> None:
        """
        Initialize exception.

        Args:
            batch_id: The ID of the batch that already exists
        """
        super().__init__(
            message=f"Batch '{batch_id}' already exists",
            code="BATCH_ALREADY_EXISTS",
            details={"batch_id": batch_id},
        )
        self.batch_id = batch_id


class BatchPersistenceError(BatchError):
    """Exception raised when batch configuration persistence fails."""

    def __init__(self, batch_id: str, reason: str) -> None:
        """
        Initialize exception.

        Args:
            batch_id: The ID of the batch
            reason: Persistence failure reason
        """
        super().__init__(
            message=f"Failed to persist batch '{batch_id}': {reason}",
            code="BATCH_PERSISTENCE_ERROR",
            details={"batch_id": batch_id, "reason": reason},
        )
        self.batch_id = batch_id
        self.reason = reason


class BatchValidationError(BatchError):
    """Exception raised when batch configuration validation fails."""

    def __init__(self, message: str, batch_id: Optional[str] = None) -> None:
        """
        Initialize exception.

        Args:
            message: Validation error message
            batch_id: The ID of the batch (if available)
        """
        super().__init__(
            message=message,
            code="BATCH_VALIDATION_ERROR",
            details={"batch_id": batch_id} if batch_id else {},
        )
        self.batch_id = batch_id


# ============================================================
# Sequence Exceptions
# ============================================================


class SequenceError(StationError):
    """Base exception for sequence-related errors."""

    pass


class SequenceNotFoundError(SequenceError):
    """Exception raised when a sequence package cannot be found."""

    def __init__(self, package_path: str) -> None:
        """
        Initialize exception.

        Args:
            package_path: The path to the sequence package
        """
        super().__init__(
            message=f"Sequence package not found: {package_path}",
            code="SEQUENCE_NOT_FOUND",
            details={"package_path": package_path},
        )
        self.package_path = package_path


class SequenceValidationError(SequenceError):
    """Exception raised when sequence validation fails."""

    def __init__(self, message: str, package_path: str) -> None:
        """
        Initialize exception.

        Args:
            message: Validation error message
            package_path: The path to the sequence package
        """
        super().__init__(
            message=message,
            code="SEQUENCE_VALIDATION_ERROR",
            details={"package_path": package_path},
        )
        self.package_path = package_path


class SequenceExecutionError(SequenceError):
    """Exception raised when sequence execution fails."""

    def __init__(
        self,
        message: str,
        batch_id: str,
        step_name: Optional[str] = None,
    ) -> None:
        """
        Initialize exception.

        Args:
            message: Error message
            batch_id: The batch ID running the sequence
            step_name: The step that failed (if applicable)
        """
        super().__init__(
            message=message,
            code="SEQUENCE_EXECUTION_ERROR",
            details={"batch_id": batch_id, "step_name": step_name},
        )
        self.batch_id = batch_id
        self.step_name = step_name


# ============================================================
# Hardware Exceptions
# ============================================================


class HardwareError(StationError):
    """Base exception for hardware-related errors."""

    pass


class HardwareConnectionError(HardwareError):
    """Exception raised when hardware connection fails."""

    def __init__(self, hardware_id: str, reason: str) -> None:
        """
        Initialize exception.

        Args:
            hardware_id: The hardware identifier
            reason: Connection failure reason
        """
        super().__init__(
            message=f"Failed to connect to hardware '{hardware_id}': {reason}",
            code="HARDWARE_CONNECTION_ERROR",
            details={"hardware_id": hardware_id, "reason": reason},
        )
        self.hardware_id = hardware_id


class HardwareTimeoutError(HardwareError):
    """Exception raised when hardware operation times out."""

    def __init__(self, hardware_id: str, operation: str, timeout: float) -> None:
        """
        Initialize exception.

        Args:
            hardware_id: The hardware identifier
            operation: The operation that timed out
            timeout: Timeout value in seconds
        """
        super().__init__(
            message=f"Hardware '{hardware_id}' operation '{operation}' timed out after {timeout}s",
            code="HARDWARE_TIMEOUT",
            details={"hardware_id": hardware_id, "operation": operation, "timeout": timeout},
        )
        self.hardware_id = hardware_id
        self.operation = operation
        self.timeout = timeout


# ============================================================
# IPC Exceptions
# ============================================================


class IPCError(StationError):
    """Base exception for IPC communication errors."""

    pass


class IPCConnectionError(IPCError):
    """Exception raised when IPC connection fails."""

    def __init__(self, address: str, reason: str) -> None:
        """
        Initialize exception.

        Args:
            address: The IPC address
            reason: Connection failure reason
        """
        super().__init__(
            message=f"IPC connection failed to '{address}': {reason}",
            code="IPC_CONNECTION_ERROR",
            details={"address": address, "reason": reason},
        )
        self.address = address


class IPCTimeoutError(IPCError):
    """Exception raised when IPC operation times out."""

    def __init__(self, operation: str, timeout: float) -> None:
        """
        Initialize exception.

        Args:
            operation: The operation that timed out
            timeout: Timeout value in milliseconds
        """
        super().__init__(
            message=f"IPC operation '{operation}' timed out after {timeout}ms",
            code="IPC_TIMEOUT",
            details={"operation": operation, "timeout": timeout},
        )
        self.operation = operation
        self.timeout = timeout


# ============================================================
# Sync Exceptions
# ============================================================


class SyncError(StationError):
    """Base exception for synchronization errors."""

    pass


class SyncConnectionError(SyncError):
    """Exception raised when backend connection fails."""

    def __init__(self, url: str, reason: str) -> None:
        """
        Initialize exception.

        Args:
            url: The backend URL
            reason: Connection failure reason
        """
        super().__init__(
            message=f"Failed to connect to backend '{url}': {reason}",
            code="SYNC_CONNECTION_ERROR",
            details={"url": url, "reason": reason},
        )
        self.url = url


# ============================================================
# Backend Exceptions
# ============================================================


class BackendError(StationError):
    """Base exception for Backend communication errors."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        response: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None,
    ) -> None:
        """
        Initialize exception.

        Args:
            message: Error message
            code: Error code
            response: Backend response data
            status_code: HTTP status code
        """
        super().__init__(message, code)
        self.response = response
        self.status_code = status_code


class WIPNotFoundError(BackendError):
    """Exception raised when WIP item is not found in Backend."""

    def __init__(self, wip_id: str) -> None:
        """
        Initialize exception.

        Args:
            wip_id: The WIP ID that was not found
        """
        super().__init__(
            message=f"WIP '{wip_id}' not found",
            code="WIP_NOT_FOUND",
        )
        self.details = {"wip_id": wip_id}
        self.wip_id = wip_id


class PrerequisiteNotMetError(BackendError):
    """Exception raised when previous process not completed (BR-003)."""

    def __init__(self, wip_id: str, process_id: int, required_process: int) -> None:
        """
        Initialize exception.

        Args:
            wip_id: WIP ID
            process_id: Attempted process ID
            required_process: Required previous process ID
        """
        super().__init__(
            message=f"Process {required_process} must be completed before starting process {process_id}",
            code="PREREQUISITE_NOT_MET",
        )
        self.details = {
            "wip_id": wip_id,
            "process_id": process_id,
            "required_process": required_process,
        }
        self.wip_id = wip_id
        self.process_id = process_id
        self.required_process = required_process


class DuplicatePassError(BackendError):
    """Exception raised when duplicate PASS result not allowed (BR-004)."""

    def __init__(self, wip_id: str, process_id: int) -> None:
        """
        Initialize exception.

        Args:
            wip_id: WIP ID
            process_id: Process ID with duplicate PASS
        """
        super().__init__(
            message=f"Duplicate PASS not allowed for process {process_id}",
            code="DUPLICATE_PASS",
        )
        self.details = {"wip_id": wip_id, "process_id": process_id}
        self.wip_id = wip_id
        self.process_id = process_id


class InvalidWIPStatusError(BackendError):
    """Exception raised when WIP is in an invalid status for the operation."""

    def __init__(self, wip_id: str, status: str, operation: str) -> None:
        """
        Initialize exception.

        Args:
            wip_id: WIP ID
            status: Current WIP status
            operation: Attempted operation
        """
        super().__init__(
            message=f"Cannot {operation} WIP in status '{status}'",
            code="INVALID_WIP_STATUS",
        )
        self.details = {"wip_id": wip_id, "status": status, "operation": operation}
        self.wip_id = wip_id
        self.status = status
        self.operation = operation


class BackendConnectionError(BackendError):
    """Exception raised when Backend connection fails."""

    def __init__(self, url: str, reason: str) -> None:
        """
        Initialize exception.

        Args:
            url: Backend URL
            reason: Connection failure reason
        """
        super().__init__(
            message=f"Failed to connect to Backend '{url}': {reason}",
            code="BACKEND_CONNECTION_ERROR",
        )
        self.details = {"url": url, "reason": reason}
        self.url = url
        self.reason = reason


class TokenExpiredError(BackendError):
    """
    Exception raised when access token is expired and refresh failed.

    This indicates the user session has expired and re-authentication is required.
    """

    def __init__(self, message: Optional[str] = None) -> None:
        """
        Initialize exception.

        Args:
            message: Optional custom message
        """
        super().__init__(
            message=message or "세션이 만료되었습니다. 다시 로그인해주세요.",
            code="TOKEN_EXPIRED",
        )


class TokenRefreshError(BackendError):
    """
    Exception raised when token refresh fails.

    This can happen when:
    - Refresh token is invalid
    - Refresh token is expired
    - Backend auth service is unavailable
    """

    def __init__(self, reason: str) -> None:
        """
        Initialize exception.

        Args:
            reason: Reason for refresh failure
        """
        super().__init__(
            message=f"토큰 갱신 실패: {reason}",
            code="TOKEN_REFRESH_ERROR",
        )
        self.details = {"reason": reason}
        self.reason = reason


# ============================================================
# Configuration Exceptions
# ============================================================


class ConfigurationError(StationError):
    """Exception raised when configuration is invalid."""

    def __init__(self, message: str, config_file: Optional[str] = None) -> None:
        """
        Initialize exception.

        Args:
            message: Error message
            config_file: Path to the configuration file
        """
        super().__init__(
            message=message,
            code="CONFIGURATION_ERROR",
            details={"config_file": config_file} if config_file else {},
        )
        self.config_file = config_file
