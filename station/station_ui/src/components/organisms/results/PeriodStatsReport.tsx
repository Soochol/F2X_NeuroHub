/**
 * Period statistics report component.
 */

import { useState } from 'react';
import { TrendingUp, TrendingDown, Minus, Calendar } from 'lucide-react';
import { usePeriodStatsReport, useExportPeriodStatsReport } from '../../../hooks';
import { LoadingSpinner } from '../../atoms/LoadingSpinner';
import { Input } from '../../atoms/Input';
import { Select } from '../../atoms/Select';
import { ExportButton } from './ExportButton';
import type { PeriodType, ExportFormat } from '../../../types';

interface PeriodStatsReportProps {
  batchId?: string;
}

const periodOptions = [
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'monthly', label: 'Monthly' },
];

function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms.toFixed(0)}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(2)}s`;
  return `${Math.floor(ms / 60000)}m ${((ms % 60000) / 1000).toFixed(1)}s`;
}

function getDefaultDates(): { from: string; to: string } {
  const to = new Date();
  const from = new Date();
  from.setDate(from.getDate() - 30);
  return {
    from: from.toISOString().slice(0, 10),
    to: to.toISOString().slice(0, 10),
  };
}

/**
 * Get the CSS variable for pass rate color based on value.
 */
function getPassRateColor(rate: number): string {
  if (rate >= 0.9) return 'var(--color-rate-high)';
  if (rate >= 0.7) return 'var(--color-rate-medium)';
  return 'var(--color-rate-low)';
}

/**
 * Get the CSS variable for trend direction color.
 */
function getTrendColor(direction: 'increasing' | 'decreasing' | 'stable'): string {
  if (direction === 'increasing') return 'var(--color-rate-high)';
  if (direction === 'decreasing') return 'var(--color-rate-low)';
  return 'var(--color-text-secondary)';
}

export function PeriodStatsReport({ batchId }: PeriodStatsReportProps) {
  const defaults = getDefaultDates();
  const [periodType, setPeriodType] = useState<PeriodType>('daily');
  const [fromDate, setFromDate] = useState(defaults.from);
  const [toDate, setToDate] = useState(defaults.to);

  const { data: report, isLoading, error } = usePeriodStatsReport(
    periodType,
    fromDate,
    toDate,
    batchId
  );
  const exportMutation = useExportPeriodStatsReport();

  const handleExport = (format: ExportFormat) => {
    exportMutation.mutate({ periodType, fromDate, toDate, format, batchId });
  };

  const TrendIcon = () => {
    if (!report) return null;
    const trendColor = getTrendColor(report.trendDirection);
    switch (report.trendDirection) {
      case 'increasing':
        return <TrendingUp className="w-5 h-5" style={{ color: trendColor }} />;
      case 'decreasing':
        return <TrendingDown className="w-5 h-5" style={{ color: trendColor }} />;
      default:
        return <Minus className="w-5 h-5" style={{ color: trendColor }} />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex flex-wrap items-end gap-4">
        <div className="w-40">
          <label className="block text-xs mb-1" style={{ color: 'var(--color-text-tertiary)' }}>
            Period
          </label>
          <Select
            options={periodOptions}
            value={periodType}
            onChange={(e) => setPeriodType(e.target.value as PeriodType)}
          />
        </div>
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4" style={{ color: 'var(--color-text-secondary)' }} />
          <div>
            <label className="block text-xs mb-1" style={{ color: 'var(--color-text-tertiary)' }}>
              From
            </label>
            <Input
              type="date"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
            />
          </div>
        </div>
        <div>
          <label className="block text-xs mb-1" style={{ color: 'var(--color-text-tertiary)' }}>
            To
          </label>
          <Input
            type="date"
            value={toDate}
            onChange={(e) => setToDate(e.target.value)}
          />
        </div>
        <ExportButton
          onExport={handleExport}
          isLoading={exportMutation.isPending}
          disabled={!fromDate || !toDate}
        />
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner size="lg" />
        </div>
      ) : error ? (
        <div
          className="flex items-center justify-center h-64 text-sm"
          style={{ color: 'var(--color-rate-low)' }}
        >
          Failed to load report: {(error as Error).message}
        </div>
      ) : !report ? (
        <div
          className="flex items-center justify-center h-64 text-sm"
          style={{ color: 'var(--color-text-tertiary)' }}
        >
          No data available for the selected period
        </div>
      ) : (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div
              className="p-4 rounded-lg"
              style={{ backgroundColor: 'var(--color-bg-tertiary)' }}
            >
              <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                Total Executions
              </span>
              <p className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>
                {report.totalExecutions}
              </p>
            </div>
            <div
              className="p-4 rounded-lg"
              style={{ backgroundColor: 'var(--color-bg-tertiary)' }}
            >
              <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                Overall Pass Rate
              </span>
              <p
                className="text-2xl font-bold"
                style={{ color: getPassRateColor(report.overallPassRate) }}
              >
                {formatPercent(report.overallPassRate)}
              </p>
            </div>
            <div
              className="p-4 rounded-lg"
              style={{ backgroundColor: 'var(--color-bg-tertiary)' }}
            >
              <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                Periods
              </span>
              <p className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>
                {report.dataPoints.length}
              </p>
            </div>
            <div
              className="p-4 rounded-lg"
              style={{ backgroundColor: 'var(--color-bg-tertiary)' }}
            >
              <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                Trend
              </span>
              <div className="flex items-center gap-2 mt-1">
                <TrendIcon />
                <span
                  className="text-xl font-bold"
                  style={{ color: getTrendColor(report.trendDirection) }}
                >
                  {report.trendPercentage > 0 ? '+' : ''}
                  {formatPercent(report.trendPercentage / 100)}
                </span>
              </div>
            </div>
          </div>

          {/* Period Data Table */}
          <div>
            <h4 className="text-sm font-medium mb-3" style={{ color: 'var(--color-text-primary)' }}>
              Period Breakdown
            </h4>
            <div
              className="rounded-lg border overflow-hidden"
              style={{ borderColor: 'var(--color-border-default)' }}
            >
              <table className="min-w-full">
                <thead style={{ backgroundColor: 'var(--color-bg-tertiary)' }}>
                  <tr>
                    <th
                      className="px-4 py-3 text-left text-xs font-medium uppercase"
                      style={{ color: 'var(--color-text-secondary)' }}
                    >
                      Period
                    </th>
                    <th
                      className="px-4 py-3 text-right text-xs font-medium uppercase"
                      style={{ color: 'var(--color-text-secondary)' }}
                    >
                      Total
                    </th>
                    <th
                      className="px-4 py-3 text-right text-xs font-medium uppercase"
                      style={{ color: 'var(--color-text-secondary)' }}
                    >
                      Pass
                    </th>
                    <th
                      className="px-4 py-3 text-right text-xs font-medium uppercase"
                      style={{ color: 'var(--color-text-secondary)' }}
                    >
                      Fail
                    </th>
                    <th
                      className="px-4 py-3 text-right text-xs font-medium uppercase"
                      style={{ color: 'var(--color-text-secondary)' }}
                    >
                      Pass Rate
                    </th>
                    <th
                      className="px-4 py-3 text-right text-xs font-medium uppercase"
                      style={{ color: 'var(--color-text-secondary)' }}
                    >
                      Avg Duration
                    </th>
                  </tr>
                </thead>
                <tbody
                  className="divide-y"
                  style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-subtle)' }}
                >
                  {report.dataPoints.map((point) => (
                    <tr key={point.periodLabel}>
                      <td className="px-4 py-3">
                        <span className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
                          {point.periodLabel}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <span className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                          {point.total}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <span className="text-sm" style={{ color: 'var(--color-rate-high)' }}>
                          {point.passCount}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <span className="text-sm" style={{ color: 'var(--color-rate-low)' }}>
                          {point.failCount}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <span
                          className="text-sm font-medium"
                          style={{ color: getPassRateColor(point.passRate) }}
                        >
                          {formatPercent(point.passRate)}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <span className="text-sm font-mono" style={{ color: 'var(--color-text-secondary)' }}>
                          {formatDuration(point.avgDuration)}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
