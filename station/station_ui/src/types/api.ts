/**
 * API response type definitions.
 */

/**
 * Error detail for error responses.
 */
export interface ErrorDetail {
  /** Error code identifier */
  code: string;
  /** Human-readable error message */
  message: string;
}

/**
 * Standard API response wrapper.
 */
export interface ApiResponse<T> {
  /** Whether the request was successful */
  success: true;
  /** Response payload */
  data: T;
  /** Optional response message */
  message?: string;
  /** Optional warning messages (e.g., backend connection issues) */
  warnings?: string[];
}

/**
 * Standard error response wrapper.
 */
export interface ErrorResponse {
  /** Always false for error responses */
  success: false;
  /** Error details */
  error: ErrorDetail;
}

/**
 * Paginated data container.
 */
export interface PaginatedData<T> {
  /** Total number of items available */
  total: number;
  /** List of items for the current page */
  items: T[];
}

/**
 * Standard paginated response wrapper.
 */
export interface PaginatedResponse<T> {
  /** Whether the request was successful */
  success: true;
  /** Paginated data */
  data: PaginatedData<T>;
}

/**
 * Combined response type that can be success or error.
 */
export type ApiResult<T> = ApiResponse<T> | ErrorResponse;

/**
 * API error codes.
 */
export const API_ERROR_CODES = {
  BATCH_NOT_FOUND: 'BATCH_NOT_FOUND',
  BATCH_ALREADY_RUNNING: 'BATCH_ALREADY_RUNNING',
  BATCH_NOT_RUNNING: 'BATCH_NOT_RUNNING',
  SEQUENCE_NOT_FOUND: 'SEQUENCE_NOT_FOUND',
  SEQUENCE_ALREADY_RUNNING: 'SEQUENCE_ALREADY_RUNNING',
  HARDWARE_ERROR: 'HARDWARE_ERROR',
  HARDWARE_NOT_CONNECTED: 'HARDWARE_NOT_CONNECTED',
  INVALID_PARAMETERS: 'INVALID_PARAMETERS',
  TIMEOUT: 'TIMEOUT',
  INTERNAL_ERROR: 'INTERNAL_ERROR',
  RESULT_NOT_FOUND: 'RESULT_NOT_FOUND',
  INVALID_FORMAT: 'INVALID_FORMAT',
} as const;

export type ApiErrorCode = typeof API_ERROR_CODES[keyof typeof API_ERROR_CODES];
