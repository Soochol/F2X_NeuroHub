/**
 * ToastContainer Component
 *
 * Listens to toast events and displays toast notifications.
 * Toasts appear in the bottom-right corner and auto-dismiss after a duration.
 */

import { useState, useEffect, useCallback } from 'react';
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-react';
import type { ToastType } from '../../utils/toast';

interface Toast {
  id: string;
  type: ToastType;
  message: string;
  duration: number;
}

const typeConfig: Record<ToastType, { icon: React.ReactNode; bgColor: string; borderColor: string }> = {
  success: {
    icon: <CheckCircle className="w-5 h-5" />,
    bgColor: 'var(--color-status-success)',
    borderColor: 'var(--color-status-success)',
  },
  error: {
    icon: <XCircle className="w-5 h-5" />,
    bgColor: 'var(--color-status-error)',
    borderColor: 'var(--color-status-error)',
  },
  warning: {
    icon: <AlertTriangle className="w-5 h-5" />,
    bgColor: 'var(--color-status-warning)',
    borderColor: 'var(--color-status-warning)',
  },
  info: {
    icon: <Info className="w-5 h-5" />,
    bgColor: 'var(--color-accent-blue)',
    borderColor: 'var(--color-accent-blue)',
  },
};

const DEFAULT_DURATION = 5000; // 5 seconds

export function ToastContainer() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  const addToast = useCallback((type: ToastType, message: string, duration: number = DEFAULT_DURATION) => {
    const id = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const toast: Toast = { id, type, message, duration };

    setToasts((prev) => [...prev, toast]);

    // Auto-remove after duration
    if (duration > 0) {
      setTimeout(() => removeToast(id), duration);
    }
  }, [removeToast]);

  // Listen to toast events
  useEffect(() => {
    const handleToast = (event: CustomEvent<{ type: ToastType; message: string; duration?: number }>) => {
      const { type, message, duration } = event.detail;
      addToast(type, message, duration ?? DEFAULT_DURATION);
    };

    window.addEventListener('toast', handleToast as EventListener);
    return () => window.removeEventListener('toast', handleToast as EventListener);
  }, [addToast]);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed top-4 left-1/2 -translate-x-1/2 z-[9999] flex flex-col gap-2 max-w-md">
      {toasts.map((toast) => {
        const config = typeConfig[toast.type];
        return (
          <div
            key={toast.id}
            className="flex items-start gap-3 p-4 rounded-lg shadow-lg animate-slide-in-down"
            style={{
              backgroundColor: 'var(--color-bg-secondary)',
              border: `1px solid ${config.borderColor}`,
            }}
          >
            <div style={{ color: config.bgColor }} className="flex-shrink-0 mt-0.5">
              {config.icon}
            </div>
            <p
              className="flex-1 text-sm"
              style={{ color: 'var(--color-text-primary)' }}
            >
              {toast.message}
            </p>
            <button
              onClick={() => removeToast(toast.id)}
              className="flex-shrink-0 p-1 rounded hover:bg-white/10 transition-colors"
              style={{ color: 'var(--color-text-tertiary)' }}
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        );
      })}

      <style>{`
        @keyframes slide-in-down {
          from {
            transform: translateY(-100%);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }
        .animate-slide-in-down {
          animation: slide-in-down 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}
