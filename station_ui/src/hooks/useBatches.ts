/**
 * Batch-related React Query hooks.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useShallow } from 'zustand/react/shallow';
import { queryKeys } from '../api/queryClient';
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
  getBatchStatistics,
  getAllBatchStatistics,
  syncBatchToBackend,
} from '../api/endpoints/batches';
import { useBatchStore } from '../stores/batchStore';
import { useConnectionStore } from '../stores/connectionStore';
import { useEffect } from 'react';
import { toast, getErrorMessage } from '../utils';
import { POLLING_INTERVALS } from '../config';
import type {
  SequenceStartRequest,
  ManualControlRequest,
  CreateBatchRequest,
  UpdateBatchConfigRequest,
} from '../types';

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
 * For local batches (prefixed with 'local-batch-'), returns from store directly.
 */
export function useBatch(batchId: string | null) {
  // Check if it's a local batch
  const isLocalBatch = batchId?.startsWith('local-batch-') ?? false;

  // Subscribe to the specific local batch from the store (reactive with useShallow)
  const localBatch = useBatchStore(
    useShallow((state) => {
      if (!isLocalBatch || !batchId) return undefined;
      return state.localBatches.get(batchId);
    })
  );

  const query = useQuery({
    queryKey: queryKeys.batch(batchId ?? ''),
    queryFn: () => getBatch(batchId!),
    enabled: !!batchId && !isLocalBatch,
  });

  // For local batches, return the data from the store
  if (isLocalBatch) {
    return {
      ...query,
      data: localBatch,
      isLoading: false,
      isError: !localBatch,
    };
  }

  return query;
}

/**
 * Hook to start a batch.
 */
export function useStartBatch() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (batchId: string) => startBatch(batchId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.batches });
      toast.success('Batch started successfully');
    },
    onError: (error: unknown) => {
      toast.error(`Failed to start batch: ${getErrorMessage(error)}`);
    },
  });
}

/**
 * Hook to stop a batch.
 */
export function useStopBatch() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (batchId: string) => stopBatch(batchId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.batches });
      toast.success('Batch stopped successfully');
    },
    onError: (error: unknown) => {
      toast.error(`Failed to stop batch: ${getErrorMessage(error)}`);
    },
  });
}

/**
 * Hook to start a sequence.
 */
export function useStartSequence() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      batchId,
      request,
    }: {
      batchId: string;
      request?: SequenceStartRequest;
    }) => startSequence(batchId, request),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.batch(variables.batchId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.batches });
      toast.success('Sequence started successfully');
    },
    onError: (error: unknown) => {
      toast.error(`Failed to start sequence: ${getErrorMessage(error)}`);
    },
  });
}

/**
 * Hook to stop a sequence.
 */
export function useStopSequence() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (batchId: string) => stopSequence(batchId),
    onSuccess: (_, batchId) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.batch(batchId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.batches });
      toast.success('Sequence stopped successfully');
    },
    onError: (error: unknown) => {
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
    queryKey: ['batchStatistics', batchId],
    queryFn: () => getBatchStatistics(batchId!),
    enabled: !!batchId,
    staleTime: 30 * 1000, // 30 seconds
  });
}

/**
 * Hook to fetch all batch statistics.
 */
export function useAllBatchStatistics() {
  return useQuery({
    queryKey: ['allBatchStatistics'],
    queryFn: getAllBatchStatistics,
    staleTime: 30 * 1000, // 30 seconds
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
