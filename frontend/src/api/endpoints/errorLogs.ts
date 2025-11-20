/**
 * Error Logs API Client
 *
 * Provides functions for accessing error log data and statistics.
 * Used by ErrorDashboardPage for monitoring and debugging.
 */

import apiClient from '../client';

/**
 * Error log entry from the database
 */
export interface ErrorLog {
  id: number;
  trace_id: string;
  error_code: string;
  message: string;
  path?: string;
  method?: string;
  status_code: number;
  user_id?: number;
  username?: string;
  details?: any;
  timestamp: string;
}

/**
 * Paginated error log list response
 */
export interface ErrorLogListResponse {
  items: ErrorLog[];
  total: number;
  skip: number;
  limit: number;
}

/**
 * Error code distribution item
 */
export interface ErrorCodeCount {
  error_code: string;
  count: number;
}

/**
 * Hourly error count for trend chart
 */
export interface HourlyErrorCount {
  hour: string;
  count: number;
}

/**
 * Top error-prone endpoint
 */
export interface TopErrorPath {
  path: string;
  method: string;
  count: number;
}

/**
 * Comprehensive error statistics for dashboard
 */
export interface ErrorLogStats {
  total_errors: number;
  by_error_code: ErrorCodeCount[];
  by_hour: HourlyErrorCount[];
  top_paths: TopErrorPath[];
}

/**
 * Query parameters for error log filtering
 */
export interface ErrorLogFilters {
  skip?: number;
  limit?: number;
  error_code?: string;
  start_date?: string;
  end_date?: string;
  user_id?: number;
  path?: string;
  method?: string;
  min_status_code?: number;
  max_status_code?: number;
}

/**
 * Error Logs API
 */
export const errorLogsApi = {
  /**
   * Get paginated list of error logs with optional filters
   *
   * @param filters - Query parameters for filtering
   * @returns Paginated error log list
   *
   * @example
   * // Get recent 404 errors
   * const logs = await errorLogsApi.getErrorLogs({
   *   error_code: 'RES_002',
   *   min_status_code: 404,
   *   max_status_code: 404,
   *   limit: 20
   * });
   */
  getErrorLogs: async (filters?: ErrorLogFilters): Promise<ErrorLogListResponse> => {
    const params: Record<string, any> = {};

    if (filters?.skip !== undefined) params.skip = filters.skip;
    if (filters?.limit !== undefined) params.limit = filters.limit;
    if (filters?.error_code) params.error_code = filters.error_code;
    if (filters?.start_date) params.start_date = filters.start_date;
    if (filters?.end_date) params.end_date = filters.end_date;
    if (filters?.user_id !== undefined) params.user_id = filters.user_id;
    if (filters?.path) params.path = filters.path;
    if (filters?.method) params.method = filters.method;
    if (filters?.min_status_code !== undefined) params.min_status_code = filters.min_status_code;
    if (filters?.max_status_code !== undefined) params.max_status_code = filters.max_status_code;

    const response = await apiClient.get<ErrorLogListResponse>('/error-logs/', { params });
    return response.data;
  },

  /**
   * Get error statistics for dashboard visualization
   *
   * @param hours - Time range in hours (default: 24)
   * @returns Error statistics including total count, distribution, trends, and top paths
   *
   * @example
   * // Get last 7 days statistics
   * const stats = await errorLogsApi.getErrorStats(168);
   */
  getErrorStats: async (hours: number = 24): Promise<ErrorLogStats> => {
    const response = await apiClient.get<ErrorLogStats>('/error-logs/stats', {
      params: { hours }
    });
    return response.data;
  },

  /**
   * Get single error log by ID
   *
   * @param id - Error log primary key
   * @returns Error log details
   *
   * @example
   * const errorLog = await errorLogsApi.getErrorById(123);
   */
  getErrorById: async (id: number): Promise<ErrorLog> => {
    const response = await apiClient.get<ErrorLog>(`/error-logs/${id}`);
    return response.data;
  },

  /**
   * Get error log by trace ID (for debugging)
   *
   * Use this to correlate frontend errors with backend logs.
   * The trace_id from StandardErrorResponse can be used here.
   *
   * @param traceId - UUID trace ID from error response
   * @returns Error log details
   *
   * @example
   * // When user reports an error with trace ID
   * const errorLog = await errorLogsApi.getErrorByTraceId('f51de9db-0803-40b8-86b7-7003428fd855');
   */
  getErrorByTraceId: async (traceId: string): Promise<ErrorLog> => {
    const response = await apiClient.get<ErrorLog>(`/error-logs/trace/${traceId}`);
    return response.data;
  },
};
