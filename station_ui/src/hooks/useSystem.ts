/**
 * System-related React Query hooks.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '../api/queryClient';
import { getSystemInfo, getHealthStatus, updateStationInfo, type UpdateStationInfoRequest } from '../api/endpoints/system';
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

/**
 * Hook to update station information.
 */
export function useUpdateStationInfo() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateStationInfoRequest) => updateStationInfo(data),
    onSuccess: (data) => {
      // Update the cache with the new data
      queryClient.setQueryData(queryKeys.systemInfo, data);
    },
  });
}
