/**
 * Unit tests for StepAnalysisReport component.
 */

import { describe, it, expect, vi, beforeEach, type Mock } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { StepAnalysisReport } from '../StepAnalysisReport';
import type { StepAnalysisReport as StepAnalysisReportType, StepAnalysisItem, FailureReason } from '../../../../types';

// Mock hooks
vi.mock('../../../../hooks', () => ({
  useStepAnalysisReport: vi.fn(),
  useExportStepAnalysisReport: vi.fn(),
}));

import { useStepAnalysisReport, useExportStepAnalysisReport } from '../../../../hooks';

describe('StepAnalysisReport', () => {
  const mockMutate = vi.fn();

  const mockFailureReasons: FailureReason[] = [
    {
      errorMessage: 'Timeout exceeded',
      occurrenceCount: 5,
      percentage: 0.50,
    },
    {
      errorMessage: 'Connection failed',
      occurrenceCount: 3,
      percentage: 0.30,
    },
  ];

  const mockSteps: StepAnalysisItem[] = [
    {
      stepName: 'Initialize',
      totalRuns: 100,
      failCount: 5,
      failRate: 0.05,
      avgDuration: 1200,
      minDuration: 800,
      maxDuration: 2500,
      p50Duration: 1100,
      p95Duration: 2200,
      failureReasons: [],
    },
    {
      stepName: 'Execute Test',
      totalRuns: 100,
      failCount: 15,
      failRate: 0.15,
      avgDuration: 8000,
      minDuration: 3000,
      maxDuration: 15000,
      p50Duration: 7500,
      p95Duration: 14000,
      failureReasons: mockFailureReasons,
    },
    {
      stepName: 'Cleanup',
      totalRuns: 100,
      failCount: 2,
      failRate: 0.02,
      avgDuration: 500,
      minDuration: 300,
      maxDuration: 1000,
      p50Duration: 450,
      p95Duration: 900,
      failureReasons: [],
    },
  ];

  const mockReport: StepAnalysisReportType = {
    fromDate: null,
    toDate: null,
    batchId: null,
    reportGeneratedAt: '2025-01-03T12:00:00Z',
    steps: mockSteps,
    totalSteps: 3,
    mostFailedStep: 'Execute Test',
    slowestStep: 'Execute Test',
  };

  beforeEach(() => {
    vi.clearAllMocks();

    (useExportStepAnalysisReport as Mock).mockReturnValue({
      mutate: mockMutate,
      isPending: false,
    });
  });

  it('should show loading spinner when loading', () => {
    (useStepAnalysisReport as Mock).mockReturnValue({
      data: null,
      isLoading: true,
      error: null,
    });

    render(<StepAnalysisReport />);

    // Table headers should not be visible when loading
    expect(screen.queryByText('Step Name')).not.toBeInTheDocument();
  });

  it('should show error message when error occurs', () => {
    (useStepAnalysisReport as Mock).mockReturnValue({
      data: null,
      isLoading: false,
      error: new Error('Failed to fetch'),
    });

    render(<StepAnalysisReport />);

    expect(screen.getByText(/failed to load report/i)).toBeInTheDocument();
  });

  it('should show no data message when report is empty', () => {
    (useStepAnalysisReport as Mock).mockReturnValue({
      data: null,
      isLoading: false,
      error: null,
    });

    render(<StepAnalysisReport />);

    expect(screen.getByText(/no step data available/i)).toBeInTheDocument();
  });

  it('should show no data message when steps array is empty', () => {
    (useStepAnalysisReport as Mock).mockReturnValue({
      data: { ...mockReport, steps: [] },
      isLoading: false,
      error: null,
    });

    render(<StepAnalysisReport />);

    expect(screen.getByText(/no step data available/i)).toBeInTheDocument();
  });

  it('should render report header with step count', () => {
    (useStepAnalysisReport as Mock).mockReturnValue({
      data: mockReport,
      isLoading: false,
      error: null,
    });

    render(<StepAnalysisReport />);

    expect(screen.getByText('Step Analysis')).toBeInTheDocument();
    expect(screen.getByText('3 steps analyzed')).toBeInTheDocument();
  });

  it('should render summary cards for most failed and slowest steps', () => {
    (useStepAnalysisReport as Mock).mockReturnValue({
      data: mockReport,
      isLoading: false,
      error: null,
    });

    render(<StepAnalysisReport />);

    expect(screen.getByText('Most Failed Step')).toBeInTheDocument();
    expect(screen.getByText('Slowest Step')).toBeInTheDocument();
    expect(screen.getAllByText('Execute Test')).toHaveLength(3); // In summary cards and table
  });

  it('should render step analysis table with all steps', () => {
    (useStepAnalysisReport as Mock).mockReturnValue({
      data: mockReport,
      isLoading: false,
      error: null,
    });

    render(<StepAnalysisReport />);

    expect(screen.getByText('Initialize')).toBeInTheDocument();
    expect(screen.getAllByText('Execute Test')).toHaveLength(3);
    expect(screen.getByText('Cleanup')).toBeInTheDocument();
  });

  it('should display badges for most failed and slowest steps', () => {
    (useStepAnalysisReport as Mock).mockReturnValue({
      data: mockReport,
      isLoading: false,
      error: null,
    });

    render(<StepAnalysisReport />);

    expect(screen.getByText('Most Failed')).toBeInTheDocument();
    expect(screen.getByText('Slowest')).toBeInTheDocument();
  });

  it('should render export button', () => {
    (useStepAnalysisReport as Mock).mockReturnValue({
      data: mockReport,
      isLoading: false,
      error: null,
    });

    render(<StepAnalysisReport />);

    expect(screen.getByRole('button', { name: /export/i })).toBeInTheDocument();
  });

  it('should call export mutation when export button is clicked', () => {
    (useStepAnalysisReport as Mock).mockReturnValue({
      data: mockReport,
      isLoading: false,
      error: null,
    });

    render(<StepAnalysisReport />);

    // Open dropdown and click xlsx
    fireEvent.click(screen.getByRole('button', { name: /export/i }));
    fireEvent.click(screen.getByText('Excel (.xlsx)'));

    expect(mockMutate).toHaveBeenCalledWith(
      expect.objectContaining({
        format: 'xlsx',
      })
    );
  });

  it('should expand step row to show failure reasons when clicked', () => {
    (useStepAnalysisReport as Mock).mockReturnValue({
      data: mockReport,
      isLoading: false,
      error: null,
    });

    render(<StepAnalysisReport />);

    // Click on Execute Test row (which has failure reasons)
    const executeTestRows = screen.getAllByText('Execute Test');
    fireEvent.click(executeTestRows[2]); // Click the one in the table

    // Failure reasons should be visible
    expect(screen.getByText('Failure Reasons')).toBeInTheDocument();
    expect(screen.getByText('Timeout exceeded')).toBeInTheDocument();
    expect(screen.getByText('Connection failed')).toBeInTheDocument();
  });

  it('should display occurrence count for failure reasons', () => {
    (useStepAnalysisReport as Mock).mockReturnValue({
      data: mockReport,
      isLoading: false,
      error: null,
    });

    render(<StepAnalysisReport />);

    // Expand the step with failures
    const executeTestRows = screen.getAllByText('Execute Test');
    fireEvent.click(executeTestRows[2]);

    expect(screen.getByText('5x')).toBeInTheDocument();
    expect(screen.getByText('3x')).toBeInTheDocument();
  });

  it('should display failure percentage', () => {
    (useStepAnalysisReport as Mock).mockReturnValue({
      data: mockReport,
      isLoading: false,
      error: null,
    });

    render(<StepAnalysisReport />);

    // Expand the step with failures
    const executeTestRows = screen.getAllByText('Execute Test');
    fireEvent.click(executeTestRows[2]);

    expect(screen.getByText('50.0% of failures')).toBeInTheDocument();
    expect(screen.getByText('30.0% of failures')).toBeInTheDocument();
  });

  it('should pass batchId to hook when provided', () => {
    (useStepAnalysisReport as Mock).mockReturnValue({
      data: mockReport,
      isLoading: false,
      error: null,
    });

    render(<StepAnalysisReport batchId="batch-001" />);

    expect(useStepAnalysisReport).toHaveBeenCalledWith(
      expect.objectContaining({
        batchId: 'batch-001',
      })
    );
  });

  it('should display report generation timestamp', () => {
    (useStepAnalysisReport as Mock).mockReturnValue({
      data: mockReport,
      isLoading: false,
      error: null,
    });

    render(<StepAnalysisReport />);

    expect(screen.getByText(/report generated at/i)).toBeInTheDocument();
  });

  it('should not render summary cards when most failed and slowest are null', () => {
    const reportWithoutHighlights = {
      ...mockReport,
      mostFailedStep: null,
      slowestStep: null,
    };

    (useStepAnalysisReport as Mock).mockReturnValue({
      data: reportWithoutHighlights,
      isLoading: false,
      error: null,
    });

    render(<StepAnalysisReport />);

    expect(screen.queryByText('Most Failed Step')).not.toBeInTheDocument();
    expect(screen.queryByText('Slowest Step')).not.toBeInTheDocument();
  });
});
