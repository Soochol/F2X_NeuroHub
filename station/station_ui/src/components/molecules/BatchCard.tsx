/**
 * Batch card component for batch list.
 * Enhanced with statistics and summary information.
 */

import { Play, Square, ChevronRight, CheckCircle, XCircle, Clock, Layers, Trash2 } from 'lucide-react';
import { ProgressBar } from '../atoms/ProgressBar';
import { StatusBadge } from '../atoms/StatusBadge';
import { Button } from '../atoms/Button';
import type { Batch, BatchStatistics } from '../../types';

export interface BatchCardProps {
  batch: Batch;
  statistics?: BatchStatistics;
  onStart?: (batchId: string) => void;
  onStop?: (batchId: string) => void;
  onDelete?: (batchId: string) => void;
  onSelect?: (batchId: string) => void;
  isLoading?: boolean;
  isSelected?: boolean;
}

export function BatchCard({
  batch,
  statistics,
  onStart,
  onStop,
  onDelete,
  onSelect,
  isLoading,
  isSelected,
}: BatchCardProps) {
  const isRunning = batch.status === 'running' || batch.status === 'starting';
  const canStart = batch.status === 'idle' || batch.status === 'completed' || batch.status === 'error';

  // Default statistics if not provided
  const stats = statistics || { total: 0, passCount: 0, fail: 0, passRate: 0 };

  return (
    <div
      className={`p-4 rounded-lg border transition-all cursor-pointer ${
        isSelected
          ? 'border-brand-500 ring-1 ring-brand-500/50'
          : 'hover:opacity-90'
      }`}
      style={{
        backgroundColor: 'var(--color-bg-secondary)',
        borderColor: isSelected ? undefined : 'var(--color-border-default)',
      }}
      onClick={() => onSelect?.(batch.id)}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <h3 className="font-medium" style={{ color: 'var(--color-text-primary)' }}>{batch.name}</h3>
          <StatusBadge status={batch.status} size="sm" />
        </div>
        <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
          {canStart && onStart && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onStart(batch.id)}
              disabled={isLoading}
              title="Start"
            >
              <Play className="w-4 h-4" />
            </Button>
          )}
          {isRunning && onStop && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onStop(batch.id)}
              disabled={isLoading}
              title="Stop"
            >
              <Square className="w-4 h-4" />
            </Button>
          )}
          {!isRunning && onDelete && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onDelete(batch.id)}
              disabled={isLoading}
              title="Delete"
              className="text-red-500 hover:text-red-400 hover:bg-red-500/10"
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          )}
          <ChevronRight className="w-4 h-4" style={{ color: 'var(--color-text-tertiary)' }} />
        </div>
      </div>

      {/* Progress */}
      <div className="space-y-2 mb-3">
        <div className="flex items-center gap-2">
          <ProgressBar
            value={batch.progress * 100}
            variant={
              batch.status === 'error'
                ? 'error'
                : batch.status === 'completed'
                  ? batch.lastRunPassed === false
                    ? 'error'
                    : 'success'
                  : 'default'
            }
            size="sm"
          />
          <span className="text-xs w-12 text-right" style={{ color: 'var(--color-text-secondary)' }}>
            {Math.round(batch.progress * 100)}%
          </span>
        </div>
      </div>

      {/* Sequence Info */}
      <div className="flex items-center gap-2 text-xs mb-3" style={{ color: 'var(--color-text-tertiary)' }}>
        <Layers className="w-3 h-3" />
        <span className="truncate">
          {batch.sequenceName || 'No sequence'}
          {batch.sequenceVersion && ` v${batch.sequenceVersion}`}
        </span>
      </div>

      {/* Current Step (when running) */}
      {batch.currentStep && (
        <div className="flex items-center gap-2 text-xs mb-3 p-2 rounded" style={{ backgroundColor: 'var(--color-bg-tertiary)' }}>
          <Clock className="w-3 h-3 text-brand-500" />
          <span style={{ color: 'var(--color-text-secondary)' }}>Step:</span>
          <span className="font-medium truncate" style={{ color: 'var(--color-text-primary)' }}>{batch.currentStep}</span>
          <span className="ml-auto" style={{ color: 'var(--color-text-tertiary)' }}>
            ({(batch.stepIndex ?? 0) + 1}/{batch.totalSteps ?? 0})
          </span>
        </div>
      )}

      {/* Statistics */}
      <div className="flex items-center gap-4 pt-3 border-t" style={{ borderColor: 'var(--color-border-default)' }}>
        <StatBadge
          icon={<Layers className="w-3 h-3" style={{ color: 'var(--color-text-secondary)' }} />}
          value={stats.total}
          label="Total"
        />
        <StatBadge
          icon={<CheckCircle className="w-3 h-3 text-green-500" />}
          value={stats.passCount}
          label="Pass"
          color="text-green-500"
        />
        <StatBadge
          icon={<XCircle className="w-3 h-3 text-red-500" />}
          value={stats.fail}
          label="Fail"
          color="text-red-500"
        />
        <div className="ml-auto">
          <span
            className={`text-sm font-medium ${
              stats.passRate >= 0.9
                ? 'text-green-500'
                : stats.passRate >= 0.7
                  ? 'text-yellow-500'
                  : stats.passRate > 0
                    ? 'text-red-500'
                    : 'text-zinc-500'
            }`}
          >
            {stats.total > 0 ? `${(stats.passRate * 100).toFixed(0)}%` : '-'}
          </span>
        </div>
      </div>
    </div>
  );
}

function StatBadge({
  icon,
  value,
  label,
  color,
}: {
  icon: React.ReactNode;
  value: number;
  label: string;
  color?: string;
}) {
  return (
    <div className="flex items-center gap-1.5" title={label}>
      {icon}
      <span className={`text-sm font-medium ${color || ''}`} style={color ? undefined : { color: 'var(--color-text-primary)' }}>{value}</span>
    </div>
  );
}
