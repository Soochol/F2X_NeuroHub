/**
 * Centralized application configuration.
 */

/**
 * Polling intervals for React Query refetch (in milliseconds).
 */
export const POLLING_INTERVALS = {
  /** Batch list polling interval (normal mode) */
  batches: 10_000, // 10 seconds
  /** Batch list polling interval (fallback mode when WebSocket is disconnected) */
  batchesFallback: 3_000, // 3 seconds - faster polling when WS is down
  /** Batch detail polling interval (for real-time step updates) */
  batchDetail: 1_000, // 1 second - fast polling for step progress
  /** Health status polling interval */
  health: 30_000, // 30 seconds
  /** System info cache time (not polling, just stale time) */
  systemInfo: 60_000, // 1 minute
} as const;

/**
 * React Query default options.
 */
export const QUERY_OPTIONS = {
  /** Default stale time for queries */
  staleTime: 30_000, // 30 seconds
  /** Default garbage collection time */
  gcTime: 5 * 60_000, // 5 minutes
  /** Default retry count for queries */
  queryRetry: 2,
  /** Default retry count for mutations */
  mutationRetry: 1,
} as const;

/**
 * WebSocket configuration.
 */
export const WEBSOCKET_CONFIG = {
  /** WebSocket endpoint path */
  path: '/ws',
  /** Reconnection delay in milliseconds */
  reconnectionDelay: 1000,
  /** Maximum reconnection delay in milliseconds */
  reconnectionDelayMax: 30_000,
} as const;

/**
 * Log configuration.
 */
export const LOG_CONFIG = {
  /** Maximum number of logs to keep in store */
  maxLogs: 1000,
  /** Number of recent logs to show on dashboard */
  dashboardLogCount: 10,
} as const;
