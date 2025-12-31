/**
 * Station Monitor Hooks
 *
 * React Query hooks for station monitoring functionality.
 * Stations are auto-registered when they connect to the backend.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState, useEffect, useCallback, useRef } from 'react';
import { stationMonitorApi, stationRegistryApi, StationServiceClient } from '@/api/endpoints/stationApi';
import type {
  Station,
  StationConfig,
  BatchSummary,
  BatchDetail,
  BatchStatistics,
  StationWebSocketMessage,
} from '@/types/station';

/**
 * Hook to fetch all registered stations from backend with real-time enrichment
 *
 * Stations auto-register when they connect to the backend.
 * This hook fetches registered stations and enriches with real-time data.
 */
export const useRegisteredStations = (refetchInterval = 10000) => {
  return useQuery({
    queryKey: ['registered-stations'],
    queryFn: () => stationRegistryApi.fetchStationsWithRealtime(),
    refetchInterval,
    staleTime: 5000,
  });
};

/**
 * Hook to fetch a single registered station by ID
 */
export const useRegisteredStation = (stationId: string | null, refetchInterval = 5000) => {
  return useQuery({
    queryKey: ['registered-station', stationId],
    queryFn: () => (stationId ? stationRegistryApi.fetchStationById(stationId) : null),
    refetchInterval,
    staleTime: 3000,
    enabled: !!stationId,
  });
};

// Legacy hooks for backward compatibility
// These will be deprecated in favor of useRegisteredStations

/**
 * @deprecated Use useRegisteredStations instead. Stations now auto-register.
 */
export const useStationConfigs = () => {
  // Return empty functions - stations are now managed by backend
  return {
    configs: [] as StationConfig[],
    addStation: () => null,
    updateStation: () => {},
    removeStation: () => {},
    toggleStation: () => {},
  };
};

/**
 * @deprecated Use useRegisteredStations instead
 */
export const useStations = (configs: StationConfig[], refetchInterval = 10000) => {
  return useQuery({
    queryKey: ['stations', configs.map((c) => `${c.host}:${c.port}`)],
    queryFn: () => stationMonitorApi.fetchStations(configs),
    refetchInterval,
    staleTime: 5000,
    enabled: configs.length > 0,
  });
};

/**
 * @deprecated Use useRegisteredStation instead
 */
export const useStation = (config: StationConfig | null, refetchInterval = 5000) => {
  return useQuery({
    queryKey: ['station', config?.id],
    queryFn: () => (config ? stationMonitorApi.fetchStation(config) : null),
    refetchInterval,
    staleTime: 3000,
    enabled: !!config,
  });
};

/**
 * Hook to fetch batches for a station
 */
export const useStationBatches = (
  host: string,
  port: number,
  refetchInterval = 3000
) => {
  const client = useRef(new StationServiceClient(host, port));

  useEffect(() => {
    client.current = new StationServiceClient(host, port);
  }, [host, port]);

  return useQuery({
    queryKey: ['station-batches', host, port],
    queryFn: () => client.current.getBatches(),
    refetchInterval,
    staleTime: 2000,
  });
};

/**
 * Hook to fetch batch statistics for a station
 */
export const useStationBatchStatistics = (host: string, port: number) => {
  const client = useRef(new StationServiceClient(host, port));

  useEffect(() => {
    client.current = new StationServiceClient(host, port);
  }, [host, port]);

  return useQuery({
    queryKey: ['station-batch-statistics', host, port],
    queryFn: () => client.current.getBatchStatistics(),
    refetchInterval: 5000,
    staleTime: 3000,
  });
};

/**
 * Hook to start/stop batches
 */
export const useStationBatchControl = (host: string, port: number) => {
  const queryClient = useQueryClient();
  const client = useRef(new StationServiceClient(host, port));

  useEffect(() => {
    client.current = new StationServiceClient(host, port);
  }, [host, port]);

  const startBatch = useMutation({
    mutationFn: (batchId: string) => client.current.startBatch(batchId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['station-batches', host, port] });
    },
  });

  const stopBatch = useMutation({
    mutationFn: (batchId: string) => client.current.stopBatch(batchId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['station-batches', host, port] });
    },
  });

  const startSequence = useMutation({
    mutationFn: ({
      batchId,
      parameters,
    }: {
      batchId: string;
      parameters?: Record<string, unknown>;
    }) => client.current.startSequence(batchId, parameters),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['station-batches', host, port] });
    },
  });

  const stopSequence = useMutation({
    mutationFn: (batchId: string) => client.current.stopSequence(batchId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['station-batches', host, port] });
    },
  });

  const deleteBatch = useMutation({
    mutationFn: (batchId: string) => client.current.deleteBatch(batchId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['station-batches', host, port] });
    },
  });

  const createBatch = useMutation({
    mutationFn: (batch: {
      id: string;
      name: string;
      sequence_package: string;
      hardware?: Record<string, Record<string, unknown>>;
      auto_start?: boolean;
      process_id?: number;
    }) => client.current.createBatch(batch),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['station-batches', host, port] });
    },
  });

  return {
    startBatch,
    stopBatch,
    startSequence,
    stopSequence,
    deleteBatch,
    createBatch,
  };
};

/**
 * Hook for WebSocket connection to a station
 * Automatically invalidates React Query cache on batch_created/batch_deleted events
 */
export const useStationWebSocket = (
  host: string,
  port: number,
  options: {
    onMessage?: (message: StationWebSocketMessage) => void;
    onConnect?: () => void;
    onDisconnect?: () => void;
    autoReconnect?: boolean;
    batchIds?: string[];
  } = {}
) => {
  const queryClient = useQueryClient();
  const {
    onMessage,
    onConnect,
    onDisconnect,
    autoReconnect = true,
    batchIds = [],
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);

  const connect = useCallback(() => {
    const wsUrl = `ws://${host}:${port}/ws`;

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('[StationWS] Connected to', wsUrl);
        setIsConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0;
        onConnect?.();
        // NOTE: Subscription handled by separate useEffect to avoid dependency issues
      };

      ws.onmessage = (event) => {
        try {
          console.log('[StationWS] Received:', event.data);
          const message = JSON.parse(event.data) as StationWebSocketMessage;

          // Auto-invalidate queries on batch lifecycle events
          if (message.type === 'batch_created' || message.type === 'batch_deleted') {
            queryClient.invalidateQueries({ queryKey: ['station-batches', host, port] });
            queryClient.invalidateQueries({ queryKey: ['registered-stations'] });
          }

          onMessage?.(message);
        } catch (err) {
          console.error('[StationWS] Failed to parse message:', err);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        onDisconnect?.();

        if (autoReconnect) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++;
            connect();
          }, delay);
        }
      };

      ws.onerror = () => {
        setError('WebSocket connection error');
      };
    } catch (err) {
      setError('Failed to create WebSocket connection');
    }
  }, [host, port, onMessage, onConnect, onDisconnect, autoReconnect, queryClient]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const subscribe = useCallback((batchId: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.log('[StationWS] Subscribing to batch:', batchId);
      wsRef.current.send(JSON.stringify({ type: 'subscribe', batch_ids: [batchId] }));
    }
  }, []);

  const unsubscribe = useCallback((batchId: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.log('[StationWS] Unsubscribing from batch:', batchId);
      wsRef.current.send(JSON.stringify({ type: 'unsubscribe', batch_ids: [batchId] }));
    }
  }, []);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  // Subscribe to new batch IDs
  useEffect(() => {
    if (isConnected) {
      batchIds.forEach((batchId) => subscribe(batchId));
    }
  }, [isConnected, batchIds, subscribe]);

  return {
    isConnected,
    error,
    connect,
    disconnect,
    subscribe,
    unsubscribe,
  };
};

export default {
  useStationConfigs,
  useStations,
  useStation,
  useStationBatches,
  useStationBatchStatistics,
  useStationBatchControl,
  useStationWebSocket,
};
