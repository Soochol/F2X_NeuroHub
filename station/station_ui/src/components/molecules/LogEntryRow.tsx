/**
 * Log entry row component.
 */

import type { LogEntry, LogLevel } from '../../types';

export interface LogEntryRowProps {
  log: LogEntry;
  showBatchId?: boolean;
}

const levelStyles: Record<LogLevel, { text: string; badge: string; badgeText: string }> = {
  debug: {
    text: 'var(--color-text-tertiary)',
    badge: 'rgba(113, 113, 122, 0.2)',
    badgeText: 'var(--color-text-secondary)',
  },
  info: {
    text: 'var(--color-text-primary)',
    badge: 'rgba(59, 130, 246, 0.2)',
    badgeText: '#60a5fa',
  },
  warning: {
    text: '#fbbf24',
    badge: 'rgba(245, 158, 11, 0.2)',
    badgeText: '#fbbf24',
  },
  error: {
    text: '#f87171',
    badge: 'rgba(239, 68, 68, 0.2)',
    badgeText: '#f87171',
  },
};

export function LogEntryRow({ log, showBatchId = true }: LogEntryRowProps) {
  const formatTime = (date: Date) => {
    return new Date(date).toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const styles = levelStyles[log.level];

  return (
    <div
      className="flex items-start gap-3 py-1.5 px-2 rounded text-sm font-mono transition-colors"
      style={{ backgroundColor: 'transparent' }}
      onMouseEnter={(e) => {
        e.currentTarget.style.backgroundColor = 'var(--color-bg-tertiary)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.backgroundColor = 'transparent';
      }}
    >
      <span
        className="text-xs w-20 flex-shrink-0"
        style={{ color: 'var(--color-text-tertiary)' }}
      >
        {formatTime(log.timestamp)}
      </span>
      <span
        className="px-1.5 py-0.5 rounded text-xs uppercase w-16 text-center flex-shrink-0"
        style={{ backgroundColor: styles.badge, color: styles.badgeText }}
      >
        {log.level}
      </span>
      {showBatchId && log.batchId && (
        <span className="flex-shrink-0" style={{ color: 'var(--color-text-tertiary)' }}>
          [{log.batchId}]
        </span>
      )}
      <span className="flex-1 break-all" style={{ color: styles.text }}>
        {log.message}
      </span>
    </div>
  );
}
