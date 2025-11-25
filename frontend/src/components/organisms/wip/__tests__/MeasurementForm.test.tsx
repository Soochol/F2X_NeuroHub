/**
 * Tests for MeasurementForm component
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MeasurementForm } from '../MeasurementForm';
import type { Process } from '@/types/api';
import { ProcessResult, DataLevel } from '@/types/api';

describe('MeasurementForm', () => {
  const mockOnSubmit = vi.fn();
  const mockOnCancel = vi.fn();

  const mockProcess: Process = {
    id: 1,
    process_number: 1,
    process_code: 'ASSY',
    process_name_ko: '조립',
    process_name_en: 'Assembly',
    sort_order: 1,
    is_active: true,
    auto_print_label: false,
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
  };

  beforeEach(() => {
    mockOnSubmit.mockClear();
    mockOnCancel.mockClear();
  });

  // Rendering tests
  it('renders without crashing', () => {
    const { container } = render(
      <MeasurementForm process={mockProcess} onSubmit={mockOnSubmit} />
    );
    expect(container).toBeTruthy();
  });

  it('renders all form fields', () => {
    render(<MeasurementForm process={mockProcess} onSubmit={mockOnSubmit} />);

    // Result selection
    expect(screen.getByLabelText(/result/i)).toBeTruthy();

    // Data level selection
    expect(screen.getByLabelText(/data level/i)).toBeTruthy();

    // Notes textarea
    expect(screen.getByPlaceholderText(/add any additional notes/i)).toBeTruthy();

    // Submit button
    expect(screen.getByRole('button', { name: /submit/i })).toBeTruthy();
  });

  it('displays process information', () => {
    render(<MeasurementForm process={mockProcess} onSubmit={mockOnSubmit} />);

    expect(screen.getByText(/process: 조립/i)).toBeTruthy();
    expect(screen.getByText(/assembly/i)).toBeTruthy();
    expect(screen.getByText(/process #1/i)).toBeTruthy();
  });

  // Result selection tests
  it('has PASS as default result', () => {
    render(<MeasurementForm process={mockProcess} onSubmit={mockOnSubmit} />);

    const resultSelect = screen.getByLabelText(/result/i) as HTMLSelectElement;
    expect(resultSelect.value).toBe(ProcessResult.PASS);
  });

  it('can select FAIL result', async () => {
    const user = userEvent.setup();
    render(<MeasurementForm process={mockProcess} onSubmit={mockOnSubmit} />);

    const resultSelect = screen.getByLabelText(/result/i);

    await user.selectOptions(resultSelect, ProcessResult.FAIL);

    expect((resultSelect as HTMLSelectElement).value).toBe(ProcessResult.FAIL);
  });

  it('can select REWORK result', async () => {
    const user = userEvent.setup();
    render(<MeasurementForm process={mockProcess} onSubmit={mockOnSubmit} />);

    const resultSelect = screen.getByLabelText(/result/i);

    await user.selectOptions(resultSelect, ProcessResult.REWORK);

    expect((resultSelect as HTMLSelectElement).value).toBe(ProcessResult.REWORK);
  });

  // Data level tests
  it('has NORMAL as default data level', () => {
    render(<MeasurementForm process={mockProcess} onSubmit={mockOnSubmit} />);

    const dataLevelSelect = screen.getByLabelText(/data level/i) as HTMLSelectElement;
    expect(dataLevelSelect.value).toBe(DataLevel.NORMAL);
  });

  it('can select DETAILED data level', async () => {
    const user = userEvent.setup();
    render(<MeasurementForm process={mockProcess} onSubmit={mockOnSubmit} />);

    const dataLevelSelect = screen.getByLabelText(/data level/i);

    await user.selectOptions(dataLevelSelect, DataLevel.DETAILED);

    expect((dataLevelSelect as HTMLSelectElement).value).toBe(DataLevel.DETAILED);
  });

  // Defect codes tests
  it('does not show defect codes when result is PASS', () => {
    render(<MeasurementForm process={mockProcess} onSubmit={mockOnSubmit} />);

    expect(screen.queryByText(/defect codes/i)).toBeNull();
  });

  it('shows defect codes when result is FAIL', async () => {
    const user = userEvent.setup();
    render(<MeasurementForm process={mockProcess} onSubmit={mockOnSubmit} />);

    const resultSelect = screen.getByLabelText(/result/i);
    await user.selectOptions(resultSelect, ProcessResult.FAIL);

    await waitFor(() => {
      expect(screen.getByText(/defect codes \*/i)).toBeTruthy();
    });
  });

  it('displays defect code options when result is FAIL', async () => {
    const user = userEvent.setup();
    render(<MeasurementForm process={mockProcess} onSubmit={mockOnSubmit} />);

    const resultSelect = screen.getByLabelText(/result/i);
    await user.selectOptions(resultSelect, ProcessResult.FAIL);

    await waitFor(() => {
      expect(screen.getByText(/scratch/i)).toBeTruthy();
      expect(screen.getByText(/dent/i)).toBeTruthy();
      expect(screen.getByText(/crack/i)).toBeTruthy();
    });
  });

  it('can select multiple defect codes', async () => {
    const user = userEvent.setup();
    render(<MeasurementForm process={mockProcess} onSubmit={mockOnSubmit} />);

    const resultSelect = screen.getByLabelText(/result/i);
    await user.selectOptions(resultSelect, ProcessResult.FAIL);

    await waitFor(async () => {
      const scratchCheckbox = screen.getByRole('checkbox', { name: /scratch/i });
      const dentCheckbox = screen.getByRole('checkbox', { name: /dent/i });

      await user.click(scratchCheckbox);
      await user.click(dentCheckbox);

      expect(scratchCheckbox).toBeChecked();
      expect(dentCheckbox).toBeChecked();
    });
  });

  it('can deselect defect codes', async () => {
    const user = userEvent.setup();
    render(<MeasurementForm process={mockProcess} onSubmit={mockOnSubmit} />);

    const resultSelect = screen.getByLabelText(/result/i);
    await user.selectOptions(resultSelect, ProcessResult.FAIL);

    await waitFor(async () => {
      const scratchCheckbox = screen.getByRole('checkbox', { name: /scratch/i });

      // Select
      await user.click(scratchCheckbox);
      expect(scratchCheckbox).toBeChecked();

      // Deselect
      await user.click(scratchCheckbox);
      expect(scratchCheckbox).not.toBeChecked();
    });
  });

  // Validation tests
  it('requires at least one defect code when result is FAIL', async () => {
    const user = userEvent.setup();
    render(<MeasurementForm process={mockProcess} onSubmit={mockOnSubmit} />);

    const resultSelect = screen.getByLabelText(/result/i);
    await user.selectOptions(resultSelect, ProcessResult.FAIL);

    const submitButton = screen.getByRole('button', { name: /submit fail/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/at least one defect code must be selected/i)).toBeTruthy();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('clears defect code error when code is selected', async () => {
    const user = userEvent.setup();
    render(<MeasurementForm process={mockProcess} onSubmit={mockOnSubmit} />);

    const resultSelect = screen.getByLabelText(/result/i);
    await user.selectOptions(resultSelect, ProcessResult.FAIL);

    // Submit without defect codes to trigger error
    const submitButton = screen.getByRole('button', { name: /submit fail/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/at least one defect code must be selected/i)).toBeTruthy();
    });

    // Select a defect code - error should clear on next submit attempt
    const scratchCheckbox = screen.getByRole('checkbox', { name: /scratch/i });
    await user.click(scratchCheckbox);

    await user.click(submitButton);

    expect(mockOnSubmit).toHaveBeenCalled();
  });

  // Measurement fields tests
  it('renders custom measurement fields', () => {
    const measurementFields = [
      { key: 'length', label: 'Length', type: 'number' as const, unit: 'mm', required: true },
      { key: 'weight', label: 'Weight', type: 'number' as const, unit: 'g', required: false },
    ];

    render(
      <MeasurementForm
        process={mockProcess}
        onSubmit={mockOnSubmit}
        measurementFields={measurementFields}
      />
    );

    expect(screen.getByText(/measurements/i)).toBeTruthy();
    expect(screen.getByLabelText(/length \(mm\)/i)).toBeTruthy();
    expect(screen.getByLabelText(/weight \(g\)/i)).toBeTruthy();
  });

  it('validates required measurement fields', async () => {
    const user = userEvent.setup();
    const measurementFields = [
      { key: 'length', label: 'Length', type: 'number' as const, required: true },
    ];

    render(
      <MeasurementForm
        process={mockProcess}
        onSubmit={mockOnSubmit}
        measurementFields={measurementFields}
      />
    );

    const submitButton = screen.getByRole('button', { name: /submit/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/length is required/i)).toBeTruthy();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('handles measurement field input', async () => {
    const user = userEvent.setup();
    const measurementFields = [
      { key: 'length', label: 'Length', type: 'number' as const, unit: 'mm', required: true },
    ];

    render(
      <MeasurementForm
        process={mockProcess}
        onSubmit={mockOnSubmit}
        measurementFields={measurementFields}
      />
    );

    const lengthInput = screen.getByLabelText(/length \(mm\)/i);
    await user.type(lengthInput, '100');

    expect((lengthInput as HTMLInputElement).value).toBe('100');
  });

  it('renders select-type measurement fields', () => {
    const measurementFields = [
      {
        key: 'color',
        label: 'Color',
        type: 'select' as const,
        options: ['Red', 'Blue', 'Green'],
        required: true,
      },
    ];

    render(
      <MeasurementForm
        process={mockProcess}
        onSubmit={mockOnSubmit}
        measurementFields={measurementFields}
      />
    );

    expect(screen.getByLabelText(/color/i)).toBeTruthy();
  });

  // Notes tests
  it('handles notes input', async () => {
    const user = userEvent.setup();
    render(<MeasurementForm process={mockProcess} onSubmit={mockOnSubmit} />);

    const notesTextarea = screen.getByPlaceholderText(/add any additional notes/i);
    await user.type(notesTextarea, 'Test notes');

    expect((notesTextarea as HTMLTextAreaElement).value).toBe('Test notes');
  });

  // Submit tests
  it('calls onSubmit with correct data for PASS result', async () => {
    const user = userEvent.setup();
    render(<MeasurementForm process={mockProcess} onSubmit={mockOnSubmit} />);

    const submitButton = screen.getByRole('button', { name: /submit pass/i });
    await user.click(submitButton);

    expect(mockOnSubmit).toHaveBeenCalledWith({
      result: ProcessResult.PASS,
      data_level: DataLevel.NORMAL,
      measurements: {},
      defect_codes: [],
      notes: '',
    });
  });

  it('calls onSubmit with correct data for FAIL result', async () => {
    const user = userEvent.setup();
    render(<MeasurementForm process={mockProcess} onSubmit={mockOnSubmit} />);

    const resultSelect = screen.getByLabelText(/result/i);
    await user.selectOptions(resultSelect, ProcessResult.FAIL);

    await waitFor(async () => {
      const scratchCheckbox = screen.getByRole('checkbox', { name: /scratch/i });
      await user.click(scratchCheckbox);
    });

    const notesTextarea = screen.getByPlaceholderText(/add any additional notes/i);
    await user.type(notesTextarea, 'Defect found');

    const submitButton = screen.getByRole('button', { name: /submit fail/i });
    await user.click(submitButton);

    expect(mockOnSubmit).toHaveBeenCalledWith({
      result: ProcessResult.FAIL,
      data_level: DataLevel.NORMAL,
      measurements: {},
      defect_codes: ['DEF001'],
      notes: 'Defect found',
    });
  });

  it('calls onSubmit with measurements data', async () => {
    const user = userEvent.setup();
    const measurementFields = [
      { key: 'length', label: 'Length', type: 'number' as const, unit: 'mm', required: true },
    ];

    render(
      <MeasurementForm
        process={mockProcess}
        onSubmit={mockOnSubmit}
        measurementFields={measurementFields}
      />
    );

    const lengthInput = screen.getByLabelText(/length \(mm\)/i);
    await user.type(lengthInput, '100');

    const submitButton = screen.getByRole('button', { name: /submit/i });
    await user.click(submitButton);

    expect(mockOnSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        measurements: { length: 100 },
      })
    );
  });

  // Cancel button tests
  it('does not show cancel button when onCancel is not provided', () => {
    render(<MeasurementForm process={mockProcess} onSubmit={mockOnSubmit} />);

    expect(screen.queryByRole('button', { name: /cancel/i })).toBeNull();
  });

  it('shows cancel button when onCancel is provided', () => {
    render(
      <MeasurementForm
        process={mockProcess}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
      />
    );

    expect(screen.getByRole('button', { name: /cancel/i })).toBeTruthy();
  });

  it('calls onCancel when cancel button is clicked', async () => {
    const user = userEvent.setup();
    render(
      <MeasurementForm
        process={mockProcess}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
      />
    );

    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    await user.click(cancelButton);

    expect(mockOnCancel).toHaveBeenCalledTimes(1);
  });

  // Loading state tests
  it('disables submit button when isSubmitting is true', () => {
    render(
      <MeasurementForm
        process={mockProcess}
        onSubmit={mockOnSubmit}
        isSubmitting={true}
      />
    );

    const submitButton = screen.getByRole('button', { name: /submit/i });
    expect(submitButton).toBeDisabled();
  });

  it('disables cancel button when isSubmitting is true', () => {
    render(
      <MeasurementForm
        process={mockProcess}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        isSubmitting={true}
      />
    );

    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    expect(cancelButton).toBeDisabled();
  });

  // Submit button text tests
  it('shows correct button text for PASS result', () => {
    render(<MeasurementForm process={mockProcess} onSubmit={mockOnSubmit} />);

    expect(screen.getByRole('button', { name: /submit pass/i })).toBeTruthy();
  });

  it('shows correct button text for FAIL result', async () => {
    const user = userEvent.setup();
    render(<MeasurementForm process={mockProcess} onSubmit={mockOnSubmit} />);

    const resultSelect = screen.getByLabelText(/result/i);
    await user.selectOptions(resultSelect, ProcessResult.FAIL);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /submit fail/i })).toBeTruthy();
    });
  });

  it('shows correct button text for REWORK result', async () => {
    const user = userEvent.setup();
    render(<MeasurementForm process={mockProcess} onSubmit={mockOnSubmit} />);

    const resultSelect = screen.getByLabelText(/result/i);
    await user.selectOptions(resultSelect, ProcessResult.REWORK);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /submit rework/i })).toBeTruthy();
    });
  });

  // Form reset tests
  it('does not reset form automatically after submit', async () => {
    const user = userEvent.setup();
    render(<MeasurementForm process={mockProcess} onSubmit={mockOnSubmit} />);

    const notesTextarea = screen.getByPlaceholderText(/add any additional notes/i);
    await user.type(notesTextarea, 'Test notes');

    const submitButton = screen.getByRole('button', { name: /submit/i });
    await user.click(submitButton);

    // Form should not auto-reset (parent component controls this)
    expect((notesTextarea as HTMLTextAreaElement).value).toBe('Test notes');
  });
});
