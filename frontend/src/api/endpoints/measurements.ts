/**
 * Measurement History API Client
 *
 * API endpoints for measurement data history and summary statistics.
 * Used by quality management features for analyzing process measurement data.
 */

import apiClient from '../client';
import type {
  MeasurementHistoryFilters,
  MeasurementHistoryListResponse,
  MeasurementSummaryResponse,
  MeasurementCodesResponse,
} from '@/types/api';

export const measurementsApi = {
  /**
   * Get measurement data history with filtering and pagination.
   *
   * @param filters - Optional filters for date range, process, lot, and result
   * @returns Paginated list of measurement history records
   */
  getMeasurementHistory: async (
    filters?: MeasurementHistoryFilters
  ): Promise<MeasurementHistoryListResponse> => {
    const params: Record<string, any> = {};

    if (filters?.start_date) params.start_date = filters.start_date;
    if (filters?.end_date) params.end_date = filters.end_date;
    if (filters?.process_id) params.process_id = filters.process_id;
    if (filters?.lot_id) params.lot_id = filters.lot_id;
    if (filters?.result) params.result = filters.result;
    if (filters?.skip !== undefined) params.skip = filters.skip;
    if (filters?.limit !== undefined) params.limit = filters.limit;

    const response = await apiClient.get<MeasurementHistoryListResponse>(
      '/process-data/measurements/history',
      { params }
    );
    return response.data;
  },

  /**
   * Get measurement data summary statistics.
   *
   * @param filters - Optional filters for date range and process
   * @returns Summary statistics including pass/fail rates and process breakdown
   */
  getMeasurementSummary: async (
    filters?: Omit<MeasurementHistoryFilters, 'skip' | 'limit' | 'lot_id' | 'result'>
  ): Promise<MeasurementSummaryResponse> => {
    const params: Record<string, any> = {};

    if (filters?.start_date) params.start_date = filters.start_date;
    if (filters?.end_date) params.end_date = filters.end_date;
    if (filters?.process_id) params.process_id = filters.process_id;

    const response = await apiClient.get<MeasurementSummaryResponse>(
      '/process-data/measurements/summary',
      { params }
    );
    return response.data;
  },

  /**
   * Get all unique measurement codes from the database.
   *
   * @param processId - Optional filter to get codes only from a specific process
   * @returns List of unique measurement codes with metadata
   */
  getMeasurementCodes: async (
    processId?: number
  ): Promise<MeasurementCodesResponse> => {
    const params: Record<string, any> = {};

    if (processId) params.process_id = processId;

    const response = await apiClient.get<MeasurementCodesResponse>(
      '/process-data/measurements/codes',
      { params }
    );
    return response.data;
  },
};
