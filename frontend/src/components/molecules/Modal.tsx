/**
 * Reusable Modal Component
 */

import { forwardRef, type ReactNode, type Ref } from 'react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  footer?: ReactNode;
  width?: string;
}

export const Modal = forwardRef<HTMLDivElement, ModalProps>(
  ({ isOpen, onClose, title, children, footer, width = '600px' }, ref: Ref<HTMLDivElement>) => {
    if (!isOpen) return null;

    return (
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'var(--color-bg-overlay)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
        }}
        onClick={onClose}
      >
        <div
          ref={ref}
          style={{
            backgroundColor: 'var(--color-modal-bg)',
            borderRadius: 'var(--radius-lg)',
            width,
            maxWidth: '90vw',
            maxHeight: '90vh',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            boxShadow: 'var(--shadow-xl)',
            border: '1px solid var(--color-modal-border)',
          }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div
            style={{
              padding: '20px',
              borderBottom: '1px solid var(--color-modal-border)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <h2 style={{ fontSize: '18px', fontWeight: 'bold', margin: 0 }}>{title}</h2>
            <button
              onClick={onClose}
              style={{
                background: 'none',
                border: 'none',
                fontSize: '24px',
                cursor: 'pointer',
                color: 'var(--color-text-secondary)',
              }}
            >
              ×
            </button>
          </div>

          {/* Body */}
          <div
            style={{
              padding: '20px',
              overflow: 'auto',
              flex: 1,
            }}
          >
            {children}
          </div>

          {/* Footer */}
          {footer && (
            <div
              style={{
                padding: '15px 20px',
                borderTop: '1px solid var(--color-modal-border)',
                display: 'flex',
                justifyContent: 'flex-end',
                gap: '10px',
              }}
            >
              {footer}
            </div>
          )}
        </div>
      </div>
    );
  }
);
