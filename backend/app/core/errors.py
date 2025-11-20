"""
에러 코드 매핑 및 유틸리티

이 모듈은 에러 코드를 HTTP 상태 코드로 매핑하고
에러 처리에 필요한 유틸리티 함수를 제공합니다.
"""

from typing import Dict
from fastapi import status

from app.schemas.error import ErrorCode


# ============================================================================
# 에러 코드 → HTTP 상태 코드 매핑
# ============================================================================

ERROR_CODE_TO_HTTP_STATUS: Dict[ErrorCode, int] = {
    # 401 Unauthorized
    ErrorCode.UNAUTHORIZED: status.HTTP_401_UNAUTHORIZED,
    ErrorCode.INVALID_TOKEN: status.HTTP_401_UNAUTHORIZED,
    ErrorCode.TOKEN_EXPIRED: status.HTTP_401_UNAUTHORIZED,

    # 403 Forbidden
    ErrorCode.INSUFFICIENT_PERMISSIONS: status.HTTP_403_FORBIDDEN,

    # 404 Not Found
    ErrorCode.RESOURCE_NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ErrorCode.LOT_NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ErrorCode.SERIAL_NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ErrorCode.PROCESS_NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ErrorCode.EQUIPMENT_NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ErrorCode.USER_NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ErrorCode.PRODUCT_MODEL_NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ErrorCode.PRODUCTION_LINE_NOT_FOUND: status.HTTP_404_NOT_FOUND,

    # 400 Bad Request
    ErrorCode.VALIDATION_ERROR: status.HTTP_400_BAD_REQUEST,
    ErrorCode.MISSING_REQUIRED_FIELD: status.HTTP_400_BAD_REQUEST,
    ErrorCode.INVALID_DATA_FORMAT: status.HTTP_400_BAD_REQUEST,
    ErrorCode.BUSINESS_RULE_VIOLATION: status.HTTP_400_BAD_REQUEST,
    ErrorCode.INVALID_PROCESS_SEQUENCE: status.HTTP_400_BAD_REQUEST,
    ErrorCode.INVALID_DATA_LEVEL: status.HTTP_400_BAD_REQUEST,

    # 409 Conflict
    ErrorCode.DUPLICATE_RESOURCE: status.HTTP_409_CONFLICT,
    ErrorCode.CONSTRAINT_VIOLATION: status.HTTP_409_CONFLICT,
    ErrorCode.STATE_CONFLICT: status.HTTP_409_CONFLICT,
    ErrorCode.CONCURRENT_MODIFICATION: status.HTTP_409_CONFLICT,

    # 500 Internal Server Error
    ErrorCode.INTERNAL_SERVER_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ErrorCode.DATABASE_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ErrorCode.EXTERNAL_SERVICE_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ErrorCode.CONFIGURATION_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
}


def get_http_status_for_error_code(error_code: ErrorCode) -> int:
    """
    에러 코드에 해당하는 HTTP 상태 코드 반환

    Args:
        error_code: 에러 코드

    Returns:
        HTTP 상태 코드 (매핑이 없으면 500)
    """
    return ERROR_CODE_TO_HTTP_STATUS.get(
        error_code,
        status.HTTP_500_INTERNAL_SERVER_ERROR
    )


# ============================================================================
# 에러 분류 헬퍼 함수
# ============================================================================

def is_client_error(error_code: ErrorCode) -> bool:
    """
    클라이언트 에러인지 확인 (4xx)

    Args:
        error_code: 에러 코드

    Returns:
        클라이언트 에러이면 True
    """
    http_status = get_http_status_for_error_code(error_code)
    return 400 <= http_status < 500


def is_server_error(error_code: ErrorCode) -> bool:
    """
    서버 에러인지 확인 (5xx)

    Args:
        error_code: 에러 코드

    Returns:
        서버 에러이면 True
    """
    http_status = get_http_status_for_error_code(error_code)
    return http_status >= 500


def is_authentication_error(error_code: ErrorCode) -> bool:
    """
    인증 에러인지 확인

    Args:
        error_code: 에러 코드

    Returns:
        인증 에러이면 True
    """
    return error_code in {
        ErrorCode.UNAUTHORIZED,
        ErrorCode.INVALID_TOKEN,
        ErrorCode.TOKEN_EXPIRED,
    }


def is_authorization_error(error_code: ErrorCode) -> bool:
    """
    권한 에러인지 확인

    Args:
        error_code: 에러 코드

    Returns:
        권한 에러이면 True
    """
    return error_code == ErrorCode.INSUFFICIENT_PERMISSIONS


def is_not_found_error(error_code: ErrorCode) -> bool:
    """
    리소스 Not Found 에러인지 확인

    Args:
        error_code: 에러 코드

    Returns:
        Not Found 에러이면 True
    """
    return error_code in {
        ErrorCode.RESOURCE_NOT_FOUND,
        ErrorCode.LOT_NOT_FOUND,
        ErrorCode.SERIAL_NOT_FOUND,
        ErrorCode.PROCESS_NOT_FOUND,
        ErrorCode.EQUIPMENT_NOT_FOUND,
        ErrorCode.USER_NOT_FOUND,
        ErrorCode.PRODUCT_MODEL_NOT_FOUND,
        ErrorCode.PRODUCTION_LINE_NOT_FOUND,
    }


def is_validation_error(error_code: ErrorCode) -> bool:
    """
    검증 에러인지 확인

    Args:
        error_code: 에러 코드

    Returns:
        검증 에러이면 True
    """
    return error_code in {
        ErrorCode.VALIDATION_ERROR,
        ErrorCode.MISSING_REQUIRED_FIELD,
        ErrorCode.INVALID_DATA_FORMAT,
        ErrorCode.BUSINESS_RULE_VIOLATION,
        ErrorCode.INVALID_PROCESS_SEQUENCE,
        ErrorCode.INVALID_DATA_LEVEL,
    }


def is_conflict_error(error_code: ErrorCode) -> bool:
    """
    충돌 에러인지 확인

    Args:
        error_code: 에러 코드

    Returns:
        충돌 에러이면 True
    """
    return error_code in {
        ErrorCode.DUPLICATE_RESOURCE,
        ErrorCode.CONSTRAINT_VIOLATION,
        ErrorCode.STATE_CONFLICT,
        ErrorCode.CONCURRENT_MODIFICATION,
    }
