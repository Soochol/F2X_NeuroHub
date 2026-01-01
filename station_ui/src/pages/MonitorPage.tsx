/**
 * Monitor page - System monitoring, health status, and statistics.
 */

import { Activity, Database, Server, RefreshCw, Wifi, Cloud } from 'lucide-react';
import { useSystemInfo, useHealthStatus } from '../hooks';
import { useConnectionStore } from '../stores/connectionStore';
import { Button } from '../components/atoms/Button';
import { StatusBadge } from '../components/atoms/StatusBadge';
import { ProgressBar } from '../components/atoms/ProgressBar';
import { LoadingSpinner } from '../components/atoms/LoadingSpinner';

export function MonitorPage() {
  const { data: systemInfo, isLoading: infoLoading, refetch: refetchInfo } = useSystemInfo();
  const { data: health, isLoading: healthLoading, refetch: refetchHealth } = useHealthStatus();
  const websocketStatus = useConnectionStore((state) => state.websocketStatus);
  const lastHeartbeat = useConnectionStore((state) => state.lastHeartbeat);

  const handleRefresh = () => {
    refetchInfo();
    refetchHealth();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Activity className="w-6 h-6 text-brand-500" />
          <h2 className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>
            Monitor
          </h2>
        </div>
        <Button variant="ghost" size="sm" onClick={handleRefresh}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      <div className="flex flex-col gap-6 max-w-2xl mx-auto w-full">
        {/* Station Overview */}
        <Section
          icon={<Server className="w-5 h-5" />}
          title="Station Overview"
          isLoading={infoLoading}
        >
          {systemInfo && (
            <div className="space-y-3">
              <InfoRow label="Station ID" value={systemInfo.stationId} />
              <InfoRow label="Station Name" value={systemInfo.stationName} />
              <InfoRow label="Description" value={systemInfo.description || '-'} />
              <InfoRow label="Version" value={systemInfo.version} />
              <InfoRow label="Uptime" value={formatUptime(systemInfo.uptime)} />
            </div>
          )}
        </Section>

        {/* Connection Status */}
        <Section
          icon={<Wifi className="w-5 h-5" />}
          title="Connection Status"
          isLoading={healthLoading}
        >
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span style={{ color: 'var(--color-text-secondary)' }}>WebSocket</span>
              <StatusBadge
                status={websocketStatus === 'connected' ? 'connected' : 'disconnected'}
                size="sm"
              />
            </div>
            <div className="flex items-center justify-between">
              <span style={{ color: 'var(--color-text-secondary)' }}>Backend</span>
              <StatusBadge
                status={
                  health?.backendStatus === 'connected' ? 'connected' : 'disconnected'
                }
                size="sm"
              />
            </div>
            {lastHeartbeat && (
              <div className="flex items-center justify-between text-sm">
                <span style={{ color: 'var(--color-text-tertiary)' }}>Last Heartbeat</span>
                <span style={{ color: 'var(--color-text-secondary)' }}>
                  {lastHeartbeat.toLocaleTimeString()}
                </span>
              </div>
            )}
          </div>
        </Section>

        {/* System Health */}
        <Section
          icon={<Database className="w-5 h-5" />}
          title="System Health"
          isLoading={healthLoading}
        >
          {health && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span style={{ color: 'var(--color-text-secondary)' }}>Overall Status</span>
                <StatusBadge
                  status={health.status === 'healthy' ? 'connected' : 'disconnected'}
                  size="sm"
                />
              </div>
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span style={{ color: 'var(--color-text-secondary)' }}>Batches Running</span>
                  <span className="font-medium" style={{ color: 'var(--color-text-primary)' }}>
                    {health.batchesRunning}
                  </span>
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span style={{ color: 'var(--color-text-secondary)' }}>Disk Usage</span>
                  <span style={{ color: 'var(--color-text-primary)' }}>
                    {health.diskUsage.toFixed(1)}%
                  </span>
                </div>
                <ProgressBar
                  value={health.diskUsage}
                  variant={
                    health.diskUsage > 90
                      ? 'error'
                      : health.diskUsage > 70
                        ? 'warning'
                        : 'default'
                  }
                  size="sm"
                />
              </div>
            </div>
          )}
        </Section>

        {/* Sync Status */}
        <Section
          icon={<Cloud className="w-5 h-5" />}
          title="Sync Status"
          isLoading={healthLoading}
        >
          {health && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span style={{ color: 'var(--color-text-secondary)' }}>Backend Connection</span>
                <StatusBadge
                  status={health.backendStatus === 'connected' ? 'connected' : 'disconnected'}
                  size="sm"
                />
              </div>
              <div className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>
                Sync queue and statistics will be displayed here when available.
              </div>
            </div>
          )}
        </Section>
      </div>

      {/* System Info Footer */}
      <div
        className="p-4 rounded-lg border max-w-2xl mx-auto w-full"
        style={{
          backgroundColor: 'var(--color-bg-secondary)',
          borderColor: 'var(--color-border-default)',
        }}
      >
        <div
          className="flex items-center justify-between text-sm"
          style={{ color: 'var(--color-text-tertiary)' }}
        >
          <span>Station Service v{systemInfo?.version ?? '...'}</span>
          <span>
            WebSocket: {websocketStatus} | Backend: {health?.backendStatus ?? 'unknown'}
          </span>
        </div>
      </div>
    </div>
  );
}

interface SectionProps {
  icon: React.ReactNode;
  title: string;
  children: React.ReactNode;
  isLoading?: boolean;
}

function Section({ icon, title, children, isLoading }: SectionProps) {
  return (
    <div
      className="p-4 rounded-lg border"
      style={{
        backgroundColor: 'var(--color-bg-secondary)',
        borderColor: 'var(--color-border-default)',
      }}
    >
      <div className="flex items-center justify-between mb-4">
        <h3
          className="flex items-center gap-2 text-lg font-semibold"
          style={{ color: 'var(--color-text-primary)' }}
        >
          {icon}
          {title}
        </h3>
      </div>
      {isLoading ? (
        <div className="py-8 flex items-center justify-center">
          <LoadingSpinner />
        </div>
      ) : (
        children
      )}
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between">
      <span style={{ color: 'var(--color-text-secondary)' }}>{label}</span>
      <span className="font-medium" style={{ color: 'var(--color-text-primary)' }}>
        {value}
      </span>
    </div>
  );
}

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
