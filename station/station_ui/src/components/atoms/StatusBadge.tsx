/**
 * Status badge component.
 */

import type { BatchStatus } from '../../types';

interface StatusBadgeProps {
  status: BatchStatus | 'connected' | 'disconnected' | 'warning' | 'pass' | 'fail';
  size?: 'sm' | 'md';
  className?: string;
}

const statusConfig: Record<
  string,
  { label: string; bg: string; text: string; dot: string; animate?: boolean }
> = {
  idle: {
    label: 'IDLE',
    bg: 'rgba(113, 113, 122, 0.2)',
    text: '#a1a1aa',
    dot: '#a1a1aa',
  },
  starting: {
    label: 'STARTING',
    bg: 'rgba(59, 130, 246, 0.2)',
    text: '#60a5fa',
    dot: '#60a5fa',
  },
  running: {
    label: 'RUNNING',
    bg: 'rgba(62, 207, 142, 0.2)',
    text: '#3ecf8e',
    dot: '#3ecf8e',
    animate: true,
  },
  stopping: {
    label: 'STOPPING',
    bg: 'rgba(245, 158, 11, 0.2)',
    text: '#fbbf24',
    dot: '#fbbf24',
  },
  completed: {
    label: 'COMPLETED',
    bg: 'rgba(34, 197, 94, 0.2)',
    text: '#4ade80',
    dot: '#4ade80',
  },
  error: {
    label: 'ERROR',
    bg: 'rgba(239, 68, 68, 0.2)',
    text: '#f87171',
    dot: '#f87171',
  },
  connected: {
    label: 'CONNECTED',
    bg: 'rgba(34, 197, 94, 0.2)',
    text: '#4ade80',
    dot: '#4ade80',
  },
  disconnected: {
    label: 'DISCONNECTED',
    bg: 'rgba(239, 68, 68, 0.2)',
    text: '#f87171',
    dot: '#f87171',
  },
  warning: {
    label: 'WARNING',
    bg: 'rgba(245, 158, 11, 0.2)',
    text: '#fbbf24',
    dot: '#fbbf24',
    animate: true,
  },
  pass: {
    label: 'PASS',
    bg: 'rgba(34, 197, 94, 0.2)',
    text: '#4ade80',
    dot: '#4ade80',
  },
  fail: {
    label: 'FAIL',
    bg: 'rgba(239, 68, 68, 0.2)',
    text: '#f87171',
    dot: '#f87171',
  },
};

const sizeClasses = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-xs',
};

const dotSizeClasses = {
  sm: 'w-1.5 h-1.5',
  md: 'w-2 h-2',
};

export function StatusBadge({ status, size = 'md', className = '' }: StatusBadgeProps) {
  const config = statusConfig[status] ?? statusConfig['idle']!;

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-medium ${sizeClasses[size]} ${className}`}
      style={{ backgroundColor: config.bg, color: config.text }}
    >
      <span
        className={`rounded-full ${dotSizeClasses[size]} ${config.animate ? 'animate-pulse' : ''}`}
        style={{ backgroundColor: config.dot }}
      />
      {config.label}
    </span>
  );
}
