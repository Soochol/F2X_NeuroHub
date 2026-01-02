/**
 * Hooks barrel export.
 */

// System hooks
export { useSystemInfo, useHealthStatus, useUpdateStationInfo } from './useSystem';

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
  useValidateSequence,
  useUploadSequence,
  useDeleteSequence,
  useDownloadSequence,
  // Deploy hooks
  useDeploySequence,
  useDeployments,
  useDeployedSequence,
  // Simulation hooks
  useSimulation,
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
