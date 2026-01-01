/**
 * LogEntryList - Log entries display with auto-scroll support.
 */

import { useEffect, useRef, useCallback, useMemo } from 'react';
import { FileText, AlertCircle, Info, AlertTriangle, Bug, ArrowDown } from 'lucide-react';
import { useLogStore } from '../../../stores';
import { useDebugPanelStore } from '../../../stores/debugPanelStore';
import { Button } from '../../atoms/Button';
import type { LogEntry, LogLevel } from '../../../types';

interface LogEntryListProps {
  /** Batch ID to filter logs */
  batchId: string;
}

const levelConfig: Record<
  LogLevel,
  { icon: React.ReactNode; bgClass: string; textClass: string; borderClass: string; label: string }
> = {
  debug: {
    icon: <Bug className="w-3 h-3" />,
    bgClass: 'bg-zinc-500/10',
    textClass: 'text-zinc-400',
    borderClass: 'border-l-zinc-500',
    label: 'DBG',
  },
  info: {
    icon: <Info className="w-3 h-3" />,
    bgClass: 'bg-blue-500/10',
    textClass: 'text-blue-400',
    borderClass: 'border-l-blue-500',
    label: 'INF',
  },
  warning: {
    icon: <AlertTriangle className="w-3 h-3" />,
    bgClass: 'bg-yellow-500/10',
    textClass: 'text-yellow-400',
    borderClass: 'border-l-yellow-500',
    label: 'WRN',
  },
  error: {
    icon: <AlertCircle className="w-3 h-3" />,
    bgClass: 'bg-red-500/10',
    textClass: 'text-red-400',
    borderClass: 'border-l-red-500',
    label: 'ERR',
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
  onClick?: () => void;
}

function LogEntryRow({ log, onClick }: LogEntryRowProps) {
  const config = levelConfig[log.level];

  return (
    <div
      onClick={onClick}
      className={`flex items-start gap-1.5 px-2 py-1 text-xs font-mono ${config.bgClass} border-l-2 ${config.borderClass} cursor-pointer hover:bg-zinc-800/50`}
    >
      <span className="text-zinc-500 flex-shrink-0 text-[10px]">{formatTimestamp(log.timestamp)}</span>
      <span className={`flex items-center gap-0.5 flex-shrink-0 ${config.textClass}`}>
        {config.icon}
        <span className="text-[10px]">{config.label}</span>
      </span>
      <span className={`flex-1 break-all text-[11px] leading-relaxed ${config.textClass}`}>
        {log.message}
      </span>
    </div>
  );
}

export function LogEntryList({ batchId }: LogEntryListProps) {
  const logs = useLogStore((s) => s.logs);
  const { selectedStep, logLevel, searchQuery, autoScroll, setAutoScroll } =
    useDebugPanelStore();

  const containerRef = useRef<HTMLDivElement>(null);
  const prevLogsLengthRef = useRef(logs.length);

  // Filter logs based on current filters
  const filteredLogs = useMemo(() => {
    return logs.filter((log) => {
      // Filter by batch ID
      if (log.batchId !== batchId) return false;

      // Filter by log level
      if (logLevel && log.level !== logLevel) return false;

      // Filter by search query
      if (searchQuery && !log.message.toLowerCase().includes(searchQuery.toLowerCase())) {
        return false;
      }

      // Note: Step filtering would require step name in log entries
      // For now, we search for step name in the message
      if (selectedStep && !log.message.toLowerCase().includes(selectedStep.toLowerCase())) {
        return false;
      }

      return true;
    });
  }, [logs, batchId, selectedStep, logLevel, searchQuery]);

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

  return (
    <div className="relative flex flex-col h-full">
      {/* Entry count */}
      <div
        className="flex items-center justify-between px-2 py-1 text-[10px] border-b"
        style={{
          color: 'var(--color-text-tertiary)',
          borderColor: 'var(--color-border-subtle)',
          backgroundColor: 'var(--color-bg-tertiary)',
        }}
      >
        <span>{filteredLogs.length} entries</span>
        {!autoScroll && <span className="text-yellow-500">Scroll paused</span>}
      </div>

      {/* Log entries */}
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto"
        style={{ backgroundColor: 'var(--color-bg-tertiary)' }}
      >
        {filteredLogs.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8" style={{ color: 'var(--color-text-tertiary)' }}>
            <FileText className="w-6 h-6 mb-2 opacity-50" />
            <p className="text-xs">No log entries</p>
            {(selectedStep || logLevel || searchQuery) && (
              <p className="text-[10px] mt-1">Try adjusting filters</p>
            )}
          </div>
        ) : (
          <div className="divide-y" style={{ borderColor: 'var(--color-border-subtle)' }}>
            {filteredLogs.map((log) => (
              <LogEntryRow key={log.id} log={log} />
            ))}
          </div>
        )}
      </div>

      {/* Scroll to bottom button */}
      {!autoScroll && filteredLogs.length > 0 && (
        <div className="absolute bottom-2 right-2">
          <Button variant="secondary" size="sm" onClick={scrollToBottom} className="shadow-lg text-xs px-2 py-1">
            <ArrowDown className="w-3 h-3 mr-1" />
            Latest
          </Button>
        </div>
      )}
    </div>
  );
}
