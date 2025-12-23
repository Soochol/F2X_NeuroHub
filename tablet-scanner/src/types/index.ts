/**
 * Type definitions for Tablet Scanner App
 */

// Process result enum
export type ProcessResult = 'PASS' | 'FAIL' | 'REWORK';

// WIP Status enum
export type WIPStatus = 'CREATED' | 'IN_PROGRESS' | 'COMPLETED' | 'CONVERTED';

// Process definition
export interface Process {
  id: number;
  process_number: number;
  process_code: string;
  process_name_ko: string;
  process_name_en: string;
}

// WIP Item from trace API
export interface WIPTrace {
  wip_id: string;
  lot_number: string;
  sequence_in_lot: number;
  status: WIPStatus;
  created_at: string;
  completed_at: string | null;
  converted_at: string | null;
  serial_id: number | null;
  lot_info: {
    lot_number: string;
    product_model: string | null;
    production_date: string | null;
    target_quantity: number;
  } | null;
  process_history: ProcessHistoryItem[];
  total_cycle_time_seconds: number;
}

// Process history item
export interface ProcessHistoryItem {
  process_number: number;
  process_code: string;
  process_name: string;
  worker_id: string | null;
  worker_name: string | null;
  start_time: string | null;
  complete_time: string | null;
  cycle_time_seconds: number | null;
  duration_seconds: number | null;
  result: ProcessResult | null;
  measurements: Record<string, unknown>;
  defect_codes: string[];
  defects: string[];
  notes: string | null;
  is_rework: boolean;
}

// Process start request
export interface ProcessStartRequest {
  wip_id: string;
  process_id: string;
  worker_id: string;
  equipment_id?: string;
  line_id?: string;
  start_time?: string;
}

// Process start response
export interface ProcessStartResponse {
  success: boolean;
  message: string;
  wip_id: string;
  process_id: number;
  started_at: string;
}

// Process complete request
export interface ProcessCompleteRequest {
  wip_id: string;
  process_id: string;
  worker_id: string;
  result: ProcessResult;
  measurements?: Record<string, unknown>;
  defect_data?: {
    defect_codes: string[];
    notes?: string;
  };
}

// Process complete response
export interface ProcessCompleteResponse {
  success: boolean;
  message: string;
  wip_id: string;
  process_id: number;
  result: ProcessResult;
  completed_at: string;
}

// Statistics
export interface TodayStatistics {
  started: number;
  completed: number;
  passed: number;
  failed: number;
}

// App Settings stored locally
export interface AppSettings {
  workerId: string;
  workerName: string;
  equipmentId: string;
  lineId: string;
  apiBaseUrl: string;
}

// Scan result
export interface ScanResult {
  wipId: string;
  timestamp: Date;
  action: 'start' | 'complete';
  success: boolean;
  message: string;
  processNumber?: number;
}

// Next process recommendation
export interface NextProcessRecommendation {
  processId: number;
  processNumber: number;
  processName: string;
  reason: string;
}

// Auth
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    username: string;
    full_name: string;
    role: string;
  };
}

export interface User {
  id: number;
  username: string;
  full_name: string;
  role: string;
}
