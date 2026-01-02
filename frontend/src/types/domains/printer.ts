/**
 * Printer Types - Printer monitoring and print logging
 */

import type { BaseQueryParams } from './common';

// ============================================================================
// Printer Status
// ============================================================================

export interface PrinterStatus {
  online: boolean;
  ip: string;
  port: number;
  response_time_ms?: number;
  error?: string;
  last_check: string;
}

// ============================================================================
// Print Log
// ============================================================================

export interface PrintLog {
  id: number;
  label_type: string;
  label_id: string;
  process_id?: number;
  process_data_id?: number;
  printer_ip?: string;
  printer_port?: number;
  status: 'SUCCESS' | 'FAILED';
  error_message?: string;
  operator_id?: number;
  created_at: string;
}

// ============================================================================
// Print Statistics
// ============================================================================

export interface PrintStatistics {
  total_prints: number;
  success_count: number;
  failed_count: number;
  success_rate: number;
  today_prints: number;
  by_label_type: Record<string, number>;
  recent_failures: Array<{
    label_id: string;
    label_type: string;
    error?: string;
    time: string;
  }>;
  date_range: {
    start: string;
    end: string;
  };
}

// ============================================================================
// Query Parameters
// ============================================================================

export interface PrintLogQueryParams extends BaseQueryParams {
  label_type?: string;
  status?: string;
  start_date?: string;
  end_date?: string;
}

export interface PrintLogsResponse {
  total: number;
  logs: PrintLog[];
}
