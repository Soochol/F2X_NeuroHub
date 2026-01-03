/**
 * Station UI Type Definitions
 *
 * This module exports all TypeScript types for the Station UI.
 */

// Station types
export type { Station, StationStatus, SystemInfo, HealthStatus } from './station';

// Batch types
export type {
  Batch,
  BatchDetail,
  BatchStatus,
  BatchStatistics,
  StepStatistics,
  BatchConfiguration,
  BatchWithStats,
  SequenceStartRequest,
  ManualControlRequest,
  BatchStartResponse,
  BatchStopResponse,
  SequenceStartResponse,
  ManualControlResponse,
  CreateBatchRequest,
  CreateBatchResponse,
  UpdateBatchConfigRequest,
} from './batch';

// Execution types
export type {
  ExecutionResult,
  ExecutionStatus,
  ExecutionSummary,
  StepResult,
  StepStatus,
} from './execution';

// Sequence types
export type {
  SequencePackage,
  SequenceSummary,
  ParameterSchema,
  ParameterType,
  HardwareSchema,
  StepSchema,
  SequenceUpdateRequest,
  SequenceUpdateResponse,
  // Registry types
  SequenceStatus,
  SequenceRegistryItem,
  PullResult,
  // Deploy types
  DeployResponse,
  DeployedSequenceInfo,
  BatchDeploymentInfo,
  // Simulation types
  SimulationMode,
  SimulationRequest,
  StepPreview,
  SimulationStepResult,
  SimulationResult,
} from './sequence';

// Hardware types
export type { HardwareStatus, HardwareConnectionStatus } from './hardware';

// Log types
export type { LogEntry, LogLevel } from './log';

// WebSocket message types
export type {
  // Client messages
  SubscribeMessage,
  UnsubscribeMessage,
  ClientMessage,
  // Server messages
  BatchStatusMessage,
  StepStartMessage,
  StepCompleteMessage,
  SequenceCompleteMessage,
  LogMessage,
  ErrorMessage,
  SubscriptionAckMessage,
  ServerMessage,
} from './messages';

// API types
export type {
  ApiResponse,
  ApiResult,
  ErrorResponse,
  ErrorDetail,
  PaginatedData,
  PaginatedResponse,
  ApiErrorCode,
} from './api';

export { API_ERROR_CODES } from './api';

// Manual control types
export type {
  CommandParameter,
  CommandInfo,
  HardwareCommandsResponse,
  HardwareDetailedStatus,
  ManualStepConfig,
  ManualStepInfo,
  CommandPreset,
  CreatePresetRequest,
  ResultHistoryEntry,
  ManualControlState,
} from './manual';

// Report types
export type {
  ReportType,
  PeriodType,
  ExportFormat,
  StepSummary,
  BatchSummaryReport,
  PeriodDataPoint,
  PeriodStatisticsReport,
  FailureReason,
  StepAnalysisItem,
  StepAnalysisReport,
  ReportFilters,
  BulkExportRequest,
  ReportTypeInfo,
  ExportFormatInfo,
  ReportTypesResponse,
} from './report';

export { EXPORT_FORMAT_INFO, REPORT_TYPE_INFO } from './report';
