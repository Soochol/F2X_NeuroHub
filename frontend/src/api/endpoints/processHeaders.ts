/**
 * Process Headers API Client
 *
 * API endpoints for process header (execution session) management.
 * Used for quality analysis filtering by batch/execution session.
 */

import apiClient from '../client';
import type {
  ProcessHeaderListResponse,
  ProcessHeaderFilter,
} from '@/types/api';
import { HeaderStatus } from '@/types/api';

export const processHeadersApi = {
  /**
   * Get process headers with filtering and pagination.
   *
   * @param filters - Optional filters for station, batch, process, status, date range
   * @returns Paginated list of process header summaries
   */
  getHeaders: async (
    filters?: ProcessHeaderFilter
  ): Promise<ProcessHeaderListResponse> => {
    const params: Record<string, any> = {};

    if (filters?.station_id) params.station_id = filters.station_id;
    if (filters?.batch_id) params.batch_id = filters.batch_id;
    if (filters?.process_id) params.process_id = filters.process_id;
    if (filters?.status) params.status = filters.status;
    if (filters?.opened_after) params.opened_after = filters.opened_after;
    if (filters?.opened_before) params.opened_before = filters.opened_before;
    if (filters?.skip !== undefined) params.skip = filters.skip;
    if (filters?.limit !== undefined) params.limit = filters.limit;

    const response = await apiClient.get<ProcessHeaderListResponse>(
      '/process-headers/',
      { params }
    );
    return response.data;
  },

  /**
   * Get closed headers for filter dropdown (most common use case).
   *
   * @param processId - Optional filter by process ID
   * @param limit - Maximum number of headers to return (default: 100)
   * @returns List of closed process header summaries
   */
  getClosedHeaders: async (
    processId?: number,
    limit: number = 100
  ): Promise<ProcessHeaderListResponse> => {
    const params: Record<string, any> = {
      status: HeaderStatus.CLOSED,
      limit,
    };

    if (processId) params.process_id = processId;

    const response = await apiClient.get<ProcessHeaderListResponse>(
      '/process-headers/',
      { params }
    );
    return response.data;
  },
};
