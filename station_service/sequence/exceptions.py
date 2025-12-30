"""
Exception hierarchy for sequence-related errors.

This module defines a comprehensive exception hierarchy for handling
various error conditions during sequence execution.
"""

from typing import Any, Optional


class SequenceError(Exception):
    """Base exception for all sequence-related errors."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


class PackageError(SequenceError):
    """Exception for package structure and validation errors."""

    def __init__(
        self,
        message: str,
        package_name: Optional[str] = None,
        details: Optional[dict] = None,
    ) -> None:
        super().__init__(message, details)
        self.package_name = package_name


class ManifestError(PackageError):
    """Exception for manifest parsing and validation errors."""

    def __init__(
        self,
        message: str,
        package_name: Optional[str] = None,
        manifest_path: Optional[str] = None,
        details: Optional[dict] = None,
    ) -> None:
        super().__init__(message, package_name, details)
        self.manifest_path = manifest_path


class DriverError(SequenceError):
    """Base exception for hardware driver errors."""

    def __init__(
        self,
        message: str,
        driver_name: Optional[str] = None,
        details: Optional[dict] = None,
    ) -> None:
        super().__init__(message, details)
        self.driver_name = driver_name


class ConnectionError(DriverError):
    """Exception for driver connection errors."""

    def __init__(
        self,
        message: str,
        driver_name: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        details: Optional[dict] = None,
    ) -> None:
        super().__init__(message, driver_name, details)
        self.host = host
        self.port = port


class CommunicationError(DriverError):
    """Exception for driver communication errors."""

    def __init__(
        self,
        message: str,
        driver_name: Optional[str] = None,
        command: Optional[str] = None,
        response: Optional[str] = None,
        details: Optional[dict] = None,
    ) -> None:
        super().__init__(message, driver_name, details)
        self.command = command
        self.response = response


class ExecutionError(SequenceError):
    """Base exception for sequence execution errors."""

    def __init__(
        self,
        message: str,
        step_name: Optional[str] = None,
        details: Optional[dict] = None,
    ) -> None:
        super().__init__(message, details)
        self.step_name = step_name


class TestFailure(ExecutionError):
    """Exception for test verification failures."""

    def __init__(
        self,
        message: str,
        step_name: Optional[str] = None,
        actual: Any = None,
        limit: Any = None,
        limit_type: Optional[str] = None,
        details: Optional[dict] = None,
    ) -> None:
        super().__init__(message, step_name, details)
        self.actual = actual
        self.limit = limit
        self.limit_type = limit_type  # e.g., "min", "max", "range", "equals"

    def __str__(self) -> str:
        base_msg = self.message
        if self.actual is not None and self.limit is not None:
            base_msg = f"{base_msg} (actual={self.actual}, limit={self.limit})"
        if self.details:
            base_msg = f"{base_msg} - Details: {self.details}"
        return base_msg


class TestSkipped(ExecutionError):
    """Exception for skipped tests."""

    def __init__(
        self,
        message: str,
        step_name: Optional[str] = None,
        reason: Optional[str] = None,
        details: Optional[dict] = None,
    ) -> None:
        super().__init__(message, step_name, details)
        self.reason = reason


class StepTimeoutError(ExecutionError):
    """Exception for step timeout errors."""

    def __init__(
        self,
        message: str,
        step_name: Optional[str] = None,
        timeout: Optional[float] = None,
        elapsed: Optional[float] = None,
        details: Optional[dict] = None,
    ) -> None:
        super().__init__(message, step_name, details)
        self.timeout = timeout
        self.elapsed = elapsed

    def __str__(self) -> str:
        base_msg = self.message
        if self.timeout is not None:
            base_msg = f"{base_msg} (timeout={self.timeout}s"
            if self.elapsed is not None:
                base_msg = f"{base_msg}, elapsed={self.elapsed:.2f}s)"
            else:
                base_msg = f"{base_msg})"
        if self.details:
            base_msg = f"{base_msg} - Details: {self.details}"
        return base_msg
