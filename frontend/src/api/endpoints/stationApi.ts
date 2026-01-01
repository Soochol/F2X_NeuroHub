/**
 * Station Service API Endpoints
 *
 * API functions for communicating with Station Service instances
 * and the backend station registry.
 */

import axios, { type AxiosInstance, type AxiosError } from 'axios';
import { apiClient } from '@/api/client';
import type {
  Station,
  StationConfig,
  StationHealth,
  StationSystemInfo,
  BatchSummary,
  BatchDetail,
  BatchStatistics,
  StationApiResponse,
} from '@/types/station';

// Backend station registry response types
interface BackendStation {
  id: number;
  station_id: string;
  station_name: string;
  host: string;
  port: number;
  description: string | null;
  status: 'ONLINE' | 'OFFLINE' | 'DEGRADED';
  health_data: {
    status?: string;
    batches_running?: number;
    backend_status?: string;
    disk_usage?: number;
    uptime?: number;
    version?: string;
  } | null;
  last_seen_at: string | null;
  created_at: string;
  updated_at: string;
}

// Create a separate axios instance for station service (no auth required)
const createStationClient = (baseUrl: string): AxiosInstance => {
  return axios.create({
    baseURL: baseUrl,
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: 10000,
  });
};

// Helper to convert snake_case to camelCase
const snakeToCamel = (str: string): string =>
  str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());

interface TransformKeysOptions {
  /** If true, top-level keys are preserved (useful for ID-keyed dictionaries) */
  preserveTopLevelKeys?: boolean;
}

const transformKeys = <T>(obj: unknown, options?: TransformKeysOptions): T => {
  if (Array.isArray(obj)) {
    return obj.map((item) => transformKeys(item)) as T;
  }
  if (obj !== null && typeof obj === 'object') {
    return Object.entries(obj).reduce((acc, [key, value]) => {
      const newKey = options?.preserveTopLevelKeys ? key : snakeToCamel(key);
      // Child objects always get full transformation (no preserveTopLevelKeys)
      acc[newKey] = transformKeys(value);
      return acc;
    }, {} as Record<string, unknown>) as T;
  }
  return obj as T;
};

/**
 * Station Service API client for a single station
 */
export class StationServiceClient {
  private client: AxiosInstance;
  private baseUrl: string;

  constructor(host: string, port: number) {
    this.baseUrl = `http://${host}:${port}`;
    this.client = createStationClient(this.baseUrl);
  }

  /**
   * Get station system information
   */
  async getSystemInfo(): Promise<StationSystemInfo> {
    const response = await this.client.get<StationApiResponse<StationSystemInfo>>(
      '/api/system/info'
    );
    return transformKeys<StationSystemInfo>(response.data.data);
  }

  /**
   * Get station health status
   */
  async getHealth(): Promise<StationHealth> {
    const response = await this.client.get<StationApiResponse<{
      status: string;
      batches_running: number;
      backend_status: string;
      disk_usage: number;
    }>>('/api/system/health');

    const data = response.data.data;
    return {
      status: data.status as 'healthy' | 'degraded' | 'unhealthy',
      batchesRunning: data.batches_running,
      backendStatus: data.backend_status as 'connected' | 'disconnected',
      diskUsage: data.disk_usage,
      uptime: 0,
      version: '',
    };
  }

  /**
   * Get all batches
   */
  async getBatches(): Promise<BatchSummary[]> {
    const response = await this.client.get<StationApiResponse<BatchSummary[]>>(
      '/api/batches'
    );
    return transformKeys<BatchSummary[]>(response.data.data);
  }

  /**
   * Get batch details
   */
  async getBatch(batchId: string): Promise<BatchDetail> {
    const response = await this.client.get<StationApiResponse<BatchDetail>>(
      `/api/batches/${batchId}`
    );
    return transformKeys<BatchDetail>(response.data.data);
  }

  /**
   * Get batch statistics
   * Note: Batch IDs are used as dictionary keys and must remain as snake_case
   * to match batch.id. We preserve top-level keys while transforming values.
   */
  async getBatchStatistics(): Promise<Record<string, BatchStatistics>> {
    const response = await this.client.get<StationApiResponse<Record<string, BatchStatistics>>>(
      '/api/batches/statistics'
    );
    return transformKeys<Record<string, BatchStatistics>>(response.data.data, {
      preserveTopLevelKeys: true,
    });
  }

  /**
   * Start batch process
   */
  async startBatch(batchId: string): Promise<void> {
    await this.client.post(`/api/batches/${batchId}/start`);
  }

  /**
   * Stop batch process
   */
  async stopBatch(batchId: string): Promise<void> {
    await this.client.post(`/api/batches/${batchId}/stop`);
  }

  /**
   * Start sequence execution on a batch
   */
  async startSequence(batchId: string, parameters?: Record<string, unknown>): Promise<string> {
    const response = await this.client.post<StationApiResponse<{ execution_id: string }>>(
      `/api/batches/${batchId}/sequence/start`,
      { parameters }
    );
    return response.data.data.execution_id;
  }

  /**
   * Stop sequence execution on a batch
   */
  async stopSequence(batchId: string): Promise<void> {
    await this.client.post(`/api/batches/${batchId}/sequence/stop`);
  }

  /**
   * Delete a batch configuration
   */
  async deleteBatch(batchId: string): Promise<void> {
    await this.client.delete(`/api/batches/${batchId}`);
  }

  /**
   * Create a new batch configuration
   */
  async createBatch(batch: {
    id: string;
    name: string;
    sequence_package: string;
    hardware?: Record<string, Record<string, unknown>>;
    auto_start?: boolean;
    process_id?: number;
  }): Promise<{ batch_id: string; name: string; status: string }> {
    const response = await this.client.post<StationApiResponse<{
      batch_id: string;
      name: string;
      status: string;
    }>>('/api/batches', batch);
    return response.data.data;
  }

  /**
   * Check if station is reachable
   */
  async ping(): Promise<boolean> {
    try {
      await this.client.get('/api/system/health', { timeout: 3000 });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get WebSocket URL for this station
   */
  getWebSocketUrl(): string {
    return this.baseUrl.replace('http://', 'ws://').replace('https://', 'wss://') + '/ws';
  }
}

/**
 * Station Monitor API - manages multiple stations
 */
export const stationMonitorApi = {
  /**
   * Fetch status of multiple stations
   */
  fetchStations: async (configs: StationConfig[]): Promise<Station[]> => {
    const fetchPromises = configs.filter(c => c.enabled).map(async (config): Promise<Station> => {
      const client = new StationServiceClient(config.host, config.port);

      try {
        const [systemInfo, health, batches] = await Promise.all([
          client.getSystemInfo(),
          client.getHealth(),
          client.getBatches(),
        ]);

        return {
          id: config.id,
          name: systemInfo.stationName || config.name,
          description: systemInfo.description || config.description,
          host: config.host,
          port: config.port,
          status: 'connected',
          health: {
            ...health,
            uptime: systemInfo.uptime,
            version: systemInfo.version,
          },
          batches,
          lastSeen: new Date().toISOString(),
        };
      } catch (error) {
        const axiosError = error as AxiosError;
        console.warn(`Failed to connect to station ${config.name}:`, axiosError.message);

        return {
          id: config.id,
          name: config.name,
          description: config.description,
          host: config.host,
          port: config.port,
          status: axiosError.code === 'ECONNABORTED' ? 'connecting' : 'disconnected',
        };
      }
    });

    const results = await Promise.allSettled(fetchPromises);

    return results
      .filter((r): r is PromiseFulfilledResult<Station> => r.status === 'fulfilled')
      .map(r => r.value);
  },

  /**
   * Fetch single station status
   */
  fetchStation: async (config: StationConfig): Promise<Station> => {
    const client = new StationServiceClient(config.host, config.port);

    try {
      const [systemInfo, health, batches] = await Promise.all([
        client.getSystemInfo(),
        client.getHealth(),
        client.getBatches(),
      ]);

      return {
        id: config.id,
        name: systemInfo.stationName || config.name,
        description: systemInfo.description || config.description,
        host: config.host,
        port: config.port,
        status: 'connected',
        health: {
          ...health,
          uptime: systemInfo.uptime,
          version: systemInfo.version,
        },
        batches,
        lastSeen: new Date().toISOString(),
      };
    } catch (error) {
      const axiosError = error as AxiosError;
      return {
        id: config.id,
        name: config.name,
        description: config.description,
        host: config.host,
        port: config.port,
        status: axiosError.code === 'ECONNABORTED' ? 'connecting' : 'disconnected',
      };
    }
  },

  /**
   * Create a client for a specific station
   */
  createClient: (host: string, port: number): StationServiceClient => {
    return new StationServiceClient(host, port);
  },
};

/**
 * Station Registry API - fetches registered stations from backend
 *
 * Stations auto-register when they connect to the backend.
 * This API fetches the list of registered stations and enriches
 * them with real-time data from each station service.
 */
export const stationRegistryApi = {
  /**
   * Fetch all registered stations from backend
   */
  fetchRegisteredStations: async (): Promise<BackendStation[]> => {
    const response = await apiClient.get<{ stations: BackendStation[]; total: number }>('/stations/');
    return response.data.stations;
  },

  /**
   * Fetch stations from backend registry and enrich with real-time data
   */
  fetchStationsWithRealtime: async (): Promise<Station[]> => {
    // Get registered stations from backend
    const registeredStations = await stationRegistryApi.fetchRegisteredStations();

    // Enrich each station with real-time data from station service
    const enrichPromises = registeredStations.map(async (backendStation): Promise<Station> => {
      const client = new StationServiceClient(backendStation.host, backendStation.port);

      // Base station from backend registry
      const baseStation: Station = {
        id: backendStation.station_id,
        name: backendStation.station_name,
        description: backendStation.description || undefined,
        host: backendStation.host,
        port: backendStation.port,
        status: backendStation.status === 'ONLINE' ? 'connected' : 'disconnected',
        lastSeen: backendStation.last_seen_at || undefined,
      };

      // If station is offline according to backend, don't try to connect
      if (backendStation.status !== 'ONLINE') {
        // Use cached health data from backend
        if (backendStation.health_data) {
          baseStation.health = {
            status: (backendStation.health_data.status as 'healthy' | 'degraded' | 'unhealthy') || 'unhealthy',
            batchesRunning: backendStation.health_data.batches_running || 0,
            backendStatus: (backendStation.health_data.backend_status as 'connected' | 'disconnected') || 'disconnected',
            diskUsage: backendStation.health_data.disk_usage || 0,
            uptime: backendStation.health_data.uptime || 0,
            version: backendStation.health_data.version || '',
          };
        }
        return baseStation;
      }

      // Try to get real-time data from station service
      try {
        const [systemInfo, health, batches] = await Promise.all([
          client.getSystemInfo(),
          client.getHealth(),
          client.getBatches(),
        ]);

        return {
          ...baseStation,
          name: systemInfo.stationName || baseStation.name,
          status: 'connected',
          health: {
            ...health,
            uptime: systemInfo.uptime,
            version: systemInfo.version,
          },
          batches,
          lastSeen: new Date().toISOString(),
        };
      } catch (error) {
        const axiosError = error as AxiosError;
        console.warn(`Failed to connect to station ${baseStation.name}:`, axiosError.message);

        // Return backend data with updated status
        return {
          ...baseStation,
          status: axiosError.code === 'ECONNABORTED' ? 'connecting' : 'disconnected',
        };
      }
    });

    const results = await Promise.allSettled(enrichPromises);

    return results
      .filter((r): r is PromiseFulfilledResult<Station> => r.status === 'fulfilled')
      .map(r => r.value);
  },

  /**
   * Fetch a single station by ID with real-time data
   */
  fetchStationById: async (stationId: string): Promise<Station | null> => {
    try {
      const response = await apiClient.get<BackendStation>(`/stations/${stationId}`);
      const backendStation = response.data;

      const client = new StationServiceClient(backendStation.host, backendStation.port);

      const baseStation: Station = {
        id: backendStation.station_id,
        name: backendStation.station_name,
        description: backendStation.description || undefined,
        host: backendStation.host,
        port: backendStation.port,
        status: backendStation.status === 'ONLINE' ? 'connected' : 'disconnected',
        lastSeen: backendStation.last_seen_at || undefined,
      };

      if (backendStation.status !== 'ONLINE') {
        if (backendStation.health_data) {
          baseStation.health = {
            status: (backendStation.health_data.status as 'healthy' | 'degraded' | 'unhealthy') || 'unhealthy',
            batchesRunning: backendStation.health_data.batches_running || 0,
            backendStatus: (backendStation.health_data.backend_status as 'connected' | 'disconnected') || 'disconnected',
            diskUsage: backendStation.health_data.disk_usage || 0,
            uptime: backendStation.health_data.uptime || 0,
            version: backendStation.health_data.version || '',
          };
        }
        return baseStation;
      }

      try {
        const [systemInfo, health, batches] = await Promise.all([
          client.getSystemInfo(),
          client.getHealth(),
          client.getBatches(),
        ]);

        return {
          ...baseStation,
          name: systemInfo.stationName || baseStation.name,
          status: 'connected',
          health: {
            ...health,
            uptime: systemInfo.uptime,
            version: systemInfo.version,
          },
          batches,
          lastSeen: new Date().toISOString(),
        };
      } catch {
        return baseStation;
      }
    } catch {
      return null;
    }
  },
};

export default stationMonitorApi;
