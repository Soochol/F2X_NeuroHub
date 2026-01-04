/**
 * Log-related React Query hooks.
 */

import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '../api/queryClient';
import { getLogs, type LogsQueryParams } from '../api/endpoints/logs';

/**
 * Hook to fetch logs with filtering.
 */
export function useLogList(params?: LogsQueryParams) {
  return useQuery({
    queryKey: queryKeys.logs(params as Record<string, unknown> | undefined),
    queryFn: () => getLogs(params),
    enabled: params !== undefined,
  });
}
