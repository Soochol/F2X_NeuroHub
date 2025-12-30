/**
 * Error Boundary Component
 *
 * Catches JavaScript errors anywhere in child component tree,
 * logs those errors, and displays a fallback UI.
 *
 * Usage:
 * <ErrorBoundary>
 *   <YourComponent />
 * </ErrorBoundary>
 *
 * With custom fallback:
 * <ErrorBoundary fallback={<CustomErrorUI />}>
 *   <YourComponent />
 * </ErrorBoundary>
 */

import { Component, type ReactNode, type ErrorInfo } from 'react';
import { Button, Result } from 'antd';
import Logger from '@/utils/logger';

interface ErrorBoundaryProps {
  children: ReactNode;
  /** Custom fallback UI to show when error occurs */
  fallback?: ReactNode;
  /** Called when an error is caught */
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  /** Show reset button in default fallback */
  showReset?: boolean;
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
    Logger.error('ErrorBoundary caught an error:', {
      error: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
    });

    // Call custom error handler if provided
    this.props.onError?.(error, errorInfo);
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  handleReload = (): void => {
    window.location.reload();
  };

  render(): ReactNode {
    const { hasError, error } = this.state;
    const { children, fallback, showReset = true } = this.props;

    if (hasError) {
      // Custom fallback provided
      if (fallback) {
        return fallback;
      }

      // Default error UI
      return (
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '400px',
          padding: '24px',
          backgroundColor: 'var(--color-bg-primary)',
        }}>
          <Result
            status="error"
            title="오류가 발생했습니다"
            subTitle={
              import.meta.env.DEV
                ? error?.message || '알 수 없는 오류'
                : '페이지를 불러오는 중 문제가 발생했습니다. 잠시 후 다시 시도해주세요.'
            }
            extra={
              showReset && (
                <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
                  <Button type="primary" onClick={this.handleReset}>
                    다시 시도
                  </Button>
                  <Button onClick={this.handleReload}>
                    페이지 새로고침
                  </Button>
                </div>
              )
            }
          />
        </div>
      );
    }

    return children;
  }
}

/**
 * Page-level Error Boundary with navigation support
 */
interface PageErrorBoundaryProps extends ErrorBoundaryProps {
  /** Page title for error context */
  pageName?: string;
}

export class PageErrorBoundary extends Component<PageErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: PageErrorBoundaryProps) {
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

    Logger.error(`PageErrorBoundary [${this.props.pageName || 'Unknown'}]:`, {
      error: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
    });

    this.props.onError?.(error, errorInfo);
  }

  handleGoHome = (): void => {
    window.location.href = '/';
  };

  handleReload = (): void => {
    window.location.reload();
  };

  render(): ReactNode {
    const { hasError, error } = this.state;
    const { children, fallback, pageName } = this.props;

    if (hasError) {
      if (fallback) {
        return fallback;
      }

      return (
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
          padding: '24px',
          backgroundColor: 'var(--color-bg-primary)',
        }}>
          <Result
            status="500"
            title="페이지 오류"
            subTitle={
              <>
                {pageName && <div style={{ marginBottom: '8px' }}>{pageName} 페이지에서 오류가 발생했습니다.</div>}
                {import.meta.env.DEV && (
                  <div style={{ color: 'var(--color-text-secondary)', fontSize: '12px', fontFamily: 'monospace' }}>
                    {error?.message}
                  </div>
                )}
              </>
            }
            extra={
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
                <Button type="primary" onClick={this.handleGoHome}>
                  홈으로 이동
                </Button>
                <Button onClick={this.handleReload}>
                  새로고침
                </Button>
              </div>
            }
          />
        </div>
      );
    }

    return children;
  }
}

export default ErrorBoundary;
