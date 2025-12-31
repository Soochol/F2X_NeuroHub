/**
 * HealthMetrics Component
 *
 * Displays station health metrics with visual indicators
 */

import { Progress, Tooltip } from 'antd';
import {
  Activity,
  HardDrive,
  Clock,
  Server,
  Wifi,
  WifiOff,
  AlertTriangle,
  CheckCircle,
  XCircle,
} from 'lucide-react';
import type { StationHealth } from '@/types/station';
import styles from './HealthMetrics.module.css';

interface HealthMetricsProps {
  health: StationHealth;
  showDetails?: boolean;
}

const formatUptime = (seconds: number): string => {
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
  if (seconds < 86400) {
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${mins}m`;
  }
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  return `${days}d ${hours}h`;
};

const getHealthStatusConfig = (status: 'healthy' | 'degraded' | 'unhealthy') => {
  switch (status) {
    case 'healthy':
      return {
        icon: CheckCircle,
        color: 'var(--color-success)',
        label: 'Healthy',
        description: 'All systems are operating normally',
      };
    case 'degraded':
      return {
        icon: AlertTriangle,
        color: 'var(--color-warning)',
        label: 'Degraded',
        description: 'Some systems have issues',
      };
    case 'unhealthy':
      return {
        icon: XCircle,
        color: 'var(--color-error)',
        label: 'Unhealthy',
        description: 'System maintenance required',
      };
  }
};

const getDiskUsageColor = (usage: number): string => {
  if (usage < 60) return 'var(--color-success)';
  if (usage < 80) return 'var(--color-warning)';
  return 'var(--color-error)';
};

export const HealthMetrics = ({ health, showDetails = true }: HealthMetricsProps) => {
  const statusConfig = getHealthStatusConfig(health.status);
  const StatusIcon = statusConfig.icon;

  return (
    <div className={styles.container}>
      {/* Overall Status */}
      <div className={styles.statusSection}>
        <div
          className={styles.statusBadge}
          style={{ backgroundColor: statusConfig.color }}
        >
          <StatusIcon size={18} />
          <span>{statusConfig.label}</span>
        </div>
        {showDetails && (
          <p className={styles.statusDescription}>{statusConfig.description}</p>
        )}
      </div>

      {/* Metrics Grid */}
      <div className={styles.metricsGrid}>
        {/* Disk Usage */}
        <div className={styles.metricCard}>
          <div className={styles.metricHeader}>
            <HardDrive size={16} />
            <span>Disk Usage</span>
          </div>
          <div className={styles.metricContent}>
            <Progress
              type="dashboard"
              percent={health.diskUsage}
              strokeColor={getDiskUsageColor(health.diskUsage)}
              trailColor="var(--color-bg-tertiary)"
              size={80}
              format={(percent) => (
                <span className={styles.progressText}>{percent}%</span>
              )}
            />
          </div>
          {health.diskUsage > 80 && (
            <div className={styles.metricWarning}>
              <AlertTriangle size={12} />
              <span>Low disk space</span>
            </div>
          )}
        </div>

        {/* Running Batches */}
        <div className={styles.metricCard}>
          <div className={styles.metricHeader}>
            <Activity size={16} />
            <span>Running Batches</span>
          </div>
          <div className={styles.metricContent}>
            <div className={styles.largeNumber}>{health.batchesRunning}</div>
            <span className={styles.metricLabel}>batches</span>
          </div>
        </div>

        {/* Uptime */}
        <div className={styles.metricCard}>
          <div className={styles.metricHeader}>
            <Clock size={16} />
            <span>Uptime</span>
          </div>
          <div className={styles.metricContent}>
            <div className={styles.uptimeValue}>{formatUptime(health.uptime)}</div>
          </div>
        </div>

        {/* Backend Connection */}
        <div className={styles.metricCard}>
          <div className={styles.metricHeader}>
            <Server size={16} />
            <span>Backend Connection</span>
          </div>
          <div className={styles.metricContent}>
            {health.backendStatus === 'connected' ? (
              <div className={styles.connectionStatus}>
                <Wifi size={24} className={styles.connectedIcon} />
                <span className={styles.connectedText}>Connected</span>
              </div>
            ) : (
              <div className={styles.connectionStatus}>
                <WifiOff size={24} className={styles.disconnectedIcon} />
                <span className={styles.disconnectedText}>Disconnected</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Version Info */}
      {showDetails && health.version && (
        <div className={styles.versionInfo}>
          <span className={styles.versionLabel}>Station Service</span>
          <span className={styles.versionValue}>v{health.version}</span>
        </div>
      )}
    </div>
  );
};

export default HealthMetrics;
