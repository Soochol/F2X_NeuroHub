/**
 * F2X NeuroHub MES - API Client Configuration
 *
 * Axios instance with interceptors for authentication and error handling
 */

import axios, { type AxiosError, type AxiosResponse, type InternalAxiosRequestConfig } from 'axios';
import type { APIError } from '@/types/api';
import {
  type StandardErrorResponse,
  ErrorCode,
  ERROR_MESSAGES_KO,
  ERROR_ACTION_SUGGESTIONS,
} from '@/types/error';
import { toast, notify } from '@/utils/toast';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_VERSION = import.meta.env.VITE_API_VERSION || 'v1';

// Create axios instance
export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/${API_VERSION}`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * 표준 에러 응답 처리
 *
 * 백엔드의 StandardErrorResponse 형식을 처리합니다.
 */
function handleStandardError(
  errorResponse: StandardErrorResponse,
  statusCode: number
): void {
  const { error_code, message, details, trace_id } = errorResponse;

  console.error('API Error:', {
    code: error_code,
    message,
    details,
    trace_id,
    status: statusCode,
  });

  // 에러 코드별 특별 처리
  switch (error_code) {
    // 인증 에러 - 자동 로그아웃
    case ErrorCode.UNAUTHORIZED:
    case ErrorCode.INVALID_TOKEN:
    case ErrorCode.TOKEN_EXPIRED:
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      toast.warning(ERROR_MESSAGES_KO[error_code]);
      setTimeout(() => {
        window.location.href = '/login';
      }, 1000);
      break;

    // 권한 에러
    case ErrorCode.INSUFFICIENT_PERMISSIONS:
      notify.error({
        title: ERROR_MESSAGES_KO[error_code],
        description: ERROR_ACTION_SUGGESTIONS[error_code] || message,
      });
      break;

    // 검증 에러 - 필드별 상세 표시
    case ErrorCode.VALIDATION_ERROR:
    case ErrorCode.MISSING_REQUIRED_FIELD:
    case ErrorCode.INVALID_DATA_FORMAT:
      if (details && details.length > 0) {
        const fieldErrors = details.map((d) => `• ${d.field}: ${d.message}`).join('\n');
        notify.error({
          title: ERROR_MESSAGES_KO[error_code],
          description: fieldErrors,
        });
      } else {
        toast.error(ERROR_MESSAGES_KO[error_code] || message);
      }
      break;

    // 비즈니스 규칙 위반
    case ErrorCode.BUSINESS_RULE_VIOLATION:
    case ErrorCode.INVALID_PROCESS_SEQUENCE:
    case ErrorCode.INVALID_DATA_LEVEL:
      notify.error({
        title: ERROR_MESSAGES_KO[error_code],
        description: message,
      });
      break;

    // 리소스 Not Found 에러
    case ErrorCode.LOT_NOT_FOUND:
    case ErrorCode.SERIAL_NOT_FOUND:
    case ErrorCode.PROCESS_NOT_FOUND:
    case ErrorCode.EQUIPMENT_NOT_FOUND:
    case ErrorCode.RESOURCE_NOT_FOUND:
    case ErrorCode.USER_NOT_FOUND:
    case ErrorCode.PRODUCT_MODEL_NOT_FOUND:
    case ErrorCode.PRODUCTION_LINE_NOT_FOUND:
      toast.error(ERROR_MESSAGES_KO[error_code] || message);
      break;

    // 충돌 에러
    case ErrorCode.DUPLICATE_RESOURCE:
    case ErrorCode.CONSTRAINT_VIOLATION:
    case ErrorCode.STATE_CONFLICT:
    case ErrorCode.CONCURRENT_MODIFICATION:
      notify.warning({
        title: ERROR_MESSAGES_KO[error_code],
        description: message,
      });
      break;

    // 서버 에러 - trace_id 포함
    case ErrorCode.DATABASE_ERROR:
    case ErrorCode.INTERNAL_SERVER_ERROR:
    case ErrorCode.EXTERNAL_SERVICE_ERROR:
    case ErrorCode.CONFIGURATION_ERROR:
      notify.error({
        title: ERROR_MESSAGES_KO[error_code],
        description: trace_id
          ? `문제가 지속되면 관리자에게 문의하세요\n(추적 ID: ${trace_id.substring(0, 8)}...)`
          : ERROR_ACTION_SUGGESTIONS[error_code] || '잠시 후 다시 시도해주세요',
      });
      console.error(`[Trace ID: ${trace_id}]`, message);
      break;

    // 알 수 없는 에러 코드
    default:
      toast.error(message || '알 수 없는 오류가 발생했습니다');
  }
}

/**
 * 레거시 에러 처리 (하위 호환성)
 *
 * 표준 포맷이 아닌 기존 에러 응답을 처리합니다.
 */
function handleLegacyError(error: AxiosError<APIError>): void {
  const statusCode = error.response?.status;
  const message = error.response?.data?.detail || error.message || '오류가 발생했습니다';

  console.warn('Legacy error format detected:', { statusCode, message });

  if (statusCode === 401) {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    toast.warning('세션이 만료되었습니다');
    setTimeout(() => {
      window.location.href = '/login';
    }, 1000);
  } else if (statusCode && statusCode >= 500) {
    toast.error('서버 오류가 발생했습니다');
  } else {
    toast.error(message);
  }
}

/**
 * 에러 응답이 표준 포맷인지 확인
 */
function isStandardErrorResponse(data: any): data is StandardErrorResponse {
  return (
    data &&
    typeof data === 'object' &&
    'error_code' in data &&
    'message' in data &&
    'timestamp' in data
  );
}

// Response interceptor - Handle errors
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError<StandardErrorResponse | APIError>) => {
    // 네트워크 에러 (응답 없음)
    if (!error.response) {
      toast.error('네트워크 연결을 확인해주세요');
      return Promise.reject(error);
    }

    const errorData = error.response.data;
    const statusCode = error.response.status;
    const requestUrl = error.config?.url;

    // 로그인 요청에서 발생한 401 에러는 인터셉터에서 처리하지 않고 컴포넌트로 넘김
    if (statusCode === 401 && requestUrl?.includes('/auth/login')) {
      return Promise.reject(error);
    }

    // 표준 에러 응답 처리
    if (isStandardErrorResponse(errorData)) {
      handleStandardError(errorData, statusCode);
    }
    // 레거시 에러 응답 처리
    else {
      handleLegacyError(error as AxiosError<APIError>);
    }

    return Promise.reject(error);
  }
);

export default apiClient;
