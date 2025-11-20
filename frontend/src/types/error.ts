/**
 * 표준 에러 타입 정의
 *
 * 백엔드 API의 에러 응답 구조와 동기화된 타입 정의입니다.
 * 모든 에러 코드는 백엔드의 ErrorCode enum과 일치해야 합니다.
 */

/**
 * 표준 에러 코드 enum (백엔드와 동기화)
 *
 * 명명 규칙:
 * - AUTH_xxx: 인증/인가 관련 (1xxx)
 * - RES_xxx: 리소스 관련 (2xxx)
 * - VAL_xxx: 검증 관련 (3xxx)
 * - CONF_xxx: 충돌 관련 (4xxx)
 * - SRV_xxx: 서버 관련 (5xxx)
 */
export enum ErrorCode {
  // Authentication & Authorization (1xxx)
  UNAUTHORIZED = 'AUTH_001',
  INVALID_TOKEN = 'AUTH_002',
  TOKEN_EXPIRED = 'AUTH_003',
  INSUFFICIENT_PERMISSIONS = 'AUTH_004',

  // Resource Errors (2xxx)
  RESOURCE_NOT_FOUND = 'RES_001',
  LOT_NOT_FOUND = 'RES_002',
  SERIAL_NOT_FOUND = 'RES_003',
  PROCESS_NOT_FOUND = 'RES_004',
  EQUIPMENT_NOT_FOUND = 'RES_005',
  USER_NOT_FOUND = 'RES_006',
  PRODUCT_MODEL_NOT_FOUND = 'RES_007',
  PRODUCTION_LINE_NOT_FOUND = 'RES_008',

  // Validation Errors (3xxx)
  VALIDATION_ERROR = 'VAL_001',
  MISSING_REQUIRED_FIELD = 'VAL_002',
  INVALID_DATA_FORMAT = 'VAL_003',
  BUSINESS_RULE_VIOLATION = 'VAL_004',
  INVALID_PROCESS_SEQUENCE = 'VAL_005',
  INVALID_DATA_LEVEL = 'VAL_006',

  // Conflict Errors (4xxx)
  DUPLICATE_RESOURCE = 'CONF_001',
  CONSTRAINT_VIOLATION = 'CONF_002',
  STATE_CONFLICT = 'CONF_003',
  CONCURRENT_MODIFICATION = 'CONF_004',

  // Server Errors (5xxx)
  INTERNAL_SERVER_ERROR = 'SRV_001',
  DATABASE_ERROR = 'SRV_002',
  EXTERNAL_SERVICE_ERROR = 'SRV_003',
  CONFIGURATION_ERROR = 'SRV_004',
}

/**
 * 필드별 에러 상세 정보
 *
 * 주로 validation 에러에서 사용되며, 어떤 필드에서
 * 어떤 문제가 발생했는지 구체적으로 알려줍니다.
 */
export interface ErrorDetail {
  /** 에러가 발생한 필드명 */
  field: string;
  /** 에러 메시지 */
  message: string;
  /** 에러 타입 코드 (예: 'missing', 'invalid') */
  code?: string;
}

/**
 * 표준 에러 응답
 *
 * 백엔드에서 반환하는 모든 에러는 이 형식을 따릅니다.
 */
export interface StandardErrorResponse {
  /** 표준 에러 코드 */
  error_code: ErrorCode;
  /** 사용자 친화적 에러 메시지 */
  message: string;
  /** 필드별 상세 에러 정보 (주로 validation 에러) */
  details?: ErrorDetail[];
  /** 에러 발생 시각 (ISO 8601) */
  timestamp: string;
  /** 에러가 발생한 API 경로 */
  path?: string;
  /** 디버깅용 추적 ID (서버 로그와 연결) */
  trace_id?: string;
}

/**
 * 에러 코드별 한국어 메시지 매핑
 *
 * 백엔드에서 영어 메시지를 반환해도
 * 클라이언트에서 한국어로 표시할 수 있습니다.
 */
export const ERROR_MESSAGES_KO: Record<ErrorCode, string> = {
  // Authentication
  [ErrorCode.UNAUTHORIZED]: '인증이 필요합니다',
  [ErrorCode.INVALID_TOKEN]: '유효하지 않은 토큰입니다',
  [ErrorCode.TOKEN_EXPIRED]: '세션이 만료되었습니다',
  [ErrorCode.INSUFFICIENT_PERMISSIONS]: '권한이 부족합니다',

  // Resources
  [ErrorCode.RESOURCE_NOT_FOUND]: '요청한 리소스를 찾을 수 없습니다',
  [ErrorCode.LOT_NOT_FOUND]: '해당 LOT를 찾을 수 없습니다',
  [ErrorCode.SERIAL_NOT_FOUND]: '해당 시리얼을 찾을 수 없습니다',
  [ErrorCode.PROCESS_NOT_FOUND]: '해당 공정을 찾을 수 없습니다',
  [ErrorCode.EQUIPMENT_NOT_FOUND]: '해당 설비를 찾을 수 없습니다',
  [ErrorCode.USER_NOT_FOUND]: '해당 사용자를 찾을 수 없습니다',
  [ErrorCode.PRODUCT_MODEL_NOT_FOUND]: '해당 제품 모델을 찾을 수 없습니다',
  [ErrorCode.PRODUCTION_LINE_NOT_FOUND]: '해당 생산 라인을 찾을 수 없습니다',

  // Validation
  [ErrorCode.VALIDATION_ERROR]: '입력값이 올바르지 않습니다',
  [ErrorCode.MISSING_REQUIRED_FIELD]: '필수 항목이 누락되었습니다',
  [ErrorCode.INVALID_DATA_FORMAT]: '데이터 형식이 올바르지 않습니다',
  [ErrorCode.BUSINESS_RULE_VIOLATION]: '비즈니스 규칙을 위반했습니다',
  [ErrorCode.INVALID_PROCESS_SEQUENCE]: '공정 순서가 올바르지 않습니다',
  [ErrorCode.INVALID_DATA_LEVEL]: '데이터 레벨이 올바르지 않습니다',

  // Conflicts
  [ErrorCode.DUPLICATE_RESOURCE]: '이미 존재하는 리소스입니다',
  [ErrorCode.CONSTRAINT_VIOLATION]: '제약 조건을 위반했습니다',
  [ErrorCode.STATE_CONFLICT]: '상태 충돌이 발생했습니다',
  [ErrorCode.CONCURRENT_MODIFICATION]: '다른 사용자가 수정한 데이터입니다',

  // Server
  [ErrorCode.INTERNAL_SERVER_ERROR]: '서버 오류가 발생했습니다',
  [ErrorCode.DATABASE_ERROR]: '데이터베이스 오류가 발생했습니다',
  [ErrorCode.EXTERNAL_SERVICE_ERROR]: '외부 서비스 오류가 발생했습니다',
  [ErrorCode.CONFIGURATION_ERROR]: '서버 설정 오류가 발생했습니다',
};

/**
 * 에러 심각도 레벨
 */
export enum ErrorSeverity {
  /** 정보성 - 에러는 아니지만 알림 필요 */
  INFO = 'info',
  /** 경고 - 작업은 완료되었지만 주의 필요 */
  WARNING = 'warning',
  /** 에러 - 작업 실패, 사용자 조치 필요 */
  ERROR = 'error',
  /** 치명적 에러 - 시스템 문제, 관리자 개입 필요 */
  CRITICAL = 'critical',
}

/**
 * 에러 코드별 심각도 매핑
 */
export const ERROR_SEVERITY_MAP: Record<ErrorCode, ErrorSeverity> = {
  // Authentication - WARNING/ERROR
  [ErrorCode.UNAUTHORIZED]: ErrorSeverity.WARNING,
  [ErrorCode.INVALID_TOKEN]: ErrorSeverity.WARNING,
  [ErrorCode.TOKEN_EXPIRED]: ErrorSeverity.WARNING,
  [ErrorCode.INSUFFICIENT_PERMISSIONS]: ErrorSeverity.ERROR,

  // Resources - ERROR
  [ErrorCode.RESOURCE_NOT_FOUND]: ErrorSeverity.ERROR,
  [ErrorCode.LOT_NOT_FOUND]: ErrorSeverity.ERROR,
  [ErrorCode.SERIAL_NOT_FOUND]: ErrorSeverity.ERROR,
  [ErrorCode.PROCESS_NOT_FOUND]: ErrorSeverity.ERROR,
  [ErrorCode.EQUIPMENT_NOT_FOUND]: ErrorSeverity.ERROR,
  [ErrorCode.USER_NOT_FOUND]: ErrorSeverity.ERROR,
  [ErrorCode.PRODUCT_MODEL_NOT_FOUND]: ErrorSeverity.ERROR,
  [ErrorCode.PRODUCTION_LINE_NOT_FOUND]: ErrorSeverity.ERROR,

  // Validation - ERROR
  [ErrorCode.VALIDATION_ERROR]: ErrorSeverity.ERROR,
  [ErrorCode.MISSING_REQUIRED_FIELD]: ErrorSeverity.ERROR,
  [ErrorCode.INVALID_DATA_FORMAT]: ErrorSeverity.ERROR,
  [ErrorCode.BUSINESS_RULE_VIOLATION]: ErrorSeverity.ERROR,
  [ErrorCode.INVALID_PROCESS_SEQUENCE]: ErrorSeverity.ERROR,
  [ErrorCode.INVALID_DATA_LEVEL]: ErrorSeverity.ERROR,

  // Conflicts - WARNING
  [ErrorCode.DUPLICATE_RESOURCE]: ErrorSeverity.WARNING,
  [ErrorCode.CONSTRAINT_VIOLATION]: ErrorSeverity.WARNING,
  [ErrorCode.STATE_CONFLICT]: ErrorSeverity.WARNING,
  [ErrorCode.CONCURRENT_MODIFICATION]: ErrorSeverity.WARNING,

  // Server - CRITICAL
  [ErrorCode.INTERNAL_SERVER_ERROR]: ErrorSeverity.CRITICAL,
  [ErrorCode.DATABASE_ERROR]: ErrorSeverity.CRITICAL,
  [ErrorCode.EXTERNAL_SERVICE_ERROR]: ErrorSeverity.CRITICAL,
  [ErrorCode.CONFIGURATION_ERROR]: ErrorSeverity.CRITICAL,
};

/**
 * 에러 코드에 대한 사용자 액션 제안
 */
export const ERROR_ACTION_SUGGESTIONS: Partial<Record<ErrorCode, string>> = {
  [ErrorCode.UNAUTHORIZED]: '로그인 페이지로 이동합니다',
  [ErrorCode.TOKEN_EXPIRED]: '다시 로그인해주세요',
  [ErrorCode.INSUFFICIENT_PERMISSIONS]: '관리자에게 권한을 요청하세요',
  [ErrorCode.LOT_NOT_FOUND]: 'LOT 목록 페이지로 돌아갑니다',
  [ErrorCode.VALIDATION_ERROR]: '입력값을 확인하고 다시 시도해주세요',
  [ErrorCode.DUPLICATE_RESOURCE]: '다른 식별자를 사용해주세요',
  [ErrorCode.DATABASE_ERROR]: '잠시 후 다시 시도해주세요',
  [ErrorCode.INTERNAL_SERVER_ERROR]: '문제가 지속되면 관리자에게 문의하세요',
};
