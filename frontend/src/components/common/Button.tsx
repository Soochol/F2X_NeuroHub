/**
 * Reusable Button Component
 */

import { type ReactNode, type ButtonHTMLAttributes } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'success';
  size?: 'small' | 'medium' | 'large';
  children: ReactNode;
}

export const Button = ({
  variant = 'primary',
  size = 'medium',
  children,
  disabled,
  ...props
}: ButtonProps) => {
  const baseStyles = {
    border: 'none',
    borderRadius: '4px',
    cursor: disabled ? 'not-allowed' : 'pointer',
    fontWeight: '500',
    transition: 'all 0.2s',
    opacity: disabled ? 0.6 : 1,
  };

  const variants = {
    primary: {
      backgroundColor: '#3498db',
      color: 'white',
    },
    secondary: {
      backgroundColor: '#95a5a6',
      color: 'white',
    },
    danger: {
      backgroundColor: '#e74c3c',
      color: 'white',
    },
    success: {
      backgroundColor: '#27ae60',
      color: 'white',
    },
  };

  const sizes = {
    small: {
      padding: '6px 12px',
      fontSize: '13px',
    },
    medium: {
      padding: '10px 16px',
      fontSize: '14px',
    },
    large: {
      padding: '12px 24px',
      fontSize: '16px',
    },
  };

  return (
    <button
      style={{
        ...baseStyles,
        ...variants[variant],
        ...sizes[size],
      }}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
};
