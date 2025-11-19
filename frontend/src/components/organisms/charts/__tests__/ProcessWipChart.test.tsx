/**
 * Tests for ProcessWipChart component
 */

import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { ProcessWipChart } from '../ProcessWipChart';

const mockData = [
  { process_name: 'Laser Marking', wip_count: 15 },
  { process_name: 'Quality Check', wip_count: 8 },
  { process_name: 'Assembly', wip_count: 25 },
  { process_name: 'Testing', wip_count: 12 },
];

describe('ProcessWipChart', () => {
  it('renders without crashing', () => {
    const { container } = render(<ProcessWipChart data={mockData} />);
    expect(container).toBeTruthy();
  });

  it('renders with custom height', () => {
    const { container } = render(<ProcessWipChart data={mockData} height={500} />);
    expect(container).toBeTruthy();
  });

  it('renders with empty data', () => {
    const { container } = render(<ProcessWipChart data={[]} />);
    expect(container).toBeTruthy();
  });

  it('renders with single data point', () => {
    const { container } = render(
      <ProcessWipChart data={[{ process_name: 'Test', wip_count: 10 }]} />
    );
    expect(container).toBeTruthy();
  });

  it('handles zero WIP counts', () => {
    const zeroData = mockData.map((d) => ({ ...d, wip_count: 0 }));
    const { container } = render(<ProcessWipChart data={zeroData} />);
    expect(container).toBeTruthy();
  });
});
