/**
 * Tests for BarcodeScanner component
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BarcodeScanner } from '../BarcodeScanner';

describe('BarcodeScanner', () => {
  const mockOnScan = vi.fn();

  beforeEach(() => {
    mockOnScan.mockClear();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  // Rendering tests
  it('renders barcode scanner input', () => {
    render(<BarcodeScanner onScan={mockOnScan} />);

    // Check for input field
    expect(screen.getByLabelText(/serial number/i)).toBeTruthy();

    // Check for scan button
    expect(screen.getByRole('button', { name: /scan/i })).toBeTruthy();

    // Check for ready status
    expect(screen.getByText(/ready to scan/i)).toBeTruthy();
  });

  it('displays instructions', () => {
    render(<BarcodeScanner onScan={mockOnScan} />);

    expect(screen.getByText(/instructions/i)).toBeTruthy();
    expect(screen.getByText(/use barcode scanner to scan serial number automatically/i)).toBeTruthy();
  });

  // Manual input tests
  it('handles manual input', async () => {
    const user = userEvent.setup();
    render(<BarcodeScanner onScan={mockOnScan} />);

    const input = screen.getByLabelText(/serial number/i) as HTMLInputElement;

    // Type a valid serial number
    await user.type(input, 'KR01PSA2511001');

    expect(input.value).toBe('KR01PSA2511001');
    expect(mockOnScan).not.toHaveBeenCalled();
  });

  it('converts input to uppercase', async () => {
    const user = userEvent.setup();
    render(<BarcodeScanner onScan={mockOnScan} />);

    const input = screen.getByLabelText(/serial number/i) as HTMLInputElement;

    // Type lowercase
    await user.type(input, 'kr01psa2511001');

    expect(input.value).toBe('KR01PSA2511001');
  });

  it('removes non-alphanumeric characters', async () => {
    const user = userEvent.setup();
    render(<BarcodeScanner onScan={mockOnScan} />);

    const input = screen.getByLabelText(/serial number/i) as HTMLInputElement;

    // Type with special characters
    await user.type(input, 'KR-01-PSA-2511-001');

    expect(input.value).toBe('KR01PSA2511001');
  });

  it('shows formatted serial number when valid', async () => {
    const user = userEvent.setup();
    render(<BarcodeScanner onScan={mockOnScan} />);

    const input = screen.getByLabelText(/serial number/i) as HTMLInputElement;

    // Type a valid 14-character serial number
    await user.type(input, 'KR01PSA2511001');

    await waitFor(() => {
      expect(screen.getByText(/formatted:/i)).toBeTruthy();
      expect(screen.getByText(/KR01-PSA-2511-001/i)).toBeTruthy();
    });
  });

  // Validation tests
  it('validates serial number format - too short', async () => {
    const user = userEvent.setup();
    render(<BarcodeScanner onScan={mockOnScan} />);

    const input = screen.getByLabelText(/serial number/i) as HTMLInputElement;

    // Type only 13 characters
    await user.type(input, 'KR01PSA251100');

    await waitFor(() => {
      expect(screen.getByText(/serial number must be 14 characters/i)).toBeTruthy();
    });
  });

  it('validates serial number format - invalid pattern', async () => {
    const user = userEvent.setup();
    render(<BarcodeScanner onScan={mockOnScan} />);

    const input = screen.getByLabelText(/serial number/i) as HTMLInputElement;

    // Type 14 characters but invalid format
    await user.type(input, '12345678901234');

    await waitFor(() => {
      expect(screen.getByText(/invalid serial number format/i)).toBeTruthy();
    });
  });

  it('enforces maxLength of 14 characters', () => {
    render(<BarcodeScanner onScan={mockOnScan} />);

    const input = screen.getByLabelText(/serial number/i) as HTMLInputElement;

    expect(input).toHaveProperty('maxLength', 14);
  });

  // Submit button tests
  it('disables scan button when input is empty', () => {
    render(<BarcodeScanner onScan={mockOnScan} />);

    const button = screen.getByRole('button', { name: /scan/i });

    expect(button).toBeDisabled();
  });

  it('disables scan button when input is invalid', async () => {
    const user = userEvent.setup();
    render(<BarcodeScanner onScan={mockOnScan} />);

    const input = screen.getByLabelText(/serial number/i);
    const button = screen.getByRole('button', { name: /scan/i });

    await user.type(input, 'INVALID');

    expect(button).toBeDisabled();
  });

  it('enables scan button when input is valid', async () => {
    const user = userEvent.setup();
    render(<BarcodeScanner onScan={mockOnScan} />);

    const input = screen.getByLabelText(/serial number/i);
    const button = screen.getByRole('button', { name: /scan/i });

    await user.type(input, 'KR01PSA2511001');

    await waitFor(() => {
      expect(button).not.toBeDisabled();
    });
  });

  it('calls onScan when scan button is clicked with valid input', async () => {
    const user = userEvent.setup();
    render(<BarcodeScanner onScan={mockOnScan} />);

    const input = screen.getByLabelText(/serial number/i);
    const button = screen.getByRole('button', { name: /scan/i });

    await user.type(input, 'KR01PSA2511001');
    await user.click(button);

    expect(mockOnScan).toHaveBeenCalledWith('KR01PSA2511001');
    expect(mockOnScan).toHaveBeenCalledTimes(1);
  });

  it('clears input after successful scan', async () => {
    const user = userEvent.setup();
    render(<BarcodeScanner onScan={mockOnScan} />);

    const input = screen.getByLabelText(/serial number/i) as HTMLInputElement;
    const button = screen.getByRole('button', { name: /scan/i });

    await user.type(input, 'KR01PSA2511001');
    await user.click(button);

    await waitFor(() => {
      expect(input.value).toBe('');
    });
  });

  it('calls onScan when Enter key is pressed with valid input', async () => {
    const user = userEvent.setup();
    render(<BarcodeScanner onScan={mockOnScan} />);

    const input = screen.getByLabelText(/serial number/i);

    await user.type(input, 'KR01PSA2511001');
    await user.type(input, '{Enter}');

    expect(mockOnScan).toHaveBeenCalledWith('KR01PSA2511001');
  });

  it('does not call onScan when Enter is pressed with invalid input', async () => {
    const user = userEvent.setup();
    render(<BarcodeScanner onScan={mockOnScan} />);

    const input = screen.getByLabelText(/serial number/i);

    await user.type(input, 'INVALID');
    await user.type(input, '{Enter}');

    expect(mockOnScan).not.toHaveBeenCalled();
  });

  // Loading state tests
  it('shows processing state when isScanning is true', () => {
    render(<BarcodeScanner onScan={mockOnScan} isScanning={true} />);

    expect(screen.getByText(/processing/i)).toBeTruthy();
  });

  it('disables input when isScanning is true', () => {
    render(<BarcodeScanner onScan={mockOnScan} isScanning={true} />);

    const input = screen.getByLabelText(/serial number/i);

    expect(input).toBeDisabled();
  });

  it('disables button when isScanning is true', () => {
    render(<BarcodeScanner onScan={mockOnScan} isScanning={true} />);

    const button = screen.getByRole('button', { name: /scan/i });

    expect(button).toBeDisabled();
  });

  it('clears input when isScanning becomes false', () => {
    const { rerender } = render(<BarcodeScanner onScan={mockOnScan} isScanning={true} />);

    const input = screen.getByLabelText(/serial number/i) as HTMLInputElement;

    // Input should be cleared when isScanning becomes false
    rerender(<BarcodeScanner onScan={mockOnScan} isScanning={false} />);

    expect(input.value).toBe('');
  });

  // Custom props tests
  it('uses custom placeholder', () => {
    const customPlaceholder = 'Enter serial here';
    render(<BarcodeScanner onScan={mockOnScan} placeholder={customPlaceholder} />);

    const input = screen.getByLabelText(/serial number/i) as HTMLInputElement;

    expect(input.placeholder).toBe(customPlaceholder);
  });

  it('autofocuses input by default', () => {
    render(<BarcodeScanner onScan={mockOnScan} />);

    const input = screen.getByLabelText(/serial number/i);

    // Check if input has autofocus-related attributes
    expect(document.activeElement).toBe(input);
  });

  it('does not autofocus when autoFocus is false', () => {
    render(
      <div>
        <input data-testid="other-input" />
        <BarcodeScanner onScan={mockOnScan} autoFocus={false} />
      </div>
    );

    const input = screen.getByLabelText(/serial number/i);

    expect(document.activeElement).not.toBe(input);
  });

  // Error display tests
  it('displays error message when validation fails', async () => {
    const user = userEvent.setup();
    render(<BarcodeScanner onScan={mockOnScan} />);

    const input = screen.getByLabelText(/serial number/i);

    // Type invalid input
    await user.type(input, '12345678901234');

    await waitFor(() => {
      expect(screen.getByText(/invalid serial number format/i)).toBeTruthy();
    });
  });

  it('shows invalid format error when trying to scan invalid serial', async () => {
    const user = userEvent.setup();
    render(<BarcodeScanner onScan={mockOnScan} />);

    const input = screen.getByLabelText(/serial number/i);

    // Manually set an invalid value and try to scan
    fireEvent.change(input, { target: { value: 'XXXXXXXXXXXXXX' } });

    const button = screen.getByRole('button', { name: /scan/i });

    // Button should be disabled for invalid format
    expect(button).toBeDisabled();
  });

  // Integration tests
  it('handles complete workflow: input -> validate -> submit -> clear', async () => {
    const user = userEvent.setup();
    render(<BarcodeScanner onScan={mockOnScan} />);

    const input = screen.getByLabelText(/serial number/i) as HTMLInputElement;
    const button = screen.getByRole('button', { name: /scan/i });

    // Step 1: Input is empty, button disabled
    expect(button).toBeDisabled();

    // Step 2: Type valid serial
    await user.type(input, 'KR01PSA2511001');

    // Step 3: Validation passes, button enabled
    await waitFor(() => {
      expect(button).not.toBeDisabled();
    });

    // Step 4: Click scan
    await user.click(button);

    // Step 5: Callback fired
    expect(mockOnScan).toHaveBeenCalledWith('KR01PSA2511001');

    // Step 6: Input cleared
    await waitFor(() => {
      expect(input.value).toBe('');
    });
  });
});
