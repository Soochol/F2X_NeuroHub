/**
 * Results filter component for filtering execution results.
 */

import { Filter, X, Calendar } from 'lucide-react';
import { Select } from '../../atoms/Select';
import { Input } from '../../atoms/Input';
import { Button } from '../../atoms/Button';
import type { ExecutionStatus } from '../../../types';

interface ResultsFilterProps {
  batchId: string;
  onBatchChange: (value: string) => void;
  status: ExecutionStatus | '';
  onStatusChange: (value: ExecutionStatus | '') => void;
  fromDate: string;
  onFromDateChange: (value: string) => void;
  toDate: string;
  onToDateChange: (value: string) => void;
  search: string;
  onSearchChange: (value: string) => void;
  onClear: () => void;
  batches: Array<{ id: string; name: string }>;
}

const statusOptions = [
  { value: '', label: 'All Status' },
  { value: 'completed', label: 'Completed' },
  { value: 'failed', label: 'Failed' },
  { value: 'running', label: 'Running' },
  { value: 'stopped', label: 'Stopped' },
];

export function ResultsFilter({
  batchId,
  onBatchChange,
  status,
  onStatusChange,
  fromDate,
  onFromDateChange,
  toDate,
  onToDateChange,
  search,
  onSearchChange,
  onClear,
  batches,
}: ResultsFilterProps) {
  const batchOptions = [
    { value: '', label: 'All Batches' },
    ...batches.map((b) => ({ value: b.id, label: b.name })),
  ];

  const hasActiveFilters = batchId || status || fromDate || toDate || search;

  return (
    <div
      className="p-4 rounded-lg border"
      style={{
        backgroundColor: 'var(--color-bg-secondary)',
        borderColor: 'var(--color-border-default)',
      }}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4" style={{ color: 'var(--color-text-secondary)' }} />
          <span className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
            Filters
          </span>
        </div>
        {hasActiveFilters && (
          <Button variant="ghost" size="sm" onClick={onClear}>
            <X className="w-4 h-4 mr-1" />
            Clear
          </Button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <Select
          options={batchOptions}
          value={batchId}
          onChange={(e) => onBatchChange(e.target.value)}
        />

        <Select
          options={statusOptions}
          value={status}
          onChange={(e) => onStatusChange(e.target.value as ExecutionStatus | '')}
        />

        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 flex-shrink-0" style={{ color: 'var(--color-text-secondary)' }} />
          <Input
            type="date"
            value={fromDate}
            onChange={(e) => onFromDateChange(e.target.value)}
            placeholder="From"
          />
        </div>

        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 flex-shrink-0" style={{ color: 'var(--color-text-secondary)' }} />
          <Input
            type="date"
            value={toDate}
            onChange={(e) => onToDateChange(e.target.value)}
            placeholder="To"
          />
        </div>

        <Input
          placeholder="Search sequence..."
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </div>
    </div>
  );
}
