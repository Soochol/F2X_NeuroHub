/**
 * Workflow configuration React Query hooks.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '../api/queryClient';
import {
  getWorkflowConfig,
  updateWorkflowConfig,
  getProcesses,
  getProcessHeaders,
  type WorkflowConfig,
  type UpdateWorkflowRequest,
  type ProcessInfo,
  type ProcessHeaderInfo,
} from '../api/endpoints/system';

/**
 * Hook to fetch workflow configuration.
 */
export function useWorkflowConfig() {
  return useQuery({
    queryKey: queryKeys.workflowConfig,
    queryFn: getWorkflowConfig,
  });
}

/**
 * Hook to update workflow configuration.
 */
export function useUpdateWorkflowConfig() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateWorkflowRequest) => updateWorkflowConfig(data),
    onSuccess: (data) => {
      // Update the cache with the new data
      queryClient.setQueryData(queryKeys.workflowConfig, data);
    },
  });
}

/**
 * Hook to fetch process list from backend MES.
 */
export function useProcesses() {
  return useQuery({
    queryKey: ['system', 'processes'] as const,
    queryFn: getProcesses,
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  });
}

/**
 * Hook to fetch process headers from backend MES.
 * @param stationId Optional filter by station ID
 * @param batchId Optional filter by batch ID
 * @param processId Optional filter by process ID
 * @param status Optional filter by status (OPEN, CLOSED, CANCELLED)
 * @param enabled Whether to enable the query (default true)
 */
export function useProcessHeaders(params?: {
  stationId?: string;
  batchId?: string;
  processId?: number;
  status?: string;
  limit?: number;
  enabled?: boolean;
}) {
  const { enabled = true, ...filterParams } = params ?? {};

  return useQuery({
    queryKey: ['system', 'headers', filterParams] as const,
    queryFn: () => getProcessHeaders(filterParams),
    staleTime: 30 * 1000, // Cache for 30 seconds
    enabled,
  });
}

export type { WorkflowConfig, UpdateWorkflowRequest, ProcessInfo, ProcessHeaderInfo };
