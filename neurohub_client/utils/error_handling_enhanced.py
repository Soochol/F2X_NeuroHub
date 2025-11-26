"""
Enhanced Error Handling System for Production Tracker App.

Provides custom exception classes, retry logic, error recovery strategies,
and user-friendly error message mapping.
"""
import logging
import time
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

logger = logging.getLogger(__name__)


# =============================================================================
# Custom Exception Classes
# =============================================================================

class ProductionTrackerError(Exception):
    """Base exception for all production tracker errors."""

    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize error.

        Args:
            message: Error message
            error_code: Optional error code for categorization
            details: Optional dictionary with additional error context
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/reporting."""
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


class BarcodeValidationError(ProductionTrackerError):
    """Raised when barcode validation fails."""

    def __init__(self, barcode: str, reason: str) -> None:
        super().__init__(
            f"잘못된 바코드 형식: {barcode}",
            error_code="BARCODE_INVALID",
            details={"barcode": barcode, "reason": reason}
        )
        self.barcode = barcode
        self.reason = reason


class SerialNumberError(ProductionTrackerError):
    """Raised for serial number related errors."""

    def __init__(self, serial: str, reason: str) -> None:
        super().__init__(
            f"Serial 번호 오류: {serial}",
            error_code="SERIAL_ERROR",
            details={"serial": serial, "reason": reason}
        )


class LOTNumberError(ProductionTrackerError):
    """Raised for LOT number related errors."""

    def __init__(self, lot_number: str, reason: str) -> None:
        super().__init__(
            f"LOT 번호 오류: {lot_number}",
            error_code="LOT_ERROR",
            details={"lot_number": lot_number, "reason": reason}
        )


class PrinterError(ProductionTrackerError):
    """Raised for printer-related errors."""

    def __init__(self, message: str, printer_name: Optional[str] = None) -> None:
        super().__init__(
            message,
            error_code="PRINTER_ERROR",
            details={"printer_name": printer_name}
        )
        self.printer_name = printer_name


class PrinterConnectionError(PrinterError):
    """Raised when printer connection fails."""

    def __init__(self, printer_name: str, reason: str) -> None:
        super().__init__(
            f"프린터 연결 실패: {printer_name} - {reason}",
            printer_name=printer_name
        )


class PrinterNotConfiguredError(PrinterError):
    """Raised when printer is not configured."""

    def __init__(self) -> None:
        super().__init__("프린터가 설정되지 않았습니다")


class APIError(ProductionTrackerError):
    """Raised for API-related errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, endpoint: Optional[str] = None) -> None:
        super().__init__(
            message,
            error_code="API_ERROR",
            details={"status_code": status_code, "endpoint": endpoint}
        )
        self.status_code = status_code
        self.endpoint = endpoint


class APIConnectionError(APIError):
    """Raised when API connection fails."""

    def __init__(self, endpoint: str, reason: str) -> None:
        super().__init__(
            f"API 연결 실패: {endpoint} - {reason}",
            endpoint=endpoint
        )


class APIAuthenticationError(APIError):
    """Raised for authentication failures."""

    def __init__(self, message: str = "인증 실패") -> None:
        super().__init__(message, status_code=401)


class APINotFoundError(APIError):
    """Raised when resource not found."""

    def __init__(self, resource: str) -> None:
        super().__init__(
            f"리소스를 찾을 수 없습니다: {resource}",
            status_code=404,
            endpoint=resource
        )


class WIPGenerationError(ProductionTrackerError):
    """Raised for WIP generation errors."""

    def __init__(self, lot_number: str, reason: str) -> None:
        super().__init__(
            f"WIP 생성 실패: {lot_number} - {reason}",
            error_code="WIP_GEN_ERROR",
            details={"lot_number": lot_number, "reason": reason}
        )


class WIPScanError(ProductionTrackerError):
    """Raised for WIP scanning errors."""

    def __init__(self, serial: str, reason: str) -> None:
        super().__init__(
            f"WIP 스캔 실패: {serial} - {reason}",
            error_code="WIP_SCAN_ERROR",
            details={"serial": serial, "reason": reason}
        )


class ConfigurationError(ProductionTrackerError):
    """Raised for configuration-related errors."""

    def __init__(self, setting: str, reason: str) -> None:
        super().__init__(
            f"설정 오류: {setting} - {reason}",
            error_code="CONFIG_ERROR",
            details={"setting": setting, "reason": reason}
        )


# =============================================================================
# Error Severity Levels
# =============================================================================

class ErrorSeverity(Enum):
    """Error severity levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# =============================================================================
# Retry Logic
# =============================================================================

class RetryStrategy:
    """Configurable retry strategy for operations."""

    def __init__(
        self,
        max_attempts: int = 3,
        delay_seconds: float = 1.0,
        backoff_multiplier: float = 2.0,
        max_delay: float = 10.0,
        retry_on: Tuple[Type[Exception], ...] = (Exception,)
    ) -> None:
        """
        Initialize retry strategy.

        Args:
            max_attempts: Maximum number of retry attempts
            delay_seconds: Initial delay between retries
            backoff_multiplier: Multiplier for exponential backoff
            max_delay: Maximum delay between retries
            retry_on: Tuple of exception types to retry on
        """
        self.max_attempts = max_attempts
        self.delay_seconds = delay_seconds
        self.backoff_multiplier = backoff_multiplier
        self.max_delay = max_delay
        self.retry_on = retry_on

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number."""
        delay = self.delay_seconds * (self.backoff_multiplier ** attempt)
        return min(delay, self.max_delay)


def with_retry(
    strategy: Optional[RetryStrategy] = None,
    on_retry: Optional[Callable[[int, Exception], None]] = None
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to retry function on failure.

    Args:
        strategy: RetryStrategy instance (default: 3 attempts with exponential backoff)
        on_retry: Optional callback called on each retry (attempt_number, exception)

    Example:
        @with_retry(RetryStrategy(max_attempts=5))
        def fetch_data():
            return api_client.get_data()
    """
    if strategy is None:
        strategy = RetryStrategy()

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None

            for attempt in range(strategy.max_attempts):
                try:
                    return func(*args, **kwargs)
                except strategy.retry_on as e:
                    last_exception = e

                    if attempt < strategy.max_attempts - 1:
                        delay = strategy.calculate_delay(attempt)
                        logger.warning(
                            f"Attempt {attempt + 1}/{strategy.max_attempts} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )

                        if on_retry:
                            on_retry(attempt + 1, e)

                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {strategy.max_attempts} attempts failed for {func.__name__}: {e}"
                        )

            # Re-raise the last exception if all retries failed
            raise last_exception

        return wrapper
    return decorator


# =============================================================================
# Error Recovery Strategies
# =============================================================================

class ErrorRecovery:
    """Error recovery utility with fallback mechanisms."""

    @staticmethod
    def with_fallback(
        primary: Callable,
        fallback: Callable,
        error_message: str = "Primary operation failed, using fallback"
    ) -> Any:
        """
        Execute primary function, fall back to secondary on failure.

        Args:
            primary: Primary function to try
            fallback: Fallback function if primary fails
            error_message: Log message for fallback

        Returns:
            Result from primary or fallback function
        """
        try:
            return primary()
        except Exception as e:
            logger.warning(f"{error_message}: {e}. Using fallback.")
            return fallback()

    @staticmethod
    def with_default(
        func: Callable,
        default: Any,
        error_message: str = "Operation failed, using default"
    ) -> Any:
        """
        Execute function, return default on failure.

        Args:
            func: Function to try
            default: Default value to return on error
            error_message: Log message

        Returns:
            Function result or default value
        """
        try:
            return func()
        except Exception as e:
            logger.info(f"{error_message}: {e}")
            return default

    @staticmethod
    def circuit_breaker(
        func: Callable,
        failure_threshold: int = 5,
        timeout_seconds: float = 60.0
    ):
        """
        Circuit breaker pattern to prevent cascading failures.

        Args:
            func: Function to protect
            failure_threshold: Number of failures before opening circuit
            timeout_seconds: Time to wait before trying again

        Example:
            protected_api_call = ErrorRecovery.circuit_breaker(
                api_client.get_data,
                failure_threshold=3,
                timeout_seconds=30
            )
        """
        state = {
            "failures": 0,
            "last_failure_time": None,
            "is_open": False
        }

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if circuit is open
            if state["is_open"]:
                if time.time() - state["last_failure_time"] < timeout_seconds:
                    raise ProductionTrackerError(
                        "Circuit breaker is open - too many recent failures",
                        error_code="CIRCUIT_OPEN"
                    )
                else:
                    # Try to close circuit (half-open state)
                    logger.info("Circuit breaker: attempting to close circuit")
                    state["is_open"] = False
                    state["failures"] = 0

            try:
                result = func(*args, **kwargs)
                # Success - reset failure count
                state["failures"] = 0
                return result

            except Exception as e:
                state["failures"] += 1
                state["last_failure_time"] = time.time()

                if state["failures"] >= failure_threshold:
                    state["is_open"] = True
                    logger.error(
                        f"Circuit breaker opened after {state['failures']} failures for {func.__name__}"
                    )

                raise

        return wrapper


# =============================================================================
# User-Friendly Error Messages
# =============================================================================

class ErrorMessageMapper:
    """Maps technical errors to user-friendly Korean messages."""

    # Error message mappings
    MESSAGES: Dict[str, str] = {
        # Connection errors
        "Connection refused": "서버에 연결할 수 없습니다. 네트워크 연결을 확인하세요.",
        "Connection timeout": "서버 응답 시간이 초과되었습니다. 잠시 후 다시 시도하세요.",
        "Network is unreachable": "네트워크에 연결할 수 없습니다.",

        # Authentication errors
        "Unauthorized": "인증에 실패했습니다. 로그인 정보를 확인하세요.",
        "Forbidden": "접근 권한이 없습니다.",
        "Token expired": "세션이 만료되었습니다. 다시 로그인하세요.",

        # Data errors
        "Not found": "요청한 데이터를 찾을 수 없습니다.",
        "Bad request": "잘못된 요청입니다. 입력 데이터를 확인하세요.",
        "Invalid format": "잘못된 형식입니다.",

        # Printer errors
        "Printer not found": "프린터를 찾을 수 없습니다.",
        "Printer offline": "프린터가 오프라인 상태입니다.",
        "Paper jam": "용지 걸림이 발생했습니다.",
        "Out of paper": "용지가 부족합니다.",

        # General errors
        "Internal server error": "서버 내부 오류가 발생했습니다. 관리자에게 문의하세요.",
        "Service unavailable": "서비스를 일시적으로 사용할 수 없습니다.",
        "Timeout": "작업 시간이 초과되었습니다.",
    }

    @classmethod
    def get_user_message(cls, error: Exception) -> str:
        """
        Get user-friendly message for exception.

        Args:
            error: Exception to convert

        Returns:
            User-friendly Korean error message
        """
        error_str = str(error).lower()

        # Check for known error patterns
        for pattern, message in cls.MESSAGES.items():
            if pattern.lower() in error_str:
                return message

        # Check custom exception types
        if isinstance(error, BarcodeValidationError):
            return f"바코드 형식이 올바르지 않습니다: {error.barcode}"
        elif isinstance(error, PrinterNotConfiguredError):
            return "프린터가 설정되지 않았습니다. 설정 메뉴에서 프린터를 구성하세요."
        elif isinstance(error, PrinterConnectionError):
            return f"프린터 연결에 실패했습니다: {error.printer_name}"
        elif isinstance(error, APIAuthenticationError):
            return "인증에 실패했습니다. 로그인 정보를 확인하세요."
        elif isinstance(error, APINotFoundError):
            return "요청한 데이터를 찾을 수 없습니다."
        elif isinstance(error, WIPGenerationError):
            return "WIP 생성 중 오류가 발생했습니다. 다시 시도하세요."
        elif isinstance(error, WIPScanError):
            return "WIP 스캔 중 오류가 발생했습니다."

        # Default generic message
        return f"작업 중 오류가 발생했습니다: {str(error)}"


# =============================================================================
# Enhanced Logging with Context
# =============================================================================

class ContextLogger:
    """Logger with additional context information."""

    def __init__(self, logger_name: str) -> None:
        self.logger = logging.getLogger(logger_name)
        self.context: Dict[str, Any] = {}

    def set_context(self, **kwargs: Any) -> None:
        """Set context variables for logging."""
        self.context.update(kwargs)

    def clear_context(self) -> None:
        """Clear all context variables."""
        self.context.clear()

    def _format_message(self, message: str) -> str:
        """Format message with context."""
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{message} [{context_str}]"
        return message

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message with context."""
        self.logger.debug(self._format_message(message), extra=kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message with context."""
        self.logger.info(self._format_message(message), extra=kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message with context."""
        self.logger.warning(self._format_message(message), extra=kwargs)

    def error(self, message: str, exc_info: bool = True, **kwargs: Any) -> None:
        """Log error message with context."""
        self.logger.error(self._format_message(message), exc_info=exc_info, extra=kwargs)

    def critical(self, message: str, exc_info: bool = True, **kwargs: Any) -> None:
        """Log critical message with context."""
        self.logger.critical(self._format_message(message), exc_info=exc_info, extra=kwargs)


# =============================================================================
# Error Aggregator for Batch Operations
# =============================================================================

class ErrorAggregator:
    """
    Aggregates errors from batch operations.

    Example:
        aggregator = ErrorAggregator()

        for item in items:
            try:
                process(item)
            except Exception as e:
                aggregator.add_error(item.id, e)

        if aggregator.has_errors():
            report = aggregator.get_summary()
            logger.error(f"Batch operation failed: {report}")
    """

    def __init__(self) -> None:
        self.errors: List[Dict[str, Any]] = []

    def add_error(
        self,
        identifier: Any,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add an error to the aggregator.

        Args:
            identifier: Identifier for the failed item
            error: Exception that occurred
            context: Optional additional context
        """
        self.errors.append({
            "identifier": identifier,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        })

    def has_errors(self) -> bool:
        """Check if any errors were recorded."""
        return len(self.errors) > 0

    def error_count(self) -> int:
        """Get number of errors."""
        return len(self.errors)

    def get_errors(self) -> List[Dict[str, Any]]:
        """Get all errors."""
        return self.errors.copy()

    def get_summary(self) -> str:
        """Get formatted error summary."""
        if not self.errors:
            return "No errors"

        summary = f"Total errors: {len(self.errors)}\n"

        # Group by error type
        by_type: Dict[str, int] = {}
        for error in self.errors:
            error_type = error["error_type"]
            by_type[error_type] = by_type.get(error_type, 0) + 1

        summary += "Errors by type:\n"
        for error_type, count in by_type.items():
            summary += f"  - {error_type}: {count}\n"

        return summary

    def clear(self) -> None:
        """Clear all errors."""
        self.errors.clear()


# =============================================================================
# Convenience Functions
# =============================================================================

def raise_if_none(
    value: Any,
    error_message: str,
    error_class: Type[ProductionTrackerError] = ProductionTrackerError
) -> Any:
    """
    Raise error if value is None.

    Args:
        value: Value to check
        error_message: Error message if None
        error_class: Exception class to raise

    Raises:
        error_class: If value is None

    Example:
        serial = get_serial()
        raise_if_none(serial, "Serial not found", SerialNumberError)
    """
    if value is None:
        raise error_class(error_message)
    return value


def validate_or_raise(
    condition: bool,
    error_message: str,
    error_class: Type[ProductionTrackerError] = ProductionTrackerError
) -> None:
    """
    Raise error if condition is False.

    Args:
        condition: Condition to validate
        error_message: Error message if False
        error_class: Exception class to raise

    Raises:
        error_class: If condition is False

    Example:
        validate_or_raise(
            len(serial) == 14,
            "Serial must be 14 characters",
            SerialNumberError
        )
    """
    if not condition:
        raise error_class(error_message)
