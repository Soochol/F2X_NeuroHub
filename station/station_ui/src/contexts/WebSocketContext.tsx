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
import { useQueryClient } from '@tanstack/react-query';
import { useConnectionStore } from '../stores/connectionStore';
import { useBatchStore } from '../stores/batchStore';
import { useLogStore } from '../stores/logStore';
import { useNotificationStore } from '../stores/notificationStore';
import { WEBSOCKET_CONFIG } from '../config';
import { queryKeys } from '../api/queryClient';
import { transformKeys } from '../utils/transform';
import { toast } from '../utils/toast';
import { wsLogger as log } from '../utils';
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

export function WebSocketProvider({ children, url = '/ws' }: WebSocketProviderProps) {
  const queryClient = useQueryClient();
  const socketRef = useRef<WebSocket | null>(null);
  // Use reference counting for subscriptions to handle overlapping subscriptions from different components
  // This prevents issues when navigating between pages where cleanup runs after the new page's effect
  const subscriptionRefCount = useRef<Map<string, number>>(new Map());
  // Track batches that just subscribed - initial status push should bypass guards
  const justSubscribedBatches = useRef<Set<string>>(new Set());
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectAttemptRef = useRef(0);

  // Use selectors to extract stable action references and avoid infinite loops
  const setWebSocketStatus = useConnectionStore((s) => s.setWebSocketStatus);
  const updateHeartbeat = useConnectionStore((s) => s.updateHeartbeat);
  const resetReconnectAttempts = useConnectionStore((s) => s.resetReconnectAttempts);
  const incrementReconnectAttempts = useConnectionStore((s) => s.incrementReconnectAttempts);
  const updateBatchStatus = useBatchStore((s) => s.updateBatchStatus);
  const updateStepProgress = useBatchStore((s) => s.updateStepProgress);
  const setLastRunResult = useBatchStore((s) => s.setLastRunResult);
  const incrementBatchStats = useBatchStore((s) => s.incrementBatchStats);
  const startStep = useBatchStore((s) => s.startStep);
  const completeStep = useBatchStore((s) => s.completeStep);
  const clearSteps = useBatchStore((s) => s.clearSteps);
  const addLog = useLogStore((s) => s.addLog);
  const addNotification = useNotificationStore((s) => s.addNotification);

  // Handle incoming messages with type narrowing
  const handleMessage = useCallback(
    (message: ServerMessage) => {
      const batchIdForLog = 'batchId' in message ? log.truncateId(message.batchId as string) : null;
      log.debug(`Received: ${message.type}`, batchIdForLog ? `batch: ${batchIdForLog}` : '');
      switch (message.type) {
        case 'batch_status': {
          // Check if this is an initial status push after subscription (should bypass guards)
          const isInitialPush = justSubscribedBatches.current.has(message.batchId);
          if (isInitialPush) {
            justSubscribedBatches.current.delete(message.batchId);
          }
          log.debug(`batch_status: status=${message.data.status}, step=${message.data.currentStep}, progress=${message.data.progress}, exec=${message.data.executionId}, lastRunPassed=${message.data.lastRunPassed}, initial=${isInitialPush}`);
          // Clear steps when starting a new execution (status changes to 'running' with new executionId)
          if (message.data.status === 'running' && message.data.progress === 0) {
            clearSteps(message.batchId);
          }
          // Use force=true for initial push to bypass guards (authoritative server state after subscribe)
          updateBatchStatus(message.batchId, message.data.status, message.data.executionId, undefined, isInitialPush);
          if (message.data.currentStep !== undefined) {
            updateStepProgress(
              message.batchId,
              message.data.currentStep,
              message.data.stepIndex,
              message.data.progress,
              message.data.executionId
            );
          }
          // Update lastRunPassed from initial push (authoritative server state)
          if (isInitialPush && message.data.lastRunPassed !== undefined && message.data.lastRunPassed !== null) {
            setLastRunResult(message.batchId, message.data.lastRunPassed);
          }
          break;
        }

        case 'step_start': {
          log.debug(`step_start: step=${message.data.step}, index=${message.data.index}/${message.data.total}, exec=${message.data.executionId}, hasStepNames=${!!message.data.stepNames}`);
          // Update step tracking in store
          // stepNames is sent on first step only (for UI to display skipped steps)
          startStep(
            message.batchId,
            message.data.step,
            message.data.index,
            message.data.total,
            message.data.executionId,
            message.data.stepNames
          );
          // Also update batch status
          updateBatchStatus(message.batchId, 'running', message.data.executionId);
          break;
        }

        case 'step_complete': {
          log.debug(`step_complete: step=${message.data.step}, index=${message.data.index}, pass=${message.data.pass}, duration=${message.data.duration}`);
          // Update step in store
          completeStep(
            message.batchId,
            message.data.step,
            message.data.index,
            message.data.duration,
            message.data.pass,
            message.data.result,
            message.data.executionId
          );
          addLog({
            id: generateLogId(),
            batchId: message.batchId,
            level: message.data.pass ? 'info' : 'warning',
            message: `Step "${message.data.step}" ${message.data.pass ? 'passed' : 'failed'} (${message.data.duration.toFixed(2)}s)`,
            timestamp: new Date(),
          });
          // Add notification for failed steps
          if (!message.data.pass) {
            addNotification({
              type: 'warning',
              title: 'Step Failed',
              message: `Step "${message.data.step}" failed in batch ${message.batchId.slice(0, 8)}...`,
              batchId: message.batchId,
            });
          }
          break;
        }

        case 'sequence_complete': {
          // Pass executionId and duration (as elapsed) to updateBatchStatus
          updateBatchStatus(message.batchId, 'completed', message.data.executionId, message.data.duration);
          setLastRunResult(message.batchId, message.data.overallPass);
          incrementBatchStats(message.batchId, message.data.overallPass);
          addLog({
            id: generateLogId(),
            batchId: message.batchId,
            level: message.data.overallPass ? 'info' : 'error',
            message: `Sequence ${message.data.overallPass ? 'PASSED' : 'FAILED'} (${message.data.duration.toFixed(2)}s)`,
            timestamp: new Date(),
          });
          // Add notification for sequence completion
          addNotification({
            type: message.data.overallPass ? 'success' : 'error',
            title: message.data.overallPass ? 'Sequence Passed' : 'Sequence Failed',
            message: `Batch ${message.batchId.slice(0, 8)}... completed ${message.data.overallPass ? 'successfully' : 'with errors'} in ${message.data.duration.toFixed(2)}s`,
            batchId: message.batchId,
          });
          // Invalidate statistics cache to refetch from API (DB now has updated stats)
          queryClient.invalidateQueries({ queryKey: queryKeys.allBatchStatistics });
          queryClient.invalidateQueries({ queryKey: queryKeys.batchStatistics(message.batchId) });
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
          const code = message.data?.code || 'UNKNOWN';
          const errorMessage = message.data?.message || 'Unknown error';
          const step = message.data?.step;
          const timestamp = message.data?.timestamp;

          log.debug(`error: code=${code}, message=${errorMessage}, step=${step}`);

          // Immediate toast notification (same as 착공 error)
          toast.error(`[${code}] ${errorMessage}`);

          // Log for debug panel
          addLog({
            id: generateLogId(),
            batchId: message.batchId,
            level: 'error',
            message: `[${code}] ${errorMessage}${step ? ` (step: ${step})` : ''}`,
            timestamp: timestamp ? new Date(timestamp) : new Date(),
          });
          // Notification for history
          addNotification({
            type: 'error',
            title: `Error: ${code}`,
            message: errorMessage,
            batchId: message.batchId,
          });
          break;
        }

        case 'subscribed': {
          // Record batch IDs that just subscribed - next batch_status for these should use force mode
          const subscribedBatchIds = message.data?.batchIds || [];
          for (const batchId of subscribedBatchIds) {
            justSubscribedBatches.current.add(batchId);
          }
          log.debug(`subscribed: ${subscribedBatchIds.length} batches marked for initial push`);
          break;
        }
        case 'unsubscribed':
          // Acknowledgment received
          break;

        case 'batch_created': {
          // Invalidate batches query to refresh the list
          queryClient.invalidateQueries({ queryKey: queryKeys.batches });
          addNotification({
            type: 'info',
            title: 'Batch Created',
            message: `New batch "${message.data.name}" has been created`,
          });
          break;
        }

        case 'batch_deleted': {
          // Invalidate batches query to refresh the list
          queryClient.invalidateQueries({ queryKey: queryKeys.batches });
          addNotification({
            type: 'info',
            title: 'Batch Deleted',
            message: `Batch has been deleted`,
            batchId: message.batchId,
          });
          break;
        }
      }
    },
    [updateBatchStatus, updateStepProgress, setLastRunResult, incrementBatchStats, startStep, completeStep, clearSteps, addLog, addNotification, queryClient]
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

      // Re-subscribe to previously subscribed batches on reconnect
      const subscribedBatchIds = Array.from(subscriptionRefCount.current.keys());
      if (subscribedBatchIds.length > 0) {
        log.debug(`Re-subscribing on connect:`, subscribedBatchIds.map(id => log.truncateId(id)));
        const message: ClientMessage = {
          type: 'subscribe',
          batchIds: subscribedBatchIds,
        };
        socket.send(JSON.stringify(message));
      } else {
        log.debug('Connected, no batches to re-subscribe');
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
        log.error('Failed to parse/handle WebSocket message:', e, 'raw:', event.data);
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

  // Subscribe to batch updates with reference counting
  // This handles overlapping subscriptions from multiple components
  const subscribe = useCallback((batchIds: string[]) => {
    // Update refCount for tracking (used for unsubscribe logic)
    batchIds.forEach((id) => {
      const currentCount = subscriptionRefCount.current.get(id) || 0;
      subscriptionRefCount.current.set(id, currentCount + 1);
      log.debug(`subscribe: ${log.truncateId(id)} refCount: ${currentCount} -> ${currentCount + 1}`);
    });

    // ALWAYS send subscribe message - server uses Set so duplicates are safe
    // This fixes the bug where initial subscribe fails if WebSocket wasn't ready
    if (batchIds.length > 0 && socketRef.current?.readyState === WebSocket.OPEN) {
      log.debug('Sending subscribe for batches:', batchIds.map(id => log.truncateId(id)));
      const message: ClientMessage = {
        type: 'subscribe',
        batchIds,
      };
      socketRef.current.send(JSON.stringify(message));
    } else if (socketRef.current?.readyState !== WebSocket.OPEN) {
      log.warn(`WebSocket not open (state: ${socketRef.current?.readyState}), subscribe queued for reconnect`);
    }
  }, []);

  // Unsubscribe from batch updates with reference counting
  // Only actually unsubscribes when all subscribers have unsubscribed
  const unsubscribe = useCallback((batchIds: string[]) => {
    const actualUnsubscribes: string[] = [];

    batchIds.forEach((id) => {
      const currentCount = subscriptionRefCount.current.get(id) || 0;
      log.debug(`unsubscribe: ${log.truncateId(id)} refCount: ${currentCount} -> ${currentCount > 0 ? currentCount - 1 : 0}`);
      if (currentCount > 1) {
        // Other components still need this subscription
        subscriptionRefCount.current.set(id, currentCount - 1);
      } else if (currentCount === 1) {
        // Last subscriber - actually unsubscribe
        subscriptionRefCount.current.delete(id);
        actualUnsubscribes.push(id);
      }
      // If currentCount is 0, do nothing (wasn't subscribed)
    });

    // Only send unsubscribe for batches that no longer have any subscribers
    if (actualUnsubscribes.length > 0 && socketRef.current?.readyState === WebSocket.OPEN) {
      log.debug('Sending unsubscribe for:', actualUnsubscribes.map(id => log.truncateId(id)));
      const message: ClientMessage = {
        type: 'unsubscribe',
        batchIds: actualUnsubscribes,
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
