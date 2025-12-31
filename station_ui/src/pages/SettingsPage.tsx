/**
 * Settings page - System configuration and status.
 */

import { useState, useEffect } from 'react';
import { Settings, Server, Monitor, Database, Moon, Sun, RefreshCw, Edit2, Save, X, Loader2 } from 'lucide-react';
import { useSystemInfo, useHealthStatus, useUpdateStationInfo } from '../hooks';
import { useUIStore } from '../stores/uiStore';
import { useConnectionStore } from '../stores/connectionStore';
import { useNotificationStore } from '../stores/notificationStore';
import { Button } from '../components/atoms/Button';
import { StatusBadge } from '../components/atoms/StatusBadge';
import { ProgressBar } from '../components/atoms/ProgressBar';
import { LoadingSpinner } from '../components/atoms/LoadingSpinner';

export function SettingsPage() {
  const { data: systemInfo, isLoading: infoLoading, refetch: refetchInfo } = useSystemInfo();
  const { data: health, isLoading: healthLoading, refetch: refetchHealth } = useHealthStatus();
  const updateStationInfo = useUpdateStationInfo();
  const addNotification = useNotificationStore((state) => state.addNotification);

  const theme = useUIStore((state) => state.theme);
  const toggleTheme = useUIStore((state) => state.toggleTheme);
  const websocketStatus = useConnectionStore((state) => state.websocketStatus);
  const lastHeartbeat = useConnectionStore((state) => state.lastHeartbeat);

  // Edit mode state
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    id: '',
    name: '',
    description: '',
  });

  // Sync form with systemInfo when data loads (only when not editing)
  const stationId = systemInfo?.stationId;
  const stationName = systemInfo?.stationName;
  const stationDescription = systemInfo?.description;

  useEffect(() => {
    if (stationId && stationName && !isEditing) {
      setEditForm({
        id: stationId,
        name: stationName,
        description: stationDescription || '',
      });
    }
  }, [stationId, stationName, stationDescription, isEditing]);

  const handleRefresh = () => {
    refetchInfo();
    refetchHealth();
  };

  const handleEditStart = () => {
    if (systemInfo) {
      setEditForm({
        id: systemInfo.stationId,
        name: systemInfo.stationName,
        description: systemInfo.description || '',
      });
    }
    setIsEditing(true);
  };

  const handleEditCancel = () => {
    setIsEditing(false);
    if (systemInfo) {
      setEditForm({
        id: systemInfo.stationId,
        name: systemInfo.stationName,
        description: systemInfo.description || '',
      });
    }
  };

  const handleEditSave = async () => {
    if (!editForm.id.trim() || !editForm.name.trim()) {
      addNotification({
        type: 'error',
        title: 'Validation Error',
        message: 'Station ID and Name are required',
      });
      return;
    }

    try {
      await updateStationInfo.mutateAsync({
        id: editForm.id.trim(),
        name: editForm.name.trim(),
        description: editForm.description.trim(),
      });
      setIsEditing(false);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Station information updated successfully',
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Update Failed',
        message: error instanceof Error ? error.message : 'Failed to update station information',
      });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Settings className="w-6 h-6 text-brand-500" />
          <h2 className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>Settings</h2>
        </div>
        <Button variant="ghost" size="sm" onClick={handleRefresh}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Station Info */}
        <Section
          icon={<Server className="w-5 h-5" />}
          title="Station Information"
          isLoading={infoLoading}
          action={
            !isEditing ? (
              <Button variant="ghost" size="sm" onClick={handleEditStart}>
                <Edit2 className="w-4 h-4" />
              </Button>
            ) : null
          }
        >
          {systemInfo && (
            <div className="space-y-3">
              {isEditing ? (
                <>
                  <EditableRow
                    label="Station ID"
                    value={editForm.id}
                    onChange={(value) => setEditForm((prev) => ({ ...prev, id: value }))}
                    placeholder="e.g., station_001"
                  />
                  <EditableRow
                    label="Station Name"
                    value={editForm.name}
                    onChange={(value) => setEditForm((prev) => ({ ...prev, name: value }))}
                    placeholder="e.g., Test Station 1"
                  />
                  <EditableRow
                    label="Description"
                    value={editForm.description}
                    onChange={(value) => setEditForm((prev) => ({ ...prev, description: value }))}
                    placeholder="e.g., PCB voltage testing station"
                  />
                  <div className="flex items-center justify-end gap-2 pt-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleEditCancel}
                      disabled={updateStationInfo.isPending}
                    >
                      <X className="w-4 h-4 mr-1" />
                      Cancel
                    </Button>
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={handleEditSave}
                      disabled={updateStationInfo.isPending}
                    >
                      {updateStationInfo.isPending ? (
                        <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                      ) : (
                        <Save className="w-4 h-4 mr-1" />
                      )}
                      Save
                    </Button>
                  </div>
                </>
              ) : (
                <>
                  <InfoRow label="Station ID" value={systemInfo.stationId} />
                  <InfoRow label="Station Name" value={systemInfo.stationName} />
                  <InfoRow label="Description" value={systemInfo.description || '-'} />
                  <InfoRow label="Version" value={systemInfo.version} />
                  <InfoRow label="Uptime" value={formatUptime(systemInfo.uptime)} />
                </>
              )}
            </div>
          )}
        </Section>

        {/* Connection Status */}
        <Section
          icon={<Monitor className="w-5 h-5" />}
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
                  <span className="font-medium" style={{ color: 'var(--color-text-primary)' }}>{health.batchesRunning}</span>
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span style={{ color: 'var(--color-text-secondary)' }}>Disk Usage</span>
                  <span style={{ color: 'var(--color-text-primary)' }}>{health.diskUsage.toFixed(1)}%</span>
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

        {/* Appearance */}
        <Section icon={theme === 'dark' ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />} title="Appearance">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <span className="font-medium" style={{ color: 'var(--color-text-primary)' }}>Theme</span>
                <p className="text-sm mt-1" style={{ color: 'var(--color-text-tertiary)' }}>
                  Switch between dark and light mode
                </p>
              </div>
              <Button
                variant="secondary"
                size="sm"
                onClick={toggleTheme}
              >
                {theme === 'dark' ? (
                  <>
                    <Sun className="w-4 h-4 mr-2" />
                    Light
                  </>
                ) : (
                  <>
                    <Moon className="w-4 h-4 mr-2" />
                    Dark
                  </>
                )}
              </Button>
            </div>
          </div>
        </Section>
      </div>

      {/* System Info Footer */}
      <div className="p-4 rounded-lg border" style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)' }}>
        <div className="flex items-center justify-between text-sm" style={{ color: 'var(--color-text-tertiary)' }}>
          <span>Station Service v{systemInfo?.version ?? '...'}</span>
          <span>
            WebSocket: {websocketStatus} | Backend:{' '}
            {health?.backendStatus ?? 'unknown'}
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
  action?: React.ReactNode;
}

function Section({ icon, title, children, isLoading, action }: SectionProps) {
  return (
    <div className="p-4 rounded-lg border" style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)' }}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="flex items-center gap-2 text-lg font-semibold" style={{ color: 'var(--color-text-primary)' }}>
          {icon}
          {title}
        </h3>
        {action}
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
      <span className="font-medium" style={{ color: 'var(--color-text-primary)' }}>{value}</span>
    </div>
  );
}

interface EditableRowProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

function EditableRow({ label, value, onChange, placeholder }: EditableRowProps) {
  return (
    <div className="flex items-center justify-between gap-4">
      <label className="text-sm whitespace-nowrap" style={{ color: 'var(--color-text-secondary)' }}>
        {label}
      </label>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="flex-1 px-3 py-1.5 text-sm rounded border outline-none transition-colors"
        style={{
          backgroundColor: 'var(--color-bg-primary)',
          borderColor: 'var(--color-border-default)',
          color: 'var(--color-text-primary)',
        }}
      />
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
