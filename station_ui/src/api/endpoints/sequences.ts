/**
 * Sequences API endpoints.
 */

import type {
  ApiResponse,
  SequenceSummary,
  SequencePackage,
  SequenceUpdateRequest,
  SequenceUpdateResponse,
  ValidationResult,
  SequenceUploadResponse,
  DeployResponse,
  DeployedSequenceInfo,
  BatchDeploymentInfo,
  SimulationResult,
  SimulationMode,
} from '../../types';
import apiClient, { extractData } from '../client';

/**
 * Get all sequences.
 */
export async function getSequences(): Promise<SequenceSummary[]> {
  const response = await apiClient.get<ApiResponse<SequenceSummary[]>>('/sequences');
  return extractData(response);
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
 * Validate a sequence ZIP file without installing it.
 */
export async function validateSequence(file: File): Promise<ValidationResult> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post<ApiResponse<ValidationResult>>(
    '/sequences/validate',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return extractData(response);
}

/**
 * Upload and install a sequence package.
 */
export async function uploadSequence(
  file: File,
  force: boolean = false,
  onProgress?: (progress: number) => void
): Promise<SequenceUploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post<ApiResponse<SequenceUploadResponse>>(
    `/sequences/upload?force=${force}`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        }
      },
    }
  );
  return extractData(response);
}

/**
 * Delete a sequence package.
 */
export async function deleteSequence(name: string): Promise<void> {
  await apiClient.delete(`/sequences/${name}`);
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
