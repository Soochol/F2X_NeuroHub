/**
 * StationCard Component
 *
 * Displays a station's status, health metrics, and batch overview
 */

import { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Progress, Tooltip, Popconfirm } from 'antd';
import { sortBatchesBySlotId } from '@/utils/batchSort';
import {
  Server,
  Wifi,
  WifiOff,
  Activity,
  HardDrive,
  Clock,
  Play,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Loader2,
  Trash2,
} from 'lucide-react';
import type { Station, BatchStatus } from '@/types/station';
import styles from './StationCard.module.css';

interface StationCardProps {
  station: Station;
  onClick?: () => void;
  onDelete?: (stationId: string) => void;
  isDeleting?: boolean;
}

const formatUptime = (seconds: number): string => {
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
  return `${Math.floor(seconds / 86400)}d ${Math.floor((seconds % 86400) / 3600)}h`;
};

const getStatusIcon = (status: BatchStatus, isRunning: boolean) => {
  if (isRunning) {
    return <Loader2 className={styles.spinIcon} size={16} />;
  }

  switch (status) {
    case 'completed':
      return <CheckCircle size={16} className={styles.successIcon} />;
    case 'error':
      return <XCircle size={16} className={styles.errorIcon} />;
    case 'idle':
      return <Clock size={16} className={styles.idleIcon} />;
    default:
      return <Activity size={16} />;
  }
};

const getHealthColor = (status: 'healthy' | 'degraded' | 'unhealthy'): string => {
  switch (status) {
    case 'healthy':
      return 'var(--color-success)';
    case 'degraded':
      return 'var(--color-warning)';
    case 'unhealthy':
      return 'var(--color-error)';
  }
};

export const StationCard = ({ station, onClick, onDelete, isDeleting }: StationCardProps) => {
  const navigate = useNavigate();

  const { runningBatches, totalBatches, avgProgress } = useMemo(() => {
    const batches = station.batches || [];
    const running = batches.filter(b => b.status === 'running' || b.status === 'starting');
    const total = batches.length;
    const progress = running.length > 0
      ? running.reduce((sum, b) => sum + b.progress, 0) / running.length
      : 0;

    return {
      runningBatches: running.length,
      totalBatches: total,
      avgProgress: Math.round(progress),
    };
  }, [station.batches]);

  const sortedBatches = useMemo(() => {
    return sortBatchesBySlotId(station.batches || []);
  }, [station.batches]);

  const handleClick = () => {
    if (onClick) {
      onClick();
    } else {
      navigate(`/stations/${station.id}`);
    }
  };

  const isConnected = station.status === 'connected';
  const isConnecting = station.status === 'connecting';

  return (
    <div
      className={`${styles.card} ${!isConnected ? styles.disconnected : ''}`}
      onClick={handleClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && handleClick()}
    >
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.stationInfo}>
          <div className={styles.iconWrapper}>
            <Server size={20} />
          </div>
          <div className={styles.titleSection}>
            <h3 className={styles.title}>{station.name}</h3>
            <span className={styles.subtitle}>
              {station.host}:{station.port}
            </span>
          </div>
        </div>

        <div className={styles.connectionStatus}>
          {isConnecting ? (
            <Tooltip title="Connecting...">
              <Loader2 className={styles.spinIcon} size={18} />
            </Tooltip>
          ) : isConnected ? (
            <Tooltip title="Connected">
              <Wifi size={18} className={styles.connectedIcon} />
            </Tooltip>
          ) : (
            <Tooltip title="Disconnected">
              <WifiOff size={18} className={styles.disconnectedIcon} />
            </Tooltip>
          )}
        </div>
      </div>

      {/* Content */}
      {isConnected && station.health ? (
        <>
          {/* Health Metrics */}
          <div className={styles.healthSection}>
            <div className={styles.healthBadge} style={{ backgroundColor: getHealthColor(station.health.status) }}>
              {station.health.status.toUpperCase()}
            </div>

            <div className={styles.metricsRow}>
              <Tooltip title="Disk Usage">
                <div className={styles.metric}>
                  <HardDrive size={14} />
                  <span>{station.health.diskUsage}%</span>
                </div>
              </Tooltip>

              <Tooltip title="Uptime">
                <div className={styles.metric}>
                  <Clock size={14} />
                  <span>{formatUptime(station.health.uptime)}</span>
                </div>
              </Tooltip>

              <Tooltip title="Version">
                <div className={styles.metric}>
                  <Activity size={14} />
                  <span>v{station.health.version}</span>
                </div>
              </Tooltip>
            </div>
          </div>

          {/* Batch Overview */}
          <div className={styles.batchSection}>
            <div className={styles.batchHeader}>
              <span className={styles.batchLabel}>Batches</span>
              <span className={styles.batchCount}>
                {runningBatches} running / {totalBatches} total
              </span>
            </div>

            {runningBatches > 0 && (
              <div className={styles.progressSection}>
                <Progress
                  percent={avgProgress}
                  strokeColor="var(--color-brand)"
                  trailColor="var(--color-bg-tertiary)"
                  size="small"
                  showInfo={false}
                />
                <span className={styles.progressText}>{avgProgress}%</span>
              </div>
            )}

            {/* Batch List Preview */}
            <div className={styles.batchList}>
              {sortedBatches.slice(0, 3).map((batch) => (
                <div key={batch.id} className={styles.batchItem}>
                  <div className={styles.batchItemIcon}>
                    {getStatusIcon(batch.status, batch.status === 'running')}
                  </div>
                  <span className={styles.batchName}>{batch.name}</span>
                  {batch.status === 'running' && (
                    <span className={styles.batchProgress}>{Math.round(batch.progress)}%</span>
                  )}
                </div>
              ))}

              {(station.batches?.length || 0) > 3 && (
                <div className={styles.moreBatches}>
                  +{(station.batches?.length || 0) - 3} more
                </div>
              )}
            </div>
          </div>

          {/* Footer */}
          <div className={styles.footer}>
            <div className={styles.actionHint}>
              <Play size={14} />
              <span>Click to view details</span>
            </div>
          </div>
        </>
      ) : (
        /* Disconnected State */
        <div className={styles.disconnectedContent}>
          <AlertTriangle size={32} className={styles.warningIcon} />
          <p className={styles.disconnectedText}>
            {isConnecting ? 'Connecting to station...' : 'Station is offline'}
          </p>
          <span className={styles.disconnectedHint}>
            {station.description || 'Check network connection'}
          </span>
          {!isConnecting && onDelete && (
            <Popconfirm
              title="Delete Station"
              description={`Are you sure you want to remove "${station.name}" from the registry?`}
              onConfirm={(e) => {
                e?.stopPropagation();
                onDelete(station.id);
              }}
              onCancel={(e) => e?.stopPropagation()}
              okText="Delete"
              cancelText="Cancel"
              okButtonProps={{ danger: true, loading: isDeleting }}
            >
              <button
                className={styles.deleteButton}
                onClick={(e) => e.stopPropagation()}
                disabled={isDeleting}
              >
                <Trash2 size={14} />
                <span>Remove from registry</span>
              </button>
            </Popconfirm>
          )}
        </div>
      )}
    </div>
  );
};

export default StationCard;
