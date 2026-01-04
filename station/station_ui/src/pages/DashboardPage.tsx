/**
 * Dashboard page - Main overview of station status.
 */

import { useEffect, useMemo } from 'react';
import { Activity, CheckCircle, XCircle, WifiOff, ServerOff, RefreshCw } from 'lucide-react';
import { useBatchList, useHealthStatus, useWebSocket, useSystemInfo, useAllBatchStatistics } from '../hooks';
import { useLogStore } from '../stores/logStore';
import { useBatchStore } from '../stores/batchStore';
import { useConnectionStore } from '../stores/connectionStore';
import { useShallow } from 'zustand/react/shallow';
import { StatsCard } from '../components/molecules/StatsCard';
import { LogEntryRow } from '../components/molecules/LogEntryRow';
import { ProgressBar } from '../components/atoms/ProgressBar';
import { StatusBadge } from '../components/atoms/StatusBadge';
import { LoadingOverlay } from '../components/atoms/LoadingSpinner';
import { BatchOverviewCard } from '../components/molecules/BatchOverviewCard';

export function DashboardPage() {
  const { data: batches, isLoading: batchesLoading, isError: batchesError, refetch: refetchBatches } = useBatchList();
  const { data: health, isError: healthError, isLoading: healthLoading, refetch: refetchHealth } = useHealthStatus();
  const { data: systemInfo } = useSystemInfo();
  const { data: allStatistics } = useAllBatchStatistics();
  const { subscribe, unsubscribe } = useWebSocket();

  // Get total stats from store (updated in real-time via WebSocket)
  const setAllBatchStatistics = useBatchStore((state) => state.setAllBatchStatistics);
  const batchStatistics = useBatchStore(useShallow((state) => state.batchStatistics));

  // Compute total stats from batchStatistics (memoized to prevent infinite loops)
  const totalStats = useMemo(() => {
    const total = { total: 0, passCount: 0, fail: 0, passRate: 0 };
    batchStatistics.forEach((s) => {
      total.total += s.total;
      total.passCount += s.passCount;
      total.fail += s.fail;
    });
    total.passRate = total.total > 0 ? total.passCount / total.total : 0;
    return total;
  }, [batchStatistics]);

  // Connection status from store
  const websocketStatus = useConnectionStore((state) => state.websocketStatus);
  const setBackendStatus = useConnectionStore((state) => state.setBackendStatus);

  // Update backend status based on health check
  useEffect(() => {
    if (health) {
      setBackendStatus(health.backendStatus === 'connected' ? 'connected' : 'disconnected');
    } else if (healthError) {
      setBackendStatus('disconnected');
    }
  }, [health, healthError, setBackendStatus]);

  // Sync API statistics to store for real-time updates
  useEffect(() => {
    if (allStatistics) {
      setAllBatchStatistics(allStatistics);
    }
  }, [allStatistics, setAllBatchStatistics]);

  // Use useShallow to prevent re-renders when array contents haven't changed
  const batchesMap = useBatchStore(useShallow((state) => state.batches));
  const storeBatches = useMemo(() => Array.from(batchesMap.values()), [batchesMap]);
  const logs = useLogStore(useShallow((state) => state.logs.slice(-10)));

  // Subscribe to all batches for real-time updates
  useEffect(() => {
    if (batches && batches.length > 0) {
      const batchIds = batches.map((b) => b.id);
      subscribe(batchIds);
      return () => unsubscribe(batchIds);
    }
  }, [batches, subscribe, unsubscribe]);

  // Use store batches if available (more up-to-date from WebSocket)
  const displayBatches = storeBatches.length > 0 ? storeBatches : batches ?? [];


  // Determine if station service is connected (API reachable)
  const isStationServiceConnected = !healthError && !batchesError;

  // Handle retry
  const handleRetry = () => {
    refetchBatches();
    refetchHealth();
  };

  if (batchesLoading && !batches) {
    return <LoadingOverlay message="Loading dashboard..." />;
  }

  return (
    <div className="space-y-6">
      {/* Connection Error Banner */}
      {!isStationServiceConnected && (
        <div
          className="p-4 rounded-lg border flex items-center justify-between"
          style={{
            backgroundColor: 'var(--color-error-bg)',
            borderColor: 'var(--color-error)',
          }}
        >
          <div className="flex items-center gap-3">
            <ServerOff className="w-5 h-5" style={{ color: 'var(--color-error)' }} />
            <div>
              <p className="font-medium" style={{ color: 'var(--color-error)' }}>
                Station Service Disconnected
              </p>
              <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                Unable to connect to station service. Check if the service is running.
              </p>
            </div>
          </div>
          <button
            onClick={handleRetry}
            className="flex items-center gap-2 px-3 py-1.5 rounded text-sm font-medium transition-colors"
            style={{
              backgroundColor: 'var(--color-bg-secondary)',
              color: 'var(--color-text-primary)',
              border: '1px solid var(--color-border-default)',
            }}
          >
            <RefreshCw className="w-4 h-4" />
            Retry
          </button>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatsCard
          title="Total Runs"
          value={totalStats.total}
          icon={<Activity className="w-5 h-5" />}
          variant="default"
        />
        <StatsCard
          title="Pass"
          value={totalStats.passCount}
          icon={<CheckCircle className="w-5 h-5" />}
          variant="success"
        />
        <StatsCard
          title="Fail"
          value={totalStats.fail}
          icon={<XCircle className="w-5 h-5" />}
          variant="error"
        />
      </div>

      {/* System Health */}
      <div
        className="p-4 rounded-lg border transition-colors"
        style={{
          backgroundColor: 'var(--color-bg-secondary)',
          borderColor: 'var(--color-border-default)',
        }}
      >
        <h3
          className="text-lg font-semibold mb-3"
          style={{ color: 'var(--color-text-primary)' }}
        >
          System Health
        </h3>
        <div className="grid grid-cols-3 gap-4 text-sm">
          {/* Station Service Status */}
          <div>
            <span style={{ color: 'var(--color-text-secondary)' }}>Station Service</span>
            <div className="mt-1">
              {healthLoading ? (
                <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                  Checking...
                </span>
              ) : (
                <StatusBadge
                  status={isStationServiceConnected ? (health?.status === 'healthy' ? 'connected' : 'warning') : 'disconnected'}
                  size="sm"
                />
              )}
            </div>
          </div>

          {/* Backend Status */}
          <div>
            <span style={{ color: 'var(--color-text-secondary)' }}>Backend (MES)</span>
            <div className="mt-1">
              {!isStationServiceConnected ? (
                <StatusBadge status="disconnected" size="sm" />
              ) : (
                <StatusBadge
                  status={health?.backendStatus === 'connected' ? 'connected' : 'disconnected'}
                  size="sm"
                />
              )}
            </div>
          </div>

          {/* WebSocket Status */}
          <div>
            <span style={{ color: 'var(--color-text-secondary)' }}>WebSocket</span>
            <div className="mt-1 flex items-center gap-2">
              {websocketStatus === 'disconnected' && (
                <WifiOff className="w-3.5 h-3.5" style={{ color: 'var(--color-text-disabled)' }} />
              )}
              <StatusBadge
                status={websocketStatus === 'connected' ? 'connected' : websocketStatus === 'connecting' ? 'warning' : 'disconnected'}
                size="sm"
              />
            </div>
          </div>
        </div>

        {/* Disk Usage - separate row */}
        <div className="mt-4 pt-4" style={{ borderTop: '1px solid var(--color-border-muted)' }}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
              Disk Usage
            </span>
            <span className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
              {isStationServiceConnected && health?.diskUsage != null && !isNaN(health.diskUsage)
                ? `${health.diskUsage.toFixed(1)}%`
                : '-'}
            </span>
          </div>
          <ProgressBar
            value={isStationServiceConnected && health?.diskUsage != null && !isNaN(health.diskUsage) ? health.diskUsage : 0}
            variant={
              !isStationServiceConnected
                ? 'default'
                : health?.diskUsage != null && health.diskUsage > 90
                  ? 'error'
                  : health?.diskUsage != null && health.diskUsage > 80
                    ? 'warning'
                    : 'default'
            }
            size="sm"
          />
        </div>

        {/* System Info */}
        {systemInfo && (
          <div className="mt-4 pt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-xs" style={{ borderTop: '1px solid var(--color-border-muted)' }}>
            <div>
              <span style={{ color: 'var(--color-text-tertiary)' }}>Station ID</span>
              <div style={{ color: 'var(--color-text-secondary)' }}>{systemInfo.stationId}</div>
            </div>
            <div>
              <span style={{ color: 'var(--color-text-tertiary)' }}>Station Name</span>
              <div style={{ color: 'var(--color-text-secondary)' }}>{systemInfo.stationName}</div>
            </div>
            <div>
              <span style={{ color: 'var(--color-text-tertiary)' }}>Version</span>
              <div style={{ color: 'var(--color-text-secondary)' }}>{systemInfo.version}</div>
            </div>
            <div>
              <span style={{ color: 'var(--color-text-tertiary)' }}>Uptime</span>
              <div style={{ color: 'var(--color-text-secondary)' }}>{formatUptime(systemInfo.uptime)}</div>
            </div>
          </div>
        )}
      </div>

      {/* Batch Status Overview */}
      <div>
        <h3
          className="text-lg font-semibold mb-4"
          style={{ color: 'var(--color-text-primary)' }}
        >
          Batch Status Overview
        </h3>
        {displayBatches.length === 0 ? (
          <div
            className="p-4 rounded-lg border"
            style={{
              backgroundColor: 'var(--color-bg-secondary)',
              borderColor: 'var(--color-border-default)',
            }}
          >
            <p className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>
              No batches configured
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {displayBatches.map((batch: import('../types').Batch) => (
              <BatchOverviewCard key={batch.id} batch={batch} />
            ))}
          </div>
        )}
      </div>

      {/* Recent Activity */}
      <div
        className="p-4 rounded-lg border transition-colors"
        style={{
          backgroundColor: 'var(--color-bg-secondary)',
          borderColor: 'var(--color-border-default)',
        }}
      >
        <h3
          className="text-lg font-semibold mb-4"
          style={{ color: 'var(--color-text-primary)' }}
        >
          Recent Activity
        </h3>
        {logs.length === 0 ? (
          <p className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>
            No recent activity
          </p>
        ) : (
          <div className="space-y-1 max-h-64 overflow-y-auto">
            {logs
              .slice()
              .reverse()
              .map((log) => (
                <LogEntryRow key={log.id} log={log} showBatchId />
              ))}
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Format uptime in seconds to a human-readable string.
 */
function formatUptime(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  if (hours < 24) return `${hours}h ${minutes}m`;
  const days = Math.floor(hours / 24);
  return `${days}d ${hours % 24}h`;
}
