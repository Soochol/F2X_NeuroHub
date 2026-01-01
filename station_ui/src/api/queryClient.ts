/**
 * React Query client configuration.
 */

import { QueryClient } from '@tanstack/react-query';
import { QUERY_OPTIONS } from '../config';

/**
 * Default query options for the application.
 */
const defaultQueryOptions = {
  queries: {
    staleTime: QUERY_OPTIONS.staleTime,
    gcTime: QUERY_OPTIONS.gcTime,
    retry: QUERY_OPTIONS.queryRetry,
    refetchOnWindowFocus: false,
    refetchOnReconnect: true,
  },
  mutations: {
    retry: QUERY_OPTIONS.mutationRetry,
  },
};

/**
 * React Query client instance.
 */
export const queryClient = new QueryClient({
  defaultOptions: defaultQueryOptions,
});

/**
 * Query keys for cache management.
 */
export const queryKeys = {
  // System
  systemInfo: ['system', 'info'] as const,
  healthStatus: ['system', 'health'] as const,

  // Batches
  batches: ['batches'] as const,
  batch: (id: string) => ['batches', id] as const,
  batchStatistics: (id: string) => ['batchStatistics', id] as const,
  allBatchStatistics: ['batchStatistics'] as const,

  // Sequences
  sequences: ['sequences'] as const,
  sequence: (name: string) => ['sequences', name] as const,

  // Results
  results: (params?: Record<string, unknown>) => ['results', params] as const,
  result: (id: string) => ['results', id] as const,

  // Logs
  logs: (params?: Record<string, unknown>) => ['logs', params] as const,
};

export default queryClient;
