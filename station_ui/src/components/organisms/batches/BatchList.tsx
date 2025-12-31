/**
 * Batch list component.
 * Enhanced with statistics display for each batch.
 */

import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { BatchCard } from '../../molecules/BatchCard';
import { Select } from '../../atoms/Select';
import { useBatchStore } from '../../../stores/batchStore';
import type { Batch, BatchStatus, BatchStatistics } from '../../../types';

export interface BatchListProps {
  batches: Batch[];
  statistics?: Map<string, BatchStatistics>;
  onStart?: (batchId: string) => void;
  onStop?: (batchId: string) => void;
  onDelete?: (batchId: string) => void;
  onSelect?: (batchId: string) => void;
  isLoading?: boolean;
}

export function BatchList({ batches, statistics, onStart, onStop, onDelete, onSelect, isLoading }: BatchListProps) {
  const { batchId: selectedBatchId } = useParams<{ batchId?: string }>();
  const [statusFilter, setStatusFilter] = useState<BatchStatus | 'all'>('all');

  // Get statistics from store if not provided via props
  // Note: Don't use useShallow with Map objects - shallow comparison doesn't work correctly
  const batchStatistics = useBatchStore((state) => state.batchStatistics);
  const batchStats = statistics || batchStatistics;

  const filteredBatches =
    statusFilter === 'all' ? batches : batches.filter((b) => b.status === statusFilter);

  const statusOptions = [
    { value: 'all', label: 'All Status' },
    { value: 'idle', label: 'Idle' },
    { value: 'running', label: 'Running' },
    { value: 'completed', label: 'Completed' },
    { value: 'error', label: 'Error' },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold" style={{ color: 'var(--color-text-primary)' }}>Batches ({filteredBatches.length})</h3>
        <div className="w-40">
          <Select
            options={statusOptions}
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as BatchStatus | 'all')}
          />
        </div>
      </div>

      {filteredBatches.length === 0 ? (
        <div className="p-8 text-center rounded-lg border" style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)', color: 'var(--color-text-tertiary)' }}>
          {statusFilter === 'all' ? 'No batches configured' : `No ${statusFilter} batches`}
        </div>
      ) : (
        <div className="grid gap-4">
          {filteredBatches.map((batch) => (
            <BatchCard
              key={batch.id}
              batch={batch}
              statistics={batchStats.get(batch.id)}
              onStart={onStart}
              onStop={onStop}
              onDelete={onDelete}
              onSelect={onSelect}
              isLoading={isLoading}
              isSelected={batch.id === selectedBatchId}
            />
          ))}
        </div>
      )}
    </div>
  );
}
