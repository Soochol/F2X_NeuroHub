/**
 * Toast Notification System
 *
 * 사용자에게 피드백을 제공하는 토스트 알림 시스템
 */
import { useEffect, useState, useCallback, createContext, useContext } from 'react';
import { createPortal } from 'react-dom';
import {
  CheckCircle,
  XCircle,
  AlertTriangle,
  Info,
  X,
  Loader2,
} from 'lucide-react';
import { cn } from '@/lib/cn';

// Toast 타입 정의
type ToastType = 'success' | 'error' | 'warning' | 'info' | 'loading';

interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface ToastContextValue {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => string;
  removeToast: (id: string) => void;
  updateToast: (id: string, updates: Partial<Toast>) => void;
  clearAll: () => void;
}

// Context 생성
const ToastContext = createContext<ToastContextValue | null>(null);

// Toast Provider
export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((toast: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).slice(2, 9);
    setToasts((prev) => [...prev, { ...toast, id }]);
    return id;
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const updateToast = useCallback((id: string, updates: Partial<Toast>) => {
    setToasts((prev) =>
      prev.map((t) => (t.id === id ? { ...t, ...updates } : t))
    );
  }, []);

  const clearAll = useCallback(() => {
    setToasts([]);
  }, []);

  return (
    <ToastContext.Provider
      value={{ toasts, addToast, removeToast, updateToast, clearAll }}
    >
      {children}
      <ToastContainer />
    </ToastContext.Provider>
  );
};

// Hook for using toast
export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }

  const { addToast, removeToast, updateToast, clearAll } = context;

  return {
    success: (title: string, message?: string, duration = 3000) =>
      addToast({ type: 'success', title, message, duration }),

    error: (title: string, message?: string, duration = 5000) =>
      addToast({ type: 'error', title, message, duration }),

    warning: (title: string, message?: string, duration = 4000) =>
      addToast({ type: 'warning', title, message, duration }),

    info: (title: string, message?: string, duration = 3000) =>
      addToast({ type: 'info', title, message, duration }),

    loading: (title: string, message?: string) =>
      addToast({ type: 'loading', title, message, duration: 0 }),

    custom: (toast: Omit<Toast, 'id'>) => addToast(toast),

    dismiss: removeToast,
    update: updateToast,
    clearAll,
  };
};

// Toast Container (Portal)
const ToastContainer: React.FC = () => {
  const context = useContext(ToastContext);
  if (!context) return null;

  const { toasts, removeToast } = context;

  // Portal 생성
  const portalRoot = document.getElementById('toast-root') || document.body;

  return createPortal(
    <div
      className="fixed top-4 right-4 left-4 z-50 flex flex-col items-center gap-2 pointer-events-none sm:left-auto sm:w-96"
      role="region"
      aria-label="Notifications"
    >
      {toasts.map((toast) => (
        <ToastItem
          key={toast.id}
          toast={toast}
          onDismiss={() => removeToast(toast.id)}
        />
      ))}
    </div>,
    portalRoot
  );
};

// 개별 Toast Item
interface ToastItemProps {
  toast: Toast;
  onDismiss: () => void;
}

const ToastItem: React.FC<ToastItemProps> = ({ toast, onDismiss }) => {
  const [isExiting, setIsExiting] = useState(false);

  // 자동 dismiss
  useEffect(() => {
    if (toast.duration && toast.duration > 0) {
      const timer = setTimeout(() => {
        setIsExiting(true);
      }, toast.duration);
      return () => clearTimeout(timer);
    }
  }, [toast.duration]);

  // Exit 애니메이션 후 제거
  useEffect(() => {
    if (isExiting) {
      const timer = setTimeout(onDismiss, 300);
      return () => clearTimeout(timer);
    }
  }, [isExiting, onDismiss]);

  const handleDismiss = () => {
    setIsExiting(true);
  };

  // 아이콘 매핑
  const icons: Record<ToastType, React.ReactNode> = {
    success: <CheckCircle className="w-5 h-5 text-success-500" />,
    error: <XCircle className="w-5 h-5 text-danger-500" />,
    warning: <AlertTriangle className="w-5 h-5 text-warning-500" />,
    info: <Info className="w-5 h-5 text-primary-500" />,
    loading: <Loader2 className="w-5 h-5 text-primary-500 animate-spin" />,
  };

  // 스타일 매핑
  const styles: Record<ToastType, string> = {
    success: 'border-l-4 border-l-success-500 bg-success-50',
    error: 'border-l-4 border-l-danger-500 bg-danger-50',
    warning: 'border-l-4 border-l-warning-500 bg-warning-50',
    info: 'border-l-4 border-l-primary-500 bg-primary-50',
    loading: 'border-l-4 border-l-primary-500 bg-white',
  };

  return (
    <div
      className={cn(
        'pointer-events-auto w-full',
        'bg-white rounded-lg shadow-lg overflow-hidden',
        'transform transition-all duration-300 ease-out',
        styles[toast.type],
        isExiting
          ? 'opacity-0 translate-x-full'
          : 'opacity-100 translate-x-0 animate-toast-in'
      )}
      role="alert"
    >
      <div className="flex items-start gap-3 p-4">
        {/* Icon */}
        <div className="flex-shrink-0 mt-0.5">{icons[toast.type]}</div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-neutral-900">{toast.title}</p>
          {toast.message && (
            <p className="mt-1 text-sm text-neutral-600">{toast.message}</p>
          )}
          {toast.action && (
            <button
              onClick={() => {
                toast.action!.onClick();
                handleDismiss();
              }}
              className="mt-2 text-sm font-medium text-primary-600 hover:text-primary-700"
            >
              {toast.action.label}
            </button>
          )}
        </div>

        {/* Close Button */}
        {toast.type !== 'loading' && (
          <button
            onClick={handleDismiss}
            className="flex-shrink-0 p-1 rounded-full hover:bg-neutral-100 transition-colors"
          >
            <X className="w-4 h-4 text-neutral-400" />
          </button>
        )}
      </div>

      {/* Progress Bar (for timed toasts) */}
      {toast.duration && toast.duration > 0 && (
        <div className="h-1 bg-neutral-100">
          <div
            className={cn(
              'h-full transition-all ease-linear',
              toast.type === 'success' && 'bg-success-500',
              toast.type === 'error' && 'bg-danger-500',
              toast.type === 'warning' && 'bg-warning-500',
              toast.type === 'info' && 'bg-primary-500'
            )}
            style={{
              animation: `progress-shrink ${toast.duration}ms linear forwards`,
            }}
          />
        </div>
      )}

      <style>{`
        @keyframes progress-shrink {
          from { width: 100%; }
          to { width: 0%; }
        }
      `}</style>
    </div>
  );
};

/**
 * Simple Toast Functions (without context)
 * 간단한 사용을 위한 독립 함수들
 */
let toastContainer: HTMLDivElement | null = null;

const ensureContainer = () => {
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toast-root';
    document.body.appendChild(toastContainer);
  }
};

export const toast = {
  success: (title: string, message?: string) => {
    ensureContainer();
    const id = Math.random().toString(36).slice(2, 9);
    // 간단한 구현 - 실제 사용시 ToastProvider 사용 권장
    console.log(`[Toast Success] ${title}${message ? `: ${message}` : ''}`);
    return id;
  },
  error: (title: string, message?: string) => {
    ensureContainer();
    const id = Math.random().toString(36).slice(2, 9);
    console.log(`[Toast Error] ${title}${message ? `: ${message}` : ''}`);
    return id;
  },
  warning: (title: string, message?: string) => {
    ensureContainer();
    const id = Math.random().toString(36).slice(2, 9);
    console.log(`[Toast Warning] ${title}${message ? `: ${message}` : ''}`);
    return id;
  },
  info: (title: string, message?: string) => {
    ensureContainer();
    const id = Math.random().toString(36).slice(2, 9);
    console.log(`[Toast Info] ${title}${message ? `: ${message}` : ''}`);
    return id;
  },
};

export default ToastProvider;
