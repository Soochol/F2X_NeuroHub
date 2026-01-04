/**
 * Batch overview card for dashboard display.
 * A simplified card view showing batch status, progress, and current step.
 */

import { useNavigate } from 'react-router-dom';
import { CheckCircle, XCircle, Clock, Loader2, AlertCircle, StopCircle } from 'lucide-react';
import { ProgressBar } from '../atoms/ProgressBar';
import type { Batch } from '../../types';

export interface BatchOverviewCardProps {
  batch: Batch;
}

export function BatchOverviewCard({ batch }: BatchOverviewCardProps) {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/batches/${batch.id}`);
  };

  const statusConfig = getStatusConfig(batch.status);
  const progressPercent = Math.round(batch.progress * 100);

  return (
    <div
      onClick={handleClick}
      className="p-4 rounded-lg border transition-all cursor-pointer hover:shadow-md hover:border-brand-400"
      style={{
        backgroundColor: 'var(--color-bg-secondary)',
        borderColor: 'var(--color-border-default)',
      }}
    >
      {/* Header: Name and Status Icon */}
      <div className="flex items-start justify-between gap-2 mb-3">
        <h4
          className="text-sm font-semibold truncate flex-1"
          style={{ color: 'var(--color-text-primary)' }}
          title={batch.name}
        >
          {batch.name}
        </h4>
        <div
          className="flex-shrink-0 p-1.5 rounded-full"
          style={{ backgroundColor: statusConfig.bgColor }}
        >
          <statusConfig.icon className="w-4 h-4" style={{ color: statusConfig.iconColor }} />
        </div>
      </div>

      {/* Status Badge */}
      <div className="mb-3">
        <span
          className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium uppercase tracking-wide"
          style={{
            backgroundColor: statusConfig.badgeBg,
            color: statusConfig.badgeText,
          }}
        >
          {batch.status}
        </span>
      </div>

      {/* Progress */}
      <div className="mb-3">
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
            Progress
          </span>
          <span
            className="text-sm font-semibold"
            style={{ color: 'var(--color-text-primary)' }}
          >
            {progressPercent}%
          </span>
        </div>
        <ProgressBar
          value={progressPercent}
          variant={getProgressVariant(batch.status, batch.lastRunPassed)}
          size="md"
        />
      </div>

      {/* Current Step */}
      <div
        className="pt-3 border-t"
        style={{ borderColor: 'var(--color-border-muted)' }}
      >
        <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
          Step
        </span>
        <p
          className="text-sm font-medium truncate mt-0.5"
          style={{ color: 'var(--color-text-secondary)' }}
          title={batch.currentStep || 'No step'}
        >
          {batch.currentStep || '-'}
        </p>
      </div>
    </div>
  );
}

function getStatusConfig(status: Batch['status']) {
  switch (status) {
    case 'completed':
      return {
        icon: CheckCircle,
        iconColor: 'var(--color-success)',
        bgColor: 'var(--color-success-bg)',
        badgeBg: 'var(--color-success-bg)',
        badgeText: 'var(--color-success)',
      };
    case 'error':
      return {
        icon: XCircle,
        iconColor: 'var(--color-error)',
        bgColor: 'var(--color-error-bg)',
        badgeBg: 'var(--color-error-bg)',
        badgeText: 'var(--color-error)',
      };
    case 'running':
      return {
        icon: Loader2,
        iconColor: 'var(--color-info)',
        bgColor: 'var(--color-info-bg)',
        badgeBg: 'var(--color-info-bg)',
        badgeText: 'var(--color-info)',
      };
    case 'starting':
      return {
        icon: Clock,
        iconColor: 'var(--color-warning)',
        bgColor: 'var(--color-warning-bg)',
        badgeBg: 'var(--color-warning-bg)',
        badgeText: 'var(--color-warning)',
      };
    case 'stopping':
      return {
        icon: StopCircle,
        iconColor: 'var(--color-warning)',
        bgColor: 'var(--color-warning-bg)',
        badgeBg: 'var(--color-warning-bg)',
        badgeText: 'var(--color-warning)',
      };
    case 'idle':
    default:
      return {
        icon: AlertCircle,
        iconColor: 'var(--color-text-tertiary)',
        bgColor: 'var(--color-bg-tertiary)',
        badgeBg: 'var(--color-bg-tertiary)',
        badgeText: 'var(--color-text-secondary)',
      };
  }
}

function getProgressVariant(
  status: Batch['status'],
  lastRunPassed?: boolean
): 'default' | 'success' | 'warning' | 'error' {
  if (status === 'error') return 'error';
  if (status === 'completed') {
    return lastRunPassed === false ? 'error' : 'success';
  }
  if (status === 'stopping') return 'warning';
  return 'default';
}
