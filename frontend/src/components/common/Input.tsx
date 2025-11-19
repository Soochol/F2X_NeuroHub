/**
 * Reusable Input Component
 */

import { type InputHTMLAttributes } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = ({ label, error, ...props }: InputProps) => {
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
      <input
        style={{
          width: '100%',
          padding: '10px',
          border: error ? '1px solid #e74c3c' : '1px solid #ddd',
          borderRadius: '4px',
          fontSize: '14px',
          boxSizing: 'border-box',
        }}
        {...props}
      />
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
