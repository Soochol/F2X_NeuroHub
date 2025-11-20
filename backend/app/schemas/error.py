"""
표준 에러 응답 스키마 정의

이 모듈은 API 에러 응답의 표준 포맷을 정의합니다.
모든 에러는 일관된 구조로 클라이언트에 전달됩니다.
"""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class ErrorCode(str, Enum):
    """
    표준 에러 코드 정의

    명명 규칙:
    - AUTH_xxx: 인증/인가 관련 (1xxx)
    - RES_xxx: 리소스 관련 (2xxx)
    - VAL_xxx: 검증 관련 (3xxx)
    - CONF_xxx: 충돌 관련 (4xxx)
    - SRV_xxx: 서버 관련 (5xxx)
    """

    # Authentication & Authorization (1xxx)
    UNAUTHORIZED = "AUTH_001"
    INVALID_TOKEN = "AUTH_002"
    TOKEN_EXPIRED = "AUTH_003"
    INSUFFICIENT_PERMISSIONS = "AUTH_004"

    # Resource Errors (2xxx)
    RESOURCE_NOT_FOUND = "RES_001"
    LOT_NOT_FOUND = "RES_002"
    SERIAL_NOT_FOUND = "RES_003"
    PROCESS_NOT_FOUND = "RES_004"
    EQUIPMENT_NOT_FOUND = "RES_005"
    USER_NOT_FOUND = "RES_006"
    PRODUCT_MODEL_NOT_FOUND = "RES_007"
    PRODUCTION_LINE_NOT_FOUND = "RES_008"

    # Validation Errors (3xxx)
    VALIDATION_ERROR = "VAL_001"
    MISSING_REQUIRED_FIELD = "VAL_002"
    INVALID_DATA_FORMAT = "VAL_003"
    BUSINESS_RULE_VIOLATION = "VAL_004"
    INVALID_PROCESS_SEQUENCE = "VAL_005"
    INVALID_DATA_LEVEL = "VAL_006"

    # Conflict Errors (4xxx)
    DUPLICATE_RESOURCE = "CONF_001"
    CONSTRAINT_VIOLATION = "CONF_002"
    STATE_CONFLICT = "CONF_003"
    CONCURRENT_MODIFICATION = "CONF_004"

    # Server Errors (5xxx)
    INTERNAL_SERVER_ERROR = "SRV_001"
    DATABASE_ERROR = "SRV_002"
    EXTERNAL_SERVICE_ERROR = "SRV_003"
    CONFIGURATION_ERROR = "SRV_004"


class ErrorDetail(BaseModel):
    """
    개별 필드 에러 상세 정보

    주로 validation 에러에서 사용되며, 어떤 필드에서
    어떤 문제가 발생했는지 구체적으로 알려줍니다.
    """
    field: str = Field(..., description="에러가 발생한 필드명")
    message: str = Field(..., description="에러 메시지")
    code: Optional[str] = Field(None, description="에러 타입 코드 (예: 'missing', 'invalid')")

    class Config:
        json_schema_extra = {
            "example": {
                "field": "serial_id",
                "message": "This field is required",
                "code": "missing"
            }
        }


class StandardErrorResponse(BaseModel):
    """
    표준 에러 응답 포맷

    모든 API 에러는 이 형식으로 반환됩니다.
    클라이언트는 error_code를 기반으로 에러를 처리할 수 있습니다.
    """
    error_code: ErrorCode = Field(..., description="표준 에러 코드")
    message: str = Field(..., description="사용자 친화적 에러 메시지")
    details: Optional[List[ErrorDetail]] = Field(
        None,
        description="필드별 상세 에러 정보 (주로 validation 에러)"
    )
    timestamp: str = Field(..., description="에러 발생 시각 (ISO 8601)")
    path: Optional[str] = Field(None, description="에러가 발생한 API 경로")
    trace_id: Optional[str] = Field(
        None,
        description="디버깅용 추적 ID (서버 로그와 연결)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "error_code": "RES_002",
                "message": "Lot with ID 123 not found",
                "timestamp": "2025-11-20T10:30:00Z",
                "path": "/api/v1/lots/123",
                "trace_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
            }
        }


# 에러 메시지 템플릿 (다국어 지원 준비)
ERROR_MESSAGES = {
    # Authentication
    ErrorCode.UNAUTHORIZED: "Authentication required",
    ErrorCode.INVALID_TOKEN: "Invalid authentication token",
    ErrorCode.TOKEN_EXPIRED: "Authentication token has expired",
    ErrorCode.INSUFFICIENT_PERMISSIONS: "Insufficient permissions for this operation",

    # Resources
    ErrorCode.RESOURCE_NOT_FOUND: "Requested resource not found",
    ErrorCode.LOT_NOT_FOUND: "Lot not found",
    ErrorCode.SERIAL_NOT_FOUND: "Serial not found",
    ErrorCode.PROCESS_NOT_FOUND: "Process not found",
    ErrorCode.EQUIPMENT_NOT_FOUND: "Equipment not found",
    ErrorCode.USER_NOT_FOUND: "User not found",
    ErrorCode.PRODUCT_MODEL_NOT_FOUND: "Product model not found",
    ErrorCode.PRODUCTION_LINE_NOT_FOUND: "Production line not found",

    # Validation
    ErrorCode.VALIDATION_ERROR: "Request validation failed",
    ErrorCode.MISSING_REQUIRED_FIELD: "Required field is missing",
    ErrorCode.INVALID_DATA_FORMAT: "Invalid data format",
    ErrorCode.BUSINESS_RULE_VIOLATION: "Business rule violation",
    ErrorCode.INVALID_PROCESS_SEQUENCE: "Invalid process sequence",
    ErrorCode.INVALID_DATA_LEVEL: "Invalid data level",

    # Conflicts
    ErrorCode.DUPLICATE_RESOURCE: "Resource already exists",
    ErrorCode.CONSTRAINT_VIOLATION: "Database constraint violation",
    ErrorCode.STATE_CONFLICT: "Resource state conflict",
    ErrorCode.CONCURRENT_MODIFICATION: "Concurrent modification detected",

    # Server
    ErrorCode.INTERNAL_SERVER_ERROR: "Internal server error",
    ErrorCode.DATABASE_ERROR: "Database operation failed",
    ErrorCode.EXTERNAL_SERVICE_ERROR: "External service error",
    ErrorCode.CONFIGURATION_ERROR: "Server configuration error",
}
