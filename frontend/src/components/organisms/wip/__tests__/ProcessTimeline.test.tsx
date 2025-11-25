/**
 * Tests for ProcessTimeline component
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ProcessTimeline } from '../ProcessTimeline';
import type { Process, ProcessData, ProcessResult, DataLevel } from '@/types/api';

describe('ProcessTimeline', () => {
  const mockProcesses: Process[] = [
    {
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
    },
    {
      id: 2,
      process_number: 2,
      process_code: 'INSP',
      process_name_ko: '검사',
      process_name_en: 'Inspection',
      sort_order: 2,
      is_active: true,
      auto_print_label: false,
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
    },
    {
      id: 3,
      process_number: 3,
      process_code: 'PACK',
      process_name_ko: '포장',
      process_name_en: 'Packaging',
      sort_order: 3,
      is_active: true,
      auto_print_label: false,
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
    },
  ];

  const mockCompletedProcesses: ProcessData[] = [
    {
      id: 1,
      serial_id: 1,
      process_id: 1,
      worker_id: 1,
      result: 'PASS' as ProcessResult,
      data_level: 'NORMAL' as DataLevel,
      started_at: '2025-01-21T10:00:00Z',
      completed_at: '2025-01-21T10:05:00Z',
      cycle_time_seconds: 300,
    },
  ];

  // Rendering tests
  it('renders without crashing', () => {
    const { container } = render(
      <ProcessTimeline
        processes={mockProcesses}
        completedProcesses={[]}
        currentProcessId={undefined}
      />
    );
    expect(container).toBeTruthy();
  });

  it('renders all processes', () => {
    render(
      <ProcessTimeline
        processes={mockProcesses}
        completedProcesses={[]}
        currentProcessId={undefined}
      />
    );

    // Check all process names are displayed
    expect(screen.getByText(/조립/i)).toBeTruthy();
    expect(screen.getByText(/검사/i)).toBeTruthy();
    expect(screen.getByText(/포장/i)).toBeTruthy();
  });

  it('displays process numbers', () => {
    render(
      <ProcessTimeline
        processes={mockProcesses}
        completedProcesses={[]}
        currentProcessId={undefined}
      />
    );

    expect(screen.getByText(/1\. 조립/i)).toBeTruthy();
    expect(screen.getByText(/2\. 검사/i)).toBeTruthy();
    expect(screen.getByText(/3\. 포장/i)).toBeTruthy();
  });

  it('displays English process names', () => {
    render(
      <ProcessTimeline
        processes={mockProcesses}
        completedProcesses={[]}
        currentProcessId={undefined}
      />
    );

    expect(screen.getByText(/assembly/i)).toBeTruthy();
    expect(screen.getByText(/inspection/i)).toBeTruthy();
    expect(screen.getByText(/packaging/i)).toBeTruthy();
  });

  it('displays title', () => {
    render(
      <ProcessTimeline
        processes={mockProcesses}
        completedProcesses={[]}
        currentProcessId={undefined}
      />
    );

    expect(screen.getByText(/process progress/i)).toBeTruthy();
  });

  // Completed process tests
  it('shows completed process with Done label', () => {
    render(
      <ProcessTimeline
        processes={mockProcesses}
        completedProcesses={mockCompletedProcesses}
        currentProcessId={undefined}
      />
    );

    // Should show "Done" for completed process
    expect(screen.getByText(/done/i)).toBeTruthy();
  });

  it('displays completed process timestamp', () => {
    render(
      <ProcessTimeline
        processes={mockProcesses}
        completedProcesses={mockCompletedProcesses}
        currentProcessId={undefined}
      />
    );

    // Should show completion timestamp
    expect(screen.getByText(/completed:/i)).toBeTruthy();
  });

  it('displays cycle time for completed process', () => {
    render(
      <ProcessTimeline
        processes={mockProcesses}
        completedProcesses={mockCompletedProcesses}
        currentProcessId={undefined}
      />
    );

    // Should show cycle time (300s)
    expect(screen.getByText(/300s/i)).toBeTruthy();
  });

  it('handles multiple completed processes', () => {
    const multipleCompleted: ProcessData[] = [
      ...mockCompletedProcesses,
      {
        id: 2,
        serial_id: 1,
        process_id: 2,
        worker_id: 1,
        result: 'PASS' as ProcessResult,
        data_level: 'NORMAL' as DataLevel,
        started_at: '2025-01-21T10:05:00Z',
        completed_at: '2025-01-21T10:10:00Z',
        cycle_time_seconds: 300,
      },
    ];

    render(
      <ProcessTimeline
        processes={mockProcesses}
        completedProcesses={multipleCompleted}
        currentProcessId={undefined}
      />
    );

    // Should show multiple "Done" labels
    const doneLabels = screen.getAllByText(/done/i);
    expect(doneLabels.length).toBe(2);
  });

  // Current process tests
  it('highlights current process with In Progress label', () => {
    render(
      <ProcessTimeline
        processes={mockProcesses}
        completedProcesses={mockCompletedProcesses}
        currentProcessId={2}
      />
    );

    expect(screen.getByText(/in progress/i)).toBeTruthy();
  });

  it('shows only one In Progress process', () => {
    render(
      <ProcessTimeline
        processes={mockProcesses}
        completedProcesses={mockCompletedProcesses}
        currentProcessId={2}
      />
    );

    const inProgressLabels = screen.getAllByText(/in progress/i);
    expect(inProgressLabels.length).toBe(1);
  });

  // Pending process tests
  it('shows pending processes with Pending label', () => {
    render(
      <ProcessTimeline
        processes={mockProcesses}
        completedProcesses={mockCompletedProcesses}
        currentProcessId={2}
      />
    );

    // Process 3 should be pending
    expect(screen.getByText(/pending/i)).toBeTruthy();
  });

  it('shows all processes as pending when none completed', () => {
    render(
      <ProcessTimeline
        processes={mockProcesses}
        completedProcesses={[]}
        currentProcessId={undefined}
      />
    );

    const pendingLabels = screen.getAllByText(/pending/i);
    expect(pendingLabels.length).toBe(3);
  });

  // Process ordering tests
  it('sorts processes by process_number', () => {
    const unsortedProcesses: Process[] = [
      { ...mockProcesses[2], process_number: 3 },
      { ...mockProcesses[0], process_number: 1 },
      { ...mockProcesses[1], process_number: 2 },
    ];

    render(
      <ProcessTimeline
        processes={unsortedProcesses}
        completedProcesses={[]}
        currentProcessId={undefined}
      />
    );

    // Get all process names in order
    const processElements = screen.getAllByText(/\d\. \w+/);

    // Should be sorted by process_number
    expect(processElements[0].textContent).toMatch(/1\. 조립/);
    expect(processElements[1].textContent).toMatch(/2\. 검사/);
    expect(processElements[2].textContent).toMatch(/3\. 포장/);
  });

  // Empty state tests
  it('handles empty process list', () => {
    const { container } = render(
      <ProcessTimeline
        processes={[]}
        completedProcesses={[]}
        currentProcessId={undefined}
      />
    );

    // Should still render the card with title
    expect(screen.getByText(/process progress/i)).toBeTruthy();

    // Should not crash
    expect(container).toBeTruthy();
  });

  it('handles empty completed processes', () => {
    const { container } = render(
      <ProcessTimeline
        processes={mockProcesses}
        completedProcesses={[]}
        currentProcessId={undefined}
      />
    );

    expect(container).toBeTruthy();

    // All should be pending
    const pendingLabels = screen.getAllByText(/pending/i);
    expect(pendingLabels.length).toBe(3);
  });

  // Status combination tests
  it('shows correct status for sequential process flow', () => {
    render(
      <ProcessTimeline
        processes={mockProcesses}
        completedProcesses={mockCompletedProcesses}
        currentProcessId={2}
      />
    );

    // Process 1: Done
    expect(screen.getByText(/done/i)).toBeTruthy();

    // Process 2: In Progress
    expect(screen.getByText(/in progress/i)).toBeTruthy();

    // Process 3: Pending
    expect(screen.getByText(/pending/i)).toBeTruthy();
  });

  it('handles all processes completed', () => {
    const allCompleted: ProcessData[] = [
      {
        id: 1,
        serial_id: 1,
        process_id: 1,
        worker_id: 1,
        result: 'PASS' as ProcessResult,
        data_level: 'NORMAL' as DataLevel,
        started_at: '2025-01-21T10:00:00Z',
        completed_at: '2025-01-21T10:05:00Z',
        cycle_time_seconds: 300,
      },
      {
        id: 2,
        serial_id: 1,
        process_id: 2,
        worker_id: 1,
        result: 'PASS' as ProcessResult,
        data_level: 'NORMAL' as DataLevel,
        started_at: '2025-01-21T10:05:00Z',
        completed_at: '2025-01-21T10:10:00Z',
        cycle_time_seconds: 300,
      },
      {
        id: 3,
        serial_id: 1,
        process_id: 3,
        worker_id: 1,
        result: 'PASS' as ProcessResult,
        data_level: 'NORMAL' as DataLevel,
        started_at: '2025-01-21T10:10:00Z',
        completed_at: '2025-01-21T10:15:00Z',
        cycle_time_seconds: 300,
      },
    ];

    render(
      <ProcessTimeline
        processes={mockProcesses}
        completedProcesses={allCompleted}
        currentProcessId={undefined}
      />
    );

    // All should show "Done"
    const doneLabels = screen.getAllByText(/done/i);
    expect(doneLabels.length).toBe(3);

    // No "In Progress" or "Pending"
    expect(screen.queryByText(/in progress/i)).toBeNull();
    expect(screen.queryByText(/pending/i)).toBeNull();
  });

  // Edge cases
  it('handles currentProcessId that does not exist', () => {
    const { container } = render(
      <ProcessTimeline
        processes={mockProcesses}
        completedProcesses={[]}
        currentProcessId={999}
      />
    );

    // Should not crash
    expect(container).toBeTruthy();

    // All should be pending
    const pendingLabels = screen.getAllByText(/pending/i);
    expect(pendingLabels.length).toBe(3);
  });

  it('handles completed process without cycle_time', () => {
    const completedWithoutCycle: ProcessData[] = [
      {
        id: 1,
        serial_id: 1,
        process_id: 1,
        worker_id: 1,
        result: 'PASS' as ProcessResult,
        data_level: 'NORMAL' as DataLevel,
        started_at: '2025-01-21T10:00:00Z',
        completed_at: '2025-01-21T10:05:00Z',
        cycle_time_seconds: 0,
      },
    ];

    render(
      <ProcessTimeline
        processes={mockProcesses}
        completedProcesses={completedWithoutCycle}
        currentProcessId={undefined}
      />
    );

    // Should show "Done"
    expect(screen.getByText(/done/i)).toBeTruthy();

    // Should show completed timestamp but not cycle time
    expect(screen.getByText(/completed:/i)).toBeTruthy();
  });

  it('handles single process', () => {
    const singleProcess: Process[] = [mockProcesses[0]];

    render(
      <ProcessTimeline
        processes={singleProcess}
        completedProcesses={[]}
        currentProcessId={1}
      />
    );

    expect(screen.getByText(/1\. 조립/i)).toBeTruthy();
    expect(screen.getByText(/in progress/i)).toBeTruthy();
  });

  it('renders processes with long names without overflow', () => {
    const longNameProcess: Process[] = [
      {
        id: 1,
        process_number: 1,
        process_code: 'LONG',
        process_name_ko: '매우 긴 공정 이름을 가진 공정',
        process_name_en: 'Process with Very Long Name That Should Not Overflow',
        sort_order: 1,
        is_active: true,
        auto_print_label: false,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
      },
    ];

    const { container } = render(
      <ProcessTimeline
        processes={longNameProcess}
        completedProcesses={[]}
        currentProcessId={undefined}
      />
    );

    expect(container).toBeTruthy();
    expect(screen.getByText(/매우 긴 공정 이름을 가진 공정/i)).toBeTruthy();
  });
});
