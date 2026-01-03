/**
 * Result detail modal for viewing execution result details.
 */

import { X, CheckCircle, XCircle, PlayCircle, StopCircle, ChevronDown, ChevronRight } from 'lucide-react';
import { useState } from 'react';
import { Button } from '../../atoms/Button';
import type { ExecutionResult, StepResult, ExecutionStatus, StepStatus } from '../../../types';

interface ResultDetailModalProps {
  result: ExecutionResult;
  onClose: () => void;
}

/**
 * Get status icon with theme-aware colors.
 */
const getStatusIcon = (status: ExecutionStatus): React.ReactNode => {
  const iconProps = { className: 'w-5 h-5' };
  const styles: Record<ExecutionStatus, { color: string }> = {
    completed: { color: 'var(--color-step-completed-text)' },
    failed: { color: 'var(--color-step-failed-text)' },
    running: { color: 'var(--color-step-running-text)' },
    stopped: { color: 'var(--color-step-pending-text)' },
  };

  switch (status) {
    case 'completed':
      return <CheckCircle {...iconProps} style={styles.completed} />;
    case 'failed':
      return <XCircle {...iconProps} style={styles.failed} />;
    case 'running':
      return <PlayCircle {...iconProps} style={styles.running} />;
    case 'stopped':
      return <StopCircle {...iconProps} style={styles.stopped} />;
  }
};

/**
 * Get step status badge styles using CSS variables.
 */
const getStepStatusStyles = (status: StepStatus): React.CSSProperties => {
  const styles: Record<StepStatus, React.CSSProperties> = {
    pending: { backgroundColor: 'var(--color-step-pending-bg)', color: 'var(--color-step-pending-text)' },
    running: { backgroundColor: 'var(--color-step-running-bg)', color: 'var(--color-step-running-text)' },
    completed: { backgroundColor: 'var(--color-step-completed-bg)', color: 'var(--color-step-completed-text)' },
    failed: { backgroundColor: 'var(--color-step-failed-bg)', color: 'var(--color-step-failed-text)' },
    skipped: { backgroundColor: 'var(--color-step-skipped-bg)', color: 'var(--color-step-skipped-text)' },
  };
  return styles[status];
};

function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(2)}s`;
  return `${Math.floor(ms / 60000)}m ${((ms % 60000) / 1000).toFixed(1)}s`;
}

function formatDateTime(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleString('en-US');
}

interface StepRowProps {
  step: StepResult;
  index: number;
}

function StepRow({ step, index }: StepRowProps) {
  const [expanded, setExpanded] = useState(false);
  const hasDetails = step.result || step.error;

  return (
    <div
      className="border-b last:border-b-0"
      style={{ borderColor: 'var(--color-border-subtle)' }}
    >
      <div
        className={`flex items-center gap-3 px-4 py-3 ${hasDetails ? 'cursor-pointer' : ''}`}
        onClick={() => hasDetails && setExpanded(!expanded)}
      >
        <span
          className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium"
          style={{ backgroundColor: 'var(--color-bg-tertiary)', color: 'var(--color-text-secondary)' }}
        >
          {step.order || index + 1}
        </span>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
              {step.name}
            </span>
            {step.status && (
              <span
                className="px-2 py-0.5 rounded text-xs font-medium"
                style={getStepStatusStyles(step.status)}
              >
                {step.status}
              </span>
            )}
          </div>
        </div>

        <span className="text-sm font-mono" style={{ color: 'var(--color-text-secondary)' }}>
          {step.duration ? formatDuration(step.duration * 1000) : '-'}
        </span>

        {hasDetails && (
          expanded ? (
            <ChevronDown className="w-4 h-4" style={{ color: 'var(--color-text-tertiary)' }} />
          ) : (
            <ChevronRight className="w-4 h-4" style={{ color: 'var(--color-text-tertiary)' }} />
          )
        )}
      </div>

      {expanded && hasDetails && (
        <div
          className="px-4 pb-3 ml-9"
          style={{ backgroundColor: 'var(--color-bg-tertiary)' }}
        >
          {step.error && (
            <div className="mb-2">
              <span className="text-xs font-medium" style={{ color: 'var(--color-step-failed-text)' }}>Error:</span>
              <pre
                className="mt-1 text-xs p-2 rounded overflow-x-auto"
                style={{ backgroundColor: 'var(--color-bg-elevated)', color: 'var(--color-text-secondary)' }}
              >
                {step.error}
              </pre>
            </div>
          )}
          {step.result && Object.keys(step.result).length > 0 && (
            <div>
              <span className="text-xs font-medium" style={{ color: 'var(--color-text-secondary)' }}>
                Result Data:
              </span>
              <div className="mt-1 grid grid-cols-2 gap-2">
                {Object.entries(step.result).map(([key, value]) => (
                  <div key={key} className="flex justify-between text-xs">
                    <span style={{ color: 'var(--color-text-tertiary)' }}>{key}:</span>
                    <span className="font-mono" style={{ color: 'var(--color-text-primary)' }}>
                      {typeof value === 'number' ? value.toFixed(3) : String(value)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export function ResultDetailModal({ result, onClose }: ResultDetailModalProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
      />

      {/* Modal */}
      <div
        className="relative w-full max-w-2xl max-h-[90vh] overflow-hidden rounded-xl shadow-xl"
        style={{ backgroundColor: 'var(--color-bg-elevated)' }}
      >
        {/* Header */}
        <div
          className="flex items-center justify-between px-6 py-4 border-b"
          style={{ borderColor: 'var(--color-border-default)' }}
        >
          <div className="flex items-center gap-3">
            {getStatusIcon(result.status)}
            <div>
              <h3 className="text-lg font-semibold" style={{ color: 'var(--color-text-primary)' }}>
                {result.sequenceName}
              </h3>
              <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                {result.sequenceVersion && `v${result.sequenceVersion} · `}
                {result.id.slice(0, 8)}
              </p>
            </div>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* Content */}
        <div className="overflow-y-auto max-h-[calc(90vh-140px)]">
          {/* Summary */}
          <div
            className="grid grid-cols-2 md:grid-cols-4 gap-4 p-6 border-b"
            style={{ borderColor: 'var(--color-border-default)' }}
          >
            <div>
              <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                Batch
              </span>
              <p className="text-sm font-mono" style={{ color: 'var(--color-text-primary)' }}>
                {result.batchId?.slice(0, 8) ?? '-'}
              </p>
            </div>
            <div>
              <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                Started At
              </span>
              <p className="text-sm" style={{ color: 'var(--color-text-primary)' }}>
                {result.startedAt ? formatDateTime(result.startedAt) : '-'}
              </p>
            </div>
            <div>
              <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                Completed At
              </span>
              <p className="text-sm" style={{ color: 'var(--color-text-primary)' }}>
                {result.completedAt ? formatDateTime(result.completedAt) : '-'}
              </p>
            </div>
            <div>
              <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                Duration
              </span>
              <p className="text-sm font-mono" style={{ color: 'var(--color-text-primary)' }}>
                {result.duration ? formatDuration(result.duration) : '-'}
              </p>
            </div>
          </div>

          {/* Failed Status Indicator */}
          {!result.overallPass && (
            <div className="px-6 py-4 border-b" style={{ borderColor: 'var(--color-border-default)' }}>
              <div
                className="flex items-center gap-2"
                style={{ color: 'var(--color-step-failed-text)' }}
              >
                <XCircle className="w-4 h-4" />
                <span className="text-sm font-medium">Execution failed - check step details below</span>
              </div>
            </div>
          )}

          {/* Steps */}
          <div className="px-6 py-4">
            <h4 className="text-sm font-medium mb-3" style={{ color: 'var(--color-text-primary)' }}>
              Steps ({result.steps?.length ?? 0})
            </h4>
            <div
              className="rounded-lg border overflow-hidden"
              style={{ borderColor: 'var(--color-border-default)' }}
            >
              {result.steps && result.steps.length > 0 ? (
                result.steps.map((step, index) => (
                  <StepRow key={`${step.name}-${step.order}`} step={step} index={index} />
                ))
              ) : (
                <div
                  className="py-8 text-center text-sm"
                  style={{ color: 'var(--color-text-tertiary)' }}
                >
                  No step data available
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div
          className="flex justify-end px-6 py-4 border-t"
          style={{ borderColor: 'var(--color-border-default)' }}
        >
          <Button variant="secondary" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </div>
  );
}
