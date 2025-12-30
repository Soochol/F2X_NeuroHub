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
import { useBatchStore } from '../../stores/batchStore';

/**
 * Get all batches.
 */
export async function getBatches(): Promise<Batch[]> {
  const response = await apiClient.get<ApiResponse<Batch[]>>('/batches');
  return extractData(response);
}

/**
 * Get batch details by ID.
 */
export async function getBatch(batchId: string): Promise<BatchDetail> {
  const response = await apiClient.get<ApiResponse<BatchDetail>>(`/batches/${batchId}`);
  return extractData(response);
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
 * Start sequence execution for a batch.
 * For local batches (when API is unavailable), this runs a simulation.
 */
export async function startSequence(
  batchId: string,
  request?: SequenceStartRequest
): Promise<SequenceStartResponse> {
  // Check if it's a local batch (created when API was unavailable)
  if (batchId.startsWith('local-batch-')) {
    // Run simulation for local batches
    return simulateSequenceStart(batchId, request);
  }

  const response = await apiClient.post<ApiResponse<SequenceStartResponse>>(
    `/batches/${batchId}/sequence/start`,
    request
  );
  return extractData(response);
}

/**
 * Simulate sequence execution for local batches.
 * This provides a demo/testing experience when the API is unavailable.
 */
function simulateSequenceStart(
  batchId: string,
  _request?: SequenceStartRequest
): SequenceStartResponse {
  const { updateBatchStatus, getBatch, setLocalBatchSteps } = useBatchStore.getState();
  const batch = getBatch(batchId);

  if (!batch) {
    throw new Error(`Batch ${batchId} not found`);
  }

  // Update batch status to running
  updateBatchStatus(batchId, 'running');

  // Simulate sequence execution with steps
  const totalSteps = batch.totalSteps || 3;
  const stepNames = batch.stepNames || [];
  let currentStepIndex = 0;

  // Initialize steps array with pending status (use actual step names if available)
  const initialSteps = Array.from({ length: totalSteps }, (_, i) => ({
    order: i + 1,
    name: stepNames[i] || `Step ${i + 1}`,
    status: 'pending' as const,
    pass: false,
    duration: undefined,
    result: undefined,
    startedAt: undefined,
    completedAt: undefined,
  }));
  setLocalBatchSteps(batchId, initialSteps);

  let stepStartTime: number;

  const runStep = () => {
    const {
      getBatch,
      updateBatchStatus,
      setLastRunResult,
      updateStepProgress,
      incrementBatchStats,
      updateLocalBatchStep,
      getLocalBatchSteps,
    } = useBatchStore.getState();
    const currentBatch = getBatch(batchId);

    if (!currentBatch || currentBatch.status !== 'running') {
      return; // Stopped
    }

    const steps = getLocalBatchSteps(batchId);

    // Complete previous step if exists
    if (currentStepIndex > 0) {
      const prevStepIndex = currentStepIndex - 1;
      const prevStep = steps[prevStepIndex];
      if (prevStep && prevStep.status === 'running') {
        const duration = (Date.now() - stepStartTime) / 1000;
        const passed = Math.random() > 0.15; // 85% pass rate per step
        updateLocalBatchStep(batchId, prevStepIndex, {
          ...prevStep,
          status: 'completed',
          pass: passed,
          duration,
          completedAt: new Date(),
        });
      }
    }

    // Check if all steps are done
    if (currentStepIndex >= totalSteps) {
      // Sequence completed - determine overall result
      const finalSteps = getLocalBatchSteps(batchId);
      const allPassed = finalSteps.every((s) => s.pass);
      updateBatchStatus(batchId, 'completed');
      setLastRunResult(batchId, allPassed);
      incrementBatchStats(batchId, allPassed);
      return;
    }

    // Start current step
    stepStartTime = Date.now();
    const currentStep = steps[currentStepIndex];
    if (currentStep) {
      updateLocalBatchStep(batchId, currentStepIndex, {
        ...currentStep,
        status: 'running',
        startedAt: new Date(),
      });
    }

    // Update progress (use actual step name if available)
    const stepName = stepNames[currentStepIndex] || `Step ${currentStepIndex + 1}`;
    updateStepProgress(
      batchId,
      stepName,
      currentStepIndex + 1,
      (currentStepIndex + 1) / totalSteps
    );

    currentStepIndex++;

    // Schedule next step (simulate 1-3 seconds per step)
    setTimeout(runStep, 1000 + Math.random() * 2000);
  };

  // Start the first step after a small delay
  setTimeout(runStep, 300);

  return {
    batchId,
    executionId: `sim-${Date.now()}`,
    status: 'started',
  };
}

/**
 * Stop sequence execution for a batch.
 */
export async function stopSequence(batchId: string): Promise<{ status: string }> {
  // Check if it's a local batch
  if (batchId.startsWith('local-batch-')) {
    const { updateBatchStatus } = useBatchStore.getState();
    updateBatchStatus(batchId, 'idle');
    return { status: 'stopped' };
  }

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
 * Create new batches with configuration.
 * Falls back to local creation if API is unavailable.
 */
export async function createBatches(
  request: CreateBatchRequest
): Promise<CreateBatchResponse> {
  try {
    const response = await apiClient.post<ApiResponse<CreateBatchResponse>>(
      '/batches/create',
      request
    );
    return extractData(response);
  } catch (error) {
    // Fallback: create batches locally when API is unavailable
    console.warn('API unavailable, creating batches locally:', error);
    return createBatchesLocally(request);
  }
}

/**
 * Create batches locally when API is unavailable.
 * Generates batch IDs and stores them in the Zustand store with localStorage persistence.
 */
function createBatchesLocally(request: CreateBatchRequest): CreateBatchResponse {
  const batchIds: string[] = [];
  const timestamp = new Date().toISOString();
  const { addLocalBatch, setLocalBatchStatistics } = useBatchStore.getState();

  for (let i = 0; i < request.quantity; i++) {
    // Generate a unique batch ID
    const id = `local-batch-${Date.now()}-${Math.random().toString(36).substring(2, 9)}-${i}`;
    batchIds.push(id);

    // Extract step names from stepOrder (prefer displayName for UI)
    const stepNames = request.stepOrder
      ?.filter((s) => s.enabled)
      .sort((a, b) => a.order - b.order)
      .map((s) => s.displayName || s.name) ?? [];

    // Add each batch to the local store (persisted to localStorage)
    addLocalBatch({
      id,
      name: `${request.sequenceName} #${i + 1}`,
      status: 'idle',
      sequenceName: request.sequenceName,
      sequencePackage: request.sequenceName,
      currentStep: undefined,
      stepIndex: 0,
      totalSteps: stepNames.length,
      stepNames,
      progress: 0,
      startedAt: undefined,
      elapsed: 0,
      hardwareConfig: {},
      autoStart: false,
    });

    // Initialize statistics (persisted to localStorage)
    setLocalBatchStatistics(id, {
      total: 0,
      pass: 0,
      fail: 0,
      passRate: 0,
    });
  }

  return {
    batchIds,
    sequenceName: request.sequenceName,
    createdAt: timestamp,
  };
}

/**
 * Update batch configuration.
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
