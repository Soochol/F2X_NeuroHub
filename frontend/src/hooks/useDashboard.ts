/**
 * Dashboard Hooks with TanStack Query
 *
 * Provides data fetching and caching for dashboard-related data.
 */

import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '@/api';
import type { LotStatus } from '@/types/api';

/** Query keys for dashboard-related queries */
export const dashboardKeys = {
  all: ['dashboard'] as const,
  summary: (targetDate?: string) => [...dashboardKeys.all, 'summary', targetDate] as const,
  lots: (status?: LotStatus, limit?: number) => [...dashboardKeys.all, 'lots', { status, limit }] as const,
  processWip: () => [...dashboardKeys.all, 'process-wip'] as const,
  cycleTimes: (days?: number) => [...dashboardKeys.all, 'cycle-times', days] as const,
};

/**
 * Fetch dashboard summary with KPIs
 */
export function useDashboardSummary(targetDate?: string) {
  return useQuery({
    queryKey: dashboardKeys.summary(targetDate),
    queryFn: () => dashboardApi.getSummary(targetDate),
    staleTime: 30 * 1000, // 30 seconds - dashboard data should be relatively fresh
    refetchInterval: 60 * 1000, // Auto-refresh every minute
  });
}

/**
 * Fetch dashboard LOTs list
 */
export function useDashboardLots(status?: LotStatus, limit = 20) {
  return useQuery({
    queryKey: dashboardKeys.lots(status, limit),
    queryFn: () => dashboardApi.getLots(status, limit),
    staleTime: 30 * 1000,
  });
}

/**
 * Fetch work-in-progress by process
 */
export function useProcessWip() {
  return useQuery({
    queryKey: dashboardKeys.processWip(),
    queryFn: () => dashboardApi.getProcessWIP(),
    staleTime: 30 * 1000,
    refetchInterval: 30 * 1000, // WIP data changes frequently
  });
}

/**
 * Fetch average cycle times by process
 */
export function useCycleTimes(days = 7) {
  return useQuery({
    queryKey: dashboardKeys.cycleTimes(days),
    queryFn: () => dashboardApi.getCycleTimes(days),
    staleTime: 60 * 1000, // 1 minute - cycle times don't change rapidly
    refetchInterval: 60 * 1000,
  });
}

/**
 * Combined hook for dashboard page data
 * Fetches summary, cycle times, and equipment in parallel
 */
export function useDashboardData(targetDate?: string, cycleTimeDays = 7) {
  const summary = useDashboardSummary(targetDate);
  const cycleTimes = useCycleTimes(cycleTimeDays);

  return {
    summary,
    cycleTimes,
    isLoading: summary.isLoading || cycleTimes.isLoading,
    isError: summary.isError || cycleTimes.isError,
    error: summary.error || cycleTimes.error,
    refetchAll: () => {
      summary.refetch();
      cycleTimes.refetch();
    },
  };
}
