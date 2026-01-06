/**
 * BatchConfigEditor - Config tab content for dynamic batch configuration.
 * Uses explicit Save button instead of auto-save for reliability.
 */

import { useState, useEffect, useMemo, useCallback } from 'react';
import { Settings, Search, X, Loader2, Check, AlertTriangle, Save } from 'lucide-react';
import { useUpdateBatch, useBatch, useWorkflowConfig, useProcesses } from '../../../hooks';
import { useNotificationStore } from '../../../stores/notificationStore';
import type { BatchDetail } from '../../../types';

interface BatchConfigEditorProps {
  /** Batch ID */
  batchId: string;
  /** Whether batch is currently running */
  isRunning: boolean;
  /** Callback when dirty state changes */
  onDirtyChange?: (isDirty: boolean) => void;
}

// Type guard to check if batch has detailed info
function isBatchDetail(batch: unknown): batch is BatchDetail {
  return batch !== null && typeof batch === 'object' && 'config' in batch;
}

export function BatchConfigEditor({ batchId, isRunning, onDirtyChange }: BatchConfigEditorProps) {
  const { data: batch } = useBatch(batchId);
  const { data: workflowConfig } = useWorkflowConfig();
  const { data: processes = [] } = useProcesses();
  const updateBatch = useUpdateBatch();
  const addNotification = useNotificationStore((state) => state.addNotification);

  // Local state for editing
  const [editedConfig, setEditedConfig] = useState<Record<string, unknown>>({});
  const [originalConfig, setOriginalConfig] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved'>('idle');

  // Check if MES process is required but not configured
  const isWorkflowEnabled = workflowConfig?.enabled ?? false;
  const processId = editedConfig.processId as number | undefined;
  const headerId = editedConfig.headerId as number | undefined;
  const isMesProcessMissing = isWorkflowEnabled && !processId;

  // Check if there are unsaved changes
  const isDirty = useMemo(() => {
    return JSON.stringify(editedConfig) !== originalConfig;
  }, [editedConfig, originalConfig]);

  // Notify parent of dirty state changes
  useEffect(() => {
    onDirtyChange?.(isDirty);
  }, [isDirty, onDirtyChange]);

  // Sync batch data to local state
  useEffect(() => {
    if (batch && isBatchDetail(batch)) {
      const config = { ...(batch.config || {}) };
      setEditedConfig(config);
      setOriginalConfig(JSON.stringify(config));
      setSaveStatus('idle');
    }
  }, [batch]);

  // Filter config based on search query
  const filteredConfig = useMemo(() => {
    if (!searchQuery.trim()) {
      return Object.entries(editedConfig);
    }
    const query = searchQuery.toLowerCase();
    return Object.entries(editedConfig).filter(
      ([key, value]) =>
        key.toLowerCase().includes(query) ||
        String(value ?? '').toLowerCase().includes(query)
    );
  }, [editedConfig, searchQuery]);

  // Save function - only called when Save button is clicked
  const handleSave = useCallback(async () => {
    if (!batchId || isRunning || !isDirty) return;

    // Validate: If workflow is enabled, MES process must be selected
    if (isWorkflowEnabled && !editedConfig.processId) {
      addNotification({
        type: 'error',
        title: 'MES Process Required',
        message: 'WIP Process Start/Complete is enabled. Please set processId.',
      });
      return;
    }

    setSaveStatus('saving');
    try {
      await updateBatch.mutateAsync({ batchId, request: { config: editedConfig } });
      setOriginalConfig(JSON.stringify(editedConfig));
      setSaveStatus('saved');
      // Reset to idle after showing saved status
      setTimeout(() => setSaveStatus('idle'), 1500);
    } catch (error) {
      setSaveStatus('idle');
      addNotification({
        type: 'error',
        title: 'Save Failed',
        message: error instanceof Error ? error.message : 'Failed to save configuration',
      });
      console.error('[BatchConfigEditor] Failed to save config:', error);
    }
  }, [batchId, isRunning, isDirty, isWorkflowEnabled, editedConfig, updateBatch, addNotification]);

  // Handle config value change (no auto-save, just update local state)
  const handleConfigChange = (key: string, value: string) => {
    const newConfig = { ...editedConfig };
    // Try to parse as number or boolean
    if (value === 'true') {
      newConfig[key] = true;
    } else if (value === 'false') {
      newConfig[key] = false;
    } else if (!isNaN(Number(value)) && value !== '') {
      newConfig[key] = Number(value);
    } else {
      newConfig[key] = value;
    }
    setEditedConfig(newConfig);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div
        className="flex items-center justify-between px-3 py-2 border-b shrink-0"
        style={{ borderColor: 'var(--color-border-default)' }}
      >
        <div className="flex items-center gap-2">
          <Settings className="w-4 h-4" style={{ color: 'var(--color-text-tertiary)' }} />
          <span className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
            Configuration
          </span>
          <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
            ({filteredConfig.length}/{Object.keys(editedConfig).length})
          </span>
        </div>
        {/* Save Button */}
        <div className="flex items-center gap-1">
          {saveStatus === 'saved' ? (
            <div className="flex items-center gap-1 text-xs px-2 py-1" style={{ color: 'var(--color-status-pass)' }}>
              <Check className="w-3 h-3" />
              <span>Saved</span>
            </div>
          ) : (
            <button
              onClick={handleSave}
              disabled={!isDirty || isRunning || saveStatus === 'saving'}
              className="flex items-center gap-1 text-xs px-2 py-1 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              style={{
                backgroundColor: isDirty && saveStatus !== 'saving' ? 'var(--color-brand-500)' : 'var(--color-bg-tertiary)',
                color: isDirty && saveStatus !== 'saving' ? 'white' : 'var(--color-text-tertiary)',
              }}
              title={!isDirty ? 'No changes to save' : isRunning ? 'Cannot save while running' : 'Save changes'}
            >
              {saveStatus === 'saving' ? (
                <>
                  <Loader2 className="w-3 h-3 animate-spin" />
                  <span>Saving...</span>
                </>
              ) : (
                <>
                  <Save className="w-3 h-3" />
                  <span>Save</span>
                </>
              )}
            </button>
          )}
        </div>
      </div>

      {/* Search Bar */}
      {Object.keys(editedConfig).length > 0 && (
        <div className="px-3 py-2 border-b shrink-0" style={{ borderColor: 'var(--color-border-default)' }}>
          <div className="relative">
            <Search
              className="absolute left-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5"
              style={{ color: 'var(--color-text-tertiary)' }}
            />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search config..."
              className="w-full text-xs rounded px-2 py-1.5 pl-7 pr-7 border outline-none transition-colors"
              style={{
                backgroundColor: 'var(--color-bg-tertiary)',
                borderColor: 'var(--color-border-default)',
                color: 'var(--color-text-primary)',
              }}
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-0.5 rounded hover:bg-black/10"
                title="Clear search"
              >
                <X className="w-3 h-3" style={{ color: 'var(--color-text-tertiary)' }} />
              </button>
            )}
          </div>
        </div>
      )}

      {/* Content */}
      <div className="flex-1 overflow-auto p-3">
        {/* MES Process Selector - Always visible */}
        <div className="mb-3">
          <label
            className="block text-xs font-medium mb-1.5"
            style={{ color: 'var(--color-text-secondary)' }}
          >
            MES Process
          </label>
          <select
            value={processId ?? ''}
            onChange={(e) => handleConfigChange('processId', e.target.value)}
            disabled={isRunning}
            className="w-full text-xs rounded px-2 py-1.5 border outline-none transition-colors disabled:opacity-50"
            style={{
              backgroundColor: 'var(--color-bg-tertiary)',
              borderColor: processId ? 'var(--color-border-default)' : 'var(--color-status-fail)',
              color: 'var(--color-text-primary)',
            }}
          >
            <option value="" disabled>-- Select MES Process --</option>
            {processes.map((process) => (
              <option key={process.id} value={process.id}>
                {process.processNumber}. {process.processNameEn}
              </option>
            ))}
          </select>
        </div>

        {/* Header ID Input */}
        <div className="mb-4 pb-3 border-b" style={{ borderColor: 'var(--color-border-default)' }}>
          <label
            className="block text-xs font-medium mb-1.5"
            style={{ color: 'var(--color-text-secondary)' }}
          >
            Header ID
          </label>
          <input
            type="number"
            value={headerId ?? ''}
            onChange={(e) => handleConfigChange('headerId', e.target.value)}
            disabled={isRunning}
            placeholder="Enter header ID (e.g., 1, 2, 3...)"
            className="w-full text-xs rounded px-2 py-1.5 border outline-none transition-colors disabled:opacity-50"
            style={{
              backgroundColor: 'var(--color-bg-tertiary)',
              borderColor: headerId ? 'var(--color-border-default)' : 'var(--color-status-warning)',
              color: 'var(--color-text-primary)',
            }}
          />
          <p className="text-xs mt-1" style={{ color: 'var(--color-text-tertiary)' }}>
            Unique ID to distinguish batches within the same process
          </p>
        </div>

        {/* Other config fields */}
        {Object.keys(editedConfig).filter(k => k !== 'processId' && k !== 'headerId').length === 0 ? (
          !isWorkflowEnabled && (
            <p className="text-xs italic" style={{ color: 'var(--color-text-tertiary)' }}>
              No configuration for this batch.
            </p>
          )
        ) : filteredConfig.filter(([k]) => k !== 'processId' && k !== 'headerId').length === 0 ? (
          searchQuery && (
            <p className="text-xs italic" style={{ color: 'var(--color-text-tertiary)' }}>
              No config matches "{searchQuery}"
            </p>
          )
        ) : (
          <div className="space-y-2">
            {filteredConfig
              .filter(([key]) => key !== 'processId' && key !== 'headerId')
              .map(([key, value]) => (
              <div key={key} className="flex items-center gap-2">
                <label
                  className="text-xs w-1/3 truncate"
                  style={{ color: 'var(--color-text-secondary)' }}
                  title={key}
                >
                  {key}
                </label>
                <input
                  type="text"
                  value={String(value ?? '')}
                  onChange={(e) => handleConfigChange(key, e.target.value)}
                  disabled={isRunning}
                  className="flex-1 text-xs rounded px-2 py-1 border outline-none transition-colors disabled:opacity-50"
                  style={{
                    backgroundColor: 'var(--color-bg-tertiary)',
                    borderColor: 'var(--color-border-default)',
                    color: 'var(--color-text-primary)',
                  }}
                />
              </div>
            ))}
          </div>
        )}

        {/* Warning if workflow enabled but no process selected */}
        {isMesProcessMissing && (
          <div
            className="flex items-center gap-2 text-xs p-2 rounded mt-4"
            style={{
              backgroundColor: 'rgba(239, 68, 68, 0.1)',
              color: 'var(--color-status-fail)',
            }}
          >
            <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" />
            <span>WIP Process Start/Complete is enabled. processId is required.</span>
          </div>
        )}

        {/* Unsaved changes warning */}
        {isDirty && !isRunning && (
          <div
            className="flex items-center gap-2 text-xs p-2 rounded mt-4"
            style={{
              backgroundColor: 'rgba(234, 179, 8, 0.1)',
              color: 'var(--color-status-warning)',
            }}
          >
            <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" />
            <span>You have unsaved changes. Click Save to apply.</span>
          </div>
        )}

        {/* Status Info */}
        {isRunning && (
          <div
            className="text-xs p-2 rounded mt-4"
            style={{
              backgroundColor: 'rgba(var(--color-brand-rgb), 0.1)',
              color: 'var(--color-brand-500)',
            }}
          >
            Configuration editing is disabled while the batch is running.
          </div>
        )}
      </div>
    </div>
  );
}
