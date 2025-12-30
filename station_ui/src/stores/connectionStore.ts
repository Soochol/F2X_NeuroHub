/**
 * Connection state store.
 * Manages WebSocket and backend connection status.
 */

import { create } from 'zustand';

export type WebSocketStatus = 'connecting' | 'connected' | 'disconnected' | 'error';
export type BackendStatus = 'connected' | 'disconnected' | 'error';

interface ConnectionState {
  // State
  websocketStatus: WebSocketStatus;
  backendStatus: BackendStatus;
  lastHeartbeat: Date | null;
  reconnectAttempts: number;
  /** Whether polling fallback is active due to WebSocket disconnection */
  pollingFallbackActive: boolean;

  // Actions
  setWebSocketStatus: (status: WebSocketStatus) => void;
  setBackendStatus: (status: BackendStatus) => void;
  updateHeartbeat: () => void;
  incrementReconnectAttempts: () => void;
  resetReconnectAttempts: () => void;
  setPollingFallbackActive: (active: boolean) => void;
}

export const useConnectionStore = create<ConnectionState>((set) => ({
  // Initial state
  websocketStatus: 'disconnected',
  backendStatus: 'disconnected',
  lastHeartbeat: null,
  reconnectAttempts: 0,
  pollingFallbackActive: false,

  // Actions
  setWebSocketStatus: (status) => set({ websocketStatus: status }),

  setBackendStatus: (status) => set({ backendStatus: status }),

  updateHeartbeat: () => set({ lastHeartbeat: new Date() }),

  incrementReconnectAttempts: () =>
    set((state) => ({ reconnectAttempts: state.reconnectAttempts + 1 })),

  resetReconnectAttempts: () => set({ reconnectAttempts: 0 }),

  setPollingFallbackActive: (active) => set({ pollingFallbackActive: active }),
}));
