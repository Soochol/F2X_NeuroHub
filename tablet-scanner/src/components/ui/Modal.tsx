/**
 * Modal Component
 *
 * Modern modal dialog with backdrop
 */
import { useEffect, useCallback } from 'react';
import { X } from 'lucide-react';
import { cn } from '@/lib/cn';

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'full';
  showCloseButton?: boolean;
  closeOnBackdrop?: boolean;
  variant?: 'white' | 'glass';
  className?: string;
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  showCloseButton = true,
  closeOnBackdrop = true,
  variant = 'white',
  className,
}) => {
  // Handle escape key
  const handleEscape = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    },
    [onClose]
  );

  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = '';
    };
  }, [isOpen, handleEscape]);

  if (!isOpen) return null;

  const sizes = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    full: 'max-w-full mx-4',
  };

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6"
      role="dialog"
      aria-modal="true"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-primary-900/60 backdrop-blur-md"
        onClick={closeOnBackdrop ? onClose : undefined}
        aria-hidden="true"
      />

      {/* Modal content */}
      <div
        className={cn(
          'relative w-full overflow-hidden',
          variant === 'glass'
            ? 'glass-card border-white/20 shadow-[0_32px_64px_-12px_rgba(0,0,0,0.5)]'
            : 'bg-white rounded-xl shadow-lg',
          'max-h-[90vh] flex flex-col',
          'animate-in fade-in zoom-in-95 duration-300 ease-out',
          sizes[size],
          className
        )}
      >
        {/* Header */}
        {(title || showCloseButton) && (
          <div className={cn(
            'flex items-center justify-between p-5 border-b shrink-0',
            variant === 'glass' ? 'border-white/10' : 'border-neutral-200'
          )}>
            {title && (
              <h2 className={cn(
                'text-xl font-bold tracking-tight',
                variant === 'glass' ? 'text-white' : 'text-neutral-800'
              )}>{title}</h2>
            )}
            {showCloseButton && (
              <button
                onClick={onClose}
                className={cn(
                  'p-2 rounded-xl transition-all duration-200',
                  variant === 'glass'
                    ? 'text-white/40 hover:text-white hover:bg-white/10'
                    : 'text-neutral-400 hover:text-neutral-600 hover:bg-neutral-100',
                  !title && 'ml-auto'
                )}
                aria-label="닫기"
              >
                <X className="w-6 h-6" />
              </button>
            )}
          </div>
        )}

        {/* Body */}
        <div className="p-6 overflow-auto flex-1">{children}</div>
      </div>
    </div>
  );
};

// Modal Footer for action buttons
export interface ModalFooterProps {
  children: React.ReactNode;
  className?: string;
}

export const ModalFooter: React.FC<ModalFooterProps> = ({ children, className }) => {
  return (
    <div
      className={cn(
        'flex gap-3 pt-4 mt-4 border-t border-neutral-200',
        className
      )}
    >
      {children}
    </div>
  );
};
