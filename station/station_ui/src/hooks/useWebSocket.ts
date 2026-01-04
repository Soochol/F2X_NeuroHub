/**
 * WebSocket hook for accessing the WebSocket context.
 */

import { useContext } from 'react';
import { WebSocketContext, type WebSocketContextValue } from '../contexts/WebSocketContext';

/**
 * Hook to access WebSocket context.
 * @throws Error if used outside of WebSocketProvider
 */
export function useWebSocket(): WebSocketContextValue {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
}
