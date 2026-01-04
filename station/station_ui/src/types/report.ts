/**
 * Report type definitions for Station UI.
 */

// ============================================================================
// Enums
// ============================================================================

/**
 * Available report types.
 */
export type ReportType = 'batch_summary' | 'period_stats' | 'step_analysis';

/**
 * Time period granularity.
 */
export type PeriodType = 'daily' | 'weekly' | 'monthly';

/**
 * Supported export formats.
 */
export type ExportFormat = 'json' | 'csv' | 'xlsx' | 'pdf';

// ============================================================================
// Batch Summary Report
// ============================================================================

/**
 * Summary statistics for a single step.
 */
export interface StepSummary {
  stepName: string;
  totalRuns: number;
  passCount: number;
  failCount: number;
  passRate: number;
  avgDuration: number;
  minDuration: number;
  maxDuration: number;
}

/**
 * Batch summary report with aggregated statistics.
 */
export interface BatchSummaryReport {
  batchId: string;
  batchName?: string;
  sequenceName: string;
  sequenceVersion: string;
  reportGeneratedAt: Date;
  totalExecutions: number;
  passCount: number;
  failCount: number;
  passRate: number;
  avgDuration: number;
  steps: StepSummary[];
  firstExecution?: Date;
  lastExecution?: Date;
}

// ============================================================================
// Period Statistics Report
// ============================================================================

/**
 * Data point for a single time period.
 */
export interface PeriodDataPoint {
  periodStart: Date;
  periodEnd: Date;
  periodLabel: string;
  total: number;
  passCount: number;
  failCount: number;
  passRate: number;
  avgDuration: number;
}

/**
 * Period-based statistics report.
 */
export interface PeriodStatisticsReport {
  periodType: PeriodType;
  fromDate: Date;
  toDate: Date;
  batchId?: string;
  reportGeneratedAt: Date;
  totalExecutions: number;
  overallPassRate: number;
  dataPoints: PeriodDataPoint[];
  trendDirection: 'increasing' | 'decreasing' | 'stable';
  trendPercentage: number;
}

// ============================================================================
// Step Analysis Report
// ============================================================================

/**
 * Aggregated failure reason.
 */
export interface FailureReason {
  errorMessage: string;
  occurrenceCount: number;
  percentage: number;
}

/**
 * Detailed analysis for a single step.
 */
export interface StepAnalysisItem {
  stepName: string;
  totalRuns: number;
  failCount: number;
  failRate: number;
  avgDuration: number;
  minDuration: number;
  maxDuration: number;
  p50Duration: number;
  p95Duration: number;
  failureReasons: FailureReason[];
}

/**
 * Step-level analysis report.
 */
export interface StepAnalysisReport {
  fromDate?: Date;
  toDate?: Date;
  batchId?: string;
  reportGeneratedAt: Date;
  steps: StepAnalysisItem[];
  totalSteps: number;
  mostFailedStep?: string;
  slowestStep?: string;
}

// ============================================================================
// Request/Filter Types
// ============================================================================

/**
 * Report filter parameters.
 */
export interface ReportFilters {
  batchId?: string;
  fromDate?: string;
  toDate?: string;
  periodType?: PeriodType;
  stepName?: string;
}

/**
 * Bulk export request.
 */
export interface BulkExportRequest {
  resultIds: string[];
  format: ExportFormat;
  includeStepDetails?: boolean;
}

// ============================================================================
// Report Type Info
// ============================================================================

/**
 * Report type metadata.
 */
export interface ReportTypeInfo {
  id: ReportType;
  name: string;
  description: string;
  requiredParams: string[];
}

/**
 * Export format metadata.
 */
export interface ExportFormatInfo {
  id: ExportFormat;
  name: string;
  extension: string;
}

/**
 * Available report types and formats response.
 */
export interface ReportTypesResponse {
  reportTypes: ReportTypeInfo[];
  exportFormats: ExportFormatInfo[];
}

// ============================================================================
// Constants
// ============================================================================

/**
 * Export format display info.
 */
export const EXPORT_FORMAT_INFO: Record<ExportFormat, { label: string; icon: string }> = {
  json: { label: 'JSON', icon: 'FileJson' },
  csv: { label: 'CSV', icon: 'FileSpreadsheet' },
  xlsx: { label: 'Excel', icon: 'FileSpreadsheet' },
  pdf: { label: 'PDF', icon: 'FileText' },
};

/**
 * Report type display info.
 */
export const REPORT_TYPE_INFO: Record<ReportType, { label: string; description: string }> = {
  batch_summary: {
    label: 'Batch Summary',
    description: 'Summary statistics for a specific batch',
  },
  period_stats: {
    label: 'Period Statistics',
    description: 'Statistics grouped by time period with trend analysis',
  },
  step_analysis: {
    label: 'Step Analysis',
    description: 'Step-level failure and performance analysis',
  },
};
