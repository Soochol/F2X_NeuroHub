/**
 * Tests for DefectPieChart component
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { DefectPieChart } from '../DefectPieChart';

describe('DefectPieChart', () => {
  it('renders without crashing', () => {
    const { container } = render(<DefectPieChart passed={90} failed={10} />);
    expect(container).toBeTruthy();
  });

  it('displays correct pass rate', () => {
    render(<DefectPieChart passed={90} failed={10} />);
    expect(screen.getByText('90.0%')).toBeTruthy();
  });

  it('handles zero total', () => {
    render(<DefectPieChart passed={0} failed={0} />);
    expect(screen.getByText('0%')).toBeTruthy();
  });

  it('handles all passed', () => {
    render(<DefectPieChart passed={100} failed={0} />);
    expect(screen.getByText('100.0%')).toBeTruthy();
  });

  it('handles all failed', () => {
    render(<DefectPieChart passed={0} failed={100} />);
    expect(screen.getByText('0.0%')).toBeTruthy();
  });

  it('renders legend items', () => {
    render(<DefectPieChart passed={90} failed={10} />);
    expect(screen.getByText('Passed')).toBeTruthy();
    expect(screen.getByText('Failed')).toBeTruthy();
  });
});
