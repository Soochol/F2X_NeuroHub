/**
 * ParametersEditor - Parameters tab content for editing batch parameters.
 * Uses explicit Save button instead of auto-save for reliability.
 */

import { useState, useEffect, useMemo, useCallback } from 'react';
import { Sliders, Search, X, Loader2, Check, AlertTriangle, Save } from 'lucide-react';
import { useUpdateBatch, useBatch } from '../../../hooks';
import { useNotificationStore } from '../../../stores/notificationStore';
import type { BatchDetail } from '../../../types';

interface ParametersEditorProps {
  /** Batch ID */
  batchId: string;
  /** Whether batch is currently running */
  isRunning: boolean;
  /** Callback when dirty state changes */
  onDirtyChange?: (isDirty: boolean) => void;
}

// Type guard to check if batch has detailed info
function isBatchDetail(batch: unknown): batch is BatchDetail {
  return batch !== null && typeof batch === 'object' && 'parameters' in batch;
}

export function ParametersEditor({ batchId, isRunning, onDirtyChange }: ParametersEditorProps) {
  const { data: batch } = useBatch(batchId);
  const updateBatch = useUpdateBatch();
  const addNotification = useNotificationStore((state) => state.addNotification);

  // Local state for editing
  const [editedParams, setEditedParams] = useState<Record<string, unknown>>({});
  const [originalParams, setOriginalParams] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved'>('idle');

  // Check if there are unsaved changes
  const isDirty = useMemo(() => {
    return JSON.stringify(editedParams) !== originalParams;
  }, [editedParams, originalParams]);

  // Notify parent of dirty state changes
  useEffect(() => {
    onDirtyChange?.(isDirty);
  }, [isDirty, onDirtyChange]);

  // Sync batch data to local state
  useEffect(() => {
    if (batch && isBatchDetail(batch)) {
      const params = batch.parameters || {};
      setEditedParams(params);
      setOriginalParams(JSON.stringify(params));
      setSaveStatus('idle');
    }
  }, [batch]);

  // Filter parameters based on search query
  const filteredParams = useMemo(() => {
    if (!searchQuery.trim()) {
      return Object.entries(editedParams);
    }
    const query = searchQuery.toLowerCase();
    return Object.entries(editedParams).filter(
      ([key, value]) =>
        key.toLowerCase().includes(query) ||
        String(value ?? '').toLowerCase().includes(query)
    );
  }, [editedParams, searchQuery]);

  // Save function - only called when Save button is clicked
  const handleSave = useCallback(async () => {
    if (!batchId || isRunning || !isDirty) return;

    setSaveStatus('saving');
    try {
      await updateBatch.mutateAsync({ batchId, request: { parameters: editedParams } });
      setOriginalParams(JSON.stringify(editedParams));
      setSaveStatus('saved');
      // Reset to idle after showing saved status
      setTimeout(() => setSaveStatus('idle'), 1500);
    } catch (error) {
      setSaveStatus('idle');
      addNotification({
        type: 'error',
        title: 'Save Failed',
        message: error instanceof Error ? error.message : 'Failed to save parameters',
      });
      console.error('[ParametersEditor] Failed to save params:', error);
    }
  }, [batchId, isRunning, isDirty, editedParams, updateBatch, addNotification]);

  // Handle parameter value change (no auto-save, just update local state)
  const handleParamChange = (key: string, value: string) => {
    const newParams = { ...editedParams };
    // Try to parse as number or boolean
    if (value === 'true') {
      newParams[key] = true;
    } else if (value === 'false') {
      newParams[key] = false;
    } else if (!isNaN(Number(value)) && value !== '') {
      newParams[key] = Number(value);
    } else {
      newParams[key] = value;
    }
    setEditedParams(newParams);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div
        className="flex items-center justify-between px-3 py-2 border-b shrink-0"
        style={{ borderColor: 'var(--color-border-default)' }}
      >
        <div className="flex items-center gap-2">
          <Sliders className="w-4 h-4" style={{ color: 'var(--color-text-tertiary)' }} />
          <span className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
            Parameters
          </span>
          <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
            ({filteredParams.length}/{Object.keys(editedParams).length})
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
      {Object.keys(editedParams).length > 0 && (
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
              placeholder="Search parameters..."
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
        {Object.keys(editedParams).length === 0 ? (
          <p className="text-xs italic" style={{ color: 'var(--color-text-tertiary)' }}>
            No parameters configured for this batch.
          </p>
        ) : filteredParams.length === 0 ? (
          <p className="text-xs italic" style={{ color: 'var(--color-text-tertiary)' }}>
            No parameters match "{searchQuery}"
          </p>
        ) : (
          <div className="space-y-2">
            {filteredParams.map(([key, value]) => (
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
                  onChange={(e) => handleParamChange(key, e.target.value)}
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
            Parameter editing is disabled while the batch is running.
          </div>
        )}
      </div>
    </div>
  );
}
