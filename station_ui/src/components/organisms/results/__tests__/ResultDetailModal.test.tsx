/**
 * Unit tests for ResultDetailModal component.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ResultDetailModal } from '../ResultDetailModal';
import type { ExecutionResult, StepResult } from '../../../../types';

describe('ResultDetailModal', () => {
  const mockOnClose = vi.fn();

  const mockSteps: StepResult[] = [
    {
      name: 'Initialize',
      order: 1,
      status: 'completed',
      duration: 1.5,
      pass: true,
      result: { voltage: 3.3, current: 0.5 },
    },
    {
      name: 'Execute Test',
      order: 2,
      status: 'failed',
      duration: 2.5,
      pass: false,
      error: 'Test timeout exceeded',
    },
    {
      name: 'Cleanup',
      order: 3,
      status: 'skipped',
      duration: 0,
      pass: false,
    },
  ];

  const mockResult: ExecutionResult = {
    id: 'exec-12345678-1234-1234-1234-123456789012',
    sequenceName: 'Test Sequence',
    sequenceVersion: '1.0.0',
    status: 'failed',
    startedAt: '2025-01-01T10:00:00Z',
    completedAt: '2025-01-01T10:00:05Z',
    duration: 5000,
    batchId: 'batch-001',
    overallPass: false,
    steps: mockSteps,
    parameters: {},
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render modal with result details', () => {
    render(<ResultDetailModal result={mockResult} onClose={mockOnClose} />);

    expect(screen.getByText('Test Sequence')).toBeInTheDocument();
    expect(screen.getByText(/v1.0.0/)).toBeInTheDocument();
  });

  it('should display batch ID', () => {
    render(<ResultDetailModal result={mockResult} onClose={mockOnClose} />);

    expect(screen.getByText('batch-00')).toBeInTheDocument();
  });

  it('should display steps count', () => {
    render(<ResultDetailModal result={mockResult} onClose={mockOnClose} />);

    expect(screen.getByText('Steps (3)')).toBeInTheDocument();
  });

  it('should display step names', () => {
    render(<ResultDetailModal result={mockResult} onClose={mockOnClose} />);

    expect(screen.getByText('Initialize')).toBeInTheDocument();
    expect(screen.getByText('Execute Test')).toBeInTheDocument();
    expect(screen.getByText('Cleanup')).toBeInTheDocument();
  });

  it('should display step status badges', () => {
    render(<ResultDetailModal result={mockResult} onClose={mockOnClose} />);

    expect(screen.getByText('completed')).toBeInTheDocument();
    expect(screen.getByText('failed')).toBeInTheDocument();
    expect(screen.getByText('skipped')).toBeInTheDocument();
  });

  it('should call onClose when close button is clicked', () => {
    render(<ResultDetailModal result={mockResult} onClose={mockOnClose} />);

    const closeButtons = screen.getAllByRole('button');
    // First button is X icon, last button is Close text button
    fireEvent.click(closeButtons[0]);

    expect(mockOnClose).toHaveBeenCalled();
  });

  it('should call onClose when Close button is clicked', () => {
    render(<ResultDetailModal result={mockResult} onClose={mockOnClose} />);

    fireEvent.click(screen.getByRole('button', { name: /close/i }));

    expect(mockOnClose).toHaveBeenCalled();
  });

  it('should call onClose when backdrop is clicked', () => {
    render(<ResultDetailModal result={mockResult} onClose={mockOnClose} />);

    // Click on the backdrop (first div with bg-black/50)
    const backdrop = document.querySelector('.bg-black\\/50');
    if (backdrop) {
      fireEvent.click(backdrop);
    }

    expect(mockOnClose).toHaveBeenCalled();
  });

  it('should show failed status indicator for failed executions', () => {
    render(<ResultDetailModal result={mockResult} onClose={mockOnClose} />);

    expect(screen.getByText(/execution failed/i)).toBeInTheDocument();
  });

  it('should not show failed indicator for passed executions', () => {
    const passedResult = {
      ...mockResult,
      status: 'completed' as const,
      overallPass: true,
    };

    render(<ResultDetailModal result={passedResult} onClose={mockOnClose} />);

    expect(screen.queryByText(/execution failed/i)).not.toBeInTheDocument();
  });

  it('should expand step details when clicked', () => {
    render(<ResultDetailModal result={mockResult} onClose={mockOnClose} />);

    // Click on step with error to expand
    fireEvent.click(screen.getByText('Execute Test'));

    // Error should be visible after expand
    expect(screen.getByText('Test timeout exceeded')).toBeInTheDocument();
  });

  it('should show result data when step is expanded', () => {
    render(<ResultDetailModal result={mockResult} onClose={mockOnClose} />);

    // Click on step with result data to expand
    fireEvent.click(screen.getByText('Initialize'));

    // Result data should be visible
    expect(screen.getByText('voltage:')).toBeInTheDocument();
    expect(screen.getByText('current:')).toBeInTheDocument();
  });

  it('should display step order numbers', () => {
    render(<ResultDetailModal result={mockResult} onClose={mockOnClose} />);

    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('should format duration correctly', () => {
    render(<ResultDetailModal result={mockResult} onClose={mockOnClose} />);

    // Step duration is in seconds, so 1.5s -> 1500ms displayed as 1.50s
    expect(screen.getByText('1.50s')).toBeInTheDocument();
    expect(screen.getByText('2.50s')).toBeInTheDocument();
  });

  it('should display no step data message when steps are empty', () => {
    const emptyStepsResult = { ...mockResult, steps: [] };

    render(<ResultDetailModal result={emptyStepsResult} onClose={mockOnClose} />);

    expect(screen.getByText('No step data available')).toBeInTheDocument();
  });

  it('should handle missing optional fields', () => {
    const minimalResult: ExecutionResult = {
      id: 'exec-123',
      sequenceName: 'Minimal Test',
      status: 'running',
      steps: [],
      overallPass: false,
      parameters: {},
    };

    render(<ResultDetailModal result={minimalResult} onClose={mockOnClose} />);

    expect(screen.getByText('Minimal Test')).toBeInTheDocument();
    // Should show dashes for missing fields
    const dashes = screen.getAllByText('-');
    expect(dashes.length).toBeGreaterThan(0);
  });
});
