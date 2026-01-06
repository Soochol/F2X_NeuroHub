/**
 * React Query client configuration.
 */

import { QueryClient, MutationCache } from '@tanstack/react-query';
import { QUERY_OPTIONS } from '../config';
import { toast, getErrorMessage } from '../utils';

/**
 * Error codes for specific handling.
 */
const ERROR_MESSAGES: Record<string, string> = {
  UNAUTHORIZED: 'API 키가 만료되었거나 유효하지 않습니다. 다시 로그인해주세요.',
  NETWORK_ERROR: '네트워크 연결을 확인해주세요.',
  NOT_FOUND: '요청한 리소스를 찾을 수 없습니다.',
  TIMEOUT: '요청 시간이 초과되었습니다.',
  INTERNAL_ERROR: '서버 내부 오류가 발생했습니다.',
};

/**
 * Extract error code from error object.
 */
function extractErrorCode(error: unknown): string | null {
  if (!error || typeof error !== 'object') return null;

  // Axios error with response
  const axiosError = error as { response?: { status?: number; data?: { error?: { code?: string } } } };
  if (axiosError.response?.data?.error?.code) {
    return axiosError.response.data.error.code;
  }

  // HTTP status based codes
  const status = axiosError.response?.status;
  if (status === 401) return 'UNAUTHORIZED';
  if (status === 404) return 'NOT_FOUND';
  if (status === 500) return 'INTERNAL_ERROR';

  // Network error
  const errWithCode = error as { code?: string };
  if (errWithCode.code === 'ERR_NETWORK') return 'NETWORK_ERROR';
  if (errWithCode.code === 'ECONNABORTED') return 'TIMEOUT';

  return null;
}

/**
 * Global mutation error handler.
 * Provides centralized error handling for all mutations.
 */
export function globalMutationErrorHandler(error: unknown): void {
  const errorCode = extractErrorCode(error);
  const message = errorCode && ERROR_MESSAGES[errorCode]
    ? ERROR_MESSAGES[errorCode]
    : getErrorMessage(error);

  toast.error(message);

  // Log for debugging (can be extended for monitoring services)
  console.error('[API Error]', { errorCode, message, error });
}

/**
 * Mutation cache with global error handling.
 */
const mutationCache = new MutationCache({
  onError: (error, _variables, _context, mutation) => {
    // Skip if mutation has its own onError handler
    if (mutation.options.onError) return;

    globalMutationErrorHandler(error);
  },
});

/**
 * Default query options for the application.
 */
const defaultQueryOptions = {
  queries: {
    staleTime: QUERY_OPTIONS.staleTime,
    gcTime: QUERY_OPTIONS.gcTime,
    retry: QUERY_OPTIONS.queryRetry,
    refetchOnWindowFocus: false,
    refetchOnReconnect: true,
  },
  mutations: {
    retry: QUERY_OPTIONS.mutationRetry,
  },
};

/**
 * React Query client instance.
 */
export const queryClient = new QueryClient({
  defaultOptions: defaultQueryOptions,
  mutationCache,
});

/**
 * Query keys for cache management.
 */
export const queryKeys = {
  // System
  systemInfo: ['system', 'info'] as const,
  healthStatus: ['system', 'health'] as const,
  workflowConfig: ['system', 'workflow'] as const,
  operatorSession: ['system', 'operator'] as const,
  backendConfig: ['system', 'backend-config'] as const,

  // Batches
  batches: ['batches'] as const,
  batch: (id: string) => ['batches', id] as const,
  batchStatistics: (id: string) => ['batchStatistics', id] as const,
  allBatchStatistics: ['batchStatistics'] as const,

  // Sequences
  sequences: ['sequences'] as const,
  sequence: (name: string) => ['sequences', name] as const,

  // Results
  results: (params?: Record<string, unknown>) => ['results', params] as const,
  result: (id: string) => ['results', id] as const,

  // Logs
  logs: (params?: Record<string, unknown>) => ['logs', params] as const,
};

export default queryClient;
