/**
 * Unit tests for BatchSummaryReport component.
 */

import { describe, it, expect, vi, beforeEach, type Mock } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BatchSummaryReport } from '../BatchSummaryReport';
import type { BatchSummaryReport as BatchSummaryReportType, StepSummary } from '../../../../types';

// Mock hooks
vi.mock('../../../../hooks', () => ({
  useBatchSummaryReport: vi.fn(),
  useExportBatchSummaryReport: vi.fn(),
}));

import { useBatchSummaryReport, useExportBatchSummaryReport } from '../../../../hooks';

describe('BatchSummaryReport', () => {
  const mockMutate = vi.fn();

  const mockSteps: StepSummary[] = [
    {
      stepName: 'Initialize',
      totalRuns: 100,
      passCount: 95,
      failCount: 5,
      passRate: 0.95,
      avgDuration: 1200,
      minDuration: 800,
      maxDuration: 2500,
    },
    {
      stepName: 'Execute Test',
      totalRuns: 100,
      passCount: 85,
      failCount: 15,
      passRate: 0.85,
      avgDuration: 3500,
      minDuration: 1500,
      maxDuration: 8000,
    },
  ];

  const mockReport: BatchSummaryReportType = {
    batchId: 'batch-001',
    batchName: 'Test Batch',
    sequenceName: 'test_sequence',
    sequenceVersion: '1.0.0',
    reportGeneratedAt: '2025-01-01T12:00:00Z',
    totalExecutions: 100,
    passCount: 85,
    failCount: 15,
    passRate: 0.85,
    avgDuration: 5000,
    steps: mockSteps,
    firstExecution: '2025-01-01T08:00:00Z',
    lastExecution: '2025-01-01T11:00:00Z',
  };

  beforeEach(() => {
    vi.clearAllMocks();

    (useExportBatchSummaryReport as Mock).mockReturnValue({
      mutate: mockMutate,
      isPending: false,
    });
  });

  it('should show select batch message when no batchId is provided', () => {
    (useBatchSummaryReport as Mock).mockReturnValue({
      data: null,
      isLoading: false,
      error: null,
    });

    render(<BatchSummaryReport batchId={null} />);

    expect(screen.getByText(/select a batch to view summary report/i)).toBeInTheDocument();
  });

  it('should show loading spinner when loading', () => {
    (useBatchSummaryReport as Mock).mockReturnValue({
      data: null,
      isLoading: true,
      error: null,
    });

    render(<BatchSummaryReport batchId="batch-001" />);

    // Check for loading state - table headers should not be present
    expect(screen.queryByText('Step Statistics')).not.toBeInTheDocument();
  });

  it('should show error message when error occurs', () => {
    (useBatchSummaryReport as Mock).mockReturnValue({
      data: null,
      isLoading: false,
      error: new Error('Failed to fetch'),
    });

    render(<BatchSummaryReport batchId="batch-001" />);

    expect(screen.getByText(/failed to load report/i)).toBeInTheDocument();
  });

  it('should show no data message when report is empty', () => {
    (useBatchSummaryReport as Mock).mockReturnValue({
      data: null,
      isLoading: false,
      error: null,
    });

    render(<BatchSummaryReport batchId="batch-001" />);

    expect(screen.getByText(/no data available/i)).toBeInTheDocument();
  });

  it('should render report header with batch name', () => {
    (useBatchSummaryReport as Mock).mockReturnValue({
      data: mockReport,
      isLoading: false,
      error: null,
    });

    render(<BatchSummaryReport batchId="batch-001" />);

    expect(screen.getByText('Test Batch')).toBeInTheDocument();
    expect(screen.getByText('test_sequence v1.0.0')).toBeInTheDocument();
  });

  it('should render summary cards with statistics', () => {
    (useBatchSummaryReport as Mock).mockReturnValue({
      data: mockReport,
      isLoading: false,
      error: null,
    });

    render(<BatchSummaryReport batchId="batch-001" />);

    expect(screen.getByText('Total Executions')).toBeInTheDocument();
    // Use getAllByText for values that may appear multiple times (in cards and table)
    expect(screen.getAllByText('100').length).toBeGreaterThan(0);

    // 'Pass Rate' may appear multiple times in summary card and table
    expect(screen.getAllByText('Pass Rate').length).toBeGreaterThan(0);
    // 85.0% may appear in summary and table, so use getAllByText
    expect(screen.getAllByText('85.0%').length).toBeGreaterThan(0);

    expect(screen.getByText('Pass / Fail')).toBeInTheDocument();

    expect(screen.getByText('Avg Duration')).toBeInTheDocument();
    expect(screen.getByText('5.00s')).toBeInTheDocument();
  });

  it('should render step statistics table', () => {
    (useBatchSummaryReport as Mock).mockReturnValue({
      data: mockReport,
      isLoading: false,
      error: null,
    });

    render(<BatchSummaryReport batchId="batch-001" />);

    expect(screen.getByText('Step Statistics')).toBeInTheDocument();
    expect(screen.getByText('Step Name')).toBeInTheDocument();
    expect(screen.getByText('Runs')).toBeInTheDocument();
    expect(screen.getByText('Initialize')).toBeInTheDocument();
    expect(screen.getByText('Execute Test')).toBeInTheDocument();
  });

  it('should render export button', () => {
    (useBatchSummaryReport as Mock).mockReturnValue({
      data: mockReport,
      isLoading: false,
      error: null,
    });

    render(<BatchSummaryReport batchId="batch-001" />);

    expect(screen.getByRole('button', { name: /export/i })).toBeInTheDocument();
  });

  it('should call export mutation when export button is clicked', () => {
    (useBatchSummaryReport as Mock).mockReturnValue({
      data: mockReport,
      isLoading: false,
      error: null,
    });

    render(<BatchSummaryReport batchId="batch-001" batchName="Test Batch" />);

    // Open dropdown and click xlsx
    fireEvent.click(screen.getByRole('button', { name: /export/i }));
    fireEvent.click(screen.getByText('Excel (.xlsx)'));

    expect(mockMutate).toHaveBeenCalledWith({
      batchId: 'batch-001',
      format: 'xlsx',
      batchName: 'Test Batch',
    });
  });

  it('should display execution time range', () => {
    (useBatchSummaryReport as Mock).mockReturnValue({
      data: mockReport,
      isLoading: false,
      error: null,
    });

    render(<BatchSummaryReport batchId="batch-001" />);

    expect(screen.getByText(/data range/i)).toBeInTheDocument();
  });

  it('should color pass rate based on value - high pass rate green', () => {
    const highPassReport = { ...mockReport, passRate: 0.95 };
    (useBatchSummaryReport as Mock).mockReturnValue({
      data: highPassReport,
      isLoading: false,
      error: null,
    });

    render(<BatchSummaryReport batchId="batch-001" />);

    // 95.0% may appear multiple times, check at least one exists
    const passRateElements = screen.getAllByText('95.0%');
    expect(passRateElements.length).toBeGreaterThan(0);
    // At least one should use the high rate CSS variable
    expect(passRateElements.some(el => el.style.color === 'var(--color-rate-high)')).toBe(true);
  });

  it('should color pass rate based on value - medium pass rate yellow', () => {
    const mediumPassReport = { ...mockReport, passRate: 0.75 };
    (useBatchSummaryReport as Mock).mockReturnValue({
      data: mediumPassReport,
      isLoading: false,
      error: null,
    });

    render(<BatchSummaryReport batchId="batch-001" />);

    const passRateElement = screen.getByText('75.0%');
    expect(passRateElement.style.color).toBe('var(--color-rate-medium)');
  });

  it('should color pass rate based on value - low pass rate red', () => {
    const lowPassReport = { ...mockReport, passRate: 0.65 };
    (useBatchSummaryReport as Mock).mockReturnValue({
      data: lowPassReport,
      isLoading: false,
      error: null,
    });

    render(<BatchSummaryReport batchId="batch-001" />);

    const passRateElement = screen.getByText('65.0%');
    expect(passRateElement.style.color).toBe('var(--color-rate-low)');
  });
});
