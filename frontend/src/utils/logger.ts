/**
 * Logger utility for environment-based logging.
 * Logs are only displayed in development environment.
 */
class Logger {
    private static isDev = import.meta.env.DEV;

    static log(...args: any[]) {
        if (this.isDev) {
            console.log(...args);
        }
    }

    static info(...args: any[]) {
        if (this.isDev) {
            console.info(...args);
        }
    }

    static warn(...args: any[]) {
        if (this.isDev) {
            console.warn(...args);
        }
    }

    static error(...args: any[]) {
        // Errors should probably be logged in production too, or sent to a tracking service (e.g. Sentry)
        // For now, we'll always log errors to console, but we can filter if needed.
        // If the requirement is strict "no console in prod", we can wrap it.
        // However, usually console.error is useful in prod for debugging if no Sentry.
        // Based on user request "Replace console.log/error", I will wrap it but maybe allow it if critical.
        // Let's stick to dev-only for now as requested, or maybe allow error in prod?
        // The request said "Environment-based logging system".
        // I'll allow error in prod for now as it's critical, but maybe silence it if strictly requested.
        // "Replace console.log/error in api/client.ts" -> usually we want to see API errors.
        // I'll log errors in all envs for now, but use this wrapper so we can control it later.
        console.error(...args);
    }

    static debug(...args: any[]) {
        if (this.isDev) {
            console.debug(...args);
        }
    }
}

export default Logger;
