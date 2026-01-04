/**
 * Sequence package type definitions.
 */

/**
 * Parameter type.
 */
export type ParameterType = 'float' | 'integer' | 'string' | 'boolean';

/**
 * Schema definition for a sequence parameter.
 */
export interface ParameterSchema {
  /** Parameter name */
  name: string;
  /** Display name */
  displayName: string;
  /** Parameter type */
  type: ParameterType;
  /** Default value */
  default: unknown;
  /** Minimum value (for numeric types) */
  min?: number;
  /** Maximum value (for numeric types) */
  max?: number;
  /** Allowed options (for string type) */
  options?: string[];
  /** Unit of measurement */
  unit?: string;
  /** Description */
  description?: string;
}

/**
 * Schema definition for hardware configuration.
 */
export interface HardwareSchema {
  /** Hardware ID */
  id: string;
  /** Display name */
  displayName: string;
  /** Driver file path */
  driver: string;
  /** Driver class name */
  className: string;
  /** Description */
  description?: string;
  /** Configuration schema */
  configSchema: Record<string, Record<string, unknown>>;
}

/**
 * Schema definition for a sequence step.
 */
export interface StepSchema {
  /** Step order (1-based) */
  order: number;
  /** Step name */
  name: string;
  /** Display name */
  displayName: string;
  /** Description */
  description: string;
  /** Timeout in seconds */
  timeout: number;
  /** Retry count on failure */
  retry: number;
  /** Whether this is a cleanup step (always runs) */
  cleanup: boolean;
  /** Condition expression for conditional execution */
  condition?: string;
}

/**
 * Complete sequence package information.
 */
export interface SequencePackage {
  /** Package name (e.g., "pcb_voltage_test") */
  name: string;
  /** Version (e.g., "1.2.0") */
  version: string;
  /** Display name */
  displayName: string;
  /** Description */
  description: string;
  /** Author */
  author?: string;
  /** Creation date */
  createdAt?: string;
  /** Last update date */
  updatedAt?: string;
  /** Package path */
  path: string;

  /** Hardware definitions */
  hardware: HardwareSchema[];
  /** Parameter definitions */
  parameters: ParameterSchema[];
  /** Step definitions */
  steps: StepSchema[];
}

/**
 * Sequence summary for list view.
 */
export interface SequenceSummary {
  /** Package name */
  name: string;
  /** Version */
  version: string;
  /** Display name */
  displayName: string;
  /** Description */
  description: string;
  /** Package path */
  path: string;
  /** Last update date */
  updatedAt?: string;
}

/**
 * Request body for updating a sequence.
 */
export interface SequenceUpdateRequest {
  parameters?: Array<{ name: string; default?: unknown }>;
  steps?: Array<{ name: string; order?: number; timeout?: number }>;
}

/**
 * Response for sequence update operation.
 */
export interface SequenceUpdateResponse {
  name: string;
  version: string;
  updatedAt: string;
}

// ============================================================================
// Registry Types (for unified local/remote view)
// ============================================================================

/**
 * Sequence installation status.
 */
export type SequenceStatus =
  | 'installed_latest'    // Installed and up-to-date
  | 'update_available'    // Installed but newer version on server
  | 'not_installed'       // Available on server, not installed locally
  | 'local_only';         // Installed locally, not on server

/**
 * Unified sequence registry item combining local and remote info.
 */
export interface SequenceRegistryItem {
  /** Sequence name */
  name: string;
  /** Human-readable name */
  displayName?: string;
  /** Sequence description */
  description?: string;

  /** Installation status */
  status: SequenceStatus;

  /** Locally installed version */
  localVersion?: string;
  /** Version available on server */
  remoteVersion?: string;

  /** When installed locally */
  installedAt?: string;
  /** When updated on server */
  remoteUpdatedAt?: string;
  /** Whether sequence is active on server */
  isActive: boolean;
}

/**
 * Response for pull operation.
 */
export interface PullResult {
  name: string;
  version: string;
  checksum: string;
  packageSize: number;
  needsUpdate: boolean;
  updated: boolean;
  error?: string;
  installedAt?: string;
}

// ============================================================================
// Deploy Types
// ============================================================================

/**
 * Response for sequence deployment.
 */
export interface DeployResponse {
  /** Name of deployed sequence */
  sequenceName: string;
  /** ID of the batch */
  batchId: string;
  /** Deployment timestamp */
  deployedAt: string;
  /** Previously deployed sequence */
  previousSequence?: string;
}

/**
 * Information about a deployed sequence.
 */
export interface DeployedSequenceInfo {
  /** Batch ID */
  batchId: string;
  /** Batch name */
  batchName: string;
  /** Deployed sequence name */
  sequenceName?: string;
  /** Deployed sequence path */
  sequencePath?: string;
}

/**
 * Deployment information for a batch.
 */
export interface BatchDeploymentInfo {
  /** Batch ID */
  batchId: string;
  /** Batch name */
  name: string;
  /** Deployed sequence package */
  sequencePackage?: string;
}

// ============================================================================
// Simulation Types
// ============================================================================

/**
 * Simulation mode.
 */
export type SimulationMode = 'dry_run' | 'preview';

/**
 * Request for running a simulation.
 */
export interface SimulationRequest {
  /** Sequence name to simulate */
  sequenceName: string;
  /** Simulation mode */
  mode: SimulationMode;
  /** Parameter overrides */
  parameters?: Record<string, unknown>;
}

/**
 * Preview of a sequence step.
 */
export interface StepPreview {
  /** Step execution order */
  order: number;
  /** Step name */
  name: string;
  /** Human-readable step name */
  displayName: string;
  /** Step timeout in seconds */
  timeout: number;
  /** Number of retry attempts */
  retry: number;
  /** Whether this is a cleanup step */
  cleanup: boolean;
  /** Step description */
  description?: string;
}

/**
 * Result of a step execution in simulation.
 */
export interface SimulationStepResult {
  /** Step name */
  name: string;
  /** Step order */
  order: number;
  /** Step status */
  status: 'passed' | 'failed' | 'skipped';
  /** Start timestamp */
  startedAt: string;
  /** Completion timestamp */
  completedAt?: string;
  /** Duration in seconds */
  duration: number;
  /** Step result data */
  result?: unknown;
  /** Error message if failed */
  error?: string;
}

/**
 * Result of a simulation run.
 */
export interface SimulationResult {
  /** Simulation ID */
  id: string;
  /** Simulated sequence name */
  sequenceName: string;
  /** Simulation mode */
  mode: SimulationMode;
  /** Simulation status */
  status: 'running' | 'completed' | 'failed';
  /** Start timestamp */
  startedAt: string;
  /** Completion timestamp */
  completedAt?: string;
  /** Step previews */
  steps: StepPreview[];
  /** Step execution results (for dry_run mode) */
  stepResults?: SimulationStepResult[];
  /** Parameters used */
  parameters?: Record<string, unknown>;
  /** Error message if failed */
  error?: string;
}
