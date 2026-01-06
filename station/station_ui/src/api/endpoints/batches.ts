/**
 * Batches API endpoints.
 */

import type {
  ApiResponse,
  Batch,
  BatchDetail,
  BatchStartResponse,
  BatchStopResponse,
  BatchStatistics,
  SequenceStartRequest,
  SequenceStartResponse,
  ManualControlRequest,
  ManualControlResponse,
  CreateBatchRequest,
  CreateBatchResponse,
  UpdateBatchConfigRequest,
} from '../../types';
import apiClient, { extractData } from '../client';

/**
 * Get all batches.
 */
export async function getBatches(): Promise<Batch[]> {
  const response = await apiClient.get<ApiResponse<Batch[]>>('/batches');
  return extractData(response);
}

/**
 * API response shape for batch details (differs from BatchDetail interface).
 */
interface BatchDetailApiResponse {
  id: string;
  name: string;
  status: string;
  config?: Record<string, unknown>;
  processId?: number;
  headerId?: number;
  sequence?: {
    name?: string;
    version?: string;
    packagePath?: string;
  };
  parameters?: Record<string, unknown>;
  hardware?: Record<string, {
    name?: string;
    type?: string;
    status?: string;
    configured?: boolean;
    connected?: boolean;
    driver?: string;
    port?: string;
    ip?: string;
    details?: Record<string, unknown>;
  }>;
  execution?: {
    status?: string;
    currentStep?: string;
    stepIndex?: number;
    totalSteps?: number;
    progress?: number;
    startedAt?: string;
    elapsed?: number;
    steps?: Array<{
      order: number;
      name: string;
      status: string;
      pass: boolean;
      duration?: number;
      result?: Record<string, unknown>;
    }>;
    /** All step names from manifest (for displaying skipped steps) */
    stepNames?: string[];
  };
}

/**
 * Get batch details by ID.
 */
export async function getBatch(batchId: string): Promise<BatchDetail> {
  const response = await apiClient.get<ApiResponse<BatchDetailApiResponse>>(`/batches/${batchId}`);
  const data = extractData(response);

  // Transform hardware from API format to HardwareStatus format
  // Note: The global interceptor transforms keys to camelCase, but hardware IDs
  // should remain as snake_case. We convert them back here.
  const hardwareStatus: Record<string, {
    id: string;
    driver: string;
    status: 'connected' | 'disconnected' | 'error';
    connected: boolean;
    lastError?: string;
    config: Record<string, unknown>;
    info?: Record<string, unknown>;
  }> = {};

  if (data.hardware) {
    for (const [hwId, hw] of Object.entries(data.hardware)) {
      // Hardware IDs are preserved as-is (server returns snake_case IDs directly)
      hardwareStatus[hwId] = {
        id: hwId,
        driver: hw.driver || hw.type || 'unknown',
        status: hw.connected ? 'connected' : 'disconnected',
        connected: hw.connected || false,
        config: hw.details || {},
      };
    }
  }

  // Transform steps to StepResult format
  const steps = (data.execution?.steps || []).map((step, index) => ({
    name: step.name,
    order: step.order ?? index + 1,  // Use index if order not provided
    status: step.status as 'pending' | 'running' | 'completed' | 'failed' | 'skipped',
    // Determine pass based on status and pass field
    pass: step.pass ?? (step.status === 'completed'),
    duration: step.duration,
    result: step.result,
  }));

  // Use step names from API (manifest) - includes all steps even if skipped
  // Fall back to extracting from executed steps if API doesn't provide stepNames
  const stepNames = data.execution?.stepNames || steps.map((step) => step.name);

  // Transform API response to match BatchDetail interface
  return {
    id: data.id,
    name: data.name,
    status: data.status as BatchDetail['status'],
    sequenceName: data.sequence?.name || '',
    sequenceVersion: data.sequence?.version || '',
    sequencePackage: data.sequence?.packagePath || '',
    currentStep: data.execution?.currentStep,
    stepIndex: data.execution?.stepIndex || 0,
    // Prefer stepNames length (from manifest) for accurate total, fall back to API totalSteps or executed steps
    totalSteps: stepNames.length || data.execution?.totalSteps || steps.length,
    stepNames,
    progress: data.execution?.progress || 0,
    startedAt: undefined,
    elapsed: data.execution?.elapsed || 0,
    hardwareConfig: {},
    autoStart: false,
    parameters: data.parameters || {},
    config: data.config || {},
    hardwareStatus,
    processId: data.processId,
    headerId: data.headerId,
    execution: data.execution ? {
      // Map API status to ExecutionStatus ('running' | 'completed' | 'failed' | 'stopped')
      status: (() => {
        const s = data.execution?.status || 'stopped';
        if (s === 'idle' || s === 'paused') return 'stopped' as const;
        if (s === 'running' || s === 'completed' || s === 'failed' || s === 'stopped') return s as 'running' | 'completed' | 'failed' | 'stopped';
        return 'stopped' as const;
      })(),
      currentStep: data.execution.currentStep,
      stepIndex: data.execution.stepIndex || 0,
      totalSteps: data.execution.totalSteps || 0,
      progress: data.execution.progress || 0,
      startedAt: data.execution.startedAt ? new Date(data.execution.startedAt) : undefined,
      elapsed: data.execution.elapsed || 0,
      steps,
    } : undefined,
  };
}

/**
 * Start a batch process.
 */
export async function startBatch(batchId: string): Promise<BatchStartResponse> {
  const response = await apiClient.post<ApiResponse<BatchStartResponse>>(
    `/batches/${batchId}/start`
  );
  return extractData(response);
}

/**
 * Stop a batch process.
 */
export async function stopBatch(batchId: string): Promise<BatchStopResponse> {
  const response = await apiClient.post<ApiResponse<BatchStopResponse>>(
    `/batches/${batchId}/stop`
  );
  return extractData(response);
}

/**
 * Delete a batch.
 */
export async function deleteBatch(batchId: string): Promise<{ batchId: string; status: string }> {
  const response = await apiClient.delete<ApiResponse<{ batchId: string; status: string }>>(
    `/batches/${batchId}`
  );
  return extractData(response);
}

/**
 * Start sequence execution for a batch.
 */
export async function startSequence(
  batchId: string,
  request?: SequenceStartRequest
): Promise<SequenceStartResponse> {
  const response = await apiClient.post<ApiResponse<SequenceStartResponse>>(
    `/batches/${batchId}/sequence/start`,
    request
  );
  return extractData(response);
}

/**
 * Stop sequence execution for a batch.
 */
export async function stopSequence(batchId: string): Promise<{ status: string }> {
  const response = await apiClient.post<ApiResponse<{ status: string }>>(
    `/batches/${batchId}/sequence/stop`
  );
  return extractData(response);
}

/**
 * Execute manual hardware control command.
 */
export async function manualControl(
  batchId: string,
  request: ManualControlRequest
): Promise<ManualControlResponse> {
  const response = await apiClient.post<ApiResponse<ManualControlResponse>>(
    `/batches/${batchId}/manual`,
    request
  );
  return extractData(response);
}

/**
 * Server-side batch creation request schema.
 */
interface ServerBatchCreateRequest {
  id: string;
  name: string;
  sequence_package: string;
  hardware?: Record<string, Record<string, unknown>>;
  auto_start?: boolean;
  process_id?: number;
  parameters?: Record<string, unknown>;
}

/**
 * Server-side batch creation response schema.
 */
interface ServerBatchCreateResponse {
  batch_id: string;
  name: string;
  status: string;
}

/**
 * Create new batches with configuration.
 * Requires server connection - throws error if API is unavailable.
 * Transforms client request format to server format and creates batches one by one.
 */
export async function createBatches(
  request: CreateBatchRequest
): Promise<CreateBatchResponse> {
  const batchIds: string[] = [];
  const timestamp = new Date().toISOString();

  // Create each batch individually
  for (let i = 0; i < request.quantity; i++) {
    const batchId = `batch-${Date.now()}-${Math.random().toString(36).substring(2, 9)}-${i}`;
    const batchName = request.quantity > 1
      ? `${request.sequenceName} #${i + 1}`
      : request.sequenceName;

    // Transform to server schema
    const serverRequest: ServerBatchCreateRequest = {
      id: batchId,
      name: batchName,
      sequence_package: `sequences/${request.sequenceName}`,
      hardware: {},
      auto_start: false,
      parameters: request.parameters,
      process_id: request.processId,
    };

    const response = await apiClient.post<ApiResponse<ServerBatchCreateResponse>>(
      '/batches',
      serverRequest
    );
    const data = extractData(response);
    batchIds.push(data.batch_id);
  }

  return {
    batchIds,
    sequenceName: request.sequenceName,
    createdAt: timestamp,
  };
}

/**
 * Update batch configuration (PATCH).
 */
export async function updateBatchConfig(
  batchId: string,
  request: UpdateBatchConfigRequest
): Promise<BatchDetail> {
  const response = await apiClient.patch<ApiResponse<BatchDetail>>(
    `/batches/${batchId}/config`,
    request
  );
  return extractData(response);
}

/**
 * Update batch request payload (PUT).
 */
export interface UpdateBatchRequest {
  name?: string;
  sequencePackage?: string;
  hardware?: Record<string, Record<string, unknown>>;
  autoStart?: boolean;
  config?: Record<string, unknown>;
  parameters?: Record<string, unknown>;
  /** @deprecated Use config.processId instead */
  processId?: number;
  /** @deprecated Use config.headerId instead */
  headerId?: number;
}

/**
 * Server-side batch update request (snake_case).
 */
interface ServerBatchUpdateRequest {
  name?: string;
  sequence_package?: string;
  hardware?: Record<string, Record<string, unknown>>;
  auto_start?: boolean;
  config?: Record<string, unknown>;
  parameters?: Record<string, unknown>;
  process_id?: number;
  header_id?: number;
}

/**
 * Update batch properties (PUT).
 * Supports updating: name, sequence_package, hardware, auto_start, config, parameters
 */
export async function updateBatch(
  batchId: string,
  request: UpdateBatchRequest
): Promise<{ batchId: string; status: string }> {
  // Transform camelCase to snake_case for server
  const serverRequest: ServerBatchUpdateRequest = {};
  if (request.name !== undefined) serverRequest.name = request.name;
  if (request.sequencePackage !== undefined) serverRequest.sequence_package = request.sequencePackage;
  if (request.hardware !== undefined) serverRequest.hardware = request.hardware;
  if (request.autoStart !== undefined) serverRequest.auto_start = request.autoStart;
  if (request.config !== undefined) serverRequest.config = request.config;
  if (request.parameters !== undefined) serverRequest.parameters = request.parameters;
  // Legacy fields (deprecated)
  if (request.processId !== undefined) serverRequest.process_id = request.processId;
  if (request.headerId !== undefined) serverRequest.header_id = request.headerId;

  const response = await apiClient.put<ApiResponse<{ batchId: string; status: string }>>(
    `/batches/${batchId}`,
    serverRequest
  );
  return extractData(response);
}

/**
 * Get batch statistics.
 */
export async function getBatchStatistics(batchId: string): Promise<BatchStatistics> {
  const response = await apiClient.get<ApiResponse<BatchStatistics>>(
    `/batches/${batchId}/statistics`
  );
  return extractData(response);
}

/**
 * Get all batch statistics.
 *
 * Server returns batch IDs as dictionary keys (snake_case preserved).
 * Field values are camelCase via Pydantic alias_generator.
 */
export async function getAllBatchStatistics(): Promise<Record<string, BatchStatistics>> {
  const response = await apiClient.get<ApiResponse<Record<string, BatchStatistics>>>(
    '/batches/statistics'
  );
  return extractData(response);
}

/**
 * Sync batch configuration to backend (main MES).
 */
export async function syncBatchToBackend(batchId: string): Promise<{ synced: boolean; syncedAt: string }> {
  const response = await apiClient.post<ApiResponse<{ synced: boolean; syncedAt: string }>>(
    `/batches/${batchId}/sync`
  );
  return extractData(response);
}
