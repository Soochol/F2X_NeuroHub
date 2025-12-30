/**
 * Error Boundary Component
 *
 * Catches JavaScript errors in child component tree and displays a fallback UI.
 * Prevents the entire app from crashing due to component errors.
 */
import { Component, type ReactNode, type ErrorInfo } from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';
import { cn } from '@/lib/cn';

interface ErrorBoundaryProps {
  children: ReactNode;
  /** Optional fallback UI to render on error */
  fallback?: ReactNode;
  /** Callback when error is caught */
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  /** Component name for error reporting */
  componentName?: string;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    this.setState({ errorInfo });

    // Log error details
    console.error('[ErrorBoundary] Caught error:', {
      component: this.props.componentName || 'Unknown',
      error: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
    });

    // Call optional error callback
    this.props.onError?.(error, errorInfo);
  }

  handleRetry = (): void => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  handleGoHome = (): void => {
    window.location.href = '/';
  };

  handleReload = (): void => {
    window.location.reload();
  };

  render(): ReactNode {
    if (this.state.hasError) {
      // Custom fallback provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return (
        <div className="min-h-[400px] flex items-center justify-center p-6">
          <div
            className={cn(
              'max-w-md w-full',
              'bg-danger-50 dark:bg-danger-900/20',
              'border border-danger-200 dark:border-danger-800',
              'rounded-2xl p-8 text-center',
              'shadow-lg'
            )}
          >
            {/* Error Icon */}
            <div
              className={cn(
                'w-16 h-16 mx-auto mb-6',
                'bg-danger-100 dark:bg-danger-900/40',
                'rounded-full flex items-center justify-center'
              )}
            >
              <AlertTriangle className="w-8 h-8 text-danger-500" />
            </div>

            {/* Error Message */}
            <h2 className="text-xl font-bold text-danger-700 dark:text-danger-400 mb-2">
              Something went wrong
            </h2>
            <p className="text-sm text-danger-600 dark:text-danger-300 mb-6">
              {this.state.error?.message || 'An unexpected error occurred'}
            </p>

            {/* Error Details (Development) */}
            {import.meta.env.DEV && this.state.error && (
              <details className="mb-6 text-left">
                <summary className="text-xs text-neutral-500 cursor-pointer hover:text-neutral-700 dark:hover:text-neutral-300">
                  Error Details
                </summary>
                <pre
                  className={cn(
                    'mt-2 p-3 rounded-lg text-xs overflow-auto max-h-40',
                    'bg-neutral-100 dark:bg-neutral-800',
                    'text-neutral-700 dark:text-neutral-300',
                    'font-mono'
                  )}
                >
                  {this.state.error.stack}
                </pre>
              </details>
            )}

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <button
                onClick={this.handleRetry}
                className={cn(
                  'inline-flex items-center justify-center gap-2',
                  'px-4 py-2 rounded-lg font-medium text-sm',
                  'bg-danger-500 hover:bg-danger-600',
                  'text-white transition-colors'
                )}
              >
                <RefreshCw className="w-4 h-4" />
                Try Again
              </button>
              <button
                onClick={this.handleGoHome}
                className={cn(
                  'inline-flex items-center justify-center gap-2',
                  'px-4 py-2 rounded-lg font-medium text-sm',
                  'bg-neutral-200 dark:bg-neutral-700',
                  'hover:bg-neutral-300 dark:hover:bg-neutral-600',
                  'text-neutral-700 dark:text-neutral-200',
                  'transition-colors'
                )}
              >
                <Home className="w-4 h-4" />
                Go Home
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

/**
 * Higher-order component to wrap a component with ErrorBoundary
 */
export function withErrorBoundary<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  componentName?: string
): React.FC<P> {
  const WithErrorBoundary: React.FC<P> = (props) => (
    <ErrorBoundary componentName={componentName || WrappedComponent.displayName || WrappedComponent.name}>
      <WrappedComponent {...props} />
    </ErrorBoundary>
  );

  WithErrorBoundary.displayName = `WithErrorBoundary(${componentName || WrappedComponent.displayName || WrappedComponent.name || 'Component'})`;

  return WithErrorBoundary;
}

export default ErrorBoundary;
