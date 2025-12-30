/**
 * Hardware type definitions.
 */

/**
 * Hardware connection status.
 */
export type HardwareConnectionStatus = 'connected' | 'disconnected' | 'error';

/**
 * Hardware device status.
 */
export interface HardwareStatus {
  /** Hardware ID (e.g., "dmm") */
  id: string;
  /** Driver name (e.g., "KeysightDMM") */
  driver: string;
  /** Connection status */
  status: HardwareConnectionStatus;
  /** Whether connected */
  connected: boolean;
  /** Last error message */
  lastError?: string;
  /** Applied configuration */
  config: Record<string, unknown>;
  /** Device info (IDN, etc.) */
  info?: Record<string, unknown>;
}
