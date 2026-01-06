/**
 * Hooks barrel export.
 */

// System hooks
export { useSystemInfo, useHealthStatus, useUpdateStationInfo, useBackendConfig, useUpdateBackendConfig } from './useSystem';

// Workflow hooks
export { useWorkflowConfig, useUpdateWorkflowConfig, useProcesses, useProcessHeaders } from './useWorkflow';
export type { WorkflowConfig, UpdateWorkflowRequest, ProcessInfo, ProcessHeaderInfo } from './useWorkflow';

// Operator hooks
export { useOperatorSession, useOperatorLogin, useOperatorLogout } from './useOperator';
export type { OperatorSession, OperatorLoginRequest } from './useOperator';

// Batch hooks
export {
  useBatchList,
  useBatch,
  useStartBatch,
  useStopBatch,
  useDeleteBatch,
  useStartSequence,
  useStopSequence,
  useManualControl,
  useCreateBatches,
  useUpdateBatchConfig,
  useUpdateBatch,
  useBatchStatistics,
  useAllBatchStatistics,
  useSyncBatchToBackend,
} from './useBatches';

// Sequence hooks
export {
  useSequenceList,
  useSequence,
  useUpdateSequence,
  useDeleteSequence,
  useDownloadSequence,
  // Registry hooks
  useSequenceRegistry,
  usePullSequence,
  useSyncSequences,
  // Deploy hooks
  useDeploySequence,
  useDeployments,
  useDeployedSequence,
  // Simulation hooks
  useSimulation,
  // Auto-sync hooks
  useAutoSyncStatus,
  useConfigureAutoSync,
  useTriggerAutoSyncCheck,
} from './useSequences';

// Result hooks
export { useResultList, useResult, useExportResult } from './useResults';

// Log hooks
export { useLogList } from './useLogs';

// WebSocket hook
export { useWebSocket } from './useWebSocket';

// Polling fallback hook
export { usePollingFallback, useAdaptivePollingInterval } from './usePollingFallback';

// Manual control hooks
export {
  useBatchHardware,
  useHardwareCommands,
  useManualSteps,
  useExecuteCommand,
  useRunManualStep,
  useSkipManualStep,
  useResetManualSequence,
  usePresets,
  useCreatePreset,
  useDeletePreset,
  manualQueryKeys,
} from './useManualControl';

// Interactive Simulation hooks
export {
  useSimulationSessions,
  useSimulationSession,
  useCreateSimulationSession,
  useDeleteSimulationSession,
  useInitializeSimulationSession,
  useFinalizeSimulationSession,
  useAbortSimulationSession,
  useRunSimulationStep,
  useSkipSimulationStep,
  useQuickSimulation,
  simulationQueryKeys,
} from './useSimulation';
export type {
  SimulationSessionDetail,
  SimulationSessionSummary,
  SimulationStepState,
} from './useSimulation';

// Manual Sequence hooks (real hardware, no batch required)
export {
  useManualSessions,
  useManualSession,
  useManualSessionHardware,
  useHardwareCommands as useManualHardwareCommands,
  useCreateManualSession,
  useDeleteManualSession,
  useInitializeManualSession,
  useFinalizeManualSession,
  useAbortManualSession,
  useRunManualStep as useRunManualSequenceStep,
  useSkipManualStep as useSkipManualSequenceStep,
  useExecuteHardwareCommand,
  manualSequenceQueryKeys,
} from './useManualSequence';
export type {
  ManualSessionDetail,
  ManualSessionSummary,
  ManualStepState,
  HardwareState,
  CommandDefinition,
  CommandResult,
} from './useManualSequence';

// Report hooks
export {
  useBatchSummaryReport,
  useExportBatchSummaryReport,
  usePeriodStatsReport,
  useExportPeriodStatsReport,
  useStepAnalysisReport,
  useExportStepAnalysisReport,
  useReportTypes,
  useExportResultsBulk,
  useExportSingleResult,
  reportQueryKeys,
} from './useReports';
