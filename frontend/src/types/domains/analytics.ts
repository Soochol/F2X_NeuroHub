/**
 * Analytics Types - Dashboard and analytics data
 */

import { LotStatus } from './enums';

// ============================================================================
// Dashboard Types
// ============================================================================

export interface DashboardSummary {
  total_started: number;
  total_in_progress: number;
  total_completed: number;
  total_defective: number;
  defect_rate: number;
  lots: Array<{
    lot_number: string;
    product_model_name: string;
    status: LotStatus;
    progress: number;
    started_count: number;
    in_progress_count: number;
    completed_count: number;
    defective_count: number;
    created_at: string;
  }>;
  process_wip: Array<{
    process_name: string;
    wip_count: number;
  }>;
}

export interface DashboardLot {
  lot_number: string;
  product_model_name: string;
  status: LotStatus;
  production_date: string;
  target_quantity: number;
  started_count: number;
  completed_count: number;
  pass_count: number;
  fail_count: number;
  rework_count: number;
  progress: number;
}

export interface ProcessWIP {
  process_id: number;
  process_name: string;
  wip_count: number;
  avg_cycle_time_seconds?: number;
}

export interface ProcessCycleTime {
  process_name: string;
  average_cycle_time: number;
}

// ============================================================================
// Production Stats
// ============================================================================

export interface ProductionStats {
  total_lots: number;
  total_serials: number;
  completed_serials: number;
  pass_count: number;
  fail_count: number;
  rework_count: number;
  pass_rate: number;
  defect_rate: number;
}

// ============================================================================
// Quality Metrics
// ============================================================================

export interface QualityMetrics {
  total_inspected: number;
  pass_count: number;
  fail_count: number;
  rework_count: number;
  pass_rate: number;
  defect_rate: number;
  rework_rate: number;
  by_process: Array<{
    process_name: string;
    total: number;
    pass: number;
    fail: number;
    rework: number;
    pass_rate: number;
  }>;
}

// ============================================================================
// Defect Analysis
// ============================================================================

export interface DefectAnalysis {
  total_defects: number;
  defect_rate: number;
  by_process: Array<{
    process_name: string;
    defect_count: number;
    defect_rate: number;
  }>;
  by_defect_type: Array<{
    defect_code: string;
    count: number;
    percentage: number;
  }>;
  top_defects: Array<{
    defect_code: string;
    count: number;
    processes: string[];
  }>;
}

export interface DefectTrend {
  date: string;
  total_processed: number;
  defect_count: number;
  defect_rate: number;
}

export interface DefectTrendsResponse {
  trends: DefectTrend[];
  summary: {
    avg_defect_rate: number;
    max_defect_rate: number;
    min_defect_rate: number;
  };
}

// ============================================================================
// Cycle Time Analysis
// ============================================================================

export interface CycleTimeAnalysis {
  by_process: Array<{
    process_id: number;
    process_name: string;
    avg_cycle_time: number;
    min_cycle_time: number;
    max_cycle_time: number;
    median_cycle_time: number;
    total_records: number;
  }>;
  bottlenecks: Array<{
    process_name: string;
    avg_cycle_time: number;
    wip_count: number;
  }>;
}
