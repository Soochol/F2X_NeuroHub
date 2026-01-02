/**
 * Process Types - Manufacturing processes and process data
 */

import { DataLevel, HeaderStatus, ProcessResult } from './enums';
import type { Serial } from './serial';
import type { User } from './user';

// ============================================================================
// Process Model
// ============================================================================

export type ProcessType = 'MANUFACTURING' | 'SERIAL_CONVERSION';

export interface Process {
  id: number;
  process_number: number;
  process_code: string;
  process_name_ko: string;
  process_name_en: string;
  description?: string;
  sort_order: number;
  is_active: boolean;
  estimated_duration_seconds?: number;
  quality_criteria?: Record<string, unknown>;
  auto_print_label: boolean;
  label_template_type?: string | null;
  defect_items?: string[];
  process_type?: ProcessType;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// Process Data
// ============================================================================

export interface ProcessData {
  id: number;
  serial_id: number;
  serial?: Serial;
  process_id: number;
  process?: Process;
  worker_id: number;
  worker?: User;
  result: ProcessResult;
  data_level: DataLevel;
  measurements?: Record<string, any>;
  defect_codes?: string[];
  notes?: string;
  started_at: string;
  completed_at: string;
  cycle_time_seconds: number;
}

export interface ProcessDataCreate {
  serial_id: number;
  process_id: number;
  worker_id: number;
  result: ProcessResult;
  data_level: DataLevel;
  measurements?: Record<string, any>;
  defect_codes?: string[];
  notes?: string;
  started_at: string;
  completed_at: string;
}

// ============================================================================
// Process History
// ============================================================================

export interface ProcessHistoryItem {
  process_number: number;
  process_code: string;
  process_name: string;
  worker_id: string;
  worker_name: string;
  result: ProcessResult | string;
  start_time: string;
  complete_time: string;
  duration_seconds: number | null;
  process_data?: Record<string, any>;
  defects?: string[];
  notes?: string | null;
  equipment_id?: string | null;
  is_rework: boolean;
}

// ============================================================================
// Process Headers
// ============================================================================

export interface ProcessHeaderSummary {
  id: number;
  station_id: string;
  batch_id: string;
  process_id: number;
  status: HeaderStatus;
  total_count: number;
  pass_count: number;
  fail_count: number;
  pass_rate: number;
  opened_at: string;
  closed_at?: string;
  process_name?: string;
  process_code?: string;
}

export interface ProcessHeaderListResponse {
  items: ProcessHeaderSummary[];
  total: number;
  skip: number;
  limit: number;
}

export interface ProcessHeaderFilter {
  station_id?: string;
  batch_id?: string;
  process_id?: number;
  status?: HeaderStatus;
  opened_after?: string;
  opened_before?: string;
  skip?: number;
  limit?: number;
}
