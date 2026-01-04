/**
 * Results table component for displaying execution results.
 */

import { useState } from 'react';
import { CheckCircle, XCircle, PlayCircle, StopCircle, Eye, ChevronUp, ChevronDown } from 'lucide-react';
import { Button } from '../../atoms/Button';
import { LoadingSpinner } from '../../atoms/LoadingSpinner';
import type { ExecutionSummary, ExecutionStatus } from '../../../types';

interface ResultsTableProps {
  results: ExecutionSummary[];
  isLoading: boolean;
  selectedIds: string[];
  onSelectionChange: (ids: string[]) => void;
  onViewDetail: (result: ExecutionSummary) => void;
  sortField: string;
  sortDirection: 'asc' | 'desc';
  onSort: (field: string) => void;
}

/**
 * Status icons using CSS variables for theme-aware colors.
 */
const getStatusIcon = (status: ExecutionStatus): React.ReactNode => {
  const iconProps = { className: 'w-4 h-4' };
  const styles: Record<ExecutionStatus, { color: string }> = {
    completed: { color: 'var(--color-step-completed-text)' },
    failed: { color: 'var(--color-step-failed-text)' },
    running: { color: 'var(--color-step-running-text)' },
    stopped: { color: 'var(--color-step-pending-text)' },
  };

  switch (status) {
    case 'completed':
      return <CheckCircle {...iconProps} style={styles.completed} />;
    case 'failed':
      return <XCircle {...iconProps} style={styles.failed} />;
    case 'running':
      return <PlayCircle {...iconProps} style={styles.running} />;
    case 'stopped':
      return <StopCircle {...iconProps} style={styles.stopped} />;
  }
};

const statusLabels: Record<ExecutionStatus, string> = {
  completed: 'Completed',
  failed: 'Failed',
  running: 'Running',
  stopped: 'Stopped',
};

function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${Math.floor(ms / 60000)}m ${Math.floor((ms % 60000) / 1000)}s`;
}

function formatDateTime(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleString('en-US', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

export function ResultsTable({
  results,
  isLoading,
  selectedIds,
  onSelectionChange,
  onViewDetail,
  sortField,
  sortDirection,
  onSort,
}: ResultsTableProps) {
  const [allSelected, setAllSelected] = useState(false);

  const handleSelectAll = () => {
    if (allSelected) {
      onSelectionChange([]);
    } else {
      onSelectionChange(results.map((r) => r.id));
    }
    setAllSelected(!allSelected);
  };

  const handleSelectOne = (id: string) => {
    if (selectedIds.includes(id)) {
      onSelectionChange(selectedIds.filter((i) => i !== id));
    } else {
      onSelectionChange([...selectedIds, id]);
    }
  };

  const SortIcon = ({ field }: { field: string }) => {
    if (sortField !== field) return null;
    return sortDirection === 'asc' ? (
      <ChevronUp className="w-4 h-4" />
    ) : (
      <ChevronDown className="w-4 h-4" />
    );
  };

  const headerClass = 'px-4 py-3 text-left text-xs font-medium uppercase tracking-wider cursor-pointer hover:bg-opacity-50 transition-colors';

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div
        className="flex items-center justify-center h-64 text-sm"
        style={{ color: 'var(--color-text-tertiary)' }}
      >
        No results found. Adjust your filters or run a sequence.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border" style={{ borderColor: 'var(--color-border-default)' }}>
      <table className="min-w-full divide-y" style={{ backgroundColor: 'var(--color-bg-secondary)' }}>
        <thead style={{ backgroundColor: 'var(--color-bg-tertiary)' }}>
          <tr>
            <th className="px-4 py-3 w-12">
              <input
                type="checkbox"
                checked={allSelected}
                onChange={handleSelectAll}
                className="rounded"
                style={{ borderColor: 'var(--color-input-border)' }}
              />
            </th>
            <th
              className={headerClass}
              style={{ color: 'var(--color-text-secondary)' }}
              onClick={() => onSort('status')}
            >
              <div className="flex items-center gap-1">
                Status <SortIcon field="status" />
              </div>
            </th>
            <th
              className={headerClass}
              style={{ color: 'var(--color-text-secondary)' }}
              onClick={() => onSort('sequenceName')}
            >
              <div className="flex items-center gap-1">
                Sequence <SortIcon field="sequenceName" />
              </div>
            </th>
            <th
              className={headerClass}
              style={{ color: 'var(--color-text-secondary)' }}
              onClick={() => onSort('batchId')}
            >
              <div className="flex items-center gap-1">
                Batch <SortIcon field="batchId" />
              </div>
            </th>
            <th
              className={headerClass}
              style={{ color: 'var(--color-text-secondary)' }}
              onClick={() => onSort('startedAt')}
            >
              <div className="flex items-center gap-1">
                Started At <SortIcon field="startedAt" />
              </div>
            </th>
            <th
              className={headerClass}
              style={{ color: 'var(--color-text-secondary)' }}
              onClick={() => onSort('duration')}
            >
              <div className="flex items-center gap-1">
                Duration <SortIcon field="duration" />
              </div>
            </th>
            <th
              className={headerClass}
              style={{ color: 'var(--color-text-secondary)' }}
            >
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="divide-y" style={{ borderColor: 'var(--color-border-subtle)' }}>
          {results.map((result) => (
            <tr
              key={result.id}
              className="transition-colors"
              style={{
                backgroundColor: selectedIds.includes(result.id)
                  ? 'var(--color-bg-tertiary)'
                  : 'transparent',
              }}
              onMouseEnter={(e) => {
                if (!selectedIds.includes(result.id)) {
                  e.currentTarget.style.backgroundColor = 'var(--color-bg-tertiary)';
                }
              }}
              onMouseLeave={(e) => {
                if (!selectedIds.includes(result.id)) {
                  e.currentTarget.style.backgroundColor = 'transparent';
                }
              }}
            >
              <td className="px-4 py-3">
                <input
                  type="checkbox"
                  checked={selectedIds.includes(result.id)}
                  onChange={() => handleSelectOne(result.id)}
                  className="rounded"
                  style={{ borderColor: 'var(--color-input-border)' }}
                />
              </td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  {getStatusIcon(result.status)}
                  <span
                    className="text-sm font-medium"
                    style={{ color: 'var(--color-text-primary)' }}
                  >
                    {statusLabels[result.status]}
                  </span>
                </div>
              </td>
              <td className="px-4 py-3">
                <span className="text-sm" style={{ color: 'var(--color-text-primary)' }}>
                  {result.sequenceName}
                </span>
                {result.sequenceVersion && (
                  <span
                    className="ml-2 text-xs px-1.5 py-0.5 rounded"
                    style={{
                      backgroundColor: 'var(--color-bg-tertiary)',
                      color: 'var(--color-text-secondary)',
                    }}
                  >
                    v{result.sequenceVersion}
                  </span>
                )}
              </td>
              <td className="px-4 py-3">
                <span className="text-sm font-mono" style={{ color: 'var(--color-text-secondary)' }}>
                  {result.batchId?.slice(0, 8) ?? '-'}
                </span>
              </td>
              <td className="px-4 py-3">
                <span className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                  {result.startedAt ? formatDateTime(result.startedAt) : '-'}
                </span>
              </td>
              <td className="px-4 py-3">
                <span className="text-sm font-mono" style={{ color: 'var(--color-text-secondary)' }}>
                  {result.duration ? formatDuration(result.duration) : '-'}
                </span>
              </td>
              <td className="px-4 py-3">
                <Button variant="ghost" size="sm" onClick={() => onViewDetail(result)}>
                  <Eye className="w-4 h-4" />
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
