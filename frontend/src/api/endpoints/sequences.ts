/**
 * Sequences API Endpoints
 *
 * Provides API client for managing test sequences on the Backend.
 */

import apiClient from '../client';

// ============================================================================
// Types
// ============================================================================

export interface Sequence {
  id: number;
  name: string;
  version: string;
  display_name: string | null;
  description: string | null;
  package_size: number;
  process_id: number | null;
  is_active: boolean;
  is_deprecated: boolean;
  created_at: string;
  updated_at: string;
}

export interface SequenceDetail extends Sequence {
  checksum: string;
  hardware: Record<string, unknown> | null;
  parameters: Record<string, unknown> | null;
  steps: Array<Record<string, unknown>> | null;
  uploaded_by: number | null;
}

export interface SequenceUploadResponse {
  id: number;
  name: string;
  version: string;
  display_name: string | null;
  checksum: string;
  package_size: number;
  is_new: boolean;
  previous_version: string | null;
  message: string;
}

export interface GithubUploadRequest {
  url: string;
  change_notes?: string;
}

export interface SequenceUpdate {
  display_name?: string;
  description?: string;
  is_active?: boolean;
  is_deprecated?: boolean;
  process_id?: number | null;
}

export interface SequenceDeployRequest {
  station_id: string;
  batch_id?: string;
  version?: string;
}

export interface SequenceDeployResponse {
  deployment_id: number;
  sequence_name: string;
  version: string;
  station_id: string;
  batch_id: string | null;
  status: string;
  message: string;
}

export interface SequenceListParams {
  is_active?: boolean;
  is_deprecated?: boolean;
  process_id?: number;
  search?: string;
  skip?: number;
  limit?: number;
}

export interface SequenceListResponse {
  items: Sequence[];
  total: number;
  skip: number;
  limit: number;
}

// ============================================================================
// API Client
// ============================================================================

export const sequencesApi = {
  /**
   * Get all sequences
   */
  getSequences: async (params?: SequenceListParams): Promise<SequenceListResponse> => {
    const response = await apiClient.get<SequenceListResponse>('/sequences', { params });
    return response.data;
  },

  /**
   * Get single sequence by name
   */
  getSequence: async (name: string): Promise<SequenceDetail> => {
    const response = await apiClient.get<SequenceDetail>(`/sequences/${name}`);
    return response.data;
  },

  /**
   * Upload sequence ZIP package
   */
  uploadSequence: async (
    file: File,
    force: boolean = false
  ): Promise<SequenceUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post<SequenceUploadResponse>(
      `/sequences/upload?force=${force}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  /**
   * Upload sequence from GitHub URL
   */
  uploadFromGithub: async (request: GithubUploadRequest): Promise<SequenceUploadResponse> => {
    const response = await apiClient.post<SequenceUploadResponse>(
      '/sequences/upload/github',
      request
    );
    return response.data;
  },

  /**
   * Update sequence metadata
   */
  updateSequence: async (name: string, data: SequenceUpdate): Promise<SequenceDetail> => {
    const response = await apiClient.patch<SequenceDetail>(`/sequences/${name}`, data);
    return response.data;
  },

  /**
   * Delete sequence
   */
  deleteSequence: async (name: string): Promise<void> => {
    await apiClient.delete(`/sequences/${name}`);
  },

  /**
   * Deploy sequence to station
   */
  deploySequence: async (
    name: string,
    deployRequest: SequenceDeployRequest
  ): Promise<SequenceDeployResponse> => {
    const response = await apiClient.post<SequenceDeployResponse>(
      `/sequences/${name}/deploy`,
      deployRequest
    );
    return response.data;
  },
};
