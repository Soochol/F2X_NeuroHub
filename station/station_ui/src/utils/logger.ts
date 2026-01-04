/**
 * Structured logging utility for station_ui.
 *
 * Features:
 * - Log levels (debug, info, warn, error)
 * - Contextual prefixes for easy filtering
 * - Development-only debug logs
 * - Production-safe (no sensitive data logging)
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LoggerConfig {
  /** Prefix for all log messages from this logger */
  prefix: string;
  /** Minimum log level to display */
  minLevel?: LogLevel;
  /** Whether to include timestamps */
  timestamps?: boolean;
}

const LOG_LEVELS: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
};

// Determine if we're in production mode
const isProduction = import.meta.env.PROD;

// Default minimum level: debug in dev, info in production
const DEFAULT_MIN_LEVEL: LogLevel = isProduction ? 'info' : 'debug';

/**
 * Creates a scoped logger with a prefix for easy filtering.
 */
export function createLogger(config: LoggerConfig) {
  const { prefix, minLevel = DEFAULT_MIN_LEVEL, timestamps = false } = config;

  const shouldLog = (level: LogLevel): boolean => {
    return LOG_LEVELS[level] >= LOG_LEVELS[minLevel];
  };

  const formatMessage = (message: string): string => {
    const parts: string[] = [];
    if (timestamps) {
      parts.push(new Date().toISOString());
    }
    parts.push(`[${prefix}]`);
    parts.push(message);
    return parts.join(' ');
  };

  const truncateId = (id: string, length = 8): string => {
    return id.length > length ? `${id.slice(0, length)}...` : id;
  };

  return {
    debug: (message: string, ...args: unknown[]) => {
      if (shouldLog('debug')) {
        console.log(formatMessage(message), ...args);
      }
    },

    info: (message: string, ...args: unknown[]) => {
      if (shouldLog('info')) {
        console.info(formatMessage(message), ...args);
      }
    },

    warn: (message: string, ...args: unknown[]) => {
      if (shouldLog('warn')) {
        console.warn(formatMessage(message), ...args);
      }
    },

    error: (message: string, ...args: unknown[]) => {
      if (shouldLog('error')) {
        console.error(formatMessage(message), ...args);
      }
    },

    /** Helper to truncate batch/execution IDs for cleaner logs */
    truncateId,

    /** Helper for logging batch-related events */
    batch: (batchId: string, action: string, details?: Record<string, unknown>) => {
      if (shouldLog('debug')) {
        const detailStr = details
          ? ` ${Object.entries(details).map(([k, v]) => `${k}=${v}`).join(', ')}`
          : '';
        console.log(formatMessage(`${action}: ${truncateId(batchId)}${detailStr}`));
      }
    },
  };
}

// Pre-configured loggers for common use cases
export const wsLogger = createLogger({ prefix: 'WS' });
export const batchLogger = createLogger({ prefix: 'batchStore' });
export const apiLogger = createLogger({ prefix: 'API' });

/**
 * No-op logger for production or disabled logging.
 */
export const nullLogger = {
  debug: () => {},
  info: () => {},
  warn: () => {},
  error: () => {},
  truncateId: (id: string) => id.slice(0, 8),
  batch: () => {},
};

export type Logger = ReturnType<typeof createLogger>;
