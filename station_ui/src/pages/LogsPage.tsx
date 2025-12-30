/**
 * Logs page - Log viewer with filtering and real-time updates.
 */

import { useState, useEffect, useRef } from 'react';
import { FileText, Download, Trash2, Filter, Pause, Play } from 'lucide-react';
import { useBatchList, useLogList } from '../hooks';
import { useLogStore } from '../stores/logStore';
import { Button } from '../components/atoms/Button';
import { Input } from '../components/atoms/Input';
import { Select } from '../components/atoms/Select';
import { LogEntryRow } from '../components/molecules/LogEntryRow';
import { LoadingSpinner } from '../components/atoms/LoadingSpinner';
import type { LogLevel } from '../types';

export function LogsPage() {
  const { data: batches } = useBatchList();
  const [batchFilter, setBatchFilter] = useState<string>('');
  const [levelFilter, setLevelFilter] = useState<LogLevel | ''>('');
  const [searchFilter, setSearchFilter] = useState<string>('');
  const [showHistorical, setShowHistorical] = useState(false);

  // Real-time logs from store
  const realTimeLogs = useLogStore((state) => state.logs);
  const autoScroll = useLogStore((state) => state.autoScroll);
  const setAutoScroll = useLogStore((state) => state.setAutoScroll);
  const clearLogs = useLogStore((state) => state.clearLogs);
  const setFilters = useLogStore((state) => state.setFilters);

  // Historical logs from API
  const { data: historicalLogs, isLoading: historicalLoading } = useLogList(
    showHistorical
      ? {
          batchId: batchFilter || undefined,
          level: levelFilter || undefined,
          search: searchFilter || undefined,
          limit: 100,
        }
      : undefined
  );

  const logContainerRef = useRef<HTMLDivElement>(null);

  // Update store filters when local filters change
  useEffect(() => {
    setFilters({
      batchId: batchFilter || undefined,
      level: levelFilter || undefined,
      search: searchFilter || undefined,
    });
  }, [batchFilter, levelFilter, searchFilter, setFilters]);

  // Auto-scroll to bottom for real-time logs
  useEffect(() => {
    if (autoScroll && logContainerRef.current && !showHistorical) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [realTimeLogs, autoScroll, showHistorical]);

  const batchOptions = [
    { value: '', label: 'All Batches' },
    ...(batches?.map((b) => ({ value: b.id, label: b.name })) ?? []),
  ];

  const levelOptions = [
    { value: '', label: 'All Levels' },
    { value: 'debug', label: 'Debug' },
    { value: 'info', label: 'Info' },
    { value: 'warning', label: 'Warning' },
    { value: 'error', label: 'Error' },
  ];

  // Filter real-time logs
  const filteredRealTimeLogs = realTimeLogs.filter((log) => {
    if (batchFilter && log.batchId !== batchFilter) return false;
    if (levelFilter && log.level !== levelFilter) return false;
    if (searchFilter && !log.message.toLowerCase().includes(searchFilter.toLowerCase()))
      return false;
    return true;
  });

  const displayLogs = showHistorical ? historicalLogs?.items ?? [] : filteredRealTimeLogs;

  const handleExport = () => {
    const logs = displayLogs;
    const data = logs.map((log) => ({
      timestamp: new Date(log.timestamp).toISOString(),
      batchId: log.batchId,
      level: log.level,
      message: log.message,
    }));

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `logs_${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <FileText className="w-6 h-6 text-brand-500" />
          <h2 className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>Logs</h2>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant={showHistorical ? 'secondary' : 'primary'}
            size="sm"
            onClick={() => setShowHistorical(!showHistorical)}
          >
            {showHistorical ? 'Real-time' : 'Historical'}
          </Button>
        </div>
      </div>

      {/* Filters */}
      <div className="p-4 rounded-lg border" style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)' }}>
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-4 h-4" style={{ color: 'var(--color-text-secondary)' }} />
          <span className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>Filters</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Select
            options={batchOptions}
            value={batchFilter}
            onChange={(e) => setBatchFilter(e.target.value)}
          />
          <Select
            options={levelOptions}
            value={levelFilter}
            onChange={(e) => setLevelFilter(e.target.value as LogLevel | '')}
          />
          <Input
            placeholder="Search logs..."
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
          />
          <div className="flex items-center gap-2">
            {!showHistorical && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setAutoScroll(!autoScroll)}
                title={autoScroll ? 'Pause auto-scroll' : 'Resume auto-scroll'}
              >
                {autoScroll ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              </Button>
            )}
            <Button variant="ghost" size="sm" onClick={handleExport} title="Export logs">
              <Download className="w-4 h-4" />
            </Button>
            {!showHistorical && (
              <Button variant="ghost" size="sm" onClick={clearLogs} title="Clear logs">
                <Trash2 className="w-4 h-4" />
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Log Viewer */}
      <div className="rounded-lg border" style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)' }}>
        <div className="flex items-center justify-between p-3 border-b" style={{ borderColor: 'var(--color-border-default)' }}>
          <span className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
            {showHistorical
              ? `Historical Logs (${historicalLogs?.total ?? 0} total)`
              : `Real-time Logs (${filteredRealTimeLogs.length} entries)`}
          </span>
          {!showHistorical && !autoScroll && (
            <span className="text-xs text-yellow-400">Auto-scroll paused</span>
          )}
        </div>

        <div
          ref={logContainerRef}
          className="h-[500px] overflow-y-auto font-mono text-sm"
        >
          {historicalLoading ? (
            <div className="flex items-center justify-center h-full">
              <LoadingSpinner size="lg" />
            </div>
          ) : displayLogs.length === 0 ? (
            <div className="flex items-center justify-center h-full" style={{ color: 'var(--color-text-tertiary)' }}>
              {showHistorical ? 'No logs found' : 'No logs yet. Waiting for activity...'}
            </div>
          ) : (
            <div className="p-2">
              {displayLogs.map((log, index) => (
                <LogEntryRow key={log.id ?? index} log={log} showBatchId />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Log Level Legend */}
      <div className="flex items-center gap-4 text-xs" style={{ color: 'var(--color-text-secondary)' }}>
        <span>Log Levels:</span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-zinc-500" />
          Debug
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-blue-500" />
          Info
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-yellow-500" />
          Warning
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-red-500" />
          Error
        </span>
      </div>
    </div>
  );
}
