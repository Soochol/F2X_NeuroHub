/**
 * Logs API endpoints.
 */

import type { PaginatedResponse, PaginatedData, LogEntry, LogLevel } from '../../types';
import apiClient from '../client';

/**
 * Query parameters for logs list.
 */
export interface LogsQueryParams {
  batchId?: string;
  level?: LogLevel;
  from?: string;
  to?: string;
  search?: string;
  limit?: number;
  offset?: number;
}

/**
 * Get logs with filtering and pagination.
 */
export async function getLogs(params?: LogsQueryParams): Promise<PaginatedData<LogEntry>> {
  const response = await apiClient.get<PaginatedResponse<LogEntry>>('/logs', {
    params,
  });
  return response.data.data;
}
