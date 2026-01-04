/**
 * Unit tests for ReportTypeSelector component.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ReportTypeSelector } from '../ReportTypeSelector';
import type { ReportType } from '../../../../types';

describe('ReportTypeSelector', () => {
  const mockOnSelect = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render all report type tabs', () => {
    render(<ReportTypeSelector selectedType="batch_summary" onSelect={mockOnSelect} />);

    expect(screen.getByRole('button', { name: /batch summary/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /period statistics/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /step analysis/i })).toBeInTheDocument();
  });

  it('should highlight the selected type', () => {
    render(<ReportTypeSelector selectedType="batch_summary" onSelect={mockOnSelect} />);

    const batchSummaryButton = screen.getByRole('button', { name: /batch summary/i });
    // Selected button has shadow-sm class
    expect(batchSummaryButton.className).toContain('shadow-sm');
  });

  it('should call onSelect with batch_summary when clicked', () => {
    render(<ReportTypeSelector selectedType="period_stats" onSelect={mockOnSelect} />);

    fireEvent.click(screen.getByRole('button', { name: /batch summary/i }));

    expect(mockOnSelect).toHaveBeenCalledWith('batch_summary');
  });

  it('should call onSelect with period_stats when clicked', () => {
    render(<ReportTypeSelector selectedType="batch_summary" onSelect={mockOnSelect} />);

    fireEvent.click(screen.getByRole('button', { name: /period statistics/i }));

    expect(mockOnSelect).toHaveBeenCalledWith('period_stats');
  });

  it('should call onSelect with step_analysis when clicked', () => {
    render(<ReportTypeSelector selectedType="batch_summary" onSelect={mockOnSelect} />);

    fireEvent.click(screen.getByRole('button', { name: /step analysis/i }));

    expect(mockOnSelect).toHaveBeenCalledWith('step_analysis');
  });

  it('should display tooltips with descriptions', () => {
    render(<ReportTypeSelector selectedType="batch_summary" onSelect={mockOnSelect} />);

    const batchSummaryButton = screen.getByRole('button', { name: /batch summary/i });
    expect(batchSummaryButton).toHaveAttribute('title');
  });

  it('should render with period_stats selected', () => {
    render(<ReportTypeSelector selectedType="period_stats" onSelect={mockOnSelect} />);

    const periodStatsButton = screen.getByRole('button', { name: /period statistics/i });
    expect(periodStatsButton.className).toContain('shadow-sm');
  });

  it('should render with step_analysis selected', () => {
    render(<ReportTypeSelector selectedType="step_analysis" onSelect={mockOnSelect} />);

    const stepAnalysisButton = screen.getByRole('button', { name: /step analysis/i });
    expect(stepAnalysisButton.className).toContain('shadow-sm');
  });
});
