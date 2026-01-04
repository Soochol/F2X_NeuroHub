/**
 * Station type definitions.
 */

/**
 * Station status.
 */
export type StationStatus = 'online' | 'offline';

/**
 * Represents a test station.
 */
export interface Station {
  /** Station ID (e.g., "ST-001") */
  id: string;
  /** Station name (e.g., "Station 1") */
  name: string;
  /** Station description */
  description?: string;
  /** Station software version */
  version: string;
  /** Current status */
  status: StationStatus;
  /** Whether connected to backend */
  backendConnected: boolean;
  /** Uptime in seconds */
  uptime: number;
}

/**
 * System information response.
 */
export interface SystemInfo {
  stationId: string;
  stationName: string;
  description: string;
  version: string;
  uptime: number;
  backendConnected: boolean;
  /** Directory for sequence packages */
  sequencesDir: string;
  /** Directory for data files (database, logs) */
  dataDir: string;
}

/**
 * Health check response.
 */
export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  batchesRunning: number;
  backendStatus: 'connected' | 'disconnected';
  diskUsage: number;
}
