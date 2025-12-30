"""
Typed Exception Hierarchy for Production Tracker App.

Provides structured exception types for:
- Clear error categorization
- User-friendly error messages
- Proper exception handling chains

Usage:
    from utils.exceptions import WorkOperationError, AuthenticationError

    try:
        work_service.start_work(wip_id, worker_id)
    except WorkOperationError as e:
        logger.error(f"Work operation failed: {e}")
        show_error(e.user_message)
"""
from enum import Enum
from typing import Any, Dict, Optional


class ErrorCode(Enum):
    """Standard error codes for categorization and logging."""

    # General errors (1xxx)
    UNKNOWN = 1000
    CONFIGURATION = 1001
    VALIDATION = 1002

    # Connection errors (2xxx)
    CONNECTION_FAILED = 2000
    TIMEOUT = 2001
    NETWORK_UNAVAILABLE = 2002

    # Authentication errors (3xxx)
    AUTH_FAILED = 3000
    TOKEN_EXPIRED = 3001
    TOKEN_INVALID = 3002
    PERMISSION_DENIED = 3003

    # Work operation errors (4xxx)
    WORK_START_FAILED = 4000
    WORK_COMPLETE_FAILED = 4001
    WORK_ALREADY_STARTED = 4002
    WORK_NOT_FOUND = 4003
    WIP_INVALID = 4004
    PROCESS_SEQUENCE_ERROR = 4005

    # Equipment errors (5xxx)
    EQUIPMENT_CONNECTION = 5000
    EQUIPMENT_TIMEOUT = 5001
    EQUIPMENT_INVALID_DATA = 5002

    # File operation errors (6xxx)
    FILE_NOT_FOUND = 6000
    FILE_PARSE_ERROR = 6001
    FILE_WRITE_ERROR = 6002


class NeuroHubError(Exception):
    """
    Base exception for all application errors.

    Provides:
    - Error code for categorization
    - Technical message for logging
    - User-friendly message for UI display
    - Additional context data
    """

    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.UNKNOWN,
        user_message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        """
        Initialize NeuroHubError.

        Args:
            message: Technical error message (for logging)
            code: Error code for categorization
            user_message: User-friendly message (Korean). Defaults to message.
            details: Additional context data
            cause: Original exception that caused this error
        """
        super().__init__(message)
        self.code = code
        self.user_message = user_message or message
        self.details = details or {}
        self.cause = cause

    def __str__(self) -> str:
        return f"[{self.code.name}] {self.args[0]}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging or serialization."""
        return {
            "code": self.code.value,
            "code_name": self.code.name,
            "message": str(self.args[0]),
            "user_message": self.user_message,
            "details": self.details,
            "cause": str(self.cause) if self.cause else None
        }


class ConnectionError(NeuroHubError):
    """
    Raised when backend connection fails.

    Examples:
    - Server unreachable
    - Network unavailable
    - DNS resolution failure
    """

    def __init__(
        self,
        message: str = "백엔드 서버에 연결할 수 없습니다",
        base_url: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        user_message = f"서버에 연결할 수 없습니다. 네트워크 상태를 확인하세요."
        if base_url:
            user_message = f"서버({base_url})에 연결할 수 없습니다."

        super().__init__(
            message=message,
            code=ErrorCode.CONNECTION_FAILED,
            user_message=user_message,
            details={"base_url": base_url} if base_url else {},
            cause=cause
        )


class TimeoutError(NeuroHubError):
    """
    Raised when a request times out.

    Examples:
    - API request timeout
    - TCP connection timeout
    - Equipment response timeout
    """

    def __init__(
        self,
        message: str = "서버 응답 시간이 초과되었습니다",
        timeout_seconds: Optional[float] = None,
        operation: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        details = {}
        if timeout_seconds:
            details["timeout_seconds"] = timeout_seconds
        if operation:
            details["operation"] = operation

        super().__init__(
            message=message,
            code=ErrorCode.TIMEOUT,
            user_message=f"서버 응답 시간이 초과되었습니다. 다시 시도해주세요.",
            details=details,
            cause=cause
        )


class AuthenticationError(NeuroHubError):
    """
    Raised when authentication fails.

    Examples:
    - Invalid credentials
    - Token expired
    - Permission denied
    """

    def __init__(
        self,
        message: str = "인증에 실패했습니다",
        code: ErrorCode = ErrorCode.AUTH_FAILED,
        username: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        user_messages = {
            ErrorCode.AUTH_FAILED: "로그인에 실패했습니다. 사용자명과 비밀번호를 확인하세요.",
            ErrorCode.TOKEN_EXPIRED: "인증이 만료되었습니다. 다시 로그인해주세요.",
            ErrorCode.TOKEN_INVALID: "인증 정보가 올바르지 않습니다. 다시 로그인해주세요.",
            ErrorCode.PERMISSION_DENIED: "해당 작업에 대한 권한이 없습니다.",
        }

        super().__init__(
            message=message,
            code=code,
            user_message=user_messages.get(code, message),
            details={"username": username} if username else {},
            cause=cause
        )


class WorkOperationError(NeuroHubError):
    """
    Raised when work start/complete operations fail.

    Examples:
    - Work already started (duplicate)
    - WIP not found
    - Process sequence violation
    """

    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.WORK_START_FAILED,
        wip_id: Optional[str] = None,
        operation: str = "start",
        cause: Optional[Exception] = None
    ):
        user_messages = {
            ErrorCode.WORK_START_FAILED: "착공 등록에 실패했습니다.",
            ErrorCode.WORK_COMPLETE_FAILED: "완공 처리에 실패했습니다.",
            ErrorCode.WORK_ALREADY_STARTED: "이미 착공된 작업입니다. 다른 WIP를 사용하세요.",
            ErrorCode.WORK_NOT_FOUND: "작업 정보를 찾을 수 없습니다.",
            ErrorCode.WIP_INVALID: f"잘못된 WIP ID 형식입니다: {wip_id}",
            ErrorCode.PROCESS_SEQUENCE_ERROR: "이전 공정이 완료되지 않았습니다.",
        }

        super().__init__(
            message=message,
            code=code,
            user_message=user_messages.get(code, message),
            details={
                "wip_id": wip_id,
                "operation": operation
            } if wip_id else {"operation": operation},
            cause=cause
        )


class ValidationError(NeuroHubError):
    """
    Raised when input validation fails.

    Examples:
    - Invalid WIP ID format
    - Invalid process number
    - Missing required fields
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        cause: Optional[Exception] = None
    ):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)

        user_message = f"입력 데이터가 올바르지 않습니다: {message}"
        if field:
            user_message = f"'{field}' 값이 올바르지 않습니다: {message}"

        super().__init__(
            message=message,
            code=ErrorCode.VALIDATION,
            user_message=user_message,
            details=details,
            cause=cause
        )


class EquipmentError(NeuroHubError):
    """
    Raised when equipment communication fails.

    Examples:
    - TCP connection failed
    - Invalid measurement data
    - Equipment timeout
    """

    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.EQUIPMENT_CONNECTION,
        equipment_id: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        user_messages = {
            ErrorCode.EQUIPMENT_CONNECTION: "설비 연결에 실패했습니다.",
            ErrorCode.EQUIPMENT_TIMEOUT: "설비 응답 시간이 초과되었습니다.",
            ErrorCode.EQUIPMENT_INVALID_DATA: "설비로부터 잘못된 데이터를 수신했습니다.",
        }

        super().__init__(
            message=message,
            code=code,
            user_message=user_messages.get(code, message),
            details={"equipment_id": equipment_id} if equipment_id else {},
            cause=cause
        )


class FileOperationError(NeuroHubError):
    """
    Raised when file operations fail.

    Examples:
    - JSON file not found
    - JSON parse error
    - File write failure
    """

    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.FILE_NOT_FOUND,
        file_path: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        user_messages = {
            ErrorCode.FILE_NOT_FOUND: "파일을 찾을 수 없습니다.",
            ErrorCode.FILE_PARSE_ERROR: "파일 형식이 올바르지 않습니다.",
            ErrorCode.FILE_WRITE_ERROR: "파일 저장에 실패했습니다.",
        }

        super().__init__(
            message=message,
            code=code,
            user_message=user_messages.get(code, message),
            details={"file_path": file_path} if file_path else {},
            cause=cause
        )


class ConfigurationError(NeuroHubError):
    """
    Raised when configuration is invalid or missing.

    Examples:
    - Missing required config key
    - Invalid config value
    - Config file not found
    """

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        user_message = "설정 오류가 발생했습니다. 관리자에게 문의하세요."
        if config_key:
            user_message = f"설정 '{config_key}'이(가) 올바르지 않습니다."

        super().__init__(
            message=message,
            code=ErrorCode.CONFIGURATION,
            user_message=user_message,
            details={"config_key": config_key} if config_key else {},
            cause=cause
        )


def convert_requests_error(error: Exception, operation: str = "") -> NeuroHubError:
    """
    Convert requests library exceptions to NeuroHubError types.

    Args:
        error: Original exception from requests library
        operation: Description of the operation being performed

    Returns:
        Appropriate NeuroHubError subclass
    """
    from requests.exceptions import (
        ConnectionError as RequestsConnectionError,
        Timeout as RequestsTimeout,
        HTTPError as RequestsHTTPError
    )

    error_str = str(error).lower()

    if isinstance(error, RequestsConnectionError):
        return ConnectionError(
            message=f"연결 실패 ({operation}): {error}",
            cause=error
        )

    if isinstance(error, RequestsTimeout):
        return TimeoutError(
            message=f"요청 시간 초과 ({operation}): {error}",
            operation=operation,
            cause=error
        )

    if isinstance(error, RequestsHTTPError):
        status_code = getattr(error.response, 'status_code', None) if hasattr(error, 'response') else None

        if status_code == 401:
            return AuthenticationError(
                message=f"인증 실패 ({operation})",
                code=ErrorCode.AUTH_FAILED,
                cause=error
            )

        if status_code == 403:
            return AuthenticationError(
                message=f"권한 없음 ({operation})",
                code=ErrorCode.PERMISSION_DENIED,
                cause=error
            )

        if status_code == 409:
            return WorkOperationError(
                message=f"중복 작업 ({operation})",
                code=ErrorCode.WORK_ALREADY_STARTED,
                cause=error
            )

        return NeuroHubError(
            message=f"HTTP 오류 ({operation}): {error}",
            code=ErrorCode.UNKNOWN,
            user_message=f"서버 오류가 발생했습니다 (HTTP {status_code})",
            cause=error
        )

    # Generic fallback
    return NeuroHubError(
        message=f"예외 발생 ({operation}): {error}",
        code=ErrorCode.UNKNOWN,
        cause=error
    )
