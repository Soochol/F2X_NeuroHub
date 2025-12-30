/**
 * Polling fallback hook for WebSocket disconnection.
 *
 * This hook manages automatic polling fallback when WebSocket connection is lost.
 * It enables faster polling intervals when WS is disconnected to maintain
 * near-real-time updates through REST API polling.
 */

import { useEffect, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useConnectionStore } from '../stores/connectionStore';
import { queryKeys } from '../api/queryClient';
import { POLLING_INTERVALS } from '../config';

/** Delay before activating fallback (to avoid flapping) */
const FALLBACK_ACTIVATION_DELAY = 5000; // 5 seconds

/**
 * Hook that automatically activates polling fallback when WebSocket disconnects.
 *
 * When WebSocket is disconnected:
 * - Activates faster polling interval for batches
 * - Sets pollingFallbackActive flag in connection store
 *
 * When WebSocket reconnects:
 * - Deactivates polling fallback
 * - Invalidates queries to get fresh data
 */
export function usePollingFallback() {
  const queryClient = useQueryClient();
  const websocketStatus = useConnectionStore((s) => s.websocketStatus);
  const pollingFallbackActive = useConnectionStore((s) => s.pollingFallbackActive);
  const setPollingFallbackActive = useConnectionStore((s) => s.setPollingFallbackActive);

  const activationTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const wasConnectedRef = useRef(false);

  useEffect(() => {
    const isConnected = websocketStatus === 'connected';

    // Clear any pending activation timeout
    if (activationTimeoutRef.current) {
      clearTimeout(activationTimeoutRef.current);
      activationTimeoutRef.current = null;
    }

    if (isConnected) {
      // WebSocket connected
      if (pollingFallbackActive) {
        // Deactivate fallback mode
        setPollingFallbackActive(false);

        // Invalidate queries to get fresh data after reconnection
        void queryClient.invalidateQueries({ queryKey: queryKeys.batches });
      }
      wasConnectedRef.current = true;
    } else if (wasConnectedRef.current) {
      // WebSocket disconnected after being connected
      // Wait before activating fallback to avoid flapping
      activationTimeoutRef.current = setTimeout(() => {
        if (!pollingFallbackActive) {
          setPollingFallbackActive(true);
        }
      }, FALLBACK_ACTIVATION_DELAY);
    }

    return () => {
      if (activationTimeoutRef.current) {
        clearTimeout(activationTimeoutRef.current);
      }
    };
  }, [websocketStatus, pollingFallbackActive, setPollingFallbackActive, queryClient]);

  return {
    isActive: pollingFallbackActive,
    pollingInterval: pollingFallbackActive
      ? POLLING_INTERVALS.batchesFallback
      : POLLING_INTERVALS.batches,
  };
}

/**
 * Get the appropriate polling interval based on WebSocket connection status.
 *
 * @param normalInterval - Normal polling interval when WebSocket is connected
 * @param fallbackInterval - Faster polling interval when WebSocket is disconnected
 * @returns The appropriate polling interval
 */
export function useAdaptivePollingInterval(
  normalInterval: number,
  fallbackInterval: number
): number {
  const pollingFallbackActive = useConnectionStore((s) => s.pollingFallbackActive);
  return pollingFallbackActive ? fallbackInterval : normalInterval;
}
