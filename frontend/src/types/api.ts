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

export enum SerialStatus {
  CREATED = 'CREATED',
  IN_PROGRESS = 'IN_PROGRESS',
  PASS = 'PASSED',
  FAIL = 'FAILED',
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

export enum WIPStatus {
  CREATED = 'CREATED',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
  CONVERTED = 'CONVERTED',
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
  email: string;
  full_name: string;
  role: UserRole;
  department?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  last_login_at?: string;
}

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

export interface Lot {
  id: number;
  lot_number: string;
  product_model_id: number;
  product_model?: ProductModel;
  target_quantity: number;
  production_date: string;
  status: LotStatus;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  closed_at?: string;
  parent_spring_lot?: string;
  sma_spring_lot?: string;
  shift?: string;
  serial_count?: number;
  wip_count?: number;
  actual_quantity?: number;
  passed_quantity?: number;
  failed_quantity?: number;
}

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
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

// Lot
export interface LotCreate {
  product_model_id: number;
  production_line_id: number;
  target_quantity: number;
  production_date: string;
  parent_spring_lot?: string;
  sma_spring_lot?: string;
}

export interface LotUpdate {
  status?: LotStatus;
}

// Serial
export interface SerialCreate {
  lot_id: number;
  sequence_in_lot: number;
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
  const error = err as any;

  // StandardErrorResponse format with details (validation errors)
  if (error?.response?.data?.details && Array.isArray(error.response.data.details)) {
    const details = error.response.data.details;
    if (details.length > 0) {
      // Format: "field: message" for each validation error
      const messages = details.map((d: { field?: string; message?: string }) => {
        const field = d.field || 'unknown';
        const message = d.message || 'validation failed';
        return `${field}: ${message}`;
      });
      return messages.join(', ');
    }
  }

  // StandardErrorResponse format
  if (error?.response?.data?.message) {
    return error.response.data.message;
  }

  // Legacy APIError format
  if (error?.response?.data?.detail) {
    return error.response.data.detail;
  }

  // Axios error message
  if (error?.message) {
    return error.message;
  }

  return defaultMessage;
};

// ============================================================================
// Measurement History Types
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

export interface MeasurementHistoryFilters {
  start_date?: string;
  end_date?: string;
  process_id?: number;
  lot_id?: number;
  header_id?: number;
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

// Measurement Code Types
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

// ============================================================================
// Printer Monitoring
// ============================================================================

export interface PrinterStatus {
  online: boolean;
  ip: string;
  port: number;
  response_time_ms?: number;
  error?: string;
  last_check: string;
}

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

// ============================================================================
// Process Headers
// ============================================================================

export enum HeaderStatus {
  OPEN = 'OPEN',
  CLOSED = 'CLOSED',
  CANCELLED = 'CANCELLED',
}

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
