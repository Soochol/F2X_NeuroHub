/**
 * Unit tests for ExportButton component.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ExportButton } from '../ExportButton';
import type { ExportFormat } from '../../../../types';

describe('ExportButton', () => {
  const mockOnExport = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render export button', () => {
    render(<ExportButton onExport={mockOnExport} />);
    expect(screen.getByRole('button', { name: /export/i })).toBeInTheDocument();
  });

  it('should open dropdown when clicked', () => {
    render(<ExportButton onExport={mockOnExport} />);

    fireEvent.click(screen.getByRole('button', { name: /export/i }));

    expect(screen.getByText('Excel (.xlsx)')).toBeInTheDocument();
    expect(screen.getByText('PDF (.pdf)')).toBeInTheDocument();
    expect(screen.getByText('CSV (.csv)')).toBeInTheDocument();
    expect(screen.getByText('JSON (.json)')).toBeInTheDocument();
  });

  it('should call onExport with xlsx format when Excel option is clicked', () => {
    render(<ExportButton onExport={mockOnExport} />);

    fireEvent.click(screen.getByRole('button', { name: /export/i }));
    fireEvent.click(screen.getByText('Excel (.xlsx)'));

    expect(mockOnExport).toHaveBeenCalledWith('xlsx');
  });

  it('should call onExport with pdf format when PDF option is clicked', () => {
    render(<ExportButton onExport={mockOnExport} />);

    fireEvent.click(screen.getByRole('button', { name: /export/i }));
    fireEvent.click(screen.getByText('PDF (.pdf)'));

    expect(mockOnExport).toHaveBeenCalledWith('pdf');
  });

  it('should call onExport with csv format when CSV option is clicked', () => {
    render(<ExportButton onExport={mockOnExport} />);

    fireEvent.click(screen.getByRole('button', { name: /export/i }));
    fireEvent.click(screen.getByText('CSV (.csv)'));

    expect(mockOnExport).toHaveBeenCalledWith('csv');
  });

  it('should call onExport with json format when JSON option is clicked', () => {
    render(<ExportButton onExport={mockOnExport} />);

    fireEvent.click(screen.getByRole('button', { name: /export/i }));
    fireEvent.click(screen.getByText('JSON (.json)'));

    expect(mockOnExport).toHaveBeenCalledWith('json');
  });

  it('should close dropdown after selecting an option', () => {
    render(<ExportButton onExport={mockOnExport} />);

    fireEvent.click(screen.getByRole('button', { name: /export/i }));
    expect(screen.getByText('Excel (.xlsx)')).toBeInTheDocument();

    fireEvent.click(screen.getByText('Excel (.xlsx)'));
    expect(screen.queryByText('Excel (.xlsx)')).not.toBeInTheDocument();
  });

  it('should show loading state when isLoading is true', () => {
    render(<ExportButton onExport={mockOnExport} isLoading={true} />);

    const button = screen.getByRole('button', { name: /export/i });
    expect(button).toBeDisabled();
  });

  it('should be disabled when disabled prop is true', () => {
    render(<ExportButton onExport={mockOnExport} disabled={true} />);

    const button = screen.getByRole('button', { name: /export/i });
    expect(button).toBeDisabled();
  });

  it('should toggle dropdown when button is clicked multiple times', () => {
    render(<ExportButton onExport={mockOnExport} />);
    const button = screen.getByRole('button', { name: /export/i });

    // Open
    fireEvent.click(button);
    expect(screen.getByText('Excel (.xlsx)')).toBeInTheDocument();

    // Close
    fireEvent.click(button);
    expect(screen.queryByText('Excel (.xlsx)')).not.toBeInTheDocument();
  });

  it('should close dropdown when clicking outside', () => {
    render(
      <div>
        <div data-testid="outside">Outside</div>
        <ExportButton onExport={mockOnExport} />
      </div>
    );

    // Open dropdown
    fireEvent.click(screen.getByRole('button', { name: /export/i }));
    expect(screen.getByText('Excel (.xlsx)')).toBeInTheDocument();

    // Click outside
    fireEvent.mouseDown(screen.getByTestId('outside'));
    expect(screen.queryByText('Excel (.xlsx)')).not.toBeInTheDocument();
  });
});
