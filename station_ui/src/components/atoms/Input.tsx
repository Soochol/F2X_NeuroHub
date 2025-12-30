/**
 * Input component.
 */

import { forwardRef, type InputHTMLAttributes } from 'react';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className = '', label, error, helperText, id, ...props }, ref) => {
    const inputId = id ?? label?.toLowerCase().replace(/\s+/g, '-');

    return (
      <div className="w-full">
        {label && (
          <label htmlFor={inputId} className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={`w-full px-3 py-2 bg-white dark:bg-zinc-800 border rounded-lg text-zinc-900 dark:text-white placeholder-zinc-400 dark:placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition-colors ${
            error ? 'border-red-500' : 'border-zinc-300 dark:border-zinc-700 hover:border-zinc-400 dark:hover:border-zinc-600'
          } ${className}`}
          {...props}
        />
        {error && <p className="mt-1.5 text-sm text-red-500 dark:text-red-400">{error}</p>}
        {helperText && !error && <p className="mt-1.5 text-sm text-zinc-600 dark:text-zinc-500">{helperText}</p>}
      </div>
    );
  }
);

Input.displayName = 'Input';
