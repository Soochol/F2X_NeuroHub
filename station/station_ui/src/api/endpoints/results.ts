/**
 * Results API endpoints.
 */

import type {
  PaginatedResponse,
  PaginatedData,
  ApiResponse,
  ExecutionSummary,
  ExecutionResult,
} from '../../types';
import apiClient, { extractData } from '../client';

/**
 * Query parameters for results list.
 */
export interface ResultsQueryParams {
  batchId?: string;
  status?: 'completed' | 'failed';
  from?: string;
  to?: string;
  limit?: number;
  offset?: number;
}

/**
 * Get execution results with filtering and pagination.
 */
export async function getResults(
  params?: ResultsQueryParams
): Promise<PaginatedData<ExecutionSummary>> {
  const response = await apiClient.get<PaginatedResponse<ExecutionSummary>>('/results', {
    params,
  });
  return response.data.data;
}

/**
 * Get execution result details by ID.
 */
export async function getResult(resultId: string): Promise<ExecutionResult> {
  const response = await apiClient.get<ApiResponse<ExecutionResult>>(`/results/${resultId}`);
  return extractData(response);
}

/**
 * Export formats for results.
 */
export type ExportFormat = 'json' | 'csv';

/**
 * Export execution result.
 */
export async function exportResult(resultId: string, format: ExportFormat): Promise<Blob> {
  const response = await apiClient.get(`/results/${resultId}/export`, {
    params: { format },
    responseType: 'blob',
  });
  return response.data;
}
