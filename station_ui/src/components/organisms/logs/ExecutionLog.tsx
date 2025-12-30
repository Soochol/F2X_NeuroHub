/**
 * ExecutionLog - Real-time execution log viewer.
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import {
  FileText,
  AlertCircle,
  Info,
  AlertTriangle,
  Bug,
  Trash2,
  Download,
  Filter,
  ArrowDown,
} from 'lucide-react';
import { useLogStore } from '../../../stores';
import { Button } from '../../atoms/Button';
import { Input } from '../../atoms/Input';
import { Select } from '../../atoms/Select';
import type { LogEntry, LogLevel } from '../../../types';

interface ExecutionLogProps {
  /** Filter by batch ID */
  batchId?: string;
  /** Maximum height in pixels */
  maxHeight?: number;
  /** Show filter controls */
  showFilters?: boolean;
  /** Show clear button */
  showClear?: boolean;
  /** Show export button */
  showExport?: boolean;
  /** Additional CSS classes */
  className?: string;
}

const levelConfig: Record<
  LogLevel,
  { icon: React.ReactNode; bgClass: string; textClass: string; label: string }
> = {
  debug: {
    icon: <Bug className="w-3.5 h-3.5" />,
    bgClass: 'bg-zinc-500/10',
    textClass: 'text-zinc-400',
    label: 'DEBUG',
  },
  info: {
    icon: <Info className="w-3.5 h-3.5" />,
    bgClass: 'bg-blue-500/10',
    textClass: 'text-blue-400',
    label: 'INFO',
  },
  warning: {
    icon: <AlertTriangle className="w-3.5 h-3.5" />,
    bgClass: 'bg-yellow-500/10',
    textClass: 'text-yellow-400',
    label: 'WARN',
  },
  error: {
    icon: <AlertCircle className="w-3.5 h-3.5" />,
    bgClass: 'bg-red-500/10',
    textClass: 'text-red-400',
    label: 'ERROR',
  },
};

function formatTimestamp(date: Date): string {
  return date.toLocaleTimeString('en-US', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

interface LogEntryRowProps {
  log: LogEntry;
}

function LogEntryRow({ log }: LogEntryRowProps) {
  const config = levelConfig[log.level];

  return (
    <div
      className={`flex items-start gap-2 px-3 py-1.5 text-xs font-mono ${config.bgClass} border-l-2 ${
        log.level === 'error'
          ? 'border-l-red-500'
          : log.level === 'warning'
            ? 'border-l-yellow-500'
            : 'border-l-transparent'
      }`}
    >
      <span className="text-zinc-500 flex-shrink-0">
        {formatTimestamp(log.timestamp)}
      </span>
      <span className={`flex items-center gap-1 flex-shrink-0 w-14 ${config.textClass}`}>
        {config.icon}
        <span>{config.label}</span>
      </span>
      {log.batchId && (
        <span className="text-zinc-500 flex-shrink-0">[{log.batchId}]</span>
      )}
      <span className={`flex-1 break-all ${config.textClass}`}>{log.message}</span>
    </div>
  );
}

export function ExecutionLog({
  batchId,
  maxHeight = 400,
  showFilters = true,
  showClear = true,
  showExport = true,
  className = '',
}: ExecutionLogProps) {
  const logs = useLogStore((s) => s.logs);
  const autoScroll = useLogStore((s) => s.autoScroll);
  const setAutoScroll = useLogStore((s) => s.setAutoScroll);
  const clearLogs = useLogStore((s) => s.clearLogs);
  const setFilters = useLogStore((s) => s.setFilters);
  const getFilteredLogs = useLogStore((s) => s.getFilteredLogs);

  const [levelFilter, setLevelFilter] = useState<LogLevel | ''>('');
  const [searchFilter, setSearchFilter] = useState('');

  const containerRef = useRef<HTMLDivElement>(null);
  const prevLogsLengthRef = useRef(logs.length);

  // Apply filters when they change
  useEffect(() => {
    setFilters({
      batchId,
      level: levelFilter || undefined,
      search: searchFilter || undefined,
    });
  }, [batchId, levelFilter, searchFilter, setFilters]);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (autoScroll && containerRef.current && logs.length > prevLogsLengthRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
    prevLogsLengthRef.current = logs.length;
  }, [logs.length, autoScroll]);

  // Handle scroll to detect if user scrolled up
  const handleScroll = useCallback(() => {
    if (!containerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
    if (isAtBottom !== autoScroll) {
      setAutoScroll(isAtBottom);
    }
  }, [autoScroll, setAutoScroll]);

  const scrollToBottom = () => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
      setAutoScroll(true);
    }
  };

  const handleExport = () => {
    const filteredLogs = getFilteredLogs();
    const content = filteredLogs
      .map(
        (log) =>
          `${formatTimestamp(log.timestamp)} [${log.level.toUpperCase()}] ${log.batchId ? `[${log.batchId}] ` : ''}${log.message}`
      )
      .join('\n');

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `execution-log-${new Date().toISOString().slice(0, 10)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const filteredLogs = getFilteredLogs();

  return (
    <div className={`bg-zinc-900 rounded-lg border border-zinc-800 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <FileText className="w-5 h-5 text-brand-400" />
          <h3 className="text-sm font-medium text-zinc-100">Execution Log</h3>
          <span className="text-xs text-zinc-500">({filteredLogs.length} entries)</span>
        </div>
        <div className="flex items-center gap-2">
          {showExport && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleExport}
              disabled={filteredLogs.length === 0}
              title="Export logs"
            >
              <Download className="w-4 h-4" />
            </Button>
          )}
          {showClear && (
            <Button
              variant="ghost"
              size="sm"
              onClick={clearLogs}
              disabled={logs.length === 0}
              title="Clear logs"
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          )}
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="flex items-center gap-2 px-4 py-2 border-b border-zinc-800 bg-zinc-800/30">
          <Filter className="w-4 h-4 text-zinc-500" />
          <Select
            value={levelFilter}
            onChange={(e) => setLevelFilter(e.target.value as LogLevel | '')}
            className="w-28 text-xs"
            placeholder="All Levels"
            options={[
              { value: '', label: 'All Levels' },
              { value: 'debug', label: 'Debug' },
              { value: 'info', label: 'Info' },
              { value: 'warning', label: 'Warning' },
              { value: 'error', label: 'Error' },
            ]}
          />
          <Input
            type="text"
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
            placeholder="Search logs..."
            className="flex-1 text-xs"
          />
        </div>
      )}

      {/* Log Content */}
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="overflow-y-auto bg-zinc-950"
        style={{ maxHeight }}
      >
        {filteredLogs.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-zinc-500">
            <FileText className="w-8 h-8 mb-2 opacity-50" />
            <p className="text-sm">No log entries</p>
          </div>
        ) : (
          <div className="divide-y divide-zinc-800/50">
            {filteredLogs.map((log) => (
              <LogEntryRow key={log.id} log={log} />
            ))}
          </div>
        )}
      </div>

      {/* Scroll to bottom indicator */}
      {!autoScroll && filteredLogs.length > 0 && (
        <div className="absolute bottom-4 right-4">
          <Button
            variant="secondary"
            size="sm"
            onClick={scrollToBottom}
            className="shadow-lg"
          >
            <ArrowDown className="w-4 h-4 mr-1" />
            New logs
          </Button>
        </div>
      )}
    </div>
  );
}
