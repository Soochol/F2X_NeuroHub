/**
 * Manual Control API Endpoints
 *
 * API functions for enhanced manual hardware control.
 */

import apiClient, { extractData } from '../client';
import type {
  ApiResponse,
  HardwareCommandsResponse,
  HardwareDetailedStatus,
  ManualStepInfo,
  CommandPreset,
  CreatePresetRequest,
} from '../../types';

/**
 * Get all hardware devices for a batch.
 */
export async function getBatchHardware(
  batchId: string
): Promise<HardwareDetailedStatus[]> {
  const response = await apiClient.get<ApiResponse<HardwareDetailedStatus[]>>(
    `/manual/batches/${batchId}/hardware`
  );
  return extractData(response);
}

/**
 * Get available commands for a hardware device.
 */
export async function getHardwareCommands(
  batchId: string,
  hardwareId: string
): Promise<HardwareCommandsResponse> {
  const response = await apiClient.get<ApiResponse<HardwareCommandsResponse>>(
    `/manual/batches/${batchId}/hardware/${hardwareId}/commands`
  );
  return extractData(response);
}

/**
 * Get sequence steps for manual execution.
 */
export async function getManualSteps(
  batchId: string
): Promise<ManualStepInfo[]> {
  const response = await apiClient.get<ApiResponse<ManualStepInfo[]>>(
    `/manual/batches/${batchId}/sequence/steps`
  );
  return extractData(response);
}

/**
 * Execute a single step manually.
 */
export async function runManualStep(
  batchId: string,
  stepName: string,
  parameters?: Record<string, unknown>
): Promise<Record<string, unknown>> {
  const response = await apiClient.post<ApiResponse<Record<string, unknown>>>(
    `/manual/batches/${batchId}/sequence/steps/${stepName}/run`,
    parameters ? { parameters } : undefined
  );
  return extractData(response);
}

/**
 * Skip a step in manual mode.
 */
export async function skipManualStep(
  batchId: string,
  stepName: string
): Promise<Record<string, unknown>> {
  const response = await apiClient.post<ApiResponse<Record<string, unknown>>>(
    `/manual/batches/${batchId}/sequence/steps/${stepName}/skip`
  );
  return extractData(response);
}

/**
 * Reset manual sequence execution.
 */
export async function resetManualSequence(
  batchId: string
): Promise<void> {
  await apiClient.post(`/manual/batches/${batchId}/sequence/reset`);
}

/**
 * List all command presets.
 */
export async function listPresets(): Promise<CommandPreset[]> {
  const response = await apiClient.get<ApiResponse<CommandPreset[]>>(
    '/manual/presets'
  );
  return extractData(response);
}

/**
 * Create a command preset.
 */
export async function createPreset(
  request: CreatePresetRequest
): Promise<CommandPreset> {
  const response = await apiClient.post<ApiResponse<CommandPreset>>(
    '/manual/presets',
    request
  );
  return extractData(response);
}

/**
 * Delete a command preset.
 */
export async function deletePreset(presetId: string): Promise<void> {
  await apiClient.delete(`/api/manual/presets/${presetId}`);
}
