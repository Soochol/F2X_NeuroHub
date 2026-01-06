/**
 * Sequences API endpoints.
 *
 * Note: Upload functionality has been moved to Backend.
 * Use pullSequence() to install sequences from Backend.
 */

import type {
  ApiResponse,
  SequenceSummary,
  SequencePackage,
  SequenceUpdateRequest,
  SequenceUpdateResponse,
  SequenceRegistryItem,
  PullResult,
  DeployResponse,
  DeployedSequenceInfo,
  BatchDeploymentInfo,
  SimulationResult,
  SimulationMode,
} from '../../types';
import apiClient, { extractData } from '../client';

// ============================================================================
// Sequence Endpoints
// ============================================================================

/**
 * Get all local (installed) sequences.
 * Uses the registry endpoint and filters to installed sequences.
 */
export async function getSequences(): Promise<SequenceSummary[]> {
  // Get registry and filter to installed sequences
  const registry = await getSequenceRegistry();

  return registry.items
    .filter((item: SequenceRegistryItem) => ['installed_latest', 'update_available', 'local_only'].includes(item.status))
    .map((item: SequenceRegistryItem) => ({
      name: item.name,
      version: item.localVersion || '0.0.0',
      displayName: item.displayName || item.name,
      description: item.description || '',
      path: `sequences/${item.name}`,
    }));
}

/**
 * Get sequence details by name.
 */
export async function getSequence(name: string): Promise<SequencePackage> {
  const response = await apiClient.get<ApiResponse<SequencePackage>>(`/sequences/${name}`);
  return extractData(response);
}

/**
 * Update sequence configuration.
 */
export async function updateSequence(
  name: string,
  request: SequenceUpdateRequest
): Promise<SequenceUpdateResponse> {
  const response = await apiClient.put<ApiResponse<SequenceUpdateResponse>>(
    `/sequences/${name}`,
    request
  );
  return extractData(response);
}

/**
 * Delete a sequence package.
 */
export async function deleteSequence(name: string): Promise<void> {
  await apiClient.delete(`/deploy/local/${name}`);
}

/**
 * Download a sequence package as ZIP.
 */
export async function downloadSequence(name: string): Promise<Blob> {
  const response = await apiClient.get(`/sequences/${name}/download`, {
    responseType: 'blob',
  });
  return response.data;
}

// ============================================================================
// Registry Endpoints (Unified Local + Remote)
// ============================================================================

/**
 * Registry response with optional warnings.
 */
export interface RegistryResponse {
  items: SequenceRegistryItem[];
  warnings?: string[];
}

/**
 * Get unified sequence registry (local + remote).
 *
 * Returns all sequences with their installation status:
 * - installed_latest: Installed and up-to-date
 * - update_available: Installed but newer version on server
 * - not_installed: Available on server, not installed locally
 * - local_only: Installed locally, not on server
 */
export async function getSequenceRegistry(): Promise<RegistryResponse> {
  interface RawRegistryItem {
    name: string;
    display_name?: string;
    description?: string;
    status: SequenceRegistryItem['status'];
    local_version?: string;
    remote_version?: string;
    installed_at?: string;
    remote_updated_at?: string;
    is_active: boolean;
  }

  const response = await apiClient.get<ApiResponse<RawRegistryItem[]>>('/deploy/registry');
  const rawData = extractData(response);
  const warnings = response.data.warnings;

  // Transform snake_case to camelCase
  const items = rawData.map((item) => ({
    name: item.name,
    displayName: item.display_name,
    description: item.description,
    status: item.status,
    localVersion: item.local_version,
    remoteVersion: item.remote_version,
    installedAt: item.installed_at,
    remoteUpdatedAt: item.remote_updated_at,
    isActive: item.is_active,
  }));

  return { items, warnings };
}

/**
 * Pull (install/update) a sequence from Backend.
 *
 * @param name Sequence name
 * @param force Force download even if up-to-date
 */
export async function pullSequence(name: string, force: boolean = false): Promise<PullResult> {
  const response = await apiClient.post<ApiResponse<PullResult>>(
    `/deploy/pull/${name}`,
    { force }
  );
  return extractData(response);
}

/**
 * Sync all sequences from Backend.
 *
 * @param sequenceNames Optional list of specific sequences to sync
 */
export async function syncSequences(sequenceNames?: string[]): Promise<{
  syncedAt: string;
  sequencesChecked: number;
  sequencesUpdated: number;
  sequencesFailed: number;
}> {
  const response = await apiClient.post<ApiResponse<{
    synced_at: string;
    sequences_checked: number;
    sequences_updated: number;
    sequences_failed: number;
  }>>('/deploy/sync', { sequence_names: sequenceNames });

  const data = extractData(response);
  return {
    syncedAt: data.synced_at,
    sequencesChecked: data.sequences_checked,
    sequencesUpdated: data.sequences_updated,
    sequencesFailed: data.sequences_failed,
  };
}

// ============================================================================
// Deploy Endpoints
// ============================================================================

/**
 * Deploy a sequence to a batch.
 */
export async function deploySequence(
  sequenceName: string,
  batchId: string
): Promise<DeployResponse> {
  const response = await apiClient.post<ApiResponse<DeployResponse>>(
    `/deploy/${sequenceName}`,
    null,
    { params: { batch_id: batchId } }
  );
  return extractData(response);
}

/**
 * Get all batch deployments.
 */
export async function getDeployments(): Promise<BatchDeploymentInfo[]> {
  const response = await apiClient.get<ApiResponse<BatchDeploymentInfo[]>>('/deploy');
  return extractData(response);
}

/**
 * Get deployed sequence for a specific batch.
 */
export async function getDeployedSequence(batchId: string): Promise<DeployedSequenceInfo> {
  const response = await apiClient.get<ApiResponse<DeployedSequenceInfo>>(
    `/deploy/batch/${batchId}`
  );
  return extractData(response);
}

// ============================================================================
// Simulation Endpoints
// ============================================================================

/**
 * Run a simulation of a sequence.
 */
export async function runSimulation(
  sequenceName: string,
  mode: SimulationMode,
  parameters?: Record<string, unknown>
): Promise<SimulationResult> {
  const response = await apiClient.post<ApiResponse<SimulationResult>>(
    `/deploy/simulate/${sequenceName}`,
    { mode, parameters }
  );
  return extractData(response);
}

// ============================================================================
// Auto-Sync Endpoints
// ============================================================================

export interface AutoSyncStatus {
  enabled: boolean;
  running: boolean;
  pollInterval: number;
  autoPull: boolean;
  lastCheckAt?: string;
  lastSyncAt?: string;
  updatesAvailable: number;
  lastError?: string;
}

export interface AutoSyncConfig {
  enabled: boolean;
  poll_interval: number;
  auto_pull: boolean;
}

/**
 * Get auto-sync status.
 */
export async function getAutoSyncStatus(): Promise<AutoSyncStatus> {
  interface RawStatus {
    enabled: boolean;
    running: boolean;
    poll_interval: number;
    auto_pull: boolean;
    last_check_at?: string;
    last_sync_at?: string;
    updates_available: number;
    last_error?: string;
  }

  const response = await apiClient.get<ApiResponse<RawStatus>>('/deploy/auto-sync/status');
  const data = extractData(response);

  return {
    enabled: data.enabled,
    running: data.running,
    pollInterval: data.poll_interval,
    autoPull: data.auto_pull,
    lastCheckAt: data.last_check_at,
    lastSyncAt: data.last_sync_at,
    updatesAvailable: data.updates_available,
    lastError: data.last_error,
  };
}

/**
 * Configure auto-sync.
 */
export async function configureAutoSync(config: AutoSyncConfig): Promise<AutoSyncStatus> {
  interface RawStatus {
    enabled: boolean;
    running: boolean;
    poll_interval: number;
    auto_pull: boolean;
    last_check_at?: string;
    last_sync_at?: string;
    updates_available: number;
    last_error?: string;
  }

  const response = await apiClient.post<ApiResponse<RawStatus>>('/deploy/auto-sync/configure', config);
  const data = extractData(response);

  return {
    enabled: data.enabled,
    running: data.running,
    pollInterval: data.poll_interval,
    autoPull: data.auto_pull,
    lastCheckAt: data.last_check_at,
    lastSyncAt: data.last_sync_at,
    updatesAvailable: data.updates_available,
    lastError: data.last_error,
  };
}

/**
 * Trigger manual update check.
 */
export async function triggerAutoSyncCheck(): Promise<AutoSyncStatus> {
  interface RawStatus {
    enabled: boolean;
    running: boolean;
    poll_interval: number;
    auto_pull: boolean;
    last_check_at?: string;
    last_sync_at?: string;
    updates_available: number;
    last_error?: string;
  }

  const response = await apiClient.post<ApiResponse<RawStatus>>('/deploy/auto-sync/check');
  const data = extractData(response);

  return {
    enabled: data.enabled,
    running: data.running,
    pollInterval: data.poll_interval,
    autoPull: data.auto_pull,
    lastCheckAt: data.last_check_at,
    lastSyncAt: data.last_sync_at,
    updatesAvailable: data.updates_available,
    lastError: data.last_error,
  };
}
