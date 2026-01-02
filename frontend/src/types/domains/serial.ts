/**
 * Serial Types - Serial number management and tracing
 */

import { SerialStatus } from './enums';
import type { Lot } from './lot';
import type { ProcessHistoryItem } from './process';

// ============================================================================
// Serial Model
// ============================================================================

export interface Serial {
  id: number;
  serial_number: string;
  lot_id: number;
  sequence_in_lot: number;
  lot?: Lot;
  status: SerialStatus;
  rework_count: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

// ============================================================================
// Serial CRUD
// ============================================================================

export interface SerialCreate {
  lot_id: number;
  sequence_in_lot: number;
}

export interface SerialUpdate {
  status?: SerialStatus;
}

// ============================================================================
// Serial Trace
// ============================================================================

export interface SerialTrace {
  serial_number: string;
  lot_number: string;
  status: SerialStatus;
  rework_count: number;
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
    pin_lot?: string;
    hsg_lot?: string;
  };
  total_cycle_time_seconds: number;
}
