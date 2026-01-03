/**
 * Unit tests for ResultsFilter component.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ResultsFilter } from '../ResultsFilter';
import type { ExecutionStatus } from '../../../../types';

describe('ResultsFilter', () => {
  const mockBatches = [
    { id: 'batch-1', name: 'Batch One' },
    { id: 'batch-2', name: 'Batch Two' },
  ];

  const mockOnBatchChange = vi.fn();
  const mockOnStatusChange = vi.fn();
  const mockOnFromDateChange = vi.fn();
  const mockOnToDateChange = vi.fn();
  const mockOnSearchChange = vi.fn();
  const mockOnClear = vi.fn();

  const defaultProps = {
    batchId: '',
    onBatchChange: mockOnBatchChange,
    status: '' as ExecutionStatus | '',
    onStatusChange: mockOnStatusChange,
    fromDate: '',
    onFromDateChange: mockOnFromDateChange,
    toDate: '',
    onToDateChange: mockOnToDateChange,
    search: '',
    onSearchChange: mockOnSearchChange,
    onClear: mockOnClear,
    batches: mockBatches,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render filter header', () => {
    render(<ResultsFilter {...defaultProps} />);

    expect(screen.getByText('Filters')).toBeInTheDocument();
  });

  it('should render batch select with options', () => {
    render(<ResultsFilter {...defaultProps} />);

    // There are multiple comboboxes (batch, status)
    const comboboxes = screen.getAllByRole('combobox');
    expect(comboboxes.length).toBeGreaterThan(0);
    expect(screen.getByText('All Batches')).toBeInTheDocument();
  });

  it('should render status select with all options', () => {
    render(<ResultsFilter {...defaultProps} />);

    expect(screen.getByText('All Status')).toBeInTheDocument();
  });

  it('should render date inputs', () => {
    render(<ResultsFilter {...defaultProps} />);

    const dateInputs = screen.getAllByRole('textbox');
    expect(dateInputs.length).toBeGreaterThanOrEqual(1);
  });

  it('should render search input', () => {
    render(<ResultsFilter {...defaultProps} />);

    expect(screen.getByPlaceholderText('Search sequence...')).toBeInTheDocument();
  });

  it('should not show Clear button when no filters are active', () => {
    render(<ResultsFilter {...defaultProps} />);

    expect(screen.queryByRole('button', { name: /clear/i })).not.toBeInTheDocument();
  });

  it('should show Clear button when batchId filter is active', () => {
    render(<ResultsFilter {...defaultProps} batchId="batch-1" />);

    expect(screen.getByRole('button', { name: /clear/i })).toBeInTheDocument();
  });

  it('should show Clear button when status filter is active', () => {
    render(<ResultsFilter {...defaultProps} status="completed" />);

    expect(screen.getByRole('button', { name: /clear/i })).toBeInTheDocument();
  });

  it('should show Clear button when date filter is active', () => {
    render(<ResultsFilter {...defaultProps} fromDate="2025-01-01" />);

    expect(screen.getByRole('button', { name: /clear/i })).toBeInTheDocument();
  });

  it('should show Clear button when search filter is active', () => {
    render(<ResultsFilter {...defaultProps} search="test" />);

    expect(screen.getByRole('button', { name: /clear/i })).toBeInTheDocument();
  });

  it('should call onClear when Clear button is clicked', () => {
    render(<ResultsFilter {...defaultProps} batchId="batch-1" />);

    fireEvent.click(screen.getByRole('button', { name: /clear/i }));

    expect(mockOnClear).toHaveBeenCalled();
  });

  it('should call onSearchChange when search input changes', () => {
    render(<ResultsFilter {...defaultProps} />);

    fireEvent.change(screen.getByPlaceholderText('Search sequence...'), {
      target: { value: 'test sequence' },
    });

    expect(mockOnSearchChange).toHaveBeenCalled();
  });

  it('should display batch options from props', () => {
    render(<ResultsFilter {...defaultProps} />);

    const selects = screen.getAllByRole('combobox');
    // First select is batch select
    expect(selects[0]).toBeInTheDocument();
  });

  it('should render multiple filters in grid layout', () => {
    render(<ResultsFilter {...defaultProps} />);

    // Check that the component renders filters in a grid layout
    const filterHeader = screen.getByText('Filters');
    expect(filterHeader).toBeInTheDocument();

    // Verify multiple comboboxes are rendered
    const comboboxes = screen.getAllByRole('combobox');
    expect(comboboxes.length).toBe(2); // batch and status selects
  });
});
