/**
 * Reusable Input Component
 *
 * A themed input component with CSS variable support for dark/light mode switching.
 * Supports labels, error states, and uses forwardRef for DOM access.
 */

import { forwardRef, type InputHTMLAttributes, type Ref } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  /** Label text displayed above the input */
  label?: string;
  /** Error message displayed below the input */
  error?: string;
  /** Custom className for the wrapper */
  wrapperClassName?: string;
  /** Custom className for the input element */
  inputClassName?: string;
  /** Custom style for the wrapper (overrides default marginBottom) */
  wrapperStyle?: React.CSSProperties;
}

/**
 * Input component with theme support
 *
 * @example
 * ```tsx
 * <Input
 *   label="Email"
 *   type="email"
 *   placeholder="Enter your email"
 *   required
 *   error={emailError}
 * />
 * ```
 */
export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, wrapperClassName, inputClassName, wrapperStyle, id, ...props }, ref: Ref<HTMLInputElement>) => {
    // Generate unique ID if not provided
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;

    return (
      <div
        className={wrapperClassName}
        style={{
          marginBottom: 'var(--spacing-4)',
          ...wrapperStyle,
        }}
      >
        {label && (
          <label
            htmlFor={inputId}
            style={{
              display: 'block',
              marginBottom: 'var(--spacing-1)',
              fontWeight: 'var(--font-weight-medium)',
              color: 'var(--color-text-primary)',
              fontSize: 'var(--font-size-sm)',
              transition: 'color var(--transition-fast)',
            }}
          >
            {label}
            {props.required && (
              <span
                style={{
                  color: 'var(--color-error)',
                  marginLeft: 'var(--spacing-1)',
                }}
              >
                *
              </span>
            )}
          </label>
        )}
        <input
          id={inputId}
          ref={ref}
          className={inputClassName}
          style={{
            width: '100%',
            padding: 'var(--spacing-2) var(--spacing-3)',
            backgroundColor: 'var(--color-input-bg)',
            border: error
              ? '1px solid var(--color-error)'
              : '1px solid var(--color-input-border)',
            borderRadius: 'var(--radius-base)',
            fontSize: 'var(--font-size-sm)',
            color: 'var(--color-text-primary)',
            boxSizing: 'border-box',
            transition: 'border-color var(--transition-fast), box-shadow var(--transition-fast)',
            outline: 'none',
          }}
          {...props}
          onFocus={(e) => {
            e.currentTarget.style.borderColor = 'var(--color-input-focus-border)';
            e.currentTarget.style.boxShadow = '0 0 0 3px var(--color-brand-alpha)';
            props.onFocus?.(e);
          }}
          onBlur={(e) => {
            e.currentTarget.style.borderColor = error
              ? 'var(--color-error)'
              : 'var(--color-input-border)';
            e.currentTarget.style.boxShadow = 'none';
            props.onBlur?.(e);
          }}
        />
        {error && (
          <div
            style={{
              color: 'var(--color-error)',
              fontSize: 'var(--font-size-xs)',
              marginTop: 'var(--spacing-1)',
              fontWeight: 'var(--font-weight-normal)',
            }}
          >
            {error}
          </div>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
