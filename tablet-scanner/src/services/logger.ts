/**
 * Logger Service
 *
 * Environment-aware logging with structured output.
 * Suppresses console output in production unless explicitly enabled.
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogEntry {
  level: LogLevel;
  message: string;
  context?: string;
  data?: unknown;
  timestamp: string;
}

interface LoggerConfig {
  enabled: boolean;
  minLevel: LogLevel;
  prefix: string;
}

const LOG_LEVELS: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
};

// Default configuration
const config: LoggerConfig = {
  enabled: import.meta.env.DEV || import.meta.env.VITE_ENABLE_LOGS === 'true',
  minLevel: import.meta.env.DEV ? 'debug' : 'warn',
  prefix: '[Scanner]',
};

/**
 * Check if a log level should be output
 */
function shouldLog(level: LogLevel): boolean {
  if (!config.enabled) return false;
  return LOG_LEVELS[level] >= LOG_LEVELS[config.minLevel];
}

/**
 * Format a log entry for console output
 */
function formatLog(entry: LogEntry): string {
  const contextStr = entry.context ? `[${entry.context}]` : '';
  return `${config.prefix}${contextStr} ${entry.message}`;
}

/**
 * Create a log entry and output it
 */
function log(level: LogLevel, message: string, context?: string, data?: unknown): void {
  if (!shouldLog(level)) return;

  const entry: LogEntry = {
    level,
    message,
    context,
    data,
    timestamp: new Date().toISOString(),
  };

  const formattedMessage = formatLog(entry);

  switch (level) {
    case 'debug':
      if (data !== undefined) {
        console.debug(formattedMessage, data);
      } else {
        console.debug(formattedMessage);
      }
      break;
    case 'info':
      if (data !== undefined) {
        console.info(formattedMessage, data);
      } else {
        console.info(formattedMessage);
      }
      break;
    case 'warn':
      if (data !== undefined) {
        console.warn(formattedMessage, data);
      } else {
        console.warn(formattedMessage);
      }
      break;
    case 'error':
      if (data !== undefined) {
        console.error(formattedMessage, data);
      } else {
        console.error(formattedMessage);
      }
      break;
  }
}

/**
 * Logger with context support
 */
export const logger = {
  debug: (message: string, data?: unknown) => log('debug', message, undefined, data),
  info: (message: string, data?: unknown) => log('info', message, undefined, data),
  warn: (message: string, data?: unknown) => log('warn', message, undefined, data),
  error: (message: string, data?: unknown) => log('error', message, undefined, data),

  /**
   * Create a scoped logger with a specific context
   */
  scope: (context: string) => ({
    debug: (message: string, data?: unknown) => log('debug', message, context, data),
    info: (message: string, data?: unknown) => log('info', message, context, data),
    warn: (message: string, data?: unknown) => log('warn', message, context, data),
    error: (message: string, data?: unknown) => log('error', message, context, data),
  }),

  /**
   * Update logger configuration at runtime
   */
  configure: (newConfig: Partial<LoggerConfig>) => {
    Object.assign(config, newConfig);
  },

  /**
   * Check if logging is enabled
   */
  isEnabled: () => config.enabled,
};

export default logger;
