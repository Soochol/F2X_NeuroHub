/**
 * Operator session React Query hooks.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '../api/queryClient';
import {
  getOperatorSession,
  operatorLogin,
  operatorLogout,
  type OperatorSession,
  type OperatorLoginRequest,
} from '../api/endpoints/system';

/**
 * Hook to fetch current operator session.
 */
export function useOperatorSession() {
  return useQuery({
    queryKey: queryKeys.operatorSession,
    queryFn: getOperatorSession,
    // Refetch on window focus to stay in sync
    refetchOnWindowFocus: true,
    // Don't retry on 401 (not logged in is not an error)
    retry: false,
  });
}

/**
 * Hook to login operator.
 */
export function useOperatorLogin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: OperatorLoginRequest) => operatorLogin(data),
    onSuccess: (data) => {
      // Update the cache with the new session
      queryClient.setQueryData(queryKeys.operatorSession, data);
    },
  });
}

/**
 * Hook to logout operator.
 */
export function useOperatorLogout() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => operatorLogout(),
    onSuccess: (data) => {
      // Update the cache with the empty session
      queryClient.setQueryData(queryKeys.operatorSession, data);
    },
  });
}

export type { OperatorSession, OperatorLoginRequest };
