/**
 * Manual Sequence React Query hooks.
 *
 * Provides hooks for manual step-by-step sequence execution
 * with real hardware, without requiring a Batch.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  createManualSession,
  listManualSessions,
  getManualSession,
  deleteManualSession,
  initializeManualSession,
  finalizeManualSession,
  abortManualSession,
  runManualStep,
  skipManualStep,
  getManualSessionHardware,
  getHardwareCommands,
  executeHardwareCommand,
} from '../api/endpoints/manualSequence';
import type {
  ManualSessionDetail,
  ManualSessionSummary,
  ManualStepState,
  HardwareState,
  CommandDefinition,
  CommandResult,
} from '../api/endpoints/manualSequence';

// ============================================================================
// Query Keys
// ============================================================================

export const manualSequenceQueryKeys = {
  all: ['manual-sequence'] as const,
  sessions: () => [...manualSequenceQueryKeys.all, 'sessions'] as const,
  session: (id: string) => [...manualSequenceQueryKeys.sessions(), id] as const,
  hardware: (sessionId: string) =>
    [...manualSequenceQueryKeys.session(sessionId), 'hardware'] as const,
  commands: (sessionId: string, hardwareId: string) =>
    [...manualSequenceQueryKeys.hardware(sessionId), hardwareId, 'commands'] as const,
};

// ============================================================================
// Query Hooks
// ============================================================================

/**
 * Hook to list all manual test sessions.
 */
export function useManualSessions() {
  return useQuery({
    queryKey: manualSequenceQueryKeys.sessions(),
    queryFn: listManualSessions,
    staleTime: 10 * 1000, // 10 seconds
  });
}

/**
 * Hook to get a specific manual test session.
 */
export function useManualSession(sessionId: string | null) {
  return useQuery({
    queryKey: manualSequenceQueryKeys.session(sessionId ?? ''),
    queryFn: () => getManualSession(sessionId!),
    enabled: !!sessionId,
    refetchInterval: (query) => {
      // Refetch while session is active
      const data = query.state.data;
      if (data && ['connecting', 'running', 'ready'].includes(data.status)) {
        return 1000; // 1 second
      }
      return false;
    },
  });
}

/**
 * Hook to get hardware state for a session.
 */
export function useManualSessionHardware(sessionId: string | null) {
  return useQuery({
    queryKey: manualSequenceQueryKeys.hardware(sessionId ?? ''),
    queryFn: () => getManualSessionHardware(sessionId!),
    enabled: !!sessionId,
    staleTime: 5 * 1000, // 5 seconds
  });
}

/**
 * Hook to get available commands for a hardware device.
 */
export function useHardwareCommands(sessionId: string | null, hardwareId: string | null) {
  return useQuery({
    queryKey: manualSequenceQueryKeys.commands(sessionId ?? '', hardwareId ?? ''),
    queryFn: () => getHardwareCommands(sessionId!, hardwareId!),
    enabled: !!sessionId && !!hardwareId,
  });
}

// ============================================================================
// Mutation Hooks
// ============================================================================

/**
 * Hook to create a new manual test session.
 */
export function useCreateManualSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      sequenceName,
      hardwareConfig,
      parameters,
    }: {
      sequenceName: string;
      hardwareConfig?: Record<string, Record<string, unknown>>;
      parameters?: Record<string, unknown>;
    }) => createManualSession(sequenceName, hardwareConfig, parameters),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: manualSequenceQueryKeys.sessions() });
    },
  });
}

/**
 * Hook to delete a manual test session.
 */
export function useDeleteManualSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (sessionId: string) => deleteManualSession(sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: manualSequenceQueryKeys.sessions() });
    },
  });
}

/**
 * Hook to initialize a manual test session.
 */
export function useInitializeManualSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (sessionId: string) => initializeManualSession(sessionId),
    onSuccess: (data) => {
      queryClient.setQueryData(manualSequenceQueryKeys.session(data.id), data);
    },
  });
}

/**
 * Hook to finalize a manual test session.
 */
export function useFinalizeManualSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (sessionId: string) => finalizeManualSession(sessionId),
    onSuccess: (data) => {
      queryClient.setQueryData(manualSequenceQueryKeys.session(data.id), data);
    },
  });
}

/**
 * Hook to abort a manual test session.
 */
export function useAbortManualSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (sessionId: string) => abortManualSession(sessionId),
    onSuccess: (data) => {
      queryClient.setQueryData(manualSequenceQueryKeys.session(data.id), data);
    },
  });
}

/**
 * Hook to run a step in the manual session.
 */
export function useRunManualStep() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      sessionId,
      stepName,
      parameterOverrides,
    }: {
      sessionId: string;
      stepName: string;
      parameterOverrides?: Record<string, unknown>;
    }) => runManualStep(sessionId, stepName, parameterOverrides),
    onSuccess: (data, variables) => {
      // Update the session in cache with the new step state
      queryClient.setQueryData<ManualSessionDetail>(
        manualSequenceQueryKeys.session(variables.sessionId),
        (old) => {
          if (!old) return old;
          return {
            ...old,
            steps: old.steps.map((s) => (s.name === data.name ? data : s)),
          };
        }
      );
      // Also invalidate to get full session update
      queryClient.invalidateQueries({
        queryKey: manualSequenceQueryKeys.session(variables.sessionId),
      });
    },
  });
}

/**
 * Hook to skip a step in the manual session.
 */
export function useSkipManualStep() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      sessionId,
      stepName,
    }: {
      sessionId: string;
      stepName: string;
    }) => skipManualStep(sessionId, stepName),
    onSuccess: (data, variables) => {
      queryClient.setQueryData<ManualSessionDetail>(
        manualSequenceQueryKeys.session(variables.sessionId),
        (old) => {
          if (!old) return old;
          return {
            ...old,
            steps: old.steps.map((s) => (s.name === data.name ? data : s)),
          };
        }
      );
      queryClient.invalidateQueries({
        queryKey: manualSequenceQueryKeys.session(variables.sessionId),
      });
    },
  });
}

/**
 * Hook to execute a hardware command.
 */
export function useExecuteHardwareCommand() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      sessionId,
      hardwareId,
      command,
      parameters,
    }: {
      sessionId: string;
      hardwareId: string;
      command: string;
      parameters?: Record<string, unknown>;
    }) => executeHardwareCommand(sessionId, hardwareId, command, parameters),
    onSuccess: (_, variables) => {
      // Invalidate hardware state after command execution
      queryClient.invalidateQueries({
        queryKey: manualSequenceQueryKeys.hardware(variables.sessionId),
      });
    },
  });
}

// ============================================================================
// Type exports
// ============================================================================

export type {
  ManualSessionDetail,
  ManualSessionSummary,
  ManualStepState,
  HardwareState,
  CommandDefinition,
  CommandResult,
};
