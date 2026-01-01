/**
 * Workflow configuration React Query hooks.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '../api/queryClient';
import {
  getWorkflowConfig,
  updateWorkflowConfig,
  type WorkflowConfig,
  type UpdateWorkflowRequest,
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

export type { WorkflowConfig, UpdateWorkflowRequest };
