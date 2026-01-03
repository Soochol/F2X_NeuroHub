/**
 * Reports API endpoints.
 */

import type {
  ApiResponse,
  BatchSummaryReport,
  PeriodStatisticsReport,
  StepAnalysisReport,
  ReportFilters,
  PeriodType,
  ExportFormat,
  BulkExportRequest,
  ReportTypesResponse,
} from '../../types';
import apiClient, { extractData } from '../client';

// ============================================================================
// Batch Summary Report
// ============================================================================

/**
 * Get batch summary report.
 */
export async function getBatchSummaryReport(
  batchId: string,
  batchName?: string
): Promise<BatchSummaryReport> {
  const response = await apiClient.get<ApiResponse<BatchSummaryReport>>(
    `/reports/batch/${batchId}`,
    { params: { batchName } }
  );
  return extractData(response);
}

/**
 * Export batch summary report.
 */
export async function exportBatchSummaryReport(
  batchId: string,
  format: ExportFormat,
  batchName?: string
): Promise<Blob> {
  const response = await apiClient.get(`/reports/batch/${batchId}`, {
    params: { format, batchName },
    responseType: 'blob',
  });
  return response.data;
}

// ============================================================================
// Period Statistics Report
// ============================================================================

/**
 * Get period statistics report.
 */
export async function getPeriodStatsReport(
  periodType: PeriodType,
  fromDate: string,
  toDate: string,
  batchId?: string
): Promise<PeriodStatisticsReport> {
  const response = await apiClient.get<ApiResponse<PeriodStatisticsReport>>('/reports/period', {
    params: {
      period: periodType,
      from: fromDate,
      to: toDate,
      batchId,
    },
  });
  return extractData(response);
}

/**
 * Export period statistics report.
 */
export async function exportPeriodStatsReport(
  periodType: PeriodType,
  fromDate: string,
  toDate: string,
  format: ExportFormat,
  batchId?: string
): Promise<Blob> {
  const response = await apiClient.get('/reports/period', {
    params: {
      period: periodType,
      from: fromDate,
      to: toDate,
      batchId,
      format,
    },
    responseType: 'blob',
  });
  return response.data;
}

// ============================================================================
// Step Analysis Report
// ============================================================================

/**
 * Get step analysis report.
 */
export async function getStepAnalysisReport(
  filters?: ReportFilters
): Promise<StepAnalysisReport> {
  const response = await apiClient.get<ApiResponse<StepAnalysisReport>>(
    '/reports/step-analysis',
    {
      params: {
        from: filters?.fromDate,
        to: filters?.toDate,
        batchId: filters?.batchId,
        stepName: filters?.stepName,
      },
    }
  );
  return extractData(response);
}

/**
 * Export step analysis report.
 */
export async function exportStepAnalysisReport(
  format: ExportFormat,
  filters?: ReportFilters
): Promise<Blob> {
  const response = await apiClient.get('/reports/step-analysis', {
    params: {
      from: filters?.fromDate,
      to: filters?.toDate,
      batchId: filters?.batchId,
      stepName: filters?.stepName,
      format,
    },
    responseType: 'blob',
  });
  return response.data;
}

// ============================================================================
// Report Types Info
// ============================================================================

/**
 * Get available report types and formats.
 */
export async function getReportTypes(): Promise<ReportTypesResponse> {
  const response = await apiClient.get<ApiResponse<ReportTypesResponse>>('/reports/types');
  return extractData(response);
}

// ============================================================================
// Bulk Export
// ============================================================================

/**
 * Export multiple execution results.
 */
export async function exportResultsBulk(request: BulkExportRequest): Promise<Blob> {
  const response = await apiClient.post('/results/export', request, {
    responseType: 'blob',
  });
  return response.data;
}

/**
 * Export single result in specified format.
 */
export async function exportSingleResult(
  resultId: string,
  format: ExportFormat
): Promise<Blob> {
  const response = await apiClient.get(`/results/${resultId}/export`, {
    params: { format },
    responseType: 'blob',
  });
  return response.data;
}

// ============================================================================
// Download Helper
// ============================================================================

/**
 * Download blob as file.
 */
export function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Get file extension for export format.
 */
export function getFileExtension(format: ExportFormat): string {
  return format;
}
