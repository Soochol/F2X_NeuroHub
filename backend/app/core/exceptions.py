"""
커스텀 애플리케이션 예외 정의

이 모듈은 애플리케이션에서 사용되는 커스텀 예외 클래스들을 정의합니다.
모든 예외는 AppException을 상속하여 일관된 에러 처리를 보장합니다.
"""

from typing import Optional, List, Any
from datetime import datetime
import uuid

from app.schemas.error import ErrorCode, ErrorDetail


class AppException(Exception):
    """
    애플리케이션 공통 예외 기본 클래스

    모든 커스텀 예외는 이 클래스를 상속해야 합니다.
    글로벌 exception handler가 이 예외를 인식하여
    표준 에러 응답으로 변환합니다.
    """

    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        details: Optional[List[ErrorDetail]] = None,
        trace_id: Optional[str] = None,
    ):
        """
        Args:
            error_code: 표준 에러 코드
            message: 사용자 친화적 에러 메시지
            details: 필드별 상세 에러 (주로 validation)
            trace_id: 디버깅용 추적 ID (자동 생성됨)
        """
        self.error_code = error_code
        self.message = message
        self.details = details
        self.trace_id = trace_id or str(uuid.uuid4())
        self.timestamp = datetime.utcnow().isoformat()
        super().__init__(message)


# ============================================================================
# Authentication & Authorization Exceptions
# ============================================================================


class UnauthorizedException(AppException):
    """인증되지 않은 요청"""

    def __init__(self, message: str = "Authentication required", headers: dict = None):
        super().__init__(
            error_code=ErrorCode.UNAUTHORIZED,
            message=message,
        )
        self.headers = headers or {}


class InvalidTokenException(AppException):
    """유효하지 않은 토큰"""

    def __init__(self, message: str = "Invalid authentication token"):
        super().__init__(
            error_code=ErrorCode.INVALID_TOKEN,
            message=message,
        )


class TokenExpiredException(AppException):
    """만료된 토큰"""

    def __init__(self, message: str = "Authentication token has expired"):
        super().__init__(
            error_code=ErrorCode.TOKEN_EXPIRED,
            message=message,
        )


class InsufficientPermissionsException(AppException):
    """권한 부족"""

    def __init__(self, message: str = "Insufficient permissions for this operation"):
        super().__init__(
            error_code=ErrorCode.INSUFFICIENT_PERMISSIONS,
            message=message,
        )


# ============================================================================
# Resource Exceptions
# ============================================================================


class ResourceNotFoundException(AppException):
    """리소스를 찾을 수 없음"""

    def __init__(self, resource_type: str, resource_id: Any):
        super().__init__(
            error_code=ErrorCode.RESOURCE_NOT_FOUND,
            message=f"{resource_type} with ID {resource_id} not found",
        )


class LotNotFoundException(AppException):
    """Lot을 찾을 수 없음"""

    def __init__(self, lot_id: Any):
        super().__init__(
            error_code=ErrorCode.LOT_NOT_FOUND,
            message=f"Lot with ID {lot_id} not found",
        )


class SerialNotFoundException(AppException):
    """Serial을 찾을 수 없음"""

    def __init__(self, serial_id: Any):
        super().__init__(
            error_code=ErrorCode.SERIAL_NOT_FOUND,
            message=f"Serial with ID {serial_id} not found",
        )


class WIPItemNotFoundException(AppException):
    """WIP Item을 찾을 수 없음"""

    def __init__(self, wip_id: Any):
        super().__init__(
            error_code=ErrorCode.RESOURCE_NOT_FOUND,
            message=f"WIP Item with ID {wip_id} not found",
        )


class ProcessNotFoundException(AppException):
    """Process를 찾을 수 없음"""

    def __init__(self, process_id: Any):
        super().__init__(
            error_code=ErrorCode.PROCESS_NOT_FOUND,
            message=f"Process with ID {process_id} not found",
        )


class EquipmentNotFoundException(AppException):
    """Equipment를 찾을 수 없음"""

    def __init__(self, equipment_id: Any):
        super().__init__(
            error_code=ErrorCode.EQUIPMENT_NOT_FOUND,
            message=f"Equipment with ID {equipment_id} not found",
        )


class UserNotFoundException(AppException):
    """User를 찾을 수 없음"""

    def __init__(self, user_id: Any):
        super().__init__(
            error_code=ErrorCode.USER_NOT_FOUND,
            message=f"User with ID {user_id} not found",
        )


class ProductModelNotFoundException(AppException):
    """Product Model을 찾을 수 없음"""

    def __init__(self, model_id: Any):
        super().__init__(
            error_code=ErrorCode.PRODUCT_MODEL_NOT_FOUND,
            message=f"Product model with ID {model_id} not found",
        )


class ProductionLineNotFoundException(AppException):
    """Production Line을 찾을 수 없음"""

    def __init__(self, line_id: Any):
        super().__init__(
            error_code=ErrorCode.PRODUCTION_LINE_NOT_FOUND,
            message=f"Production line with ID {line_id} not found",
        )


class AlertNotFoundException(AppException):
    """Alert를 찾을 수 없음"""

    def __init__(self, alert_id: Any):
        super().__init__(
            error_code=ErrorCode.ALERT_NOT_FOUND,
            message=f"Alert with ID {alert_id} not found",
        )


class AuditLogNotFoundException(AppException):
    """Audit Log를 찾을 수 없음"""

    def __init__(self, audit_log_id: Any):
        super().__init__(
            error_code=ErrorCode.AUDIT_LOG_NOT_FOUND,
            message=f"Audit log with ID {audit_log_id} not found",
        )


# ============================================================================
# Validation Exceptions
# ============================================================================


class ValidationException(AppException):
    """데이터 검증 실패"""

    def __init__(
        self,
        message: str = "Request validation failed",
        details: Optional[List[ErrorDetail]] = None,
    ):
        super().__init__(
            error_code=ErrorCode.VALIDATION_ERROR,
            message=message,
            details=details,
        )


class MissingRequiredFieldException(AppException):
    """필수 필드 누락"""

    def __init__(self, field_name: str):
        super().__init__(
            error_code=ErrorCode.MISSING_REQUIRED_FIELD,
            message=f"Required field '{field_name}' is missing",
            details=[
                ErrorDetail(
                    field=field_name,
                    message="This field is required",
                    code="missing",
                )
            ],
        )


class InvalidDataFormatException(AppException):
    """잘못된 데이터 형식"""

    def __init__(self, field_name: str, expected_format: str):
        super().__init__(
            error_code=ErrorCode.INVALID_DATA_FORMAT,
            message=f"Invalid format for field '{field_name}'. Expected: {expected_format}",
            details=[
                ErrorDetail(
                    field=field_name,
                    message=f"Expected format: {expected_format}",
                    code="invalid_format",
                )
            ],
        )


class BusinessRuleException(AppException):
    """비즈니스 규칙 위반"""

    def __init__(self, message: str, details: Optional[List[ErrorDetail]] = None):
        super().__init__(
            error_code=ErrorCode.BUSINESS_RULE_VIOLATION,
            message=message,
            details=details,
        )


class InvalidProcessSequenceException(AppException):
    """공정 순서 위반"""

    def __init__(self, message: str):
        super().__init__(
            error_code=ErrorCode.INVALID_PROCESS_SEQUENCE,
            message=message,
        )


class InvalidDataLevelException(AppException):
    """잘못된 데이터 레벨"""

    def __init__(self, message: str):
        super().__init__(
            error_code=ErrorCode.INVALID_DATA_LEVEL,
            message=message,
        )


# ============================================================================
# Conflict Exceptions
# ============================================================================


class DuplicateResourceException(AppException):
    """중복 리소스"""

    def __init__(self, resource_type: str, identifier: str):
        super().__init__(
            error_code=ErrorCode.DUPLICATE_RESOURCE,
            message=f"{resource_type} with {identifier} already exists",
        )


class ConstraintViolationException(AppException):
    """데이터베이스 제약 조건 위반"""

    def __init__(self, message: str = "Database constraint violation"):
        super().__init__(
            error_code=ErrorCode.CONSTRAINT_VIOLATION,
            message=message,
        )


class StateConflictException(AppException):
    """리소스 상태 충돌"""

    def __init__(self, message: str):
        super().__init__(
            error_code=ErrorCode.STATE_CONFLICT,
            message=message,
        )


class ConcurrentModificationException(AppException):
    """동시 수정 감지"""

    def __init__(self, resource_type: str, resource_id: Any):
        super().__init__(
            error_code=ErrorCode.CONCURRENT_MODIFICATION,
            message=f"{resource_type} with ID {resource_id} was modified by another user",
        )


# ============================================================================
# Server Exceptions
# ============================================================================


class InternalServerException(AppException):
    """내부 서버 오류"""

    def __init__(self, message: str = "Internal server error", trace_id: Optional[str] = None):
        super().__init__(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message=message,
            trace_id=trace_id,
        )


class DatabaseException(AppException):
    """데이터베이스 오류"""

    def __init__(self, message: str = "Database operation failed", trace_id: Optional[str] = None):
        super().__init__(
            error_code=ErrorCode.DATABASE_ERROR,
            message=message,
            trace_id=trace_id,
        )


class ExternalServiceException(AppException):
    """외부 서비스 오류"""

    def __init__(self, service_name: str, message: str = "External service error"):
        super().__init__(
            error_code=ErrorCode.EXTERNAL_SERVICE_ERROR,
            message=f"{service_name}: {message}",
        )


class ConfigurationException(AppException):
    """설정 오류"""

    def __init__(self, message: str = "Server configuration error"):
        super().__init__(
            error_code=ErrorCode.CONFIGURATION_ERROR,
            message=message,
        )
