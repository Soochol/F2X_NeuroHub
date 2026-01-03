/**
 * Unit tests for ResultsTable component.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ResultsTable } from '../ResultsTable';
import type { ExecutionSummary } from '../../../../types';

describe('ResultsTable', () => {
  const mockOnSelectionChange = vi.fn();
  const mockOnViewDetail = vi.fn();
  const mockOnSort = vi.fn();

  const mockResults: ExecutionSummary[] = [
    {
      id: 'exec-1',
      sequenceName: 'Test Sequence 1',
      sequenceVersion: '1.0.0',
      status: 'completed',
      startedAt: '2025-01-01T10:00:00Z',
      duration: 5000,
      batchId: 'batch-001',
    },
    {
      id: 'exec-2',
      sequenceName: 'Test Sequence 2',
      sequenceVersion: '2.0.0',
      status: 'failed',
      startedAt: '2025-01-01T11:00:00Z',
      duration: 3000,
      batchId: 'batch-002',
    },
    {
      id: 'exec-3',
      sequenceName: 'Test Sequence 3',
      sequenceVersion: '1.5.0',
      status: 'running',
      startedAt: '2025-01-01T12:00:00Z',
      batchId: 'batch-003',
    },
  ];

  const defaultProps = {
    results: mockResults,
    isLoading: false,
    selectedIds: [] as string[],
    onSelectionChange: mockOnSelectionChange,
    onViewDetail: mockOnViewDetail,
    sortField: 'startedAt',
    sortDirection: 'desc' as const,
    onSort: mockOnSort,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render table with column headers', () => {
    render(<ResultsTable {...defaultProps} />);

    expect(screen.getByText('Status')).toBeInTheDocument();
    expect(screen.getByText('Sequence')).toBeInTheDocument();
    expect(screen.getByText('Batch')).toBeInTheDocument();
    expect(screen.getByText('Started At')).toBeInTheDocument();
    expect(screen.getByText('Duration')).toBeInTheDocument();
    expect(screen.getByText('Actions')).toBeInTheDocument();
  });

  it('should render result rows', () => {
    render(<ResultsTable {...defaultProps} />);

    expect(screen.getByText('Test Sequence 1')).toBeInTheDocument();
    expect(screen.getByText('Test Sequence 2')).toBeInTheDocument();
    expect(screen.getByText('Test Sequence 3')).toBeInTheDocument();
  });

  it('should display status labels correctly', () => {
    render(<ResultsTable {...defaultProps} />);

    expect(screen.getByText('Completed')).toBeInTheDocument();
    expect(screen.getByText('Failed')).toBeInTheDocument();
    expect(screen.getByText('Running')).toBeInTheDocument();
  });

  it('should display version badges', () => {
    render(<ResultsTable {...defaultProps} />);

    expect(screen.getByText('v1.0.0')).toBeInTheDocument();
    expect(screen.getByText('v2.0.0')).toBeInTheDocument();
    expect(screen.getByText('v1.5.0')).toBeInTheDocument();
  });

  it('should show loading spinner when isLoading is true', () => {
    render(<ResultsTable {...defaultProps} isLoading={true} />);

    // Table should not be visible when loading
    expect(screen.queryByText('Status')).not.toBeInTheDocument();
  });

  it('should show empty state when results is empty', () => {
    render(<ResultsTable {...defaultProps} results={[]} />);

    expect(screen.getByText(/no results found/i)).toBeInTheDocument();
  });

  it('should render checkboxes for selection', () => {
    render(<ResultsTable {...defaultProps} />);

    const checkboxes = screen.getAllByRole('checkbox');
    // 1 for select all + 3 for each result
    expect(checkboxes).toHaveLength(4);
  });

  it('should handle select all', () => {
    render(<ResultsTable {...defaultProps} />);

    const selectAllCheckbox = screen.getAllByRole('checkbox')[0];
    fireEvent.click(selectAllCheckbox);

    expect(mockOnSelectionChange).toHaveBeenCalledWith(['exec-1', 'exec-2', 'exec-3']);
  });

  it('should handle individual row selection', () => {
    render(<ResultsTable {...defaultProps} />);

    const rowCheckboxes = screen.getAllByRole('checkbox');
    // First checkbox is select all, second is first row
    fireEvent.click(rowCheckboxes[1]);

    expect(mockOnSelectionChange).toHaveBeenCalledWith(['exec-1']);
  });

  it('should handle row deselection', () => {
    render(<ResultsTable {...defaultProps} selectedIds={['exec-1']} />);

    const rowCheckboxes = screen.getAllByRole('checkbox');
    fireEvent.click(rowCheckboxes[1]);

    expect(mockOnSelectionChange).toHaveBeenCalledWith([]);
  });

  it('should call onViewDetail when view button is clicked', () => {
    render(<ResultsTable {...defaultProps} />);

    const viewButtons = screen.getAllByRole('button');
    fireEvent.click(viewButtons[0]);

    expect(mockOnViewDetail).toHaveBeenCalledWith(mockResults[0]);
  });

  it('should call onSort when column header is clicked', () => {
    render(<ResultsTable {...defaultProps} />);

    fireEvent.click(screen.getByText('Status'));
    expect(mockOnSort).toHaveBeenCalledWith('status');

    fireEvent.click(screen.getByText('Sequence'));
    expect(mockOnSort).toHaveBeenCalledWith('sequenceName');

    fireEvent.click(screen.getByText('Duration'));
    expect(mockOnSort).toHaveBeenCalledWith('duration');
  });

  it('should highlight selected rows', () => {
    render(<ResultsTable {...defaultProps} selectedIds={['exec-1']} />);

    const rowCheckboxes = screen.getAllByRole('checkbox');
    expect(rowCheckboxes[1]).toBeChecked();
  });

  it('should format duration correctly', () => {
    render(<ResultsTable {...defaultProps} />);

    // 5000ms should display as 5.0s
    expect(screen.getByText('5.0s')).toBeInTheDocument();
    // 3000ms should display as 3.0s
    expect(screen.getByText('3.0s')).toBeInTheDocument();
  });

  it('should display dash for missing duration', () => {
    render(<ResultsTable {...defaultProps} />);

    // The third result has no duration, should show '-'
    const dashes = screen.getAllByText('-');
    expect(dashes.length).toBeGreaterThan(0);
  });

  it('should truncate batch IDs', () => {
    render(<ResultsTable {...defaultProps} />);

    // Batch ID should be truncated to first 8 chars - may have multiple
    expect(screen.getAllByText('batch-00').length).toBeGreaterThan(0);
  });
});
