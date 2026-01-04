/**
 * SystemStatus - Displays overall system health and status information.
 */

import { Activity, Server, HardDrive, Wifi, WifiOff, RefreshCw } from 'lucide-react';
import { useSystemInfo, useHealthStatus } from '../../../hooks';
import { StatusBadge } from '../../atoms/StatusBadge';
import { LoadingSpinner } from '../../atoms/LoadingSpinner';

interface SystemStatusProps {
  /** Show compact view */
  compact?: boolean;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Format uptime in human-readable format.
 */
function formatUptime(seconds: number): string {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);

  if (days > 0) {
    return `${days}d ${hours}h ${minutes}m`;
  }
  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  return `${minutes}m`;
}

/**
 * Format disk usage percentage.
 */
function formatDiskUsage(usage: number): string {
  return `${(usage * 100).toFixed(1)}%`;
}

export function SystemStatus({ compact = false, className = '' }: SystemStatusProps) {
  const { data: systemInfo, isLoading: isLoadingInfo, refetch: refetchInfo } = useSystemInfo();
  const { data: health, isLoading: isLoadingHealth, refetch: refetchHealth } = useHealthStatus();

  const isLoading = isLoadingInfo || isLoadingHealth;

  const handleRefresh = () => {
    void refetchInfo();
    void refetchHealth();
  };

  if (isLoading) {
    return (
      <div className={`bg-zinc-900 rounded-lg border border-zinc-800 p-4 ${className}`}>
        <div className="flex items-center justify-center py-8">
          <LoadingSpinner size="md" />
        </div>
      </div>
    );
  }

  if (compact) {
    return (
      <div className={`flex items-center gap-4 ${className}`}>
        <div className="flex items-center gap-2">
          <Server className="w-4 h-4 text-zinc-400" />
          <span className="text-sm text-zinc-300">{systemInfo?.stationId ?? 'Unknown'}</span>
        </div>
        <StatusBadge
          status={health?.status === 'healthy' ? 'connected' : 'disconnected'}
          size="sm"
        />
        {health?.backendStatus === 'connected' ? (
          <Wifi className="w-4 h-4 text-green-400" />
        ) : (
          <WifiOff className="w-4 h-4 text-red-400" />
        )}
      </div>
    );
  }

  return (
    <div className={`bg-zinc-900 rounded-lg border border-zinc-800 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-brand-400" />
          <h3 className="text-sm font-medium text-zinc-100">System Status</h3>
        </div>
        <button
          onClick={handleRefresh}
          className="p-1.5 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 rounded transition-colors"
          title="Refresh"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Content */}
      <div className="p-4 space-y-4">
        {/* Station Info */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm text-zinc-400">Station</span>
            <span className="text-sm font-medium text-zinc-100">
              {systemInfo?.stationId ?? 'Unknown'} - {systemInfo?.stationName ?? 'Unknown'}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-zinc-400">Version</span>
            <span className="text-sm text-zinc-300">{systemInfo?.version ?? '-'}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-zinc-400">Uptime</span>
            <span className="text-sm text-zinc-300">
              {systemInfo?.uptime != null ? formatUptime(systemInfo.uptime) : '-'}
            </span>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-zinc-800" />

        {/* Health Status */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm text-zinc-400">Health</span>
            <StatusBadge
              status={health?.status === 'healthy' ? 'connected' : 'error'}
              size="sm"
            />
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-zinc-400">Backend</span>
            <div className="flex items-center gap-2">
              {health?.backendStatus === 'connected' ? (
                <>
                  <Wifi className="w-4 h-4 text-green-400" />
                  <span className="text-sm text-green-400">Connected</span>
                </>
              ) : (
                <>
                  <WifiOff className="w-4 h-4 text-red-400" />
                  <span className="text-sm text-red-400">Disconnected</span>
                </>
              )}
            </div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-zinc-400">Running Batches</span>
            <span className="text-sm font-medium text-zinc-100">
              {health?.batchesRunning ?? 0}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-zinc-400">Disk Usage</span>
            <div className="flex items-center gap-2">
              <HardDrive className="w-4 h-4 text-zinc-400" />
              <span
                className={`text-sm ${
                  (health?.diskUsage ?? 0) > 0.9
                    ? 'text-red-400'
                    : (health?.diskUsage ?? 0) > 0.7
                      ? 'text-yellow-400'
                      : 'text-zinc-300'
                }`}
              >
                {health?.diskUsage != null ? formatDiskUsage(health.diskUsage) : '-'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
