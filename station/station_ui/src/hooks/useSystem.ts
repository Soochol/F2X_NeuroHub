/**
 * System-related React Query hooks.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '../api/queryClient';
import {
  getSystemInfo,
  getHealthStatus,
  updateStationInfo,
  getBackendConfig,
  updateBackendConfig,
  type UpdateStationInfoRequest,
  type UpdateBackendConfigRequest,
} from '../api/endpoints/system';
import { POLLING_INTERVALS } from '../config';
import { toast } from '../utils';

// Note: Error handling is done globally via MutationCache in queryClient.ts

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
      toast.success('스테이션 정보 업데이트 완료');
    },
  });
}

/**
 * Hook to fetch backend configuration.
 */
export function useBackendConfig() {
  return useQuery({
    queryKey: queryKeys.backendConfig,
    queryFn: getBackendConfig,
    staleTime: POLLING_INTERVALS.systemInfo,
  });
}

/**
 * Hook to update backend configuration.
 */
export function useUpdateBackendConfig() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateBackendConfigRequest) => updateBackendConfig(data),
    onSuccess: (data) => {
      // Update the cache with the new data
      queryClient.setQueryData(queryKeys.backendConfig, data);
      toast.success('백엔드 설정 업데이트 완료');
    },
  });
}
