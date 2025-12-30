/**
 * WebSocket hook for real-time dashboard metrics
 * Connects to /analytics/ws/metrics/live endpoint
 * Falls back to polling when WebSocket is disconnected
 */

import { useEffect, useState, useRef, useCallback } from 'react';
import { dashboardApi } from '@/api';
import type { DashboardSummary } from '@/types/api';
import Logger from '@/utils/logger';

export interface RealtimeMetrics {
  timestamp: string;
  global_success_rate_1h: number;
  active_equipment: string; // "3/5" format
  recent_failures: Array<{
    id: number;
    process: string;
    time: string;
    serial: string;
  }>;
}

export interface UseRealtimeMetricsReturn {
  metrics: RealtimeMetrics | null;
  dashboardData: DashboardSummary | null;
  isConnected: boolean;
  lastUpdate: Date | null;
  error: string | null;
  refetch: () => Promise<void>;
}

const WS_RECONNECT_DELAYS = [1000, 2000, 5000, 10000, 30000]; // Exponential backoff
const POLLING_INTERVAL = 10000; // 10 seconds fallback polling

export function useRealtimeMetrics(): UseRealtimeMetricsReturn {
  const [metrics, setMetrics] = useState<RealtimeMetrics | null>(null);
  const [dashboardData, setDashboardData] = useState<DashboardSummary | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const connectWebSocketRef = useRef<() => void>(() => {});

  // Fetch dashboard data via REST API (fallback or initial load)
  const fetchDashboardData = useCallback(async () => {
    try {
      const data = await dashboardApi.getSummary();
      setDashboardData(data);
      setLastUpdate(new Date());
      setError(null);
    } catch (err) {
      Logger.error('Failed to fetch dashboard data:', err);
      setError('Failed to load dashboard data');
    }
  }, []);

  // WebSocket connection
  const connectWebSocket = useCallback(() => {
    // Clean up existing connection
    if (wsRef.current) {
      wsRef.current.close();
    }

    try {
      // Construct WebSocket URL
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host;
      const wsUrl = `${protocol}//${host}/api/v1/analytics/ws/metrics/live`;

      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        Logger.log('WebSocket connected');
        setIsConnected(true);
        setError(null);
        reconnectAttemptRef.current = 0;

        // Clear polling when connected
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
        }
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as RealtimeMetrics;
          setMetrics(data);
          setLastUpdate(new Date());
        } catch (err) {
          Logger.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.onerror = (event) => {
        Logger.error('WebSocket error:', event);
        setError('WebSocket connection error');
      };

      ws.onclose = (event) => {
        Logger.log('WebSocket closed:', event.code, event.reason);
        setIsConnected(false);
        wsRef.current = null;

        // Start polling as fallback
        if (!pollingIntervalRef.current) {
          pollingIntervalRef.current = setInterval(fetchDashboardData, POLLING_INTERVAL);
        }

        // Attempt reconnection with exponential backoff
        const delay = WS_RECONNECT_DELAYS[
          Math.min(reconnectAttemptRef.current, WS_RECONNECT_DELAYS.length - 1)
        ];
        reconnectAttemptRef.current++;

        reconnectTimeoutRef.current = setTimeout(() => {
          Logger.log(`Attempting WebSocket reconnection (attempt ${reconnectAttemptRef.current})`);
          connectWebSocketRef.current();
        }, delay);
      };
    } catch (err) {
      Logger.error('Failed to create WebSocket:', err);
      setError('Failed to connect to real-time updates');

      // Fall back to polling
      if (!pollingIntervalRef.current) {
        pollingIntervalRef.current = setInterval(fetchDashboardData, POLLING_INTERVAL);
      }
    }
  }, [fetchDashboardData]);

  // Update the ref whenever connectWebSocket changes
  useEffect(() => {
    connectWebSocketRef.current = connectWebSocket;
  }, [connectWebSocket]);

  // Manual refetch
  const refetch = useCallback(async () => {
    await fetchDashboardData();
  }, [fetchDashboardData]);

  // Initial setup - fetch data and establish WebSocket connection
  // This is intentional initialization, not a state sync anti-pattern
  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    // Fetch initial data
    fetchDashboardData();

    // Try WebSocket connection
    connectWebSocket();

    // Cleanup
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, [connectWebSocket, fetchDashboardData]);
  /* eslint-enable react-hooks/set-state-in-effect */

  return {
    metrics,
    dashboardData,
    isConnected,
    lastUpdate,
    error,
    refetch,
  };
}
