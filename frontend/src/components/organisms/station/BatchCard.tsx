/**
 * BatchCard Component
 *
 * Displays batch information with progress tracking (similar to station_ui)
 */

import { Progress, Tooltip, Badge, Popconfirm } from 'antd';
import {
  Play,
  Square,
  CheckCircle,
  XCircle,
  Clock,
  Loader2,
  AlertCircle,
  ChevronRight,
  Trash2,
} from 'lucide-react';
import type { BatchSummary, BatchStatistics } from '@/types/station';
import styles from './BatchCard.module.css';

interface BatchCardProps {
  batch: BatchSummary;
  statistics?: BatchStatistics;
  onStart?: () => void;
  onStop?: () => void;
  onDelete?: () => void;
  onClick?: () => void;
  isLoading?: boolean;
}

const getStatusConfig = (status: string) => {
  switch (status) {
    case 'running':
      return { color: 'var(--color-brand)', icon: Loader2, label: 'Running', spinning: true };
    case 'starting':
      return { color: 'var(--color-warning)', icon: Loader2, label: 'Starting', spinning: true };
    case 'stopping':
      return { color: 'var(--color-warning)', icon: Loader2, label: 'Stopping', spinning: true };
    case 'completed':
      return { color: 'var(--color-success)', icon: CheckCircle, label: 'Completed', spinning: false };
    case 'error':
      return { color: 'var(--color-error)', icon: XCircle, label: 'Error', spinning: false };
    case 'idle':
    default:
      return { color: 'var(--color-text-tertiary)', icon: Clock, label: 'Idle', spinning: false };
  }
};

const getProgressColor = (status: string, lastRunPassed?: boolean) => {
  if (status === 'error') return 'var(--color-error)';
  if (status === 'completed' && lastRunPassed === false) return 'var(--color-error)';
  if (status === 'completed' && lastRunPassed === true) return 'var(--color-success)';
  if (status === 'running' || status === 'starting') return 'var(--color-brand)';
  return 'var(--color-text-tertiary)';
};

const formatDuration = (seconds: number): string => {
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}m ${secs.toFixed(0)}s`;
};

export const BatchCard = ({
  batch,
  statistics,
  onStart,
  onStop,
  onDelete,
  onClick,
  isLoading = false,
}: BatchCardProps) => {
  const statusConfig = getStatusConfig(batch.status);
  const StatusIcon = statusConfig.icon;
  const isRunning = batch.status === 'running' || batch.status === 'starting';
  const isStopping = batch.status === 'stopping';

  const handleAction = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (isRunning || isStopping) {
      onStop?.();
    } else {
      onStart?.();
    }
  };

  return (
    <div
      className={`${styles.card} ${onClick ? styles.clickable : ''}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={(e) => onClick && e.key === 'Enter' && onClick()}
    >
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.batchInfo}>
          <h3 className={styles.title}>{batch.name}</h3>
          <span className={styles.sequence}>
            {batch.sequenceName} v{batch.sequenceVersion}
          </span>
        </div>

        <Badge
          status={statusConfig.spinning ? 'processing' : 'default'}
          color={statusConfig.color}
          text={
            <span className={styles.statusLabel} style={{ color: statusConfig.color }}>
              <StatusIcon
                size={14}
                className={statusConfig.spinning ? styles.spinIcon : ''}
              />
              {statusConfig.label}
            </span>
          }
        />
      </div>

      {/* Progress */}
      <div className={styles.progressSection}>
        <div className={styles.progressHeader}>
          <span className={styles.progressLabel}>
            {batch.currentStep || 'No step running'}
          </span>
          {batch.totalSteps > 0 && (
            <span className={styles.stepCount}>
              Step {batch.stepIndex + 1}/{batch.totalSteps}
            </span>
          )}
        </div>

        <Progress
          percent={batch.progress * 100}
          strokeColor={getProgressColor(batch.status, batch.lastRunPassed)}
          trailColor="var(--color-bg-tertiary)"
          showInfo={false}
          size={{ height: 8 }}
        />

        <div className={styles.progressFooter}>
          <span className={styles.progressPercent}>{Math.round(batch.progress * 100)}%</span>
          {batch.elapsed > 0 && (
            <span className={styles.elapsed}>{formatDuration(batch.elapsed)}</span>
          )}
        </div>
      </div>

      {/* Statistics */}
      {statistics && statistics.total > 0 && (
        <div className={styles.statsSection}>
          <div className={styles.statItem}>
            <span className={styles.statLabel}>Total</span>
            <span className={styles.statValue}>{statistics.total}</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.statLabel}>Pass</span>
            <span className={`${styles.statValue} ${styles.pass}`}>{statistics.pass}</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.statLabel}>Fail</span>
            <span className={`${styles.statValue} ${styles.fail}`}>{statistics.fail}</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.statLabel}>Rate</span>
            <span className={styles.statValue}>{(statistics.passRate * 100).toFixed(1)}%</span>
          </div>
        </div>
      )}

      {/* Last Run Result */}
      {batch.lastRunPassed !== undefined && !isRunning && (
        <div className={styles.lastRunSection}>
          {batch.lastRunPassed ? (
            <div className={styles.lastRunPass}>
              <CheckCircle size={14} />
              <span>Last run passed</span>
            </div>
          ) : (
            <div className={styles.lastRunFail}>
              <XCircle size={14} />
              <span>Last run failed</span>
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      <div className={styles.actions}>
        {(onStart || onStop) && (
          <Tooltip title={isRunning || isStopping ? 'Stop' : 'Start'}>
            <button
              className={`${styles.actionButton} ${isRunning ? styles.stopButton : styles.startButton}`}
              onClick={handleAction}
              disabled={isLoading || isStopping}
            >
              {isLoading ? (
                <Loader2 size={16} className={styles.spinIcon} />
              ) : isRunning || isStopping ? (
                <Square size={16} />
              ) : (
                <Play size={16} />
              )}
            </button>
          </Tooltip>
        )}

        {onDelete && !isRunning && (
          <Tooltip title="Delete batch">
            <button
              className={`${styles.actionButton} ${styles.deleteButton}`}
              onClick={(e) => {
                e.stopPropagation();
                onDelete();
              }}
              disabled={isLoading || isRunning}
            >
              <Trash2 size={16} />
            </button>
          </Tooltip>
        )}

        {onClick && (
          <div className={styles.viewMore}>
            <span>View Details</span>
            <ChevronRight size={16} />
          </div>
        )}
      </div>
    </div>
  );
};

export default BatchCard;
