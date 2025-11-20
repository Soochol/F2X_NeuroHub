/**
 * 에러 처리 유틸리티 함수
 *
 * 컴포넌트에서 에러를 쉽게 처리할 수 있도록 돕는 헬퍼 함수들입니다.
 */

import { type AxiosError } from 'axios';
import {
  type StandardErrorResponse,
  type ErrorDetail,
  ErrorCode,
  ERROR_MESSAGES_KO,
} from '@/types/error';

/**
 * 에러에서 표준 응답 추출
 *
 * Axios 에러 객체에서 StandardErrorResponse를 추출합니다.
 *
 * @param error - 에러 객체 (unknown)
 * @returns 표준 에러 응답 또는 null
 */
export function getStandardError(error: unknown): StandardErrorResponse | null {
  if (error && typeof error === 'object') {
    const axiosError = error as AxiosError<StandardErrorResponse>;
    const data = axiosError.response?.data;

    // 표준 에러 응답 형식인지 확인
    if (
      data &&
      typeof data === 'object' &&
      'error_code' in data &&
      'message' in data &&
      'timestamp' in data
    ) {
      return data;
    }
  }
  return null;
}

/**
 * 에러 코드 확인
 *
 * 에러가 특정 에러 코드를 가지고 있는지 확인합니다.
 *
 * @param error - 에러 객체
 * @param code - 확인할 에러 코드
 * @returns 에러 코드가 일치하면 true
 */
export function hasErrorCode(error: unknown, code: ErrorCode): boolean {
  const standardError = getStandardError(error);
  return standardError?.error_code === code;
}

/**
 * 여러 에러 코드 중 하나와 일치하는지 확인
 *
 * @param error - 에러 객체
 * @param codes - 확인할 에러 코드 배열
 * @returns 에러 코드가 배열 중 하나와 일치하면 true
 */
export function hasAnyErrorCode(error: unknown, codes: ErrorCode[]): boolean {
  const standardError = getStandardError(error);
  if (!standardError) return false;
  return codes.includes(standardError.error_code);
}

/**
 * 특정 에러 코드 처리
 *
 * 에러 코드별로 다른 핸들러 함수를 실행합니다.
 *
 * @param error - 에러 객체
 * @param handlers - 에러 코드별 핸들러 함수 맵
 * @param defaultHandler - 기본 핸들러 (선택적)
 *
 * @example
 * ```ts
 * try {
 *   await createLot(data);
 * } catch (error) {
 *   handleErrorCode(error, {
 *     [ErrorCode.DUPLICATE_RESOURCE]: () => {
 *       console.log('LOT already exists');
 *     },
 *     [ErrorCode.VALIDATION_ERROR]: () => {
 *       console.log('Invalid input');
 *     },
 *   }, () => {
 *     console.log('Other error');
 *   });
 * }
 * ```
 */
export function handleErrorCode(
  error: unknown,
  handlers: Partial<Record<ErrorCode, () => void>>,
  defaultHandler?: () => void
): void {
  const standardError = getStandardError(error);

  if (standardError?.error_code && handlers[standardError.error_code]) {
    handlers[standardError.error_code]!();
  } else if (defaultHandler) {
    defaultHandler();
  }
}

/**
 * 필드별 에러 메시지 추출
 *
 * Validation 에러에서 필드별 에러 메시지를 객체로 변환합니다.
 *
 * @param error - 에러 객체
 * @returns 필드명을 키로, 에러 메시지를 값으로 하는 객체
 *
 * @example
 * ```ts
 * const fieldErrors = getFieldErrors(error);
 * // { serial_id: "This field is required", lot_id: "Invalid format" }
 * ```
 */
export function getFieldErrors(error: unknown): Record<string, string> {
  const standardError = getStandardError(error);
  const fieldErrors: Record<string, string> = {};

  if (standardError?.details) {
    standardError.details.forEach((detail: ErrorDetail) => {
      fieldErrors[detail.field] = detail.message;
    });
  }

  return fieldErrors;
}

/**
 * 에러 메시지 추출
 *
 * 에러 객체에서 사용자 친화적인 메시지를 추출합니다.
 * 표준 에러 응답이면 한국어 메시지를, 아니면 원본 메시지를 반환합니다.
 *
 * @param error - 에러 객체
 * @param fallback - 폴백 메시지 (기본값: '알 수 없는 오류가 발생했습니다')
 * @returns 에러 메시지
 */
export function getErrorMessage(error: unknown, fallback?: string): string {
  const standardError = getStandardError(error);

  if (standardError) {
    // 한국어 메시지가 있으면 사용
    const koreanMessage = ERROR_MESSAGES_KO[standardError.error_code];
    return koreanMessage || standardError.message;
  }

  // 레거시 에러 형식
  if (error && typeof error === 'object') {
    const axiosError = error as AxiosError<{ detail?: string }>;
    if (axiosError.response?.data?.detail) {
      return axiosError.response.data.detail;
    }
    if (axiosError.message) {
      return axiosError.message;
    }
  }

  return fallback || '알 수 없는 오류가 발생했습니다';
}

/**
 * 에러가 클라이언트 에러(4xx)인지 확인
 *
 * @param error - 에러 객체
 * @returns 클라이언트 에러이면 true
 */
export function isClientError(error: unknown): boolean {
  if (error && typeof error === 'object') {
    const axiosError = error as AxiosError;
    const status = axiosError.response?.status;
    return !!status && status >= 400 && status < 500;
  }
  return false;
}

/**
 * 에러가 서버 에러(5xx)인지 확인
 *
 * @param error - 에러 객체
 * @returns 서버 에러이면 true
 */
export function isServerError(error: unknown): boolean {
  if (error && typeof error === 'object') {
    const axiosError = error as AxiosError;
    const status = axiosError.response?.status;
    return !!status && status >= 500;
  }
  return false;
}

/**
 * 에러가 네트워크 에러인지 확인
 *
 * @param error - 에러 객체
 * @returns 네트워크 에러이면 true
 */
export function isNetworkError(error: unknown): boolean {
  if (error && typeof error === 'object') {
    const axiosError = error as AxiosError;
    return !axiosError.response && !!axiosError.request;
  }
  return false;
}

/**
 * 에러가 타임아웃 에러인지 확인
 *
 * @param error - 에러 객체
 * @returns 타임아웃 에러이면 true
 */
export function isTimeoutError(error: unknown): boolean {
  if (error && typeof error === 'object') {
    const axiosError = error as AxiosError;
    return axiosError.code === 'ECONNABORTED' || axiosError.message.includes('timeout');
  }
  return false;
}

/**
 * 에러 정보를 콘솔에 상세히 출력 (디버깅용)
 *
 * @param error - 에러 객체
 * @param context - 추가 컨텍스트 정보
 */
export function logError(error: unknown, context?: string): void {
  const standardError = getStandardError(error);

  if (standardError) {
    console.group(`🔴 Error${context ? ` - ${context}` : ''}`);
    console.error('Error Code:', standardError.error_code);
    console.error('Message:', standardError.message);
    if (standardError.details) {
      console.error('Details:', standardError.details);
    }
    console.error('Timestamp:', standardError.timestamp);
    console.error('Path:', standardError.path);
    if (standardError.trace_id) {
      console.error('Trace ID:', standardError.trace_id);
    }
    console.groupEnd();
  } else {
    console.error(`🔴 Error${context ? ` - ${context}` : ''}:`, error);
  }
}

/**
 * 에러 상세 정보 포맷팅
 *
 * 필드별 에러를 사용자가 읽기 쉬운 문자열로 변환합니다.
 *
 * @param details - 에러 상세 배열
 * @param format - 포맷 방식 ('list' | 'inline')
 * @returns 포맷된 문자열
 */
export function formatErrorDetails(
  details: ErrorDetail[],
  format: 'list' | 'inline' = 'list'
): string {
  if (!details || details.length === 0) return '';

  if (format === 'list') {
    return details.map((d) => `• ${d.field}: ${d.message}`).join('\n');
  } else {
    return details.map((d) => `${d.field}(${d.message})`).join(', ');
  }
}

/**
 * Trace ID 추출
 *
 * 서버 로그 추적을 위한 trace_id를 추출합니다.
 *
 * @param error - 에러 객체
 * @returns trace_id 또는 null
 */
export function getTraceId(error: unknown): string | null {
  const standardError = getStandardError(error);
  return standardError?.trace_id || null;
}

/**
 * HTTP 상태 코드 추출
 *
 * @param error - 에러 객체
 * @returns HTTP 상태 코드 또는 null
 */
export function getStatusCode(error: unknown): number | null {
  if (error && typeof error === 'object') {
    const axiosError = error as AxiosError;
    return axiosError.response?.status || null;
  }
  return null;
}
