/**
 * System-related React Query hooks.
 */

import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '../api/queryClient';
import { getSystemInfo, getHealthStatus } from '../api/endpoints/system';
import { POLLING_INTERVALS } from '../config';

/**
 * Hook to fetch system information.
 */
export function useSystemInfo() {
  return useQuery({
    queryKey: queryKeys.systemInfo,
    queryFn: getSystemInfo,
    staleTime: POLLING_INTERVALS.systemInfo,
  });
}

/**
 * Hook to fetch health status.
 */
export function useHealthStatus() {
  return useQuery({
    queryKey: queryKeys.healthStatus,
    queryFn: getHealthStatus,
    refetchInterval: POLLING_INTERVALS.health,
  });
}
