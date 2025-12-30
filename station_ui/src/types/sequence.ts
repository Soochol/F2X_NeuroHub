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

/**
 * Validation error detail.
 */
export interface ValidationErrorDetail {
  field: string;
  message: string;
}

/**
 * Result of sequence validation.
 */
export interface ValidationResult {
  valid: boolean;
  errors?: ValidationErrorDetail[];
  warnings?: string[];
  manifest?: {
    name: string;
    version: string;
    displayName?: string;
    description?: string;
  };
}

/**
 * Response for sequence upload operation.
 */
export interface SequenceUploadResponse {
  name: string;
  version: string;
  path: string;
  hardware: string[];
  parameters: string[];
  uploaded_at: string;
}

/**
 * State for upload progress tracking.
 */
export interface UploadProgress {
  stage: 'idle' | 'validating' | 'uploading' | 'complete' | 'error';
  progress: number;
  message: string;
  error?: string;
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
