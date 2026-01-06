/**
 * Report-related React Query hooks.
 */

import { useQuery, useMutation, type UseQueryOptions } from '@tanstack/react-query';
import {
  getBatchSummaryReport,
  exportBatchSummaryReport,
  getPeriodStatsReport,
  exportPeriodStatsReport,
  getStepAnalysisReport,
  exportStepAnalysisReport,
  getReportTypes,
  exportResultsBulk,
  exportSingleResult,
  downloadBlob,
  getFileExtension,
} from '../api/endpoints/reports';
import { toast } from '../utils';

// Note: Error handling is done globally via MutationCache in queryClient.ts
import type {
  BatchSummaryReport,
  PeriodStatisticsReport,
  StepAnalysisReport,
  ReportFilters,
  PeriodType,
  ExportFormat,
  BulkExportRequest,
  ReportTypesResponse,
} from '../types';

// ============================================================================
// Query Keys
// ============================================================================

export const reportQueryKeys = {
  all: ['reports'] as const,
  batchSummary: (batchId: string) => ['reports', 'batch', batchId] as const,
  periodStats: (period: PeriodType, from: string, to: string, batchId?: string) =>
    ['reports', 'period', period, from, to, batchId] as const,
  stepAnalysis: (filters?: ReportFilters) => ['reports', 'step-analysis', filters] as const,
  types: () => ['reports', 'types'] as const,
};

// ============================================================================
// Batch Summary Report Hook
// ============================================================================

/**
 * Hook to fetch batch summary report.
 */
export function useBatchSummaryReport(
  batchId: string | null,
  batchName?: string,
  options?: Omit<UseQueryOptions<BatchSummaryReport>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: reportQueryKeys.batchSummary(batchId ?? ''),
    queryFn: () => getBatchSummaryReport(batchId!, batchName),
    enabled: !!batchId,
    ...options,
  });
}

/**
 * Hook to export batch summary report.
 */
export function useExportBatchSummaryReport() {
  return useMutation({
    mutationFn: ({
      batchId,
      format,
      batchName,
    }: {
      batchId: string;
      format: ExportFormat;
      batchName?: string;
    }) => exportBatchSummaryReport(batchId, format, batchName),
    onSuccess: (blob, { batchId, format }) => {
      const filename = `batch_summary_${batchId}_${new Date().toISOString().slice(0, 10)}.${getFileExtension(format)}`;
      downloadBlob(blob, filename);
      toast.success('리포트 다운로드 완료');
    },
  });
}

// ============================================================================
// Period Statistics Report Hook
// ============================================================================

/**
 * Hook to fetch period statistics report.
 */
export function usePeriodStatsReport(
  periodType: PeriodType,
  fromDate: string | null,
  toDate: string | null,
  batchId?: string,
  options?: Omit<UseQueryOptions<PeriodStatisticsReport>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: reportQueryKeys.periodStats(periodType, fromDate ?? '', toDate ?? '', batchId),
    queryFn: () => getPeriodStatsReport(periodType, fromDate!, toDate!, batchId),
    enabled: !!fromDate && !!toDate,
    ...options,
  });
}

/**
 * Hook to export period statistics report.
 */
export function useExportPeriodStatsReport() {
  return useMutation({
    mutationFn: ({
      periodType,
      fromDate,
      toDate,
      format,
      batchId,
    }: {
      periodType: PeriodType;
      fromDate: string;
      toDate: string;
      format: ExportFormat;
      batchId?: string;
    }) => exportPeriodStatsReport(periodType, fromDate, toDate, format, batchId),
    onSuccess: (blob, { periodType, format }) => {
      const filename = `period_stats_${periodType}_${new Date().toISOString().slice(0, 10)}.${getFileExtension(format)}`;
      downloadBlob(blob, filename);
      toast.success('리포트 다운로드 완료');
    },
  });
}

// ============================================================================
// Step Analysis Report Hook
// ============================================================================

/**
 * Hook to fetch step analysis report.
 */
export function useStepAnalysisReport(
  filters?: ReportFilters,
  options?: Omit<UseQueryOptions<StepAnalysisReport>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: reportQueryKeys.stepAnalysis(filters),
    queryFn: () => getStepAnalysisReport(filters),
    ...options,
  });
}

/**
 * Hook to export step analysis report.
 */
export function useExportStepAnalysisReport() {
  return useMutation({
    mutationFn: ({
      format,
      filters,
    }: {
      format: ExportFormat;
      filters?: ReportFilters;
    }) => exportStepAnalysisReport(format, filters),
    onSuccess: (blob, { format }) => {
      const filename = `step_analysis_${new Date().toISOString().slice(0, 10)}.${getFileExtension(format)}`;
      downloadBlob(blob, filename);
      toast.success('리포트 다운로드 완료');
    },
  });
}

// ============================================================================
// Report Types Hook
// ============================================================================

/**
 * Hook to get available report types and formats.
 */
export function useReportTypes(
  options?: Omit<UseQueryOptions<ReportTypesResponse>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: reportQueryKeys.types(),
    queryFn: getReportTypes,
    staleTime: 1000 * 60 * 60, // 1 hour - rarely changes
    ...options,
  });
}

// ============================================================================
// Bulk Export Hook
// ============================================================================

/**
 * Hook to export multiple results.
 */
export function useExportResultsBulk() {
  return useMutation({
    mutationFn: (request: BulkExportRequest) => exportResultsBulk(request),
    onSuccess: (blob, { format }) => {
      const filename = `results_export_${new Date().toISOString().slice(0, 10)}.${getFileExtension(format)}`;
      downloadBlob(blob, filename);
      toast.success('결과 내보내기 완료');
    },
  });
}

/**
 * Hook to export single result.
 */
export function useExportSingleResult() {
  return useMutation({
    mutationFn: ({ resultId, format }: { resultId: string; format: ExportFormat }) =>
      exportSingleResult(resultId, format),
    onSuccess: (blob, { resultId, format }) => {
      const filename = `result_${resultId}.${getFileExtension(format)}`;
      downloadBlob(blob, filename);
      toast.success('결과 내보내기 완료');
    },
  });
}
