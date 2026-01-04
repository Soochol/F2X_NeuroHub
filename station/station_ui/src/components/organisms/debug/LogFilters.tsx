/**
 * LogFilters - Filter controls for debug log panel.
 */

import { Search, X } from 'lucide-react';
import { useDebugPanelStore } from '../../../stores/debugPanelStore';
import { Select } from '../../atoms/Select';
import { Input } from '../../atoms/Input';
import type { LogLevel } from '../../../types';

interface LogFiltersProps {
  /** Available step names for filtering */
  stepNames: string[];
}

const levelOptions = [
  { value: '', label: 'All Levels' },
  { value: 'debug', label: 'Debug' },
  { value: 'info', label: 'Info' },
  { value: 'warning', label: 'Warning' },
  { value: 'error', label: 'Error' },
];

export function LogFilters({ stepNames }: LogFiltersProps) {
  const { selectedStep, logLevel, searchQuery, setSelectedStep, setLogLevel, setSearchQuery, clearFilters } =
    useDebugPanelStore();

  const stepOptions = [
    { value: '', label: 'All Steps' },
    ...stepNames.map((name) => ({ value: name, label: name })),
  ];

  const hasActiveFilters = selectedStep || logLevel || searchQuery;

  return (
    <div
      className="flex flex-col gap-2 px-3 py-2 border-b"
      style={{ borderColor: 'var(--color-border-default)' }}
    >
      {/* Step and Level filters */}
      <div className="flex items-center gap-2">
        <Select
          value={selectedStep || ''}
          onChange={(e) => setSelectedStep(e.target.value || null)}
          className="flex-1 text-xs"
          placeholder="All Steps"
          options={stepOptions}
        />
        <Select
          value={logLevel || ''}
          onChange={(e) => setLogLevel((e.target.value as LogLevel) || null)}
          className="flex-1 text-xs"
          placeholder="All Levels"
          options={levelOptions}
        />
      </div>

      {/* Search input */}
      <div className="relative">
        <Search
          className="absolute left-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5"
          style={{ color: 'var(--color-text-tertiary)' }}
        />
        <Input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search logs..."
          className="pl-7 pr-7 text-xs w-full"
        />
        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-0.5 rounded hover:bg-zinc-700"
            title="Clear filters"
          >
            <X className="w-3.5 h-3.5" style={{ color: 'var(--color-text-tertiary)' }} />
          </button>
        )}
      </div>
    </div>
  );
}
