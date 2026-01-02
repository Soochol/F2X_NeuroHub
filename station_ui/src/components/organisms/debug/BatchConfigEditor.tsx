/**
 * BatchConfigEditor - Config tab content for process selection.
 * Shows process selector for MES Start/Complete workflow.
 */

import { useState, useEffect, useMemo } from 'react';
import { Settings, Save, RefreshCw } from 'lucide-react';
import { Button } from '../../atoms/Button';
import { useProcesses, useUpdateBatch, useBatch } from '../../../hooks';
import type { ProcessInfo } from '../../../api/endpoints/system';
import type { BatchDetail } from '../../../types';

interface BatchConfigEditorProps {
  /** Batch ID */
  batchId: string;
  /** Whether batch is currently running */
  isRunning: boolean;
}

// Type guard to check if batch has detailed info
function isBatchDetail(batch: unknown): batch is BatchDetail {
  return batch !== null && typeof batch === 'object' && 'parameters' in batch;
}

export function BatchConfigEditor({ batchId, isRunning }: BatchConfigEditorProps) {
  const { data: batch } = useBatch(batchId);
  const { data: processes = [], isLoading: processesLoading } = useProcesses();
  const updateBatch = useUpdateBatch();

  // Local state for editing
  const [selectedProcessId, setSelectedProcessId] = useState<number | undefined>();
  const [headerId, setHeaderId] = useState<number | undefined>();
  const [hasChanges, setHasChanges] = useState(false);

  // Sync batch data to local state
  useEffect(() => {
    if (batch && isBatchDetail(batch)) {
      setSelectedProcessId(batch.processId);
      setHeaderId(batch.headerId);
      setHasChanges(false);
    }
  }, [batch]);

  // Handle process selection change
  const handleProcessChange = (processId: number) => {
    setSelectedProcessId(processId);
    setHasChanges(true);
  };

  // Handle header ID change
  const handleHeaderIdChange = (value: string) => {
    const parsed = parseInt(value, 10);
    setHeaderId(isNaN(parsed) ? undefined : parsed);
    setHasChanges(true);
  };

  // Save changes
  const handleSave = async () => {
    if (!batchId) return;

    await updateBatch.mutateAsync({ batchId, request: { processId: selectedProcessId, headerId } });
    setHasChanges(false);
  };

  // Reset to original values
  const handleReset = () => {
    if (batch && isBatchDetail(batch)) {
      setSelectedProcessId(batch.processId);
      setHeaderId(batch.headerId);
      setHasChanges(false);
    }
  };

  // Get selected process info
  const selectedProcess = useMemo(() => {
    return processes.find((p) => p.processNumber === selectedProcessId);
  }, [processes, selectedProcessId]);

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
            Process Configuration
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

      {/* Content */}
      <div className="flex-1 overflow-auto p-3 space-y-4">
        {/* Process Selection */}
        <div className="space-y-2">
          <label
            className="block text-xs font-medium"
            style={{ color: 'var(--color-text-secondary)' }}
          >
            MES Process (Start/Complete)
          </label>
          <select
            value={selectedProcessId ?? ''}
            onChange={(e) => handleProcessChange(Number(e.target.value))}
            disabled={isRunning || processesLoading}
            className="w-full text-sm rounded px-3 py-2 border outline-none transition-colors disabled:opacity-50"
            style={{
              backgroundColor: 'var(--color-bg-tertiary)',
              borderColor: 'var(--color-border-default)',
              color: 'var(--color-text-primary)',
            }}
          >
            <option value="">Select process...</option>
            {processes.map((p: ProcessInfo) => (
              <option key={p.id} value={p.processNumber}>
                P{p.processNumber}. {p.processNameKo}
              </option>
            ))}
          </select>
          {selectedProcess && (
            <p className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
              Code: {selectedProcess.processCode} | {selectedProcess.processNameEn}
            </p>
          )}
        </div>

        {/* Header ID Input */}
        <div className="space-y-2">
          <label
            className="block text-xs font-medium"
            style={{ color: 'var(--color-text-secondary)' }}
          >
            Process Header ID
          </label>
          <input
            type="number"
            value={headerId ?? ''}
            onChange={(e) => handleHeaderIdChange(e.target.value)}
            disabled={isRunning}
            placeholder="Enter header ID..."
            className="w-full text-sm rounded px-3 py-2 border outline-none transition-colors disabled:opacity-50"
            style={{
              backgroundColor: 'var(--color-bg-tertiary)',
              borderColor: 'var(--color-border-default)',
              color: 'var(--color-text-primary)',
            }}
          />
          <p className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
            Unique ID to distinguish batches (e.g., 1, 2, 3, 4...)
          </p>
        </div>

        {/* Status Info */}
        {isRunning && (
          <div
            className="text-xs p-2 rounded"
            style={{
              backgroundColor: 'rgba(var(--color-brand-rgb), 0.1)',
              color: 'var(--color-brand-500)',
            }}
          >
            Process selection is disabled while the batch is running.
          </div>
        )}
      </div>
    </div>
  );
}
