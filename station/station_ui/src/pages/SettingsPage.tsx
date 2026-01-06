/**
 * Settings page - System configuration.
 */

import { useState, useEffect } from 'react';
import {
  Settings,
  Server,
  Moon,
  Sun,
  RefreshCw,
  Edit2,
  Save,
  X,
  Loader2,
  Play,
  Pause,
  Cloud,
  ScanBarcode,
  FolderOpen,
} from 'lucide-react';
import { useSystemInfo, useHealthStatus, useUpdateStationInfo, useWorkflowConfig, useUpdateWorkflowConfig, useBackendConfig, useUpdateBackendConfig } from '../hooks';
import { useUIStore } from '../stores/uiStore';
import { useNotificationStore } from '../stores/notificationStore';
import { Button } from '../components/atoms/Button';
import { LoadingSpinner } from '../components/atoms/LoadingSpinner';
import { StatusBadge } from '../components/atoms/StatusBadge';

export function SettingsPage() {
  const { data: systemInfo, isLoading: infoLoading, refetch: refetchInfo } = useSystemInfo();
  const { data: health, isLoading: healthLoading, refetch: refetchHealth } = useHealthStatus();
  const { data: workflowConfig, isLoading: workflowLoading, refetch: refetchWorkflow } = useWorkflowConfig();
  const { data: backendConfig, isLoading: backendLoading, refetch: refetchBackend } = useBackendConfig();
  const updateStationInfo = useUpdateStationInfo();
  const updateWorkflow = useUpdateWorkflowConfig();
  const updateBackend = useUpdateBackendConfig();
  const addNotification = useNotificationStore((state) => state.addNotification);

  const theme = useUIStore((state) => state.theme);
  const toggleTheme = useUIStore((state) => state.toggleTheme);

  // Edit mode state for station info
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    id: '',
    name: '',
    description: '',
  });

  // Edit mode state for backend config
  const [isEditingBackend, setIsEditingBackend] = useState(false);
  const [backendForm, setBackendForm] = useState({
    url: '',
    syncInterval: 30,
    stationId: '',
    timeout: 30,
    maxRetries: 5,
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

  // Sync backend form when data loads
  useEffect(() => {
    if (backendConfig && !isEditingBackend) {
      setBackendForm({
        url: backendConfig.url,
        syncInterval: backendConfig.syncInterval,
        stationId: backendConfig.stationId,
        timeout: backendConfig.timeout,
        maxRetries: backendConfig.maxRetries,
      });
    }
  }, [backendConfig, isEditingBackend]);

  const handleRefresh = () => {
    refetchInfo();
    refetchHealth();
    refetchWorkflow();
    refetchBackend();
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

  const handleWorkflowToggle = async () => {
    if (!workflowConfig) return;

    const newEnabled = !workflowConfig.enabled;
    try {
      await updateWorkflow.mutateAsync({ enabled: newEnabled });
      addNotification({
        type: 'success',
        title: newEnabled ? 'Process Workflow Enabled' : 'Process Workflow Disabled',
        message: newEnabled
          ? 'WIP process start/complete is now enabled.'
          : 'WIP process start/complete is now disabled.',
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Update Failed',
        message: error instanceof Error ? error.message : 'Failed to update workflow configuration',
      });
    }
  };

  const handleWipInputModeChange = async (mode: 'popup' | 'barcode') => {
    try {
      await updateWorkflow.mutateAsync({ input_mode: mode });
      addNotification({
        type: 'success',
        title: 'WIP Input Mode Changed',
        message: mode === 'popup'
          ? 'WIP ID will be entered manually via popup.'
          : 'WIP ID will be read from barcode scanner.',
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Update Failed',
        message: error instanceof Error ? error.message : 'Failed to update workflow configuration',
      });
    }
  };

  const handleAutoSequenceStartToggle = async () => {
    if (!workflowConfig) return;

    const newValue = !workflowConfig.auto_sequence_start;
    try {
      await updateWorkflow.mutateAsync({ auto_sequence_start: newValue });
      addNotification({
        type: 'success',
        title: newValue ? 'Auto-start Enabled' : 'Auto-start Disabled',
        message: newValue
          ? 'Sequence will start automatically after WIP scan.'
          : 'Sequence must be started manually after WIP scan.',
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Update Failed',
        message: error instanceof Error ? error.message : 'Failed to update workflow configuration',
      });
    }
  };

  // Backend config handlers
  const handleBackendEditStart = () => {
    if (backendConfig) {
      setBackendForm({
        url: backendConfig.url,
        syncInterval: backendConfig.syncInterval,
        stationId: backendConfig.stationId,
        timeout: backendConfig.timeout,
        maxRetries: backendConfig.maxRetries,
      });
    }
    setIsEditingBackend(true);
  };

  const handleBackendEditCancel = () => {
    setIsEditingBackend(false);
    if (backendConfig) {
      setBackendForm({
        url: backendConfig.url,
        syncInterval: backendConfig.syncInterval,
        stationId: backendConfig.stationId,
        timeout: backendConfig.timeout,
        maxRetries: backendConfig.maxRetries,
      });
    }
  };

  const handleBackendEditSave = async () => {
    if (!backendForm.url.trim()) {
      addNotification({
        type: 'error',
        title: 'Validation Error',
        message: 'Backend URL is required',
      });
      return;
    }

    try {
      await updateBackend.mutateAsync({
        url: backendForm.url.trim(),
        syncInterval: backendForm.syncInterval,
        stationId: backendForm.stationId.trim(),
        timeout: backendForm.timeout,
        maxRetries: backendForm.maxRetries,
      });
      setIsEditingBackend(false);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Backend configuration updated successfully',
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Update Failed',
        message: error instanceof Error ? error.message : 'Failed to update backend configuration',
      });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Settings className="w-6 h-6 text-brand-500" />
          <h2 className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>
            Settings
          </h2>
        </div>
        <Button variant="ghost" size="sm" onClick={handleRefresh}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      <div className="flex flex-col gap-6 max-w-2xl mx-auto w-full">
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
                    disabled
                    hint="Configured in station.yaml"
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
                </>
              )}
            </div>
          )}
        </Section>

        {/* Paths Configuration */}
        <Section
          icon={<FolderOpen className="w-5 h-5" />}
          title="Paths"
          isLoading={infoLoading}
        >
          {systemInfo && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span style={{ color: 'var(--color-text-secondary)' }}>Sequences Directory</span>
                <span
                  className="text-sm font-mono px-2 py-1 rounded"
                  style={{
                    backgroundColor: 'var(--color-bg-tertiary)',
                    color: 'var(--color-text-primary)',
                  }}
                >
                  {systemInfo.sequencesDir || 'sequences'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span style={{ color: 'var(--color-text-secondary)' }}>Data Directory</span>
                <span
                  className="text-sm font-mono px-2 py-1 rounded"
                  style={{
                    backgroundColor: 'var(--color-bg-tertiary)',
                    color: 'var(--color-text-primary)',
                  }}
                >
                  {systemInfo.dataDir || 'data'}
                </span>
              </div>
              <div
                className="text-xs p-2 rounded"
                style={{
                  backgroundColor: 'var(--color-bg-tertiary)',
                  color: 'var(--color-text-tertiary)',
                }}
              >
                Paths are configured in station.yaml. Relative paths are resolved from project root.
              </div>
            </div>
          )}
        </Section>

        {/* Workflow Settings (Process Start/Complete) */}
        <Section
          icon={
            workflowConfig?.enabled ? (
              <Play className="w-5 h-5" />
            ) : (
              <Pause className="w-5 h-5" />
            )
          }
          title="Process Workflow"
          isLoading={workflowLoading}
        >
          {workflowConfig && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <span className="font-medium" style={{ color: 'var(--color-text-primary)' }}>
                    WIP Process Start/Complete
                  </span>
                  <p className="text-sm mt-1" style={{ color: 'var(--color-text-tertiary)' }}>
                    Sync with backend MES for process tracking
                  </p>
                </div>
                <ToggleSwitch
                  enabled={workflowConfig.enabled}
                  onToggle={handleWorkflowToggle}
                  disabled={updateWorkflow.isPending}
                />
              </div>
              {workflowConfig.enabled && (
                <>
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="font-medium" style={{ color: 'var(--color-text-primary)' }}>
                        WIP Input Mode
                      </span>
                      <p className="text-sm mt-1" style={{ color: 'var(--color-text-tertiary)' }}>
                        How to provide WIP ID for process tracking
                      </p>
                    </div>
                    <select
                      value={workflowConfig.input_mode}
                      onChange={(e) => handleWipInputModeChange(e.target.value as 'popup' | 'barcode')}
                      disabled={updateWorkflow.isPending}
                      className="px-3 py-1.5 text-sm rounded border outline-none transition-colors cursor-pointer disabled:opacity-50"
                      style={{
                        backgroundColor: 'var(--color-bg-primary)',
                        borderColor: 'var(--color-border-default)',
                        color: 'var(--color-text-primary)',
                      }}
                    >
                      <option value="popup">Manual Input (Popup)</option>
                      <option value="barcode">Barcode Scanner</option>
                    </select>
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="font-medium" style={{ color: 'var(--color-text-primary)' }}>
                        Auto-start Sequence
                      </span>
                      <p className="text-sm mt-1" style={{ color: 'var(--color-text-tertiary)' }}>
                        Start sequence automatically after WIP scan
                      </p>
                    </div>
                    <ToggleSwitch
                      enabled={workflowConfig.auto_sequence_start}
                      onToggle={handleAutoSequenceStartToggle}
                      disabled={updateWorkflow.isPending}
                    />
                  </div>
                </>
              )}
              <div
                className="text-xs p-2 rounded"
                style={{
                  backgroundColor: workflowConfig.enabled
                    ? 'rgba(62, 207, 142, 0.1)'
                    : 'var(--color-bg-tertiary)',
                  color: workflowConfig.enabled
                    ? 'var(--color-brand-500)'
                    : 'var(--color-text-tertiary)',
                }}
              >
                {workflowConfig.enabled
                  ? 'Enabled: Automatically calls process start/complete API during sequence execution.'
                  : 'Disabled: Runs sequence only without process tracking.'}
              </div>
            </div>
          )}
        </Section>

        {/* Barcode Scanner Settings - only show when input_mode is barcode */}
        {workflowConfig?.enabled && workflowConfig?.input_mode === 'barcode' && (
          <Section
            icon={<ScanBarcode className="w-5 h-5" />}
            title="Barcode Scanner"
          >
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span style={{ color: 'var(--color-text-secondary)' }}>Type</span>
                <select
                  value="serial"
                  disabled
                  className="px-3 py-1.5 text-sm rounded border outline-none transition-colors cursor-not-allowed opacity-60"
                  style={{
                    backgroundColor: 'var(--color-bg-primary)',
                    borderColor: 'var(--color-border-default)',
                    color: 'var(--color-text-primary)',
                  }}
                >
                  <option value="serial">Serial (COM Port)</option>
                  <option value="usb_hid">USB HID</option>
                  <option value="keyboard_wedge">Keyboard Wedge</option>
                </select>
              </div>
              <div className="flex items-center justify-between">
                <span style={{ color: 'var(--color-text-secondary)' }}>Port</span>
                <input
                  type="text"
                  value="COM3"
                  disabled
                  placeholder="e.g., COM3 or /dev/ttyUSB0"
                  className="px-3 py-1.5 text-sm rounded border outline-none transition-colors cursor-not-allowed opacity-60"
                  style={{
                    backgroundColor: 'var(--color-bg-primary)',
                    borderColor: 'var(--color-border-default)',
                    color: 'var(--color-text-primary)',
                    width: '140px',
                  }}
                />
              </div>
              <div className="flex items-center justify-between">
                <span style={{ color: 'var(--color-text-secondary)' }}>Baudrate</span>
                <select
                  value="9600"
                  disabled
                  className="px-3 py-1.5 text-sm rounded border outline-none transition-colors cursor-not-allowed opacity-60"
                  style={{
                    backgroundColor: 'var(--color-bg-primary)',
                    borderColor: 'var(--color-border-default)',
                    color: 'var(--color-text-primary)',
                  }}
                >
                  <option value="9600">9600</option>
                  <option value="19200">19200</option>
                  <option value="38400">38400</option>
                  <option value="115200">115200</option>
                </select>
              </div>
              <div className="flex items-center justify-between">
                <span style={{ color: 'var(--color-text-secondary)' }}>Status</span>
                <StatusBadge status="disconnected" size="sm" />
              </div>
              <div
                className="text-xs p-2 rounded"
                style={{
                  backgroundColor: 'var(--color-bg-tertiary)',
                  color: 'var(--color-text-tertiary)',
                }}
              >
                Barcode scanner configuration is per-batch. Configure in batch settings for full functionality (Phase 2).
              </div>
            </div>
          </Section>
        )}

        {/* Connection Settings */}
        <Section
          icon={<Cloud className="w-5 h-5" />}
          title="Backend Connection"
          isLoading={backendLoading || healthLoading}
          action={
            !isEditingBackend ? (
              <Button variant="ghost" size="sm" onClick={handleBackendEditStart}>
                <Edit2 className="w-4 h-4" />
              </Button>
            ) : null
          }
        >
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span style={{ color: 'var(--color-text-secondary)' }}>Status</span>
              <StatusBadge
                status={health?.backendStatus === 'connected' ? 'connected' : 'disconnected'}
                size="sm"
              />
            </div>
            {isEditingBackend ? (
              <>
                <EditableRow
                  label="Backend URL"
                  value={backendForm.url}
                  onChange={(value) => setBackendForm((prev) => ({ ...prev, url: value }))}
                  placeholder="http://localhost:8000"
                />
                <EditableRow
                  label="Station ID"
                  value={backendForm.stationId}
                  onChange={(value) => setBackendForm((prev) => ({ ...prev, stationId: value }))}
                  placeholder="station_001"
                  disabled
                  hint="Must match API Key"
                />
                <div className="flex items-center justify-between gap-4">
                  <label
                    className="text-sm whitespace-nowrap"
                    style={{ color: 'var(--color-text-secondary)' }}
                  >
                    Sync Interval (sec)
                  </label>
                  <input
                    type="number"
                    min={5}
                    max={3600}
                    value={backendForm.syncInterval}
                    onChange={(e) => setBackendForm((prev) => ({ ...prev, syncInterval: parseInt(e.target.value) || 30 }))}
                    className="w-24 px-3 py-1.5 text-sm rounded border outline-none transition-colors"
                    style={{
                      backgroundColor: 'var(--color-bg-primary)',
                      borderColor: 'var(--color-border-default)',
                      color: 'var(--color-text-primary)',
                    }}
                  />
                </div>
                <div className="flex items-center justify-between gap-4">
                  <label
                    className="text-sm whitespace-nowrap"
                    style={{ color: 'var(--color-text-secondary)' }}
                  >
                    Timeout (sec)
                  </label>
                  <input
                    type="number"
                    min={1}
                    max={300}
                    value={backendForm.timeout}
                    onChange={(e) => setBackendForm((prev) => ({ ...prev, timeout: parseFloat(e.target.value) || 30 }))}
                    className="w-24 px-3 py-1.5 text-sm rounded border outline-none transition-colors"
                    style={{
                      backgroundColor: 'var(--color-bg-primary)',
                      borderColor: 'var(--color-border-default)',
                      color: 'var(--color-text-primary)',
                    }}
                  />
                </div>
                <div className="flex items-center justify-between gap-4">
                  <label
                    className="text-sm whitespace-nowrap"
                    style={{ color: 'var(--color-text-secondary)' }}
                  >
                    Max Retries
                  </label>
                  <input
                    type="number"
                    min={0}
                    max={10}
                    value={backendForm.maxRetries}
                    onChange={(e) => setBackendForm((prev) => ({ ...prev, maxRetries: parseInt(e.target.value) || 5 }))}
                    className="w-24 px-3 py-1.5 text-sm rounded border outline-none transition-colors"
                    style={{
                      backgroundColor: 'var(--color-bg-primary)',
                      borderColor: 'var(--color-border-default)',
                      color: 'var(--color-text-primary)',
                    }}
                  />
                </div>
                <div className="flex items-center justify-end gap-2 pt-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleBackendEditCancel}
                    disabled={updateBackend.isPending}
                  >
                    <X className="w-4 h-4 mr-1" />
                    Cancel
                  </Button>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={handleBackendEditSave}
                    disabled={updateBackend.isPending}
                  >
                    {updateBackend.isPending ? (
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
                <InfoRow label="Backend URL" value={backendConfig?.url || '-'} />
                <InfoRow label="Station ID" value={backendConfig?.stationId || '-'} />
                <InfoRow label="Sync Interval" value={backendConfig ? `${backendConfig.syncInterval}s` : '-'} />
                <InfoRow label="Timeout" value={backendConfig ? `${backendConfig.timeout}s` : '-'} />
                <InfoRow label="Max Retries" value={backendConfig?.maxRetries?.toString() || '-'} />
                <InfoRow label="API Key" value={backendConfig?.apiKeyMasked || '-'} />
              </>
            )}
            <div
              className="text-xs p-2 rounded"
              style={{
                backgroundColor: 'var(--color-bg-tertiary)',
                color: 'var(--color-text-tertiary)',
              }}
            >
              API Key cannot be modified through UI for security reasons.
            </div>
          </div>
        </Section>

        {/* Appearance */}
        <Section
          icon={theme === 'dark' ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
          title="Appearance"
        >
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <span className="font-medium" style={{ color: 'var(--color-text-primary)' }}>
                  Theme
                </span>
                <p className="text-sm mt-1" style={{ color: 'var(--color-text-tertiary)' }}>
                  Switch between dark and light mode
                </p>
              </div>
              <Button variant="secondary" size="sm" onClick={toggleTheme}>
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

      {/* Footer */}
      <div
        className="p-4 rounded-lg border max-w-2xl mx-auto w-full"
        style={{
          backgroundColor: 'var(--color-bg-secondary)',
          borderColor: 'var(--color-border-default)',
        }}
      >
        <div className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>
          Station Service v{systemInfo?.version ?? '...'}
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
      <span className="font-medium" style={{ color: 'var(--color-text-primary)' }}>
        {value}
      </span>
    </div>
  );
}

interface EditableRowProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  hint?: string;
}

function EditableRow({ label, value, onChange, placeholder, disabled, hint }: EditableRowProps) {
  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center justify-between gap-4">
        <label
          className="text-sm whitespace-nowrap"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          {label}
        </label>
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          disabled={disabled}
          className={`flex-1 px-3 py-1.5 text-sm rounded border outline-none transition-colors ${disabled ? 'cursor-not-allowed opacity-60' : ''}`}
          style={{
            backgroundColor: disabled ? 'var(--color-bg-tertiary)' : 'var(--color-bg-primary)',
            borderColor: 'var(--color-border-default)',
            color: 'var(--color-text-primary)',
          }}
        />
      </div>
      {hint && (
        <span className="text-xs ml-auto" style={{ color: 'var(--color-text-tertiary)' }}>
          {hint}
        </span>
      )}
    </div>
  );
}

interface ToggleSwitchProps {
  enabled: boolean;
  onToggle: () => void;
  disabled?: boolean;
}

function ToggleSwitch({ enabled, onToggle, disabled }: ToggleSwitchProps) {
  return (
    <button
      onClick={onToggle}
      disabled={disabled}
      className="relative inline-flex h-6 w-11 items-center rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      style={{
        backgroundColor: enabled ? 'var(--color-brand-500)' : 'var(--color-bg-tertiary)',
      }}
    >
      <span
        className="inline-block h-4 w-4 transform rounded-full bg-white transition-transform"
        style={{
          transform: enabled ? 'translateX(24px)' : 'translateX(4px)',
        }}
      />
    </button>
  );
}
