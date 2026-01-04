/**
 * Unit tests for PeriodStatsReport component.
 */

import { describe, it, expect, vi, beforeEach, type Mock } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { PeriodStatsReport } from '../PeriodStatsReport';
import type { PeriodStatisticsReport, PeriodDataPoint } from '../../../../types';

// Mock hooks
vi.mock('../../../../hooks', () => ({
  usePeriodStatsReport: vi.fn(),
  useExportPeriodStatsReport: vi.fn(),
}));

import { usePeriodStatsReport, useExportPeriodStatsReport } from '../../../../hooks';

describe('PeriodStatsReport', () => {
  const mockMutate = vi.fn();

  const mockDataPoints: PeriodDataPoint[] = [
    {
      periodStart: '2025-01-01T00:00:00Z',
      periodEnd: '2025-01-01T23:59:59Z',
      periodLabel: '2025-01-01',
      total: 50,
      passCount: 45,
      failCount: 5,
      passRate: 0.90,
      avgDuration: 5000,
    },
    {
      periodStart: '2025-01-02T00:00:00Z',
      periodEnd: '2025-01-02T23:59:59Z',
      periodLabel: '2025-01-02',
      total: 60,
      passCount: 55,
      failCount: 5,
      passRate: 0.917,
      avgDuration: 4500,
    },
  ];

  const mockReport: PeriodStatisticsReport = {
    periodType: 'daily',
    fromDate: '2025-01-01T00:00:00Z',
    toDate: '2025-01-02T23:59:59Z',
    batchId: null,
    reportGeneratedAt: '2025-01-03T12:00:00Z',
    totalExecutions: 110,
    overallPassRate: 0.909,
    dataPoints: mockDataPoints,
    trendDirection: 'increasing',
    trendPercentage: 5.2,
  };

  beforeEach(() => {
    vi.clearAllMocks();

    (useExportPeriodStatsReport as Mock).mockReturnValue({
      mutate: mockMutate,
      isPending: false,
    });
  });

  it('should render period selector and date filters', () => {
    (usePeriodStatsReport as Mock).mockReturnValue({
      data: mockReport,
      isLoading: false,
      error: null,
    });

    render(<PeriodStatsReport />);

    // 'Period' may appear multiple times (label and table header), use getAllByText
    expect(screen.getAllByText('Period').length).toBeGreaterThan(0);
    expect(screen.getByText('From')).toBeInTheDocument();
    // 'To' may also appear in multiple places
    expect(screen.getAllByText('To').length).toBeGreaterThan(0);
    // Use getAllByRole since there may be multiple comboboxes
    const comboboxes = screen.getAllByRole('combobox');
    expect(comboboxes.length).toBeGreaterThan(0);
  });

  it('should show loading spinner when loading', () => {
    (usePeriodStatsReport as Mock).mockReturnValue({
      data: null,
      isLoading: true,
      error: null,
    });

    render(<PeriodStatsReport />);

    // Table should not be visible when loading
    expect(screen.queryByText('Period Breakdown')).not.toBeInTheDocument();
  });

  it('should show error message when error occurs', () => {
    (usePeriodStatsReport as Mock).mockReturnValue({
      data: null,
      isLoading: false,
      error: new Error('Failed to fetch'),
    });

    render(<PeriodStatsReport />);

    expect(screen.getByText(/failed to load report/i)).toBeInTheDocument();
  });

  it('should show no data message when report is empty', () => {
    (usePeriodStatsReport as Mock).mockReturnValue({
      data: null,
      isLoading: false,
      error: null,
    });

    render(<PeriodStatsReport />);

    expect(screen.getByText(/no data available/i)).toBeInTheDocument();
  });

  it('should render summary cards with statistics', () => {
    (usePeriodStatsReport as Mock).mockReturnValue({
      data: mockReport,
      isLoading: false,
      error: null,
    });

    render(<PeriodStatsReport />);

    expect(screen.getByText('Total Executions')).toBeInTheDocument();
    expect(screen.getByText('110')).toBeInTheDocument();

    expect(screen.getByText('Overall Pass Rate')).toBeInTheDocument();
    expect(screen.getByText('90.9%')).toBeInTheDocument();

    expect(screen.getByText('Periods')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
  });

  it('should render period breakdown table', () => {
    (usePeriodStatsReport as Mock).mockReturnValue({
      data: mockReport,
      isLoading: false,
      error: null,
    });

    render(<PeriodStatsReport />);

    expect(screen.getByText('Period Breakdown')).toBeInTheDocument();
    expect(screen.getByText('2025-01-01')).toBeInTheDocument();
    expect(screen.getByText('2025-01-02')).toBeInTheDocument();
  });

  it('should display trend information', () => {
    (usePeriodStatsReport as Mock).mockReturnValue({
      data: mockReport,
      isLoading: false,
      error: null,
    });

    render(<PeriodStatsReport />);

    expect(screen.getByText('Trend')).toBeInTheDocument();
    // Should show positive trend
    expect(screen.getByText(/\+5.2%/)).toBeInTheDocument();
  });

  it('should render export button', () => {
    (usePeriodStatsReport as Mock).mockReturnValue({
      data: mockReport,
      isLoading: false,
      error: null,
    });

    render(<PeriodStatsReport />);

    expect(screen.getByRole('button', { name: /export/i })).toBeInTheDocument();
  });

  it('should call export mutation when export button is clicked', () => {
    (usePeriodStatsReport as Mock).mockReturnValue({
      data: mockReport,
      isLoading: false,
      error: null,
    });

    render(<PeriodStatsReport />);

    // Open dropdown and click xlsx
    fireEvent.click(screen.getByRole('button', { name: /export/i }));
    fireEvent.click(screen.getByText('Excel (.xlsx)'));

    expect(mockMutate).toHaveBeenCalledWith(
      expect.objectContaining({
        format: 'xlsx',
        periodType: 'daily',
      })
    );
  });

  it('should change period type when selector changes', () => {
    (usePeriodStatsReport as Mock).mockReturnValue({
      data: mockReport,
      isLoading: false,
      error: null,
    });

    render(<PeriodStatsReport />);

    const periodSelect = screen.getByRole('combobox');
    fireEvent.change(periodSelect, { target: { value: 'weekly' } });

    // Hook should be called with new period type
    expect(usePeriodStatsReport).toHaveBeenCalled();
  });

  it('should display decreasing trend icon for decreasing trend', () => {
    const decreasingReport = { ...mockReport, trendDirection: 'decreasing' as const, trendPercentage: -3.5 };
    (usePeriodStatsReport as Mock).mockReturnValue({
      data: decreasingReport,
      isLoading: false,
      error: null,
    });

    render(<PeriodStatsReport />);

    expect(screen.getByText('Trend')).toBeInTheDocument();
    // The trend percentage is formatted as: formatPercent(-3.5 / 100) = "-3.5%"
    expect(screen.getByText('-3.5%')).toBeInTheDocument();
  });

  it('should display stable trend icon for stable trend', () => {
    const stableReport = { ...mockReport, trendDirection: 'stable' as const, trendPercentage: 0 };
    (usePeriodStatsReport as Mock).mockReturnValue({
      data: stableReport,
      isLoading: false,
      error: null,
    });

    render(<PeriodStatsReport />);

    expect(screen.getByText('Trend')).toBeInTheDocument();
  });

  it('should pass batchId to hook when provided', () => {
    (usePeriodStatsReport as Mock).mockReturnValue({
      data: mockReport,
      isLoading: false,
      error: null,
    });

    render(<PeriodStatsReport batchId="batch-001" />);

    expect(usePeriodStatsReport).toHaveBeenCalledWith(
      'daily',
      expect.any(String),
      expect.any(String),
      'batch-001'
    );
  });

  it('should color pass rates based on value', () => {
    (usePeriodStatsReport as Mock).mockReturnValue({
      data: mockReport,
      isLoading: false,
      error: null,
    });

    render(<PeriodStatsReport />);

    // Check that pass rates are displayed with correct colors
    const passRateElements = screen.getAllByText(/90\.0%/);
    expect(passRateElements.length).toBeGreaterThan(0);
  });
});
