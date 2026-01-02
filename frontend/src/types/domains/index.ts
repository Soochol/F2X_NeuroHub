/**
 * Domain Types - Barrel Export
 *
 * Re-exports all domain-specific types for organized imports:
 *
 * Usage:
 *   import { User, Lot, Process } from '@/types/domains';
 *   import type { LotStatus, SerialStatus } from '@/types/domains';
 */

// Enums
export {
  AlertSeverity,
  AlertStatus,
  AlertType,
  AuditAction,
  DataLevel,
  HeaderStatus,
  LotStatus,
  ProcessResult,
  SerialStatus,
  UserRole,
  WIPStatus,
} from './enums';

// Common
export type {
  APIError,
  ApiCatchError,
  BaseQueryParams,
  PaginatedResponse,
} from './common';
export { getErrorMessage } from './common';

// User
export type { LoginRequest, LoginResponse, User } from './user';

// Equipment
export type { Equipment, ProductionLine, ProductModel } from './equipment';

// Process
export type {
  Process,
  ProcessData,
  ProcessDataCreate,
  ProcessHeaderFilter,
  ProcessHeaderListResponse,
  ProcessHeaderSummary,
  ProcessHistoryItem,
  ProcessType,
} from './process';

// Lot
export type { Lot, LotCreate, LotQueryParams, LotUpdate } from './lot';

// Serial
export type { Serial, SerialCreate, SerialTrace, SerialUpdate } from './serial';

// WIP
export type { WIPItem, WipTrace } from './wip';

// Alert
export type {
  Alert,
  AlertCreate,
  AlertListResponse,
  AlertQueryParams,
  AlertUpdate,
} from './alert';

// Audit
export type { AuditLog } from './audit';

// Analytics
export type {
  CycleTimeAnalysis,
  DashboardLot,
  DashboardSummary,
  DefectAnalysis,
  DefectTrend,
  DefectTrendsResponse,
  ProcessCycleTime,
  ProcessWIP,
  ProductionStats,
  QualityMetrics,
} from './analytics';

// Measurement
export type {
  MeasurementCodeInfo,
  MeasurementCodesResponse,
  MeasurementHistory,
  MeasurementHistoryFilters,
  MeasurementHistoryItem,
  MeasurementHistoryListResponse,
  MeasurementSpec,
  MeasurementSummaryResponse,
  ProcessMeasurementSummary,
} from './measurement';

// Printer
export type {
  PrinterStatus,
  PrintLog,
  PrintLogQueryParams,
  PrintLogsResponse,
  PrintStatistics,
} from './printer';
