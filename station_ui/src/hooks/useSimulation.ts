/**
 * Interactive Simulation React Query hooks.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  createSimulationSession,
  listSimulationSessions,
  getSimulationSession,
  deleteSimulationSession,
  initializeSimulationSession,
  finalizeSimulationSession,
  abortSimulationSession,
  runSimulationStep,
  skipSimulationStep,
  runQuickSimulation,
} from '../api/endpoints/simulation';
import type {
  SimulationSessionDetail,
  SimulationSessionSummary,
  SimulationStepState,
} from '../api/endpoints/simulation';

// ============================================================================
// Query Keys
// ============================================================================

export const simulationQueryKeys = {
  all: ['simulation'] as const,
  sessions: () => [...simulationQueryKeys.all, 'sessions'] as const,
  session: (id: string) => [...simulationQueryKeys.sessions(), id] as const,
};

// ============================================================================
// Query Hooks
// ============================================================================

/**
 * Hook to list all simulation sessions.
 */
export function useSimulationSessions() {
  return useQuery({
    queryKey: simulationQueryKeys.sessions(),
    queryFn: listSimulationSessions,
    staleTime: 10 * 1000, // 10 seconds
  });
}

/**
 * Hook to get a specific simulation session.
 */
export function useSimulationSession(sessionId: string | null) {
  return useQuery({
    queryKey: simulationQueryKeys.session(sessionId ?? ''),
    queryFn: () => getSimulationSession(sessionId!),
    enabled: !!sessionId,
    refetchInterval: (query) => {
      // Refetch while session is running
      const data = query.state.data;
      if (data && ['running', 'ready'].includes(data.status)) {
        return 1000; // 1 second
      }
      return false;
    },
  });
}

// ============================================================================
// Mutation Hooks
// ============================================================================

/**
 * Hook to create a new simulation session.
 */
export function useCreateSimulationSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      sequenceName,
      parameters,
      hardwareConfig,
    }: {
      sequenceName: string;
      parameters?: Record<string, unknown>;
      hardwareConfig?: Record<string, unknown>;
    }) => createSimulationSession(sequenceName, parameters, hardwareConfig),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: simulationQueryKeys.sessions() });
    },
  });
}

/**
 * Hook to delete a simulation session.
 */
export function useDeleteSimulationSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (sessionId: string) => deleteSimulationSession(sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: simulationQueryKeys.sessions() });
    },
  });
}

/**
 * Hook to initialize a simulation session.
 */
export function useInitializeSimulationSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (sessionId: string) => initializeSimulationSession(sessionId),
    onSuccess: (data) => {
      queryClient.setQueryData(simulationQueryKeys.session(data.id), data);
    },
  });
}

/**
 * Hook to finalize a simulation session.
 */
export function useFinalizeSimulationSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (sessionId: string) => finalizeSimulationSession(sessionId),
    onSuccess: (data) => {
      queryClient.setQueryData(simulationQueryKeys.session(data.id), data);
    },
  });
}

/**
 * Hook to abort a simulation session.
 */
export function useAbortSimulationSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (sessionId: string) => abortSimulationSession(sessionId),
    onSuccess: (data) => {
      queryClient.setQueryData(simulationQueryKeys.session(data.id), data);
    },
  });
}

/**
 * Hook to run a simulation step.
 */
export function useRunSimulationStep() {
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
    }) => runSimulationStep(sessionId, stepName, parameterOverrides),
    onSuccess: (data, variables) => {
      // Update the session in cache with the new step state
      queryClient.setQueryData<SimulationSessionDetail>(
        simulationQueryKeys.session(variables.sessionId),
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
        queryKey: simulationQueryKeys.session(variables.sessionId),
      });
    },
  });
}

/**
 * Hook to skip a simulation step.
 */
export function useSkipSimulationStep() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      sessionId,
      stepName,
    }: {
      sessionId: string;
      stepName: string;
    }) => skipSimulationStep(sessionId, stepName),
    onSuccess: (data, variables) => {
      queryClient.setQueryData<SimulationSessionDetail>(
        simulationQueryKeys.session(variables.sessionId),
        (old) => {
          if (!old) return old;
          return {
            ...old,
            steps: old.steps.map((s) => (s.name === data.name ? data : s)),
          };
        }
      );
      queryClient.invalidateQueries({
        queryKey: simulationQueryKeys.session(variables.sessionId),
      });
    },
  });
}

/**
 * Hook to run a quick simulation (all steps at once).
 */
export function useQuickSimulation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      sequenceName,
      parameters,
      hardwareConfig,
    }: {
      sequenceName: string;
      parameters?: Record<string, unknown>;
      hardwareConfig?: Record<string, unknown>;
    }) => runQuickSimulation(sequenceName, parameters, hardwareConfig),
    onSuccess: (data) => {
      queryClient.setQueryData(simulationQueryKeys.session(data.id), data);
      queryClient.invalidateQueries({ queryKey: simulationQueryKeys.sessions() });
    },
  });
}

// ============================================================================
// Type exports
// ============================================================================

export type { SimulationSessionDetail, SimulationSessionSummary, SimulationStepState };
