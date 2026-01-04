/**
 * ParametersEditor - Parameters tab content for editing batch parameters.
 */

import { useState, useEffect, useMemo } from 'react';
import { Sliders, Save, RefreshCw, Search, X } from 'lucide-react';
import { Button } from '../../atoms/Button';
import { useUpdateBatch, useBatch } from '../../../hooks';
import type { BatchDetail } from '../../../types';

interface ParametersEditorProps {
  /** Batch ID */
  batchId: string;
  /** Whether batch is currently running */
  isRunning: boolean;
}

// Type guard to check if batch has detailed info
function isBatchDetail(batch: unknown): batch is BatchDetail {
  return batch !== null && typeof batch === 'object' && 'parameters' in batch;
}

export function ParametersEditor({ batchId, isRunning }: ParametersEditorProps) {
  const { data: batch } = useBatch(batchId);
  const updateBatch = useUpdateBatch();

  // Local state for editing
  const [editedParams, setEditedParams] = useState<Record<string, unknown>>({});
  const [hasChanges, setHasChanges] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Sync batch data to local state
  useEffect(() => {
    if (batch && isBatchDetail(batch)) {
      setEditedParams(batch.parameters || {});
      setHasChanges(false);
    }
  }, [batch]);

  // Get current batch parameters
  const currentParams = useMemo(() => {
    if (batch && isBatchDetail(batch)) {
      return batch.parameters || {};
    }
    return {};
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

  // Handle parameter value change
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
    setHasChanges(true);
  };

  // Save changes
  const handleSave = async () => {
    if (!batchId) return;

    // Only include parameters if they've changed
    if (JSON.stringify(editedParams) !== JSON.stringify(currentParams)) {
      await updateBatch.mutateAsync({ batchId, request: { parameters: editedParams } });
      setHasChanges(false);
    }
  };

  // Reset to original values
  const handleReset = () => {
    if (batch && isBatchDetail(batch)) {
      setEditedParams(batch.parameters || {});
      setHasChanges(false);
    }
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
        <div className="flex items-center gap-1">
          {hasChanges && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleReset}
              disabled={isRunning}
              title="Reset changes"
              className="p-1"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </Button>
          )}
          <Button
            variant="primary"
            size="sm"
            onClick={handleSave}
            disabled={!hasChanges || isRunning || updateBatch.isPending}
            isLoading={updateBatch.isPending}
            title="Save changes"
            className="px-2 py-1 text-xs"
          >
            <Save className="w-3 h-3 mr-1" />
            Save
          </Button>
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
