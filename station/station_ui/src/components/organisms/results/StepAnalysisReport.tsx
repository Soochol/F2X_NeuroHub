/**
 * Step analysis report component.
 */

import { useState } from 'react';
import { AlertTriangle, Clock, ChevronDown, ChevronRight } from 'lucide-react';
import { useStepAnalysisReport, useExportStepAnalysisReport } from '../../../hooks';
import { LoadingSpinner } from '../../atoms/LoadingSpinner';
import { ExportButton } from './ExportButton';
import type { ExportFormat, ReportFilters, StepAnalysisItem } from '../../../types';

interface StepAnalysisReportProps {
  batchId?: string;
}

function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms.toFixed(0)}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(2)}s`;
  return `${Math.floor(ms / 60000)}m ${((ms % 60000) / 1000).toFixed(1)}s`;
}

/**
 * Get the CSS variable for fail rate color based on value.
 * > 10%: low (red), 5-10%: medium (yellow), <= 5%: high (green/secondary)
 */
function getFailRateColor(rate: number): string {
  if (rate > 0.1) return 'var(--color-rate-low)';
  if (rate > 0.05) return 'var(--color-rate-medium)';
  return 'var(--color-text-secondary)';
}

interface StepRowProps {
  step: StepAnalysisItem;
  isMostFailed: boolean;
  isSlowest: boolean;
}

function StepRow({ step, isMostFailed, isSlowest }: StepRowProps) {
  const [expanded, setExpanded] = useState(false);
  const hasFailures = step.failureReasons && step.failureReasons.length > 0;

  return (
    <div
      className="border-b last:border-b-0"
      style={{ borderColor: 'var(--color-border-subtle)' }}
    >
      <div
        className={`flex items-center gap-3 px-4 py-3 ${hasFailures ? 'cursor-pointer' : ''}`}
        onClick={() => hasFailures && setExpanded(!expanded)}
      >
        {/* Step Name */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
              {step.stepName}
            </span>
            {isMostFailed && (
              <span
                className="flex items-center gap-1 px-2 py-0.5 rounded text-xs"
                style={{ backgroundColor: 'var(--color-step-failed-bg)', color: 'var(--color-step-failed-text)' }}
              >
                <AlertTriangle className="w-3 h-3" />
                Most Failed
              </span>
            )}
            {isSlowest && (
              <span
                className="flex items-center gap-1 px-2 py-0.5 rounded text-xs"
                style={{ backgroundColor: 'var(--color-step-skipped-bg)', color: 'var(--color-step-skipped-text)' }}
              >
                <Clock className="w-3 h-3" />
                Slowest
              </span>
            )}
          </div>
        </div>

        {/* Stats */}
        <div className="flex items-center gap-6 text-sm">
          <div className="text-right w-16">
            <span style={{ color: 'var(--color-text-secondary)' }}>{step.totalRuns}</span>
          </div>
          <div className="text-right w-20">
            <span style={{ color: getFailRateColor(step.failRate) }}>
              {formatPercent(step.failRate)}
            </span>
          </div>
          <div className="text-right w-24 font-mono" style={{ color: 'var(--color-text-secondary)' }}>
            {formatDuration(step.avgDuration)}
          </div>
          <div className="text-right w-24 font-mono" style={{ color: 'var(--color-text-secondary)' }}>
            {formatDuration(step.p95Duration)}
          </div>
        </div>

        {hasFailures && (
          expanded ? (
            <ChevronDown className="w-4 h-4" style={{ color: 'var(--color-text-tertiary)' }} />
          ) : (
            <ChevronRight className="w-4 h-4" style={{ color: 'var(--color-text-tertiary)' }} />
          )
        )}
      </div>

      {/* Failure Reasons */}
      {expanded && hasFailures && (
        <div
          className="px-4 pb-4"
          style={{ backgroundColor: 'var(--color-bg-tertiary)' }}
        >
          <div className="ml-4">
            <h5 className="text-xs font-medium mb-2" style={{ color: 'var(--color-text-secondary)' }}>
              Failure Reasons
            </h5>
            <div className="space-y-2">
              {step.failureReasons.map((reason, index) => (
                <div
                  key={index}
                  className="flex items-start gap-3 p-2 rounded"
                  style={{ backgroundColor: 'var(--color-bg-elevated)' }}
                >
                  <div
                    className="flex-shrink-0 px-2 py-0.5 rounded text-xs font-medium"
                    style={{ backgroundColor: 'var(--color-bg-tertiary)', color: 'var(--color-text-secondary)' }}
                  >
                    {reason.occurrenceCount}x
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs" style={{ color: 'var(--color-text-primary)' }}>
                      {reason.errorMessage}
                    </p>
                    <p className="text-xs mt-1" style={{ color: 'var(--color-text-tertiary)' }}>
                      {formatPercent(reason.percentage)} of failures
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export function StepAnalysisReport({ batchId }: StepAnalysisReportProps) {
  const filters: ReportFilters = batchId ? { batchId } : {};
  const { data: report, isLoading, error } = useStepAnalysisReport(filters);
  const exportMutation = useExportStepAnalysisReport();

  const handleExport = (format: ExportFormat) => {
    exportMutation.mutate({ format, filters });
  };

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

  if (!report || report.steps.length === 0) {
    return (
      <div
        className="flex items-center justify-center h-64 text-sm"
        style={{ color: 'var(--color-text-tertiary)' }}
      >
        No step data available for analysis
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold" style={{ color: 'var(--color-text-primary)' }}>
            Step Analysis
          </h3>
          <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
            {report.totalSteps} steps analyzed
          </p>
        </div>
        <ExportButton
          onExport={handleExport}
          isLoading={exportMutation.isPending}
        />
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 gap-4">
        {report.mostFailedStep && (
          <div
            className="p-4 rounded-lg border-l-4"
            style={{ backgroundColor: 'var(--color-bg-tertiary)', borderColor: 'var(--color-step-failed-text)' }}
          >
            <div className="flex items-center gap-2 mb-1">
              <AlertTriangle className="w-4 h-4" style={{ color: 'var(--color-step-failed-text)' }} />
              <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                Most Failed Step
              </span>
            </div>
            <p className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
              {report.mostFailedStep}
            </p>
          </div>
        )}
        {report.slowestStep && (
          <div
            className="p-4 rounded-lg border-l-4"
            style={{ backgroundColor: 'var(--color-bg-tertiary)', borderColor: 'var(--color-step-skipped-text)' }}
          >
            <div className="flex items-center gap-2 mb-1">
              <Clock className="w-4 h-4" style={{ color: 'var(--color-step-skipped-text)' }} />
              <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                Slowest Step
              </span>
            </div>
            <p className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
              {report.slowestStep}
            </p>
          </div>
        )}
      </div>

      {/* Step Analysis Table */}
      <div>
        <div
          className="flex items-center gap-3 px-4 py-2 text-xs font-medium uppercase"
          style={{ backgroundColor: 'var(--color-bg-tertiary)', color: 'var(--color-text-secondary)' }}
        >
          <div className="flex-1">Step Name</div>
          <div className="flex items-center gap-6">
            <div className="w-16 text-right">Runs</div>
            <div className="w-20 text-right">Fail Rate</div>
            <div className="w-24 text-right">Avg</div>
            <div className="w-24 text-right">P95</div>
          </div>
          <div className="w-4" />
        </div>

        <div
          className="rounded-lg border overflow-hidden"
          style={{ borderColor: 'var(--color-border-default)' }}
        >
          {report.steps.map((step) => (
            <StepRow
              key={step.stepName}
              step={step}
              isMostFailed={step.stepName === report.mostFailedStep}
              isSlowest={step.stepName === report.slowestStep}
            />
          ))}
        </div>
      </div>

      {/* Report Generated */}
      <div className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
        Report generated at: {new Date(report.reportGeneratedAt).toLocaleString('en-US')}
      </div>
    </div>
  );
}
