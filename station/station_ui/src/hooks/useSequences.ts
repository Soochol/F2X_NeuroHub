/**
 * Sequence-related React Query hooks.
 *
 * Note: Upload functionality has been moved to Backend.
 * Use usePullSequence() to install sequences from Backend.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '../api/queryClient';
import {
  getSequences,
  getSequence,
  updateSequence,
  deleteSequence,
  downloadSequence,
  getSequenceRegistry,
  pullSequence,
  syncSequences,
  deploySequence,
  getDeployments,
  getDeployedSequence,
  runSimulation,
  getAutoSyncStatus,
  configureAutoSync,
  triggerAutoSyncCheck,
  type AutoSyncConfig,
} from '../api/endpoints/sequences';
import type { SequenceUpdateRequest, SimulationMode } from '../types';

// Note: Error handling is done globally via MutationCache in queryClient.ts

// ============================================================================
// Sequence Hooks
// ============================================================================

/**
 * Hook to fetch all local sequences.
 */
export function useSequenceList() {
  return useQuery({
    queryKey: queryKeys.sequences,
    queryFn: getSequences,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to fetch a specific sequence.
 */
export function useSequence(name: string | null) {
  return useQuery({
    queryKey: queryKeys.sequence(name ?? ''),
    queryFn: () => getSequence(name!),
    enabled: !!name,
  });
}

/**
 * Hook to update a sequence.
 */
export function useUpdateSequence() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      name,
      request,
    }: {
      name: string;
      request: SequenceUpdateRequest;
    }) => updateSequence(name, request),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.sequence(variables.name) });
      queryClient.invalidateQueries({ queryKey: queryKeys.sequences });
    },
  });
}

/**
 * Hook to delete a sequence package.
 */
export function useDeleteSequence() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (name: string) => deleteSequence(name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.sequences });
      queryClient.invalidateQueries({ queryKey: ['registry'] });
    },
  });
}

/**
 * Hook to download a sequence package.
 */
export function useDownloadSequence() {
  return useMutation({
    mutationFn: async (name: string) => {
      const blob = await downloadSequence(name);

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${name}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      return { name };
    },
  });
}

// ============================================================================
// Registry Hooks
// ============================================================================

/**
 * Hook to fetch unified sequence registry (local + remote).
 */
export function useSequenceRegistry() {
  return useQuery({
    queryKey: ['registry'],
    queryFn: getSequenceRegistry,
    staleTime: 30 * 1000, // 30 seconds
    refetchOnWindowFocus: true,
  });
}

/**
 * Hook to pull (install/update) a sequence from Backend.
 */
export function usePullSequence() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ name, force = false }: { name: string; force?: boolean }) =>
      pullSequence(name, force),
    onSuccess: async () => {
      // Use refetchQueries to force immediate refetch after pull
      await queryClient.refetchQueries({ queryKey: queryKeys.sequences });
      await queryClient.refetchQueries({ queryKey: ['registry'] });
    },
  });
}

/**
 * Hook to sync all sequences from Backend.
 */
export function useSyncSequences() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (sequenceNames?: string[]) => syncSequences(sequenceNames),
    onSuccess: async () => {
      // Use refetchQueries to force immediate refetch after sync
      await queryClient.refetchQueries({ queryKey: queryKeys.sequences });
      await queryClient.refetchQueries({ queryKey: ['registry'] });
    },
  });
}

// ============================================================================
// Deploy Hooks
// ============================================================================

/**
 * Hook to deploy a sequence to a batch.
 */
export function useDeploySequence() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ sequenceName, batchId }: { sequenceName: string; batchId: string }) =>
      deploySequence(sequenceName, batchId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deployments'] });
      queryClient.invalidateQueries({ queryKey: ['deployed'] });
    },
  });
}

/**
 * Hook to fetch all deployments.
 */
export function useDeployments() {
  return useQuery({
    queryKey: ['deployments'],
    queryFn: getDeployments,
    staleTime: 30 * 1000, // 30 seconds
  });
}

/**
 * Hook to fetch deployed sequence for a batch.
 */
export function useDeployedSequence(batchId: string | null) {
  return useQuery({
    queryKey: ['deployed', batchId],
    queryFn: () => getDeployedSequence(batchId!),
    enabled: !!batchId,
    staleTime: 30 * 1000, // 30 seconds
  });
}

// ============================================================================
// Simulation Hooks
// ============================================================================

/**
 * Hook to run a sequence simulation.
 */
export function useSimulation() {
  return useMutation({
    mutationFn: ({
      sequenceName,
      mode,
      parameters,
    }: {
      sequenceName: string;
      mode: SimulationMode;
      parameters?: Record<string, unknown>;
    }) => runSimulation(sequenceName, mode, parameters),
  });
}

// ============================================================================
// Auto-Sync Hooks
// ============================================================================

/**
 * Hook to fetch auto-sync status.
 */
export function useAutoSyncStatus() {
  return useQuery({
    queryKey: ['auto-sync', 'status'],
    queryFn: getAutoSyncStatus,
    staleTime: 10 * 1000, // 10 seconds
    refetchInterval: 30 * 1000, // Refetch every 30 seconds
  });
}

/**
 * Hook to configure auto-sync.
 */
export function useConfigureAutoSync() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (config: AutoSyncConfig) => configureAutoSync(config),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['auto-sync'] });
    },
  });
}

/**
 * Hook to trigger manual update check.
 */
export function useTriggerAutoSyncCheck() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => triggerAutoSyncCheck(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['auto-sync'] });
      queryClient.invalidateQueries({ queryKey: ['registry'] });
    },
  });
}
