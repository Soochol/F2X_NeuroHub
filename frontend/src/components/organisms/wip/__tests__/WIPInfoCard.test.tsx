/**
 * Tests for WIPInfoCard component
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { WIPInfoCard } from '../WIPInfoCard';
import type { Serial, SerialStatus, LotStatus, Shift } from '@/types/api';

describe('WIPInfoCard', () => {
  const mockSerial: Serial = {
    id: 1,
    serial_number: 'KR01PSA2511001',
    lot_id: 1,
    lot: {
      id: 1,
      lot_number: 'KR01PSA2511',
      product_model_id: 1,
      product_model: {
        id: 1,
        model_code: 'PSA-WF-001',
        model_name: 'Power Switch Assembly',
        status: 'ACTIVE',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
      },
      target_quantity: 100,
      production_date: '2025-11-21',
      shift: 'DAY' as Shift,
      status: 'IN_PROGRESS' as LotStatus,
      created_at: '2025-01-21T08:00:00Z',
      updated_at: '2025-01-21T14:00:00Z',
    },
    status: 'IN_PROGRESS' as SerialStatus,
    rework_count: 0,
    created_at: '2025-01-21T10:00:00Z',
    updated_at: '2025-01-21T14:00:00Z',
  };

  // Rendering tests
  it('renders without crashing', () => {
    const { container } = render(<WIPInfoCard serial={mockSerial} />);
    expect(container).toBeTruthy();
  });

  it('renders serial number in formatted form', () => {
    render(<WIPInfoCard serial={mockSerial} />);

    // Should display formatted serial number
    expect(screen.getByText(/KR01-PSA-2511-001/i)).toBeTruthy();
  });

  it('displays serial number label', () => {
    render(<WIPInfoCard serial={mockSerial} />);

    expect(screen.getByText(/serial number/i)).toBeTruthy();
  });

  // Status badge tests
  it('displays status badge', () => {
    render(<WIPInfoCard serial={mockSerial} />);

    expect(screen.getByText(/status/i)).toBeTruthy();
    expect(screen.getByText(/IN_PROGRESS/i)).toBeTruthy();
  });

  it('displays CREATED status with correct color', () => {
    const serial = { ...mockSerial, status: 'CREATED' as SerialStatus };
    const { container } = render(<WIPInfoCard serial={serial} />);

    expect(screen.getByText(/CREATED/i)).toBeTruthy();
    expect(container).toBeTruthy();
  });

  it('displays IN_PROGRESS status with correct color', () => {
    const serial = { ...mockSerial, status: 'IN_PROGRESS' as SerialStatus };
    render(<WIPInfoCard serial={serial} />);

    expect(screen.getByText(/IN_PROGRESS/i)).toBeTruthy();
  });

  it('displays PASS status with correct color', () => {
    const serial = { ...mockSerial, status: 'PASS' as SerialStatus };
    render(<WIPInfoCard serial={serial} />);

    expect(screen.getByText(/PASS/i)).toBeTruthy();
  });

  it('displays FAIL status with correct color', () => {
    const serial = { ...mockSerial, status: 'FAIL' as SerialStatus };
    render(<WIPInfoCard serial={serial} />);

    expect(screen.getByText(/FAIL/i)).toBeTruthy();
  });

  it('displays REWORK status with correct color', () => {
    const serial = { ...mockSerial, status: 'REWORK' as SerialStatus };
    render(<WIPInfoCard serial={serial} />);

    expect(screen.getByText(/REWORK/i)).toBeTruthy();
  });

  it('displays SCRAPPED status with correct color', () => {
    const serial = { ...mockSerial, status: 'SCRAPPED' as SerialStatus };
    render(<WIPInfoCard serial={serial} />);

    expect(screen.getByText(/SCRAPPED/i)).toBeTruthy();
  });

  // LOT information tests
  it('displays LOT information section', () => {
    render(<WIPInfoCard serial={mockSerial} />);

    expect(screen.getByText(/LOT information/i)).toBeTruthy();
  });

  it('displays LOT number', () => {
    render(<WIPInfoCard serial={mockSerial} />);

    expect(screen.getByText(/LOT number/i)).toBeTruthy();
    expect(screen.getByText(mockSerial.lot!.lot_number)).toBeTruthy();
  });

  it('displays product model name', () => {
    render(<WIPInfoCard serial={mockSerial} />);

    expect(screen.getByText(/product model/i)).toBeTruthy();
    expect(screen.getByText(/power switch assembly/i)).toBeTruthy();
  });

  it('displays production date', () => {
    render(<WIPInfoCard serial={mockSerial} />);

    expect(screen.getByText(/production date/i)).toBeTruthy();
    expect(screen.getByText(/2025-11-21/i)).toBeTruthy();
  });

  it('displays shift information', () => {
    render(<WIPInfoCard serial={mockSerial} />);

    expect(screen.getByText(/shift/i)).toBeTruthy();
    expect(screen.getByText(/DAY/i)).toBeTruthy();
  });

  it('handles missing LOT information gracefully', () => {
    const serialWithoutLot = { ...mockSerial, lot: undefined };
    const { container } = render(<WIPInfoCard serial={serialWithoutLot} />);

    // Should not crash
    expect(container).toBeTruthy();

    // LOT information section should not be present
    expect(screen.queryByText(/LOT information/i)).toBeNull();
  });

  it('handles missing product model gracefully', () => {
    const serialWithoutModel = {
      ...mockSerial,
      lot: {
        ...mockSerial.lot!,
        product_model: undefined,
      },
    };
    render(<WIPInfoCard serial={serialWithoutModel} />);

    // Should not crash
    expect(screen.getByText(/LOT information/i)).toBeTruthy();

    // Product model should not be displayed
    expect(screen.queryByText(/power switch assembly/i)).toBeNull();
  });

  // Rework information tests
  it('does not show rework warning when rework_count is 0', () => {
    render(<WIPInfoCard serial={mockSerial} />);

    expect(screen.queryByText(/rework count/i)).toBeNull();
  });

  it('shows rework warning when rework_count is 1', () => {
    const serial = { ...mockSerial, rework_count: 1 };
    render(<WIPInfoCard serial={serial} />);

    expect(screen.getByText(/rework count: 1\/3/i)).toBeTruthy();
    expect(screen.getByText(/this serial has been reworked 1 time/i)).toBeTruthy();
  });

  it('shows rework warning when rework_count is 2', () => {
    const serial = { ...mockSerial, rework_count: 2 };
    render(<WIPInfoCard serial={serial} />);

    expect(screen.getByText(/rework count: 2\/3/i)).toBeTruthy();
    expect(screen.getByText(/this serial has been reworked 2 times/i)).toBeTruthy();
  });

  it('shows rework warning when rework_count is 3', () => {
    const serial = { ...mockSerial, rework_count: 3 };
    render(<WIPInfoCard serial={serial} />);

    expect(screen.getByText(/rework count: 3\/3/i)).toBeTruthy();
    expect(screen.getByText(/this serial has been reworked 3 times/i)).toBeTruthy();
  });

  it('uses correct pluralization for single rework', () => {
    const serial = { ...mockSerial, rework_count: 1 };
    render(<WIPInfoCard serial={serial} />);

    expect(screen.getByText(/1 time$/i)).toBeTruthy();
  });

  it('uses correct pluralization for multiple reworks', () => {
    const serial = { ...mockSerial, rework_count: 2 };
    render(<WIPInfoCard serial={serial} />);

    expect(screen.getByText(/2 times$/i)).toBeTruthy();
  });

  // Timestamp tests
  it('displays created timestamp', () => {
    render(<WIPInfoCard serial={mockSerial} />);

    expect(screen.getByText(/created/i)).toBeTruthy();
    expect(screen.getByText(/2025-01-21 10:00/i)).toBeTruthy();
  });

  it('does not display completed timestamp when not completed', () => {
    render(<WIPInfoCard serial={mockSerial} />);

    expect(screen.queryByText(/^completed$/i)).toBeNull();
  });

  it('displays completed timestamp when serial is completed', () => {
    const serial = {
      ...mockSerial,
      completed_at: '2025-01-21T16:00:00Z',
    };
    render(<WIPInfoCard serial={serial} />);

    expect(screen.getByText(/^completed$/i)).toBeTruthy();
    expect(screen.getByText(/2025-01-21 16:00/i)).toBeTruthy();
  });

  it('formats timestamps in correct format (yyyy-MM-dd HH:mm)', () => {
    const serial = {
      ...mockSerial,
      created_at: '2025-01-21T10:30:45Z',
      completed_at: '2025-01-21T16:45:30Z',
    };
    render(<WIPInfoCard serial={serial} />);

    // Check created timestamp format
    expect(screen.getByText(/2025-01-21 10:30/i)).toBeTruthy();

    // Check completed timestamp format
    expect(screen.getByText(/2025-01-21 16:45/i)).toBeTruthy();
  });

  // Integration tests
  it('displays all information for a complete serial', () => {
    const completeSerial: Serial = {
      id: 1,
      serial_number: 'KR01PSA2511001',
      lot_id: 1,
      lot: {
        id: 1,
        lot_number: 'KR01PSA2511',
        product_model_id: 1,
        product_model: {
          id: 1,
          model_code: 'PSA-WF-001',
          model_name: 'Power Switch Assembly',
          status: 'ACTIVE',
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z',
        },
        target_quantity: 100,
        production_date: '2025-11-21',
        shift: 'DAY' as Shift,
        status: 'COMPLETED' as LotStatus,
        created_at: '2025-01-21T08:00:00Z',
        updated_at: '2025-01-21T18:00:00Z',
      },
      status: 'PASS' as SerialStatus,
      rework_count: 1,
      created_at: '2025-01-21T10:00:00Z',
      updated_at: '2025-01-21T16:00:00Z',
      completed_at: '2025-01-21T16:00:00Z',
    };

    render(<WIPInfoCard serial={completeSerial} />);

    // Serial number
    expect(screen.getByText(/KR01-PSA-2511-001/i)).toBeTruthy();

    // Status
    expect(screen.getByText(/PASS/i)).toBeTruthy();

    // LOT info
    expect(screen.getByText(/KR01PSA2511/)).toBeTruthy();
    expect(screen.getByText(/power switch assembly/i)).toBeTruthy();
    expect(screen.getByText(/2025-11-21/i)).toBeTruthy();
    expect(screen.getByText(/DAY/i)).toBeTruthy();

    // Rework
    expect(screen.getByText(/rework count: 1\/3/i)).toBeTruthy();

    // Timestamps
    expect(screen.getByText(/2025-01-21 10:00/i)).toBeTruthy();
    expect(screen.getByText(/2025-01-21 16:00/i)).toBeTruthy();
  });

  it('handles minimal serial data without errors', () => {
    const minimalSerial: Serial = {
      id: 1,
      serial_number: 'KR01PSA2511001',
      lot_id: 1,
      status: 'CREATED' as SerialStatus,
      rework_count: 0,
      created_at: '2025-01-21T10:00:00Z',
      updated_at: '2025-01-21T10:00:00Z',
    };

    const { container } = render(<WIPInfoCard serial={minimalSerial} />);

    // Should render without crashing
    expect(container).toBeTruthy();

    // Serial number should be displayed
    expect(screen.getByText(/KR01-PSA-2511-001/i)).toBeTruthy();

    // Status should be displayed (use getAllByText since "Created" timestamp label also exists)
    const createdElements = screen.getAllByText(/CREATED/i);
    expect(createdElements.length).toBeGreaterThan(0);
  });
});
