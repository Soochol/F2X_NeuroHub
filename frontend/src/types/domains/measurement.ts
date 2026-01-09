/**
 * Measurement Types - Measurement history and analysis
 */

import { ProcessResult } from './enums';

// ============================================================================
// Measurement History
// ============================================================================

export interface MeasurementSpec {
  min?: number;
  max?: number;
  target?: number;
}

export interface MeasurementHistoryItem {
  code: string;
  name: string;
  value: number;
  unit?: string;
  spec?: MeasurementSpec;
  result: string;
}

export interface MeasurementHistory {
  id: number;
  lot_number: string;
  wip_id?: string;
  serial_number?: string;
  process_name: string;
  process_number: number;
  result: ProcessResult;
  operator_name: string;
  measurements: MeasurementHistoryItem[];
  started_at: string;
  completed_at?: string;
  duration_seconds?: number;
}

// ============================================================================
// Filters and Responses
// ============================================================================

export interface MeasurementHistoryFilters {
  start_date?: string;
  end_date?: string;
  process_id?: number;
  lot_id?: number;
  process_session_id?: number;
  result?: ProcessResult;
  skip?: number;
  limit?: number;
}

export interface MeasurementHistoryListResponse {
  items: MeasurementHistory[];
  total: number;
  skip: number;
  limit: number;
}

// ============================================================================
// Summary
// ============================================================================

export interface ProcessMeasurementSummary {
  process_id: number;
  process_name: string;
  total: number;
  fail: number;
  rate: number;
}

export interface MeasurementSummaryResponse {
  total_count: number;
  pass_count: number;
  fail_count: number;
  rework_count: number;
  pass_rate: number;
  by_process: ProcessMeasurementSummary[];
}

// ============================================================================
// Measurement Codes
// ============================================================================

export interface MeasurementCodeInfo {
  code: string;
  name: string;
  unit?: string;
  count: number;
  process_ids: number[];
}

export interface MeasurementCodesResponse {
  codes: MeasurementCodeInfo[];
  total_codes: number;
}
