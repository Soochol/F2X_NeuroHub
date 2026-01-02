/**
 * Equipment Types - Product models, production lines, and equipment
 */

// ============================================================================
// Product Model
// ============================================================================

export interface ProductModel {
  id: number;
  model_code: string;
  model_name: string;
  category?: string;
  production_cycle_days?: number;
  specifications?: Record<string, unknown>;
  status: 'ACTIVE' | 'INACTIVE' | 'DISCONTINUED';
  created_at: string;
  updated_at: string;
}

// ============================================================================
// Production Line
// ============================================================================

export interface ProductionLine {
  id: number;
  line_code: string;
  line_name: string;
  description?: string;
  cycle_time_sec?: number;
  location?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// Equipment
// ============================================================================

export interface Equipment {
  id: number;
  equipment_code: string;
  equipment_name: string;
  equipment_type: string;
  description?: string;
  process_id?: number;
  production_line_id?: number;
  manufacturer?: string;
  model_number?: string;
  serial_number?: string;
  status: string;
  is_active: boolean;
  last_maintenance_date?: string;
  next_maintenance_date?: string;
  total_operation_hours?: number;
  specifications?: Record<string, unknown>;
  maintenance_schedule?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}
