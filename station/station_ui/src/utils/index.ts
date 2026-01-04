/**
 * Utilities barrel export.
 */

export { toast, isErrorWithMessage, getErrorMessage, type ToastType } from './toast';
export {
  createLogger,
  wsLogger,
  batchLogger,
  apiLogger,
  nullLogger,
  type Logger,
} from './logger';

/**
 * Utility function for conditionally joining class names.
 * Similar to clsx/classnames but simpler.
 */
export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ');
}
