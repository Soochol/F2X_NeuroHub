/**
 * Stats card component for dashboard.
 */

import type { ReactNode } from 'react';

export interface StatsCardProps {
  title: string;
  value: string | number;
  icon: ReactNode;
  variant?: 'default' | 'info' | 'success' | 'warning' | 'error';
  trend?: {
    value: number;
    label?: string;
  };
  className?: string;
}

const variantStyles = {
  default: {
    bg: 'var(--color-bg-secondary)',
    border: 'var(--color-border-default)',
    icon: 'var(--color-text-secondary)',
  },
  info: {
    bg: 'rgba(59, 130, 246, 0.1)',
    border: 'rgba(59, 130, 246, 0.3)',
    icon: '#60a5fa',
  },
  success: {
    bg: 'rgba(34, 197, 94, 0.1)',
    border: 'rgba(34, 197, 94, 0.3)',
    icon: '#4ade80',
  },
  warning: {
    bg: 'rgba(245, 158, 11, 0.1)',
    border: 'rgba(245, 158, 11, 0.3)',
    icon: '#fbbf24',
  },
  error: {
    bg: 'rgba(239, 68, 68, 0.1)',
    border: 'rgba(239, 68, 68, 0.3)',
    icon: '#f87171',
  },
};

export function StatsCard({
  title,
  value,
  icon,
  variant = 'default',
  trend,
  className = '',
}: StatsCardProps) {
  const styles = variantStyles[variant];

  return (
    <div
      className={`p-4 rounded-lg border transition-colors ${className}`}
      style={{
        backgroundColor: styles.bg,
        borderColor: styles.border,
      }}
    >
      <div className="flex items-center justify-between">
        <span className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
          {title}
        </span>
        <span style={{ color: styles.icon }}>{icon}</span>
      </div>
      <div
        className="mt-2 text-3xl font-bold"
        style={{ color: 'var(--color-text-primary)' }}
      >
        {value}
      </div>
      {trend && (
        <div className="mt-2 flex items-center gap-1 text-sm">
          <span style={{ color: trend.value >= 0 ? '#4ade80' : '#f87171' }}>
            {trend.value >= 0 ? '+' : ''}
            {trend.value}%
          </span>
          {trend.label && (
            <span style={{ color: 'var(--color-text-tertiary)' }}>{trend.label}</span>
          )}
        </div>
      )}
    </div>
  );
}
