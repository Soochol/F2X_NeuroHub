/**
 * Tests for ProductionBarChart component
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ProductionBarChart } from '../ProductionBarChart';

const mockData = [
  { name: 'LOT-001', started: 100, completed: 90, defective: 5 },
  { name: 'LOT-002', started: 150, completed: 120, defective: 10 },
  { name: 'LOT-003', started: 80, completed: 70, defective: 2 },
];

describe('ProductionBarChart', () => {
  it('renders without crashing', () => {
    const { container } = render(<ProductionBarChart data={mockData} />);
    expect(container).toBeTruthy();
  });

  it('renders with custom height', () => {
    const { container } = render(<ProductionBarChart data={mockData} height={400} />);
    expect(container).toBeTruthy();
  });

  it('renders with empty data', () => {
    const { container } = render(<ProductionBarChart data={[]} />);
    expect(container).toBeTruthy();
  });

  it('renders legend items', () => {
    render(<ProductionBarChart data={mockData} />);
    // Check for legend text
    expect(screen.getByText('Started')).toBeTruthy();
    expect(screen.getByText('Completed')).toBeTruthy();
    expect(screen.getByText('Defective')).toBeTruthy();
  });
});
