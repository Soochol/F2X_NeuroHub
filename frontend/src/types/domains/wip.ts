/**
 * WIP Types - Work In Progress management and tracing
 */

import { WIPStatus } from './enums';
import type { ProcessHistoryItem } from './process';

// ============================================================================
// WIP Model
// ============================================================================

export interface WIPItem {
  id: number;
  wip_id: string;
  lot_id: number;
  sequence_in_lot: number;
  status: WIPStatus;
  current_process_id?: number;
  serial_id?: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  converted_at?: string;
}

// ============================================================================
// WIP Trace
// ============================================================================

export interface WipTrace {
  wip_id: string;
  lot_number: string;
  status: string;
  created_at: string;
  completed_at?: string;
  converted_at?: string;
  serial_id?: number;
  lot_info: {
    lot_number: string;
    product_model: string;
    production_date: string;
    target_quantity: number;
  };
  process_history: ProcessHistoryItem[];
  rework_history: ProcessHistoryItem[];
  component_lots: {
    busbar_lot?: string;
    sma_spring_lot?: string;
    [key: string]: string | undefined;
  };
  total_cycle_time_seconds: number;
}
