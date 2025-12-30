/**
 * Logger utility for environment-based logging.
 * Logs are only displayed in development environment (except errors).
 *
 * Usage:
 *   Logger.log('message', data);
 *   Logger.error('Error occurred:', error);
 */

/** Log argument type - accepts any serializable value */
type LogArg = unknown;

class Logger {
    private static isDev = import.meta.env.DEV;

    /**
     * General logging (dev only)
     */
    static log(...args: LogArg[]): void {
        if (this.isDev) {
            console.log(...args);
        }
    }

    /**
     * Info level logging (dev only)
     */
    static info(...args: LogArg[]): void {
        if (this.isDev) {
            console.info(...args);
        }
    }

    /**
     * Warning level logging (dev only)
     */
    static warn(...args: LogArg[]): void {
        if (this.isDev) {
            console.warn(...args);
        }
    }

    /**
     * Error level logging (always enabled for production debugging)
     * Consider integrating with error tracking service (e.g., Sentry) in production
     */
    static error(...args: LogArg[]): void {
        console.error(...args);
    }

    /**
     * Debug level logging (dev only)
     */
    static debug(...args: LogArg[]): void {
        if (this.isDev) {
            console.debug(...args);
        }
    }
}

export default Logger;
