/**
 * F2X NeuroHub MES - API Type Definitions
 *
 * TypeScript types matching backend Pydantic schemas
 */

// ============================================================================
// Enums
// ============================================================================

export enum UserRole {
  ADMIN = 'ADMIN',
  MANAGER = 'MANAGER',
  OPERATOR = 'OPERATOR',
}

export enum LotStatus {
  CREATED = 'CREATED',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  CLOSED = 'CLOSED',
}

export enum Shift {
  DAY = 'DAY',
  EVENING = 'EVENING',
  NIGHT = 'NIGHT',
}

export enum SerialStatus {
  CREATED = 'CREATED',
  IN_PROGRESS = 'IN_PROGRESS',
  PASS = 'PASS',
  FAIL = 'FAIL',
  REWORK = 'REWORK',
  SCRAPPED = 'SCRAPPED',
}

export enum ProcessResult {
  PASS = 'PASS',
  FAIL = 'FAIL',
  REWORK = 'REWORK',
}

export enum DataLevel {
  NORMAL = 'NORMAL',
  DETAILED = 'DETAILED',
}

export enum AuditAction {
  CREATE = 'CREATE',
  UPDATE = 'UPDATE',
  DELETE = 'DELETE',
}

export enum AlertType {
  DEFECT_DETECTED = 'DEFECT_DETECTED',
  REWORK_REQUEST = 'REWORK_REQUEST',
  PROCESS_DELAY = 'PROCESS_DELAY',
  LOT_COMPLETED = 'LOT_COMPLETED',
  LOT_CLOSED = 'LOT_CLOSED',
  EQUIPMENT_FAILURE = 'EQUIPMENT_FAILURE',
  QUALITY_THRESHOLD = 'QUALITY_THRESHOLD',
  SYSTEM_ERROR = 'SYSTEM_ERROR',
  MANUAL = 'MANUAL',
}

export enum AlertSeverity {
  HIGH = 'HIGH',
  MEDIUM = 'MEDIUM',
  LOW = 'LOW',
}

export enum AlertStatus {
  UNREAD = 'UNREAD',
  READ = 'READ',
  ARCHIVED = 'ARCHIVED',
}

// ============================================================================
// Base Models
// ============================================================================

export interface User {
  id: number;
  username: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProductModel {
  id: number;
  code: string;
  name: string;
  description?: string;
  version: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Process {
  id: number;
  process_number: number;
  name: string;
  description?: string;
  sequence_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Lot {
  id: number;
  lot_number: string;
  product_model_id: number;
  product_model?: ProductModel;
  target_quantity: number;
  production_date: string;
  shift: Shift;
  status: LotStatus;
  busbar_lot?: string;
  sma_spring_lot?: string;
  pin_lot?: string;
  hsg_lot?: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  closed_at?: string;
}

export interface Serial {
  id: number;
  serial_number: string;
  lot_id: number;
  lot?: Lot;
  status: SerialStatus;
  rework_count: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

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

export interface AuditLog {
  id: number;
  entity_type: string;
  entity_id: number;
  action: AuditAction;
  user_id?: number;
  user?: User;
  changes?: Record<string, any>;
  timestamp: string;
}

export interface Alert {
  id: number;
  alert_type: AlertType;
  severity: AlertSeverity;
  status: AlertStatus;
  title: string;
  message: string;
  lot_id?: number;
  lot_number?: string;
  serial_id?: number;
  serial_number?: string;
  process_id?: number;
  process_name?: string;
  created_at: string;
  read_at?: string;
  read_by_id?: number;
  archived_at?: string;
}

// ============================================================================
// Request/Response Types
// ============================================================================

// Authentication
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Lot
export interface LotCreate {
  lot_number: string;
  product_model_id: number;
  target_quantity: number;
  production_date: string;
  shift: Shift;
  busbar_lot?: string;
  sma_spring_lot?: string;
  pin_lot?: string;
  hsg_lot?: string;
}

export interface LotUpdate {
  status?: LotStatus;
  busbar_lot?: string;
  sma_spring_lot?: string;
  pin_lot?: string;
  hsg_lot?: string;
}

// Serial
export interface SerialCreate {
  serial_number: string;
  lot_id: number;
}

export interface SerialUpdate {
  status?: SerialStatus;
}

// Process Data
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

// Alert
export interface AlertCreate {
  alert_type: AlertType;
  severity: AlertSeverity;
  title: string;
  message: string;
  lot_id?: number;
  serial_id?: number;
  process_id?: number;
}

export interface AlertUpdate {
  status?: AlertStatus;
}

export interface AlertListResponse {
  alerts: Alert[];
  total: number;
  unread_count: number;
}

// ============================================================================
// Dashboard Types
// ============================================================================

export interface DashboardSummary {
  total_started: number;
  total_completed: number;
  total_defective: number;
  defect_rate: number;
  lots: Array<{
    lot_number: string;
    product_model_name: string;
    status: LotStatus;
    progress: number;
    started_count: number;
    completed_count: number;
    defective_count: number;
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
  shift: Shift;
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

// ============================================================================
// Analytics Types
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

// ============================================================================
// Serial Trace
// ============================================================================

export interface ProcessHistoryItem {
  process_number: number;
  process_name: string;
  worker_name: string;
  result: ProcessResult;
  started_at: string;
  completed_at: string;
  cycle_time_seconds: number;
  measurements?: Record<string, any>;
  defect_codes?: string[];
  notes?: string;
}

export interface SerialTrace {
  serial_number: string;
  lot_number: string;
  status: SerialStatus;
  rework_count: number;
  lot_info: {
    product_model_name: string;
    production_date: string;
    shift: Shift;
    busbar_lot?: string;
    sma_spring_lot?: string;
    pin_lot?: string;
    hsg_lot?: string;
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

// ============================================================================
// Pagination
// ============================================================================

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

// ============================================================================
// API Error
// ============================================================================

export interface APIError {
  detail: string;
}

/**
 * Type-safe error type for catch blocks
 * Use instead of `any` in error handlers
 */
export type ApiCatchError = Error & {
  message?: string;
  response?: {
    data?: APIError;
  };
};

/**
 * Helper function to extract error message from API errors
 */
export const getErrorMessage = (err: unknown, defaultMessage: string): string => {
  const error = err as ApiCatchError;
  return error.message || error?.response?.data?.detail || defaultMessage;
};

// ============================================================================
// Query Parameters
// ============================================================================

export interface BaseQueryParams {
  skip: number;
  limit: number;
}

export interface AlertQueryParams extends BaseQueryParams {
  severity?: AlertSeverity;
  status?: AlertStatus;
}

export interface LotQueryParams extends BaseQueryParams {
  status?: LotStatus;
  product_model_id?: number;
}
