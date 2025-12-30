/**
 * Tests for useAsyncData hook
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { useAsyncData } from '../useAsyncData';

describe('useAsyncData', () => {
  const mockFetchFn = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should start with loading state when autoFetch is true', () => {
    mockFetchFn.mockResolvedValue({ data: 'test' });

    const { result } = renderHook(() =>
      useAsyncData({
        fetchFn: mockFetchFn,
        autoFetch: true,
      })
    );

    expect(result.current.isLoading).toBe(true);
    expect(result.current.error).toBe('');
    expect(result.current.data).toBeUndefined();
  });

  it('should not fetch when autoFetch is false', () => {
    const { result } = renderHook(() =>
      useAsyncData({
        fetchFn: mockFetchFn,
        autoFetch: false,
      })
    );

    expect(result.current.isLoading).toBe(false);
    expect(mockFetchFn).not.toHaveBeenCalled();
  });

  it('should use initialData when provided', () => {
    const initialData = { name: 'initial' };

    const { result } = renderHook(() =>
      useAsyncData({
        fetchFn: mockFetchFn,
        initialData,
        autoFetch: false,
      })
    );

    expect(result.current.data).toEqual(initialData);
  });

  it('should fetch data and update state on success', async () => {
    const responseData = { id: 1, name: 'Test' };
    mockFetchFn.mockResolvedValue(responseData);

    const { result } = renderHook(() =>
      useAsyncData({
        fetchFn: mockFetchFn,
        autoFetch: true,
      })
    );

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toEqual(responseData);
    expect(result.current.error).toBe('');
    expect(mockFetchFn).toHaveBeenCalledTimes(1);
  });

  it('should handle fetch error and set error message', async () => {
    const errorMessage = 'Network error';
    mockFetchFn.mockRejectedValue(new Error(errorMessage));

    const { result } = renderHook(() =>
      useAsyncData({
        fetchFn: mockFetchFn,
        autoFetch: true,
        errorMessage: 'Custom error message',
      })
    );

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toBeTruthy();
    expect(result.current.data).toBeUndefined();
  });

  it('should refetch data when refetch is called', async () => {
    const initialData = { id: 1 };
    const newData = { id: 2 };
    mockFetchFn.mockResolvedValueOnce(initialData).mockResolvedValueOnce(newData);

    const { result } = renderHook(() =>
      useAsyncData({
        fetchFn: mockFetchFn,
        autoFetch: true,
      })
    );

    await waitFor(() => {
      expect(result.current.data).toEqual(initialData);
    });

    await act(async () => {
      await result.current.refetch();
    });

    expect(result.current.data).toEqual(newData);
    expect(mockFetchFn).toHaveBeenCalledTimes(2);
  });

  it('should allow manual data update via setData', async () => {
    mockFetchFn.mockResolvedValue({ id: 1 });

    const { result } = renderHook(() =>
      useAsyncData({
        fetchFn: mockFetchFn,
        autoFetch: true,
      })
    );

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    const newData = { id: 999, name: 'Manual Update' };
    act(() => {
      result.current.setData(newData);
    });

    expect(result.current.data).toEqual(newData);
  });

  it('should allow manual error update via setError', async () => {
    mockFetchFn.mockResolvedValue({ id: 1 });

    const { result } = renderHook(() =>
      useAsyncData({
        fetchFn: mockFetchFn,
        autoFetch: true,
      })
    );

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    act(() => {
      result.current.setError('Custom error');
    });

    expect(result.current.error).toBe('Custom error');
  });

  it('should clear error on refetch', async () => {
    mockFetchFn
      .mockRejectedValueOnce(new Error('First error'))
      .mockResolvedValueOnce({ success: true });

    const { result } = renderHook(() =>
      useAsyncData({
        fetchFn: mockFetchFn,
        autoFetch: true,
      })
    );

    await waitFor(() => {
      expect(result.current.error).toBeTruthy();
    });

    await act(async () => {
      await result.current.refetch();
    });

    expect(result.current.error).toBe('');
    expect(result.current.data).toEqual({ success: true });
  });
});
