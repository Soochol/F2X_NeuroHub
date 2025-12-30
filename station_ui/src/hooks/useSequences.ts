/**
 * Sequence-related React Query hooks.
 */

import { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '../api/queryClient';
import {
  getSequences,
  getSequence,
  updateSequence,
  validateSequence,
  uploadSequence,
  deleteSequence,
  downloadSequence,
  deploySequence,
  getDeployments,
  getDeployedSequence,
  runSimulation,
} from '../api/endpoints/sequences';
import type { SequenceUpdateRequest, UploadProgress, SimulationMode } from '../types';

/**
 * Hook to fetch all sequences.
 */
export function useSequenceList() {
  return useQuery({
    queryKey: queryKeys.sequences,
    queryFn: getSequences,
    staleTime: 5 * 60 * 1000, // 5 minutes - sequences don't change often
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
 * Hook to validate a sequence package.
 */
export function useValidateSequence() {
  return useMutation({
    mutationFn: (file: File) => validateSequence(file),
  });
}

/**
 * Hook to upload and install a sequence package with progress tracking.
 */
export function useUploadSequence() {
  const queryClient = useQueryClient();
  const [progress, setProgress] = useState<UploadProgress>({
    stage: 'idle',
    progress: 0,
    message: '',
  });

  const resetProgress = useCallback(() => {
    setProgress({ stage: 'idle', progress: 0, message: '' });
  }, []);

  const mutation = useMutation({
    mutationFn: async ({ file, force }: { file: File; force?: boolean }) => {
      setProgress({ stage: 'validating', progress: 0, message: 'Validating package...' });

      // First validate
      const validation = await validateSequence(file);
      if (!validation.valid) {
        throw new Error(validation.errors?.map((e) => e.message).join(', ') || 'Validation failed');
      }

      setProgress({ stage: 'uploading', progress: 0, message: 'Uploading package...' });

      // Then upload with progress tracking
      const result = await uploadSequence(file, force ?? false, (uploadProgress) => {
        setProgress({
          stage: 'uploading',
          progress: uploadProgress,
          message: `Uploading... ${uploadProgress}%`,
        });
      });

      setProgress({
        stage: 'complete',
        progress: 100,
        message: `Successfully installed ${result.name} v${result.version}`,
      });

      return { result, validation };
    },
    onSuccess: async () => {
      // Force refetch to update the list immediately
      await queryClient.refetchQueries({ queryKey: queryKeys.sequences });
    },
    onError: (error: Error) => {
      setProgress({
        stage: 'error',
        progress: 0,
        message: 'Upload failed',
        error: error.message,
      });
    },
  });

  return {
    ...mutation,
    progress,
    resetProgress,
  };
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
