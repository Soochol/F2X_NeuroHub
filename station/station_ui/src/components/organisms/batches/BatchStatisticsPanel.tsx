/**
 * Batch Statistics Panel component.
 * Displays aggregated statistics for all batches.
 */

import { CheckCircle, XCircle, Layers, TrendingUp, Clock, Activity } from 'lucide-react';
import type { BatchStatistics, Batch } from '../../../types';

export interface BatchStatisticsPanelProps {
  batches: Batch[];
  statistics: Map<string, BatchStatistics>;
}

export function BatchStatisticsPanel({ batches, statistics }: BatchStatisticsPanelProps) {
  // Calculate aggregated statistics
  const totalStats = {
    total: 0,
    pass: 0,
    fail: 0,
    passRate: 0,
  };

  statistics.forEach((stats) => {
    totalStats.total += stats.total;
    totalStats.pass += stats.passCount;
    totalStats.fail += stats.fail;
  });

  if (totalStats.total > 0) {
    totalStats.passRate = totalStats.pass / totalStats.total;
  }

  // Count batch statuses
  const statusCounts = {
    running: batches.filter((b) => b.status === 'running' || b.status === 'starting').length,
    idle: batches.filter((b) => b.status === 'idle').length,
    completed: batches.filter((b) => b.status === 'completed').length,
    error: batches.filter((b) => b.status === 'error').length,
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
      {/* Total Executions */}
      <StatCard
        icon={<Layers className="w-5 h-5" />}
        label="Total Executions"
        value={totalStats.total}
        color="text-zinc-400"
        bgColor="bg-zinc-700/50"
      />

      {/* Pass Count */}
      <StatCard
        icon={<CheckCircle className="w-5 h-5" />}
        label="Passed"
        value={totalStats.pass}
        color="text-green-500"
        bgColor="bg-green-500/10"
      />

      {/* Fail Count */}
      <StatCard
        icon={<XCircle className="w-5 h-5" />}
        label="Failed"
        value={totalStats.fail}
        color="text-red-500"
        bgColor="bg-red-500/10"
      />

      {/* Pass Rate */}
      <StatCard
        icon={<TrendingUp className="w-5 h-5" />}
        label="Pass Rate"
        value={totalStats.total > 0 ? `${(totalStats.passRate * 100).toFixed(1)}%` : '-'}
        color={
          totalStats.passRate >= 0.9
            ? 'text-green-500'
            : totalStats.passRate >= 0.7
              ? 'text-yellow-500'
              : totalStats.passRate > 0
                ? 'text-red-500'
                : 'text-zinc-400'
        }
        bgColor={
          totalStats.passRate >= 0.9
            ? 'bg-green-500/10'
            : totalStats.passRate >= 0.7
              ? 'bg-yellow-500/10'
              : totalStats.passRate > 0
                ? 'bg-red-500/10'
                : 'bg-zinc-700/50'
        }
      />

      {/* Running Batches */}
      <StatCard
        icon={<Activity className="w-5 h-5" />}
        label="Running"
        value={statusCounts.running}
        color="text-brand-500"
        bgColor="bg-brand-500/10"
        subtitle={`${batches.length} total batches`}
      />

      {/* Batch Status Summary */}
      <div className="p-4 rounded-lg border" style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)' }}>
        <div className="flex items-center gap-2 mb-2">
          <Clock className="w-5 h-5" style={{ color: 'var(--color-text-secondary)' }} />
          <span className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>Batch Status</span>
        </div>
        <div className="flex items-center gap-3">
          <StatusDot color="bg-brand-500" value={statusCounts.running} label="Running" />
          <StatusDot color="bg-zinc-500" value={statusCounts.idle} label="Idle" />
          <StatusDot color="bg-green-500" value={statusCounts.completed} label="Done" />
          <StatusDot color="bg-red-500" value={statusCounts.error} label="Error" />
        </div>
      </div>
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
  color,
  bgColor,
  subtitle,
}: {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  color: string;
  bgColor: string;
  subtitle?: string;
}) {
  // Use CSS variable background for neutral colors, keep semantic colors for pass/fail/rate
  const isNeutral = bgColor === 'bg-zinc-700/50';
  const bgStyle = isNeutral
    ? { backgroundColor: 'var(--color-bg-tertiary)', borderColor: 'var(--color-border-default)' }
    : { borderColor: 'var(--color-border-default)' };

  return (
    <div className={`p-4 rounded-lg border ${isNeutral ? '' : bgColor}`} style={bgStyle}>
      <div className={`flex items-center gap-2 mb-2 ${color}`}>
        {icon}
        <span className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>{label}</span>
      </div>
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
      {subtitle && <p className="text-xs mt-1" style={{ color: 'var(--color-text-tertiary)' }}>{subtitle}</p>}
    </div>
  );
}

function StatusDot({
  color,
  value,
  label,
}: {
  color: string;
  value: number;
  label: string;
}) {
  return (
    <div className="flex items-center gap-1" title={label}>
      <div className={`w-2 h-2 rounded-full ${color}`} />
      <span className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>{value}</span>
    </div>
  );
}
