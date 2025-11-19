/**
 * Reusable Select Component
 */

import { type SelectHTMLAttributes } from 'react';

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  options: Array<{ value: string; label: string }>;
}

export const Select = ({ label, error, options, ...props }: SelectProps) => {
  return (
    <div style={{ marginBottom: '15px' }}>
      {label && (
        <label
          style={{
            display: 'block',
            marginBottom: '5px',
            fontWeight: '500',
            color: '#2c3e50',
            fontSize: '14px',
          }}
        >
          {label}
          {props.required && <span style={{ color: '#e74c3c', marginLeft: '4px' }}>*</span>}
        </label>
      )}
      <select
        style={{
          width: '100%',
          padding: '10px',
          border: error ? '1px solid #e74c3c' : '1px solid #ddd',
          borderRadius: '4px',
          fontSize: '14px',
          boxSizing: 'border-box',
          backgroundColor: 'white',
        }}
        {...props}
      >
        <option value="">선택하세요</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && (
        <div
          style={{
            color: '#e74c3c',
            fontSize: '12px',
            marginTop: '4px',
          }}
        >
          {error}
        </div>
      )}
    </div>
  );
};
