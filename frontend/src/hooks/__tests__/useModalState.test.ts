/**
 * Tests for useModalState hook
 */

import { renderHook, act } from '@testing-library/react';
import { useModalState } from '../useModalState';

interface TestItem {
  id: number;
  name: string;
}

describe('useModalState', () => {
  it('should initialize with modal closed and no editing item', () => {
    const { result } = renderHook(() => useModalState<TestItem>());

    expect(result.current.isOpen).toBe(false);
    expect(result.current.editingItem).toBeUndefined();
  });

  it('should open modal without editing item', () => {
    const { result } = renderHook(() => useModalState<TestItem>());

    act(() => {
      result.current.open();
    });

    expect(result.current.isOpen).toBe(true);
    expect(result.current.editingItem).toBeUndefined();
  });

  it('should open modal with editing item', () => {
    const { result } = renderHook(() => useModalState<TestItem>());
    const testItem: TestItem = { id: 1, name: 'Test' };

    act(() => {
      result.current.open(testItem);
    });

    expect(result.current.isOpen).toBe(true);
    expect(result.current.editingItem).toEqual(testItem);
  });

  it('should close modal and clear editing item', () => {
    const { result } = renderHook(() => useModalState<TestItem>());
    const testItem: TestItem = { id: 1, name: 'Test' };

    act(() => {
      result.current.open(testItem);
    });

    expect(result.current.isOpen).toBe(true);

    act(() => {
      result.current.close();
    });

    expect(result.current.isOpen).toBe(false);
    expect(result.current.editingItem).toBeUndefined();
  });

  it('should toggle modal state', () => {
    const { result } = renderHook(() => useModalState<TestItem>());

    expect(result.current.isOpen).toBe(false);

    act(() => {
      result.current.toggle();
    });

    expect(result.current.isOpen).toBe(true);

    act(() => {
      result.current.toggle();
    });

    expect(result.current.isOpen).toBe(false);
  });

  it('should allow reopening with different item', () => {
    const { result } = renderHook(() => useModalState<TestItem>());
    const item1: TestItem = { id: 1, name: 'First' };
    const item2: TestItem = { id: 2, name: 'Second' };

    act(() => {
      result.current.open(item1);
    });

    expect(result.current.editingItem).toEqual(item1);

    act(() => {
      result.current.close();
    });

    act(() => {
      result.current.open(item2);
    });

    expect(result.current.editingItem).toEqual(item2);
  });

  it('should work with complex item types', () => {
    interface ComplexItem {
      id: number;
      user: {
        name: string;
        roles: string[];
      };
      metadata: Record<string, unknown>;
    }

    const { result } = renderHook(() => useModalState<ComplexItem>());
    const complexItem: ComplexItem = {
      id: 1,
      user: {
        name: 'Admin',
        roles: ['admin', 'editor'],
      },
      metadata: { createdAt: new Date().toISOString() },
    };

    act(() => {
      result.current.open(complexItem);
    });

    expect(result.current.editingItem).toEqual(complexItem);
    expect(result.current.editingItem?.user.roles).toContain('admin');
  });

  it('should maintain stable callback references', () => {
    const { result, rerender } = renderHook(() => useModalState<TestItem>());

    const openRef = result.current.open;
    const closeRef = result.current.close;
    const toggleRef = result.current.toggle;

    rerender();

    expect(result.current.open).toBe(openRef);
    expect(result.current.close).toBe(closeRef);
    expect(result.current.toggle).toBe(toggleRef);
  });
});
