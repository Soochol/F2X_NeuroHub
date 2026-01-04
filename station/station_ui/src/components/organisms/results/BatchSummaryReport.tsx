/**
 * Batch summary report component.
 */

import { useBatchSummaryReport, useExportBatchSummaryReport } from '../../../hooks';
import { LoadingSpinner } from '../../atoms/LoadingSpinner';
import { ExportButton } from './ExportButton';
import type { ExportFormat } from '../../../types';

interface BatchSummaryReportProps {
  batchId: string | null;
  batchName?: string;
}

function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms.toFixed(0)}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(2)}s`;
  return `${Math.floor(ms / 60000)}m ${((ms % 60000) / 1000).toFixed(1)}s`;
}

function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

/**
 * Get the CSS variable for pass rate color based on value.
 * >= 90%: high (green), 70-90%: medium (yellow), < 70%: low (red)
 */
function getPassRateColor(rate: number): string {
  if (rate >= 0.9) return 'var(--color-rate-high)';
  if (rate >= 0.7) return 'var(--color-rate-medium)';
  return 'var(--color-rate-low)';
}

export function BatchSummaryReport({ batchId, batchName }: BatchSummaryReportProps) {
  const { data: report, isLoading, error } = useBatchSummaryReport(batchId, batchName);
  const exportMutation = useExportBatchSummaryReport();

  const handleExport = (format: ExportFormat) => {
    if (!batchId) return;
    exportMutation.mutate({ batchId, format, batchName });
  };

  if (!batchId) {
    return (
      <div
        className="flex items-center justify-center h-64 text-sm"
        style={{ color: 'var(--color-text-tertiary)' }}
      >
        Select a batch to view summary report
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div
        className="flex items-center justify-center h-64 text-sm"
        style={{ color: 'var(--color-rate-low)' }}
      >
        Failed to load report: {(error as Error).message}
      </div>
    );
  }

  if (!report) {
    return (
      <div
        className="flex items-center justify-center h-64 text-sm"
        style={{ color: 'var(--color-text-tertiary)' }}
      >
        No data available for this batch
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold" style={{ color: 'var(--color-text-primary)' }}>
            {report.batchName || report.batchId}
          </h3>
          <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
            {report.sequenceName} v{report.sequenceVersion}
          </p>
        </div>
        <ExportButton
          onExport={handleExport}
          isLoading={exportMutation.isPending}
        />
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div
          className="p-4 rounded-lg"
          style={{ backgroundColor: 'var(--color-bg-tertiary)' }}
        >
          <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
            Total Executions
          </span>
          <p className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>
            {report.totalExecutions}
          </p>
        </div>
        <div
          className="p-4 rounded-lg"
          style={{ backgroundColor: 'var(--color-bg-tertiary)' }}
        >
          <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
            Pass Rate
          </span>
          <p
            className="text-2xl font-bold"
            style={{ color: getPassRateColor(report.passRate) }}
          >
            {formatPercent(report.passRate)}
          </p>
        </div>
        <div
          className="p-4 rounded-lg"
          style={{ backgroundColor: 'var(--color-bg-tertiary)' }}
        >
          <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
            Pass / Fail
          </span>
          <p className="text-2xl font-bold">
            <span style={{ color: 'var(--color-rate-high)' }}>{report.passCount}</span>
            {' / '}
            <span style={{ color: 'var(--color-rate-low)' }}>{report.failCount}</span>
          </p>
        </div>
        <div
          className="p-4 rounded-lg"
          style={{ backgroundColor: 'var(--color-bg-tertiary)' }}
        >
          <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
            Avg Duration
          </span>
          <p className="text-2xl font-bold font-mono" style={{ color: 'var(--color-text-primary)' }}>
            {formatDuration(report.avgDuration)}
          </p>
        </div>
      </div>

      {/* Step Statistics Table */}
      <div>
        <h4 className="text-sm font-medium mb-3" style={{ color: 'var(--color-text-primary)' }}>
          Step Statistics
        </h4>
        <div
          className="rounded-lg border overflow-hidden"
          style={{ borderColor: 'var(--color-border-default)' }}
        >
          <table className="min-w-full">
            <thead style={{ backgroundColor: 'var(--color-bg-tertiary)' }}>
              <tr>
                <th
                  className="px-4 py-3 text-left text-xs font-medium uppercase"
                  style={{ color: 'var(--color-text-secondary)' }}
                >
                  Step Name
                </th>
                <th
                  className="px-4 py-3 text-right text-xs font-medium uppercase"
                  style={{ color: 'var(--color-text-secondary)' }}
                >
                  Runs
                </th>
                <th
                  className="px-4 py-3 text-right text-xs font-medium uppercase"
                  style={{ color: 'var(--color-text-secondary)' }}
                >
                  Pass Rate
                </th>
                <th
                  className="px-4 py-3 text-right text-xs font-medium uppercase"
                  style={{ color: 'var(--color-text-secondary)' }}
                >
                  Avg
                </th>
                <th
                  className="px-4 py-3 text-right text-xs font-medium uppercase"
                  style={{ color: 'var(--color-text-secondary)' }}
                >
                  Min
                </th>
                <th
                  className="px-4 py-3 text-right text-xs font-medium uppercase"
                  style={{ color: 'var(--color-text-secondary)' }}
                >
                  Max
                </th>
              </tr>
            </thead>
            <tbody
              className="divide-y"
              style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-subtle)' }}
            >
              {report.steps.map((step) => (
                <tr key={step.stepName}>
                  <td className="px-4 py-3">
                    <span className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
                      {step.stepName}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                      {step.totalRuns}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span
                      className="text-sm font-medium"
                      style={{ color: getPassRateColor(step.passRate) }}
                    >
                      {formatPercent(step.passRate)}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span className="text-sm font-mono" style={{ color: 'var(--color-text-secondary)' }}>
                      {formatDuration(step.avgDuration)}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span className="text-sm font-mono" style={{ color: 'var(--color-text-secondary)' }}>
                      {formatDuration(step.minDuration)}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span className="text-sm font-mono" style={{ color: 'var(--color-text-secondary)' }}>
                      {formatDuration(step.maxDuration)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Execution Time Range */}
      {(report.firstExecution || report.lastExecution) && (
        <div className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
          Data range:{' '}
          {report.firstExecution && new Date(report.firstExecution).toLocaleDateString('en-US')}
          {' ~ '}
          {report.lastExecution && new Date(report.lastExecution).toLocaleDateString('en-US')}
        </div>
      )}
    </div>
  );
}
