/**
 * WebSocket context for real-time communication with Station Service.
 * Uses native WebSocket API to connect to FastAPI WebSocket endpoint.
 */

import {
  createContext,
  useEffect,
  useRef,
  useCallback,
  useMemo,
  type ReactNode,
} from 'react';
import { useConnectionStore } from '../stores/connectionStore';
import { useBatchStore } from '../stores/batchStore';
import { useLogStore } from '../stores/logStore';
import { WEBSOCKET_CONFIG } from '../config';
import type { ClientMessage, ServerMessage } from '../types';

/**
 * WebSocket context value interface.
 */
export interface WebSocketContextValue {
  isConnected: boolean;
  subscribe: (batchIds: string[]) => void;
  unsubscribe: (batchIds: string[]) => void;
  send: (message: ClientMessage) => void;
}

/**
 * WebSocket context - exported for useWebSocket hook.
 */
export const WebSocketContext = createContext<WebSocketContextValue | null>(null);

interface WebSocketProviderProps {
  children: ReactNode;
  url?: string;
}

/**
 * Generates a unique ID for log entries.
 * Uses a combination of timestamp and random number to avoid collisions.
 */
function generateLogId(): number {
  return Date.now() * 1000 + Math.floor(Math.random() * 1000);
}

/**
 * Get WebSocket URL based on current location.
 */
function getWebSocketUrl(path: string): string {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.host;
  return `${protocol}//${host}${path}`;
}

/**
 * Convert snake_case keys to camelCase recursively.
 */
function snakeToCamel(str: string): string {
  return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
}

function transformKeys<T>(obj: unknown): T {
  if (obj === null || obj === undefined) {
    return obj as T;
  }

  if (Array.isArray(obj)) {
    return obj.map((item) => transformKeys(item)) as T;
  }

  if (typeof obj === 'object') {
    const transformed: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(obj as Record<string, unknown>)) {
      transformed[snakeToCamel(key)] = transformKeys(value);
    }
    return transformed as T;
  }

  return obj as T;
}

export function WebSocketProvider({ children, url = '/ws' }: WebSocketProviderProps) {
  const socketRef = useRef<WebSocket | null>(null);
  const subscribedBatchIds = useRef<Set<string>>(new Set());
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectAttemptRef = useRef(0);

  // Use selectors to extract stable action references and avoid infinite loops
  const setWebSocketStatus = useConnectionStore((s) => s.setWebSocketStatus);
  const updateHeartbeat = useConnectionStore((s) => s.updateHeartbeat);
  const resetReconnectAttempts = useConnectionStore((s) => s.resetReconnectAttempts);
  const incrementReconnectAttempts = useConnectionStore((s) => s.incrementReconnectAttempts);
  const updateBatchStatus = useBatchStore((s) => s.updateBatchStatus);
  const updateStepProgress = useBatchStore((s) => s.updateStepProgress);
  const addLog = useLogStore((s) => s.addLog);

  // Handle incoming messages with type narrowing
  const handleMessage = useCallback(
    (message: ServerMessage) => {
      switch (message.type) {
        case 'batch_status': {
          updateBatchStatus(message.batchId, message.data.status);
          if (message.data.currentStep !== undefined) {
            updateStepProgress(
              message.batchId,
              message.data.currentStep,
              message.data.stepIndex,
              message.data.progress
            );
          }
          break;
        }

        case 'step_start': {
          updateStepProgress(
            message.batchId,
            message.data.step,
            message.data.index,
            message.data.index / message.data.total
          );
          break;
        }

        case 'step_complete': {
          addLog({
            id: generateLogId(),
            batchId: message.batchId,
            level: message.data.pass ? 'info' : 'warning',
            message: `Step "${message.data.step}" ${message.data.pass ? 'passed' : 'failed'} (${message.data.duration.toFixed(2)}s)`,
            timestamp: new Date(),
          });
          break;
        }

        case 'sequence_complete': {
          updateBatchStatus(message.batchId, 'completed');
          addLog({
            id: generateLogId(),
            batchId: message.batchId,
            level: message.data.overallPass ? 'info' : 'error',
            message: `Sequence ${message.data.overallPass ? 'PASSED' : 'FAILED'} (${message.data.duration.toFixed(2)}s)`,
            timestamp: new Date(),
          });
          break;
        }

        case 'log': {
          addLog({
            id: generateLogId(),
            batchId: message.batchId,
            level: message.data.level,
            message: message.data.message,
            timestamp: new Date(message.data.timestamp),
          });
          break;
        }

        case 'error': {
          addLog({
            id: generateLogId(),
            batchId: message.batchId,
            level: 'error',
            message: `[${message.data.code}] ${message.data.message}${message.data.step ? ` (step: ${message.data.step})` : ''}`,
            timestamp: new Date(message.data.timestamp),
          });
          break;
        }

        case 'subscribed':
        case 'unsubscribed':
          // Acknowledgment received
          break;
      }
    },
    [updateBatchStatus, updateStepProgress, addLog]
  );

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setWebSocketStatus('connecting');

    const wsUrl = getWebSocketUrl(url);
    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      setWebSocketStatus('connected');
      resetReconnectAttempts();
      reconnectAttemptRef.current = 0;
      updateHeartbeat();

      // Re-subscribe to previously subscribed batches
      if (subscribedBatchIds.current.size > 0) {
        const message: ClientMessage = {
          type: 'subscribe',
          batchIds: Array.from(subscribedBatchIds.current),
        };
        socket.send(JSON.stringify(message));
      }
    };

    socket.onmessage = (event) => {
      updateHeartbeat();
      try {
        const rawData = JSON.parse(event.data);
        // Transform snake_case to camelCase
        const data = transformKeys<ServerMessage>(rawData);
        handleMessage(data);
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e);
      }
    };

    socket.onclose = () => {
      setWebSocketStatus('disconnected');
      socketRef.current = null;

      // Reconnect with exponential backoff
      const delay = Math.min(
        WEBSOCKET_CONFIG.reconnectionDelay * Math.pow(2, reconnectAttemptRef.current),
        WEBSOCKET_CONFIG.reconnectionDelayMax
      );
      reconnectAttemptRef.current++;
      incrementReconnectAttempts();

      reconnectTimeoutRef.current = setTimeout(() => {
        connect();
      }, delay);
    };

    socket.onerror = () => {
      setWebSocketStatus('error');
    };

    socketRef.current = socket;
  }, [
    url,
    setWebSocketStatus,
    resetReconnectAttempts,
    incrementReconnectAttempts,
    updateHeartbeat,
    handleMessage,
  ]);

  // Initialize WebSocket connection
  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }
    };
  }, [connect]);

  // Subscribe to batch updates
  const subscribe = useCallback((batchIds: string[]) => {
    batchIds.forEach((id) => subscribedBatchIds.current.add(id));

    if (socketRef.current?.readyState === WebSocket.OPEN) {
      const message: ClientMessage = {
        type: 'subscribe',
        batchIds,
      };
      socketRef.current.send(JSON.stringify(message));
    }
  }, []);

  // Unsubscribe from batch updates
  const unsubscribe = useCallback((batchIds: string[]) => {
    batchIds.forEach((id) => subscribedBatchIds.current.delete(id));

    if (socketRef.current?.readyState === WebSocket.OPEN) {
      const message: ClientMessage = {
        type: 'unsubscribe',
        batchIds,
      };
      socketRef.current.send(JSON.stringify(message));
    }
  }, []);

  // Send a message
  const send = useCallback((message: ClientMessage) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(message));
    }
  }, []);

  const isConnected = useConnectionStore((state) => state.websocketStatus === 'connected');

  // Memoize value to prevent unnecessary re-renders of consumers
  const value = useMemo<WebSocketContextValue>(
    () => ({
      isConnected,
      subscribe,
      unsubscribe,
      send,
    }),
    [isConnected, subscribe, unsubscribe, send]
  );

  return <WebSocketContext.Provider value={value}>{children}</WebSocketContext.Provider>;
}
