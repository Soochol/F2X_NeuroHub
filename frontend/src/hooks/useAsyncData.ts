/**
 * Hook for managing async data fetching with loading and error states
 */

import { useState, useEffect, useCallback } from 'react';
import { getErrorMessage } from '@/types/api';

interface UseAsyncDataOptions<T> {
  fetchFn: () => Promise<T>;
  initialData?: T;
  autoFetch?: boolean;
  dependencies?: unknown[];
  errorMessage?: string;
}

interface UseAsyncDataReturn<T> {
  data: T | undefined;
  isLoading: boolean;
  error: string;
  refetch: () => Promise<void>;
  setData: React.Dispatch<React.SetStateAction<T | undefined>>;
  setError: React.Dispatch<React.SetStateAction<string>>;
}

export function useAsyncData<T>({
  fetchFn,
  initialData,
  autoFetch = true,
  dependencies = [],
  errorMessage = 'Failed to load data',
}: UseAsyncDataOptions<T>): UseAsyncDataReturn<T> {
  const [data, setData] = useState<T | undefined>(initialData);
  const [isLoading, setIsLoading] = useState(autoFetch);
  const [error, setError] = useState('');

  const refetch = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      const result = await fetchFn();
      setData(result);
    } catch (err: unknown) {
      setError(getErrorMessage(err, errorMessage));
    } finally {
      setIsLoading(false);
    }
  }, [fetchFn, errorMessage]);

  useEffect(() => {
    if (autoFetch) {
      refetch();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, dependencies);

  return {
    data,
    isLoading,
    error,
    refetch,
    setData,
    setError,
  };
}

export default useAsyncData;
