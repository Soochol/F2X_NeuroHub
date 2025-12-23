/**
 * Input Component
 *
 * Modern styled input with label and error support
 */
import { forwardRef } from 'react';
import { cn } from '@/lib/cn';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: React.ReactNode;
  error?: string;
  hint?: string;
  unit?: string;
  required?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, unit, required, className, id, ...props }, ref) => {
    const inputId = id || (typeof label === 'string' ? label.toLowerCase().replace(/\s/g, '-') : undefined);

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className="block text-[11px] font-black text-neutral-400 mb-1.5 uppercase tracking-widest"
          >
            {label}
            {required && <span className="text-danger-500 ml-0.5">*</span>}
            {unit && (
              <span className="text-neutral-400 font-normal ml-1">({unit})</span>
            )}
          </label>
        )}
        <div className="relative">
          <input
            ref={ref}
            id={inputId}
            className={cn(
              'w-full px-4 py-3 text-base font-medium border rounded-xl',
              'transition-all duration-300',
              'focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              'text-dynamic bg-transparent',
              error
                ? 'border-danger-500/50 focus:ring-danger-500/30 focus:border-danger-500'
                : 'hover:border-primary-500/50',
              className
            )}
            style={{
              backgroundColor: 'var(--input-bg)',
              borderColor: 'var(--input-border)',
            }}
            {...props}
          />
        </div>
        {error && (
          <p className="mt-1.5 text-sm text-danger-500">{error}</p>
        )}
        {hint && !error && (
          <p className="mt-1.5 text-sm text-neutral-400">{hint}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
