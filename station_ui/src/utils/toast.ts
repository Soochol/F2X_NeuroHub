/**
 * Toast notification utilities.
 * Provides a simple interface for showing user notifications.
 */

export type ToastType = 'success' | 'error' | 'warning' | 'info';

interface ToastOptions {
  type: ToastType;
  message: string;
  duration?: number;
}

/**
 * Simple toast notification manager.
 * Uses custom events to communicate with a toast container component.
 */
class ToastManager {
  private static instance: ToastManager;

  private constructor() {}

  static getInstance(): ToastManager {
    if (!ToastManager.instance) {
      ToastManager.instance = new ToastManager();
    }
    return ToastManager.instance;
  }

  /**
   * Show a toast notification.
   */
  show(options: ToastOptions): void {
    const event = new CustomEvent('toast', { detail: options });
    window.dispatchEvent(event);
  }

  /**
   * Show a success toast.
   */
  success(message: string, duration?: number): void {
    this.show({ type: 'success', message, duration });
  }

  /**
   * Show an error toast.
   */
  error(message: string, duration?: number): void {
    this.show({ type: 'error', message, duration });
  }

  /**
   * Show a warning toast.
   */
  warning(message: string, duration?: number): void {
    this.show({ type: 'warning', message, duration });
  }

  /**
   * Show an info toast.
   */
  info(message: string, duration?: number): void {
    this.show({ type: 'info', message, duration });
  }
}

export const toast = ToastManager.getInstance();

/**
 * Type guard for error objects.
 */
export function isErrorWithMessage(error: unknown): error is { message: string } {
  return (
    typeof error === 'object' &&
    error !== null &&
    'message' in error &&
    typeof (error as { message: unknown }).message === 'string'
  );
}

/**
 * Extract error message from unknown error.
 */
export function getErrorMessage(error: unknown): string {
  if (isErrorWithMessage(error)) {
    return error.message;
  }
  if (typeof error === 'string') {
    return error;
  }
  return 'An unknown error occurred';
}
