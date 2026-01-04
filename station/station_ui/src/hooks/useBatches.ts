/**
 * Batch-related React Query hooks.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useEffect, useMemo } from 'react';
import { queryKeys } from '../api/queryClient';
import type { ApiError } from '../api/client';
import {
  getBatches,
  getBatch,
  startBatch,
  stopBatch,
  startSequence,
  stopSequence,
  manualControl,
  createBatches,
  updateBatchConfig,
  updateBatch,
  getBatchStatistics,
  getAllBatchStatistics,
  syncBatchToBackend,
  type UpdateBatchRequest,
} from '../api/endpoints/batches';
import { useBatchStore } from '../stores/batchStore';
import { useConnectionStore } from '../stores/connectionStore';
import { toast, getErrorMessage } from '../utils';
import { POLLING_INTERVALS } from '../config';
import type {
  SequenceStartRequest,
  ManualControlRequest,
  CreateBatchRequest,
  UpdateBatchConfigRequest,
  BatchStatus,
} from '../types';

/**
 * Check if error is a 409 Conflict (already running).
 */
function isAlreadyRunningError(error: unknown): boolean {
  if (error && typeof error === 'object' && 'status' in error) {
    return (error as ApiError).status === 409;
  }
  return false;
}

/**
 * Hook to fetch all batches.
 * Automatically uses faster polling when WebSocket is disconnected.
 */
export function useBatchList() {
  const setBatches = useBatchStore((state) => state.setBatches);
  const pollingFallbackActive = useConnectionStore((state) => state.pollingFallbackActive);

  // Use faster polling when WebSocket is disconnected
  const pollingInterval = pollingFallbackActive
    ? POLLING_INTERVALS.batchesFallback
    : POLLING_INTERVALS.batches;

  const query = useQuery({
    queryKey: queryKeys.batches,
    queryFn: getBatches,
    refetchInterval: pollingInterval,
  });

  // Sync with Zustand store
  useEffect(() => {
    if (query.data) {
      setBatches(query.data);
    }
  }, [query.data, setBatches]);

  return query;
}

/**
 * Hook to fetch a specific batch.
 * Combines API polling with real-time WebSocket updates from batchStore.
 * Store data takes priority for real-time fields (status, progress, etc.).
 */
export function useBatch(batchId: string | null) {
  // Get real-time state from store (updated via WebSocket)
  const storeBatch = useBatchStore((state) =>
    batchId ? state.batches.get(batchId) : undefined
  );

  const query = useQuery({
    queryKey: queryKeys.batch(batchId ?? ''),
    queryFn: () => getBatch(batchId!),
    enabled: !!batchId,
    // Disable polling during active execution or transitions (WebSocket handles updates)
    // Resume polling when idle or completed for eventual consistency
    refetchInterval: () => {
      if (storeBatch?.status === 'running' || storeBatch?.status === 'starting' || storeBatch?.status === 'stopping') {
        return false; // WebSocket handles real-time updates
      }
      return POLLING_INTERVALS.batchDetail;
    },
  });

  // Sync API data to store (store guards prevent status regression)
  useEffect(() => {
    if (query.data && batchId) {
      useBatchStore.getState().setBatches([query.data]);
    }
  }, [query.data, batchId]);

  // Merge: API provides detailed data, Store provides real-time status
  const mergedData = useMemo(() => {
    if (!batchId) return undefined;
    if (!query.data && !storeBatch) return undefined;

    // If store has real-time data and API has detailed data, merge them
    if (storeBatch && query.data) {
      return {
        ...query.data,
        // Real-time fields from store take priority
        status: storeBatch.status,
        progress: storeBatch.progress,
        currentStep: storeBatch.currentStep,
        stepIndex: storeBatch.stepIndex,
        executionId: storeBatch.executionId,
        lastRunPassed: storeBatch.lastRunPassed,
        // Include steps from store for real-time step updates
        steps: storeBatch.steps,
        // Include elapsed time from store (updated via WebSocket sequence_complete)
        elapsed: storeBatch.elapsed,
      };
    }

    // Fallback to whichever is available
    return query.data ?? storeBatch;
  }, [batchId, storeBatch, query.data]);

  return {
    ...query,
    data: mergedData,
  };
}

/**
 * Hook to start a batch.
 * Handles 409 Conflict (already running) gracefully.
 * Uses optimistic update for immediate UI feedback.
 */
export function useStartBatch() {
  const queryClient = useQueryClient();
  const updateBatchStatus = useBatchStore((state) => state.updateBatchStatus);

  return useMutation({
    mutationFn: async (batchId: string) => {
      try {
        return await startBatch(batchId);
      } catch (error: unknown) {
        // If already running (409), treat as success
        if (isAlreadyRunningError(error)) {
          return { batchId, status: 'already_running' as const, message: 'Batch already running' };
        }
        throw error;
      }
    },
    onMutate: async (batchId: string) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: queryKeys.batch(batchId) });
      await queryClient.cancelQueries({ queryKey: queryKeys.batches });

      // Get previous status for rollback
      const batch = useBatchStore.getState().batches.get(batchId);
      const previousStatus = batch?.status ?? 'idle';

      // Optimistically update to 'starting' immediately
      updateBatchStatus(batchId, 'starting');

      return { batchId, previousStatus };
    },
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.batches });
      if ('status' in result && result.status === 'already_running') {
        // Silent - no toast for already running
      } else {
        toast.success('Batch started successfully');
      }
    },
    onError: (error: unknown, batchId: string, context) => {
      // Rollback to previous status on error
      if (context?.previousStatus) {
        updateBatchStatus(batchId, context.previousStatus as BatchStatus);
      }
      toast.error(`Failed to start batch: ${getErrorMessage(error)}`);
    },
  });
}

/**
 * Hook to stop a batch.
 * Uses optimistic update for immediate UI feedback.
 */
export function useStopBatch() {
  const queryClient = useQueryClient();
  const updateBatchStatus = useBatchStore((state) => state.updateBatchStatus);

  return useMutation({
    mutationFn: (batchId: string) => stopBatch(batchId),
    onMutate: async (batchId: string) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: queryKeys.batch(batchId) });
      await queryClient.cancelQueries({ queryKey: queryKeys.batches });

      // Get previous status for rollback
      const batch = useBatchStore.getState().batches.get(batchId);
      const previousStatus = batch?.status ?? 'running';

      // Optimistically update to 'stopping' immediately
      updateBatchStatus(batchId, 'stopping');

      return { batchId, previousStatus };
    },
    onSuccess: (_, batchId) => {
      // Set to idle after successful stop
      updateBatchStatus(batchId, 'idle');
      queryClient.invalidateQueries({ queryKey: queryKeys.batches });
      toast.success('Batch stopped successfully');
    },
    onError: (error: unknown, batchId: string, context) => {
      // Rollback to previous status on error
      if (context?.previousStatus) {
        updateBatchStatus(batchId, context.previousStatus as BatchStatus);
      }
      toast.error(`Failed to stop batch: ${getErrorMessage(error)}`);
    },
  });
}

/**
 * Hook to delete a batch.
 */
export function useDeleteBatch() {
  const queryClient = useQueryClient();
  const removeBatch = useBatchStore((state) => state.removeBatch);

  return useMutation({
    mutationFn: async (batchId: string) => {
      const { deleteBatch } = await import('../api/endpoints/batches');
      return deleteBatch(batchId);
    },
    onSuccess: (_, batchId) => {
      removeBatch(batchId);
      queryClient.invalidateQueries({ queryKey: queryKeys.batches });
      toast.success('Batch deleted successfully');
    },
    onError: (error: unknown) => {
      toast.error(`Failed to delete batch: ${getErrorMessage(error)}`);
    },
  });
}

/**
 * Hook to start a sequence.
 * Handles 409 Conflict (already running) gracefully.
 * Uses optimistic update for immediate UI feedback.
 */
export function useStartSequence() {
  const queryClient = useQueryClient();
  const updateBatchStatus = useBatchStore((state) => state.updateBatchStatus);

  return useMutation({
    mutationFn: async ({
      batchId,
      request,
    }: {
      batchId: string;
      request?: SequenceStartRequest;
    }) => {
      try {
        return await startSequence(batchId, request);
      } catch (error: unknown) {
        // If already running (409), treat as success
        if (isAlreadyRunningError(error)) {
          return { batchId, status: 'already_running' as const, message: 'Sequence already running' };
        }
        throw error;
      }
    },
    onMutate: async ({ batchId }) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: queryKeys.batch(batchId) });
      await queryClient.cancelQueries({ queryKey: queryKeys.batches });

      // Get previous status for rollback
      const batch = useBatchStore.getState().batches.get(batchId);
      const previousStatus = batch?.status ?? 'idle';

      // Optimistically update to 'starting' immediately
      updateBatchStatus(batchId, 'starting');

      return { batchId, previousStatus };
    },
    onSuccess: (result, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.batch(variables.batchId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.batches });
      if ('status' in result && result.status === 'already_running') {
        // Silent - no toast for already running
      } else {
        toast.success('Sequence started successfully');
      }
    },
    onError: (error: unknown, variables, context) => {
      // Rollback to previous status on error
      if (context?.previousStatus) {
        updateBatchStatus(variables.batchId, context.previousStatus as BatchStatus);
      }
      toast.error(`Failed to start sequence: ${getErrorMessage(error)}`);
    },
  });
}

/**
 * Hook to stop a sequence.
 * Uses optimistic update for immediate UI feedback.
 */
export function useStopSequence() {
  const queryClient = useQueryClient();
  const updateBatchStatus = useBatchStore((state) => state.updateBatchStatus);

  return useMutation({
    mutationFn: (batchId: string) => stopSequence(batchId),
    onMutate: async (batchId: string) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: queryKeys.batch(batchId) });
      await queryClient.cancelQueries({ queryKey: queryKeys.batches });

      // Get previous status for rollback
      const batch = useBatchStore.getState().batches.get(batchId);
      const previousStatus = batch?.status ?? 'running';

      // Optimistically update to 'stopping' immediately
      updateBatchStatus(batchId, 'stopping');

      return { batchId, previousStatus };
    },
    onSuccess: (_, batchId) => {
      // Set to idle after successful stop
      updateBatchStatus(batchId, 'idle');
      queryClient.invalidateQueries({ queryKey: queryKeys.batch(batchId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.batches });
      toast.success('Sequence stopped successfully');
    },
    onError: (error: unknown, batchId: string, context) => {
      // Rollback to previous status on error
      if (context?.previousStatus) {
        updateBatchStatus(batchId, context.previousStatus as BatchStatus);
      }
      toast.error(`Failed to stop sequence: ${getErrorMessage(error)}`);
    },
  });
}

/**
 * Hook for manual control.
 */
export function useManualControl() {
  return useMutation({
    mutationFn: ({
      batchId,
      request,
    }: {
      batchId: string;
      request: ManualControlRequest;
    }) => manualControl(batchId, request),
    onSuccess: () => {
      toast.success('Command executed successfully');
    },
    onError: (error: unknown) => {
      toast.error(`Command failed: ${getErrorMessage(error)}`);
    },
  });
}

/**
 * Hook to create batches.
 */
export function useCreateBatches() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: CreateBatchRequest) => createBatches(request),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.batches });
      toast.success(`Created ${data.batchIds.length} batch(es) successfully`);
    },
    onError: (error: unknown) => {
      toast.error(`Failed to create batches: ${getErrorMessage(error)}`);
    },
  });
}

/**
 * Hook to update batch configuration.
 */
export function useUpdateBatchConfig() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      batchId,
      request,
    }: {
      batchId: string;
      request: UpdateBatchConfigRequest;
    }) => updateBatchConfig(batchId, request),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.batch(variables.batchId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.batches });
      toast.success('Batch configuration updated');
    },
    onError: (error: unknown) => {
      toast.error(`Failed to update batch config: ${getErrorMessage(error)}`);
    },
  });
}

/**
 * Hook to fetch batch statistics.
 */
export function useBatchStatistics(batchId: string | null) {
  return useQuery({
    queryKey: queryKeys.batchStatistics(batchId ?? ''),
    queryFn: () => getBatchStatistics(batchId!),
    enabled: !!batchId,
    staleTime: 10 * 1000, // 10 seconds - shorter for real-time updates
  });
}

/**
 * Hook to fetch all batch statistics.
 * Returns empty object on error (endpoint may not exist).
 */
export function useAllBatchStatistics() {
  return useQuery({
    queryKey: queryKeys.allBatchStatistics,
    queryFn: getAllBatchStatistics,
    staleTime: 10 * 1000, // 10 seconds - shorter for real-time updates
    retry: false, // Don't retry on 404
    throwOnError: false, // Don't throw errors
  });
}

/**
 * Hook to sync batch to backend.
 */
export function useSyncBatchToBackend() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (batchId: string) => syncBatchToBackend(batchId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.batches });
      toast.success('Batch synced to backend successfully');
    },
    onError: (error: unknown) => {
      toast.error(`Failed to sync batch: ${getErrorMessage(error)}`);
    },
  });
}

/**
 * Hook to update batch properties (PUT).
 * Supports: name, sequencePackage, hardware, autoStart, processId
 */
export function useUpdateBatch() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      batchId,
      request,
    }: {
      batchId: string;
      request: UpdateBatchRequest;
    }) => updateBatch(batchId, request),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.batch(variables.batchId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.batches });
    },
    onError: (error: unknown) => {
      toast.error(`Failed to update batch: ${getErrorMessage(error)}`);
    },
  });
}
