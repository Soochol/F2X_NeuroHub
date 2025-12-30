/**
 * WebSocket context for real-time communication with Station Service.
 */

import {
  createContext,
  useEffect,
  useRef,
  useCallback,
  useMemo,
  type ReactNode,
} from 'react';
import { io, Socket } from 'socket.io-client';
import { useConnectionStore } from '../stores/connectionStore';
import { useBatchStore } from '../stores/batchStore';
import { useLogStore } from '../stores/logStore';
import { WEBSOCKET_CONFIG } from '../config';
import type {
  ClientMessage,
  ServerMessage,
  BatchStatusMessage,
  StepStartMessage,
  StepCompleteMessage,
  SequenceCompleteMessage,
  LogMessage,
  ErrorMessage,
} from '../types';

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

export function WebSocketProvider({ children, url = WEBSOCKET_CONFIG.path }: WebSocketProviderProps) {
  const socketRef = useRef<Socket | null>(null);
  const subscribedBatchIds = useRef<Set<string>>(new Set());

  // Use selectors to extract stable action references and avoid infinite loops
  // (extracting with destructuring causes new references on every render)
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

  // Initialize WebSocket connection
  useEffect(() => {
    setWebSocketStatus('connecting');

    const socket = io(url, {
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: Infinity,
      reconnectionDelay: WEBSOCKET_CONFIG.reconnectionDelay,
      reconnectionDelayMax: WEBSOCKET_CONFIG.reconnectionDelayMax,
    });

    socketRef.current = socket;

    socket.on('connect', () => {
      setWebSocketStatus('connected');
      resetReconnectAttempts();
      updateHeartbeat();

      // Re-subscribe to previously subscribed batches
      if (subscribedBatchIds.current.size > 0) {
        socket.emit('message', {
          type: 'subscribe',
          batchIds: Array.from(subscribedBatchIds.current),
        });
      }
    });

    socket.on('disconnect', () => {
      setWebSocketStatus('disconnected');
    });

    socket.on('connect_error', () => {
      setWebSocketStatus('error');
      incrementReconnectAttempts();
    });

    socket.on('message', (data: ServerMessage) => {
      updateHeartbeat();
      handleMessage(data);
    });

    // Handle individual event types as well (for flexibility)
    socket.on('batch_status', (data: BatchStatusMessage['data'] & { batchId: string }) => {
      handleMessage({ type: 'batch_status', batchId: data.batchId, data });
    });

    socket.on('step_start', (data: StepStartMessage['data'] & { batchId: string }) => {
      handleMessage({ type: 'step_start', batchId: data.batchId, data });
    });

    socket.on('step_complete', (data: StepCompleteMessage['data'] & { batchId: string }) => {
      handleMessage({ type: 'step_complete', batchId: data.batchId, data });
    });

    socket.on('sequence_complete', (data: SequenceCompleteMessage['data'] & { batchId: string }) => {
      handleMessage({ type: 'sequence_complete', batchId: data.batchId, data });
    });

    socket.on('log', (data: LogMessage['data'] & { batchId: string }) => {
      handleMessage({ type: 'log', batchId: data.batchId, data });
    });

    socket.on('error', (data: ErrorMessage['data'] & { batchId: string }) => {
      handleMessage({ type: 'error', batchId: data.batchId, data });
    });

    return () => {
      socket.disconnect();
      socketRef.current = null;
    };
  }, [
    url,
    setWebSocketStatus,
    resetReconnectAttempts,
    incrementReconnectAttempts,
    updateHeartbeat,
    handleMessage,
  ]);

  // Subscribe to batch updates
  const subscribe = useCallback((batchIds: string[]) => {
    batchIds.forEach((id) => subscribedBatchIds.current.add(id));

    if (socketRef.current?.connected) {
      socketRef.current.emit('message', {
        type: 'subscribe',
        batchIds,
      });
    }
  }, []);

  // Unsubscribe from batch updates
  const unsubscribe = useCallback((batchIds: string[]) => {
    batchIds.forEach((id) => subscribedBatchIds.current.delete(id));

    if (socketRef.current?.connected) {
      socketRef.current.emit('message', {
        type: 'unsubscribe',
        batchIds,
      });
    }
  }, []);

  // Send a message
  const send = useCallback((message: ClientMessage) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('message', message);
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
