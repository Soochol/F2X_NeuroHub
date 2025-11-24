/**
 * Reusable Select Component
 */

import { forwardRef, type SelectHTMLAttributes, type Ref } from 'react';

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  options: Array<{ value: string; label: string }>;
  /** Custom style for the wrapper (overrides default marginBottom) */
  wrapperStyle?: React.CSSProperties;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, options, wrapperStyle, id, ...props }, ref: Ref<HTMLSelectElement>) => {
    // Generate unique ID if not provided
    const selectId = id || `select-${Math.random().toString(36).substr(2, 9)}`;

    return (
      <div style={{ marginBottom: '15px', ...wrapperStyle }}>
        {label && (
          <label
            htmlFor={selectId}
            style={{
              display: 'block',
              marginBottom: '5px',
              fontWeight: '500',
              color: 'var(--color-text-primary)',
              fontSize: '14px',
            }}
          >
            {label}
            {props.required && <span style={{ color: 'var(--color-error)', marginLeft: '4px' }}>*</span>}
          </label>
        )}
        <select
          id={selectId}
          ref={ref}
          style={{
            width: '100%',
            padding: '10px',
            border: error ? '1px solid var(--color-error)' : '1px solid var(--color-input-border)',
            borderRadius: '4px',
            fontSize: '14px',
            boxSizing: 'border-box',
            backgroundColor: 'var(--color-input-bg)',
            color: 'var(--color-text-primary)',
          }}
          {...props}
        >
          <option value="">- Please select -</option>
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        {error && (
          <div
            style={{
              color: 'var(--color-error)',
              fontSize: '12px',
              marginTop: '4px',
            }}
          >
            {error}
          </div>
        )}
      </div>
    );
  }
);
