/**
 * Common Types - Shared types and utilities
 */

// ============================================================================
// Pagination
// ============================================================================

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export interface BaseQueryParams {
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
