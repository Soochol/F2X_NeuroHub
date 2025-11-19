/**
 * Reusable Button Component with CSS Variables for Theming
 *
 * Supports multiple variants (primary, secondary, danger, ghost),
 * sizes (sm, md, lg), loading state, and forwardRef pattern.
 * Uses CSS variables from theme.css for consistent theming.
 */

import {
  type ReactNode,
  type ButtonHTMLAttributes,
  type CSSProperties,
  forwardRef,
  useState,
  useCallback,
} from 'react';

type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  /** Visual variant of the button */
  variant?: ButtonVariant;
  /** Button size */
  size?: ButtonSize;
  /** Button content */
  children: ReactNode;
  /** Loading state - shows spinner and disables interaction */
  isLoading?: boolean;
  /** Loading indicator component (defaults to spinner text) */
  loadingIndicator?: ReactNode;
  /** Full width button */
  fullWidth?: boolean;
}

/**
 * Base styles applied to all button variants
 */
const getBaseStyles = (disabled: boolean, fullWidth?: boolean): CSSProperties => ({
  display: fullWidth ? 'flex' : 'inline-flex',
  alignItems: 'center',
  justifyContent: 'center',
  gap: '0.5rem',
  border: 'none',
  borderRadius: 'var(--radius-base)',
  cursor: disabled ? 'not-allowed' : 'pointer',
  fontWeight: 'var(--font-weight-medium)',
  transition: 'all var(--transition-fast)',
  fontFamily: 'var(--font-sans)',
  whiteSpace: 'nowrap',
  width: fullWidth ? '100%' : 'auto',
  opacity: disabled ? 0.6 : 1,
  outline: 'none',
});

/**
 * Variant-specific styles using CSS variables
 */
const getVariantStyles = (
  variant: ButtonVariant,
  isHovered: boolean
): CSSProperties => {
  const baseVariantStyles: Record<ButtonVariant, CSSProperties> = {
    primary: {
      backgroundColor: 'var(--color-brand-400)',
      color: 'var(--color-text-inverse)',
      border: '1px solid transparent',
    },
    secondary: {
      backgroundColor: 'transparent',
      color: 'var(--color-text-primary)',
      border: '1px solid var(--color-border-strong)',
    },
    danger: {
      backgroundColor: 'var(--color-error)',
      color: 'var(--color-text-inverse)',
      border: '1px solid transparent',
    },
    ghost: {
      backgroundColor: 'transparent',
      color: 'var(--color-text-primary)',
      border: '1px solid transparent',
    },
  };

  const hoverStyles: Record<ButtonVariant, CSSProperties> = {
    primary: {
      backgroundColor: isHovered ? 'var(--color-brand-500)' : 'var(--color-brand-400)',
    },
    secondary: {
      backgroundColor: isHovered ? 'var(--color-bg-tertiary)' : 'transparent',
      borderColor: isHovered ? 'var(--color-text-primary)' : 'var(--color-border-strong)',
    },
    danger: {
      backgroundColor: 'var(--color-error)',
      filter: isHovered ? 'brightness(0.85)' : 'brightness(1)',
    },
    ghost: {
      backgroundColor: isHovered ? 'var(--color-bg-tertiary)' : 'transparent',
      color: isHovered ? 'var(--color-brand-400)' : 'var(--color-text-primary)',
    },
  };

  return {
    ...baseVariantStyles[variant],
    ...(isHovered ? hoverStyles[variant] : {}),
  };
};

/**
 * Size-specific padding and font sizes
 */
const getSizeStyles = (size: ButtonSize): CSSProperties => {
  const sizeStyles: Record<ButtonSize, CSSProperties> = {
    sm: {
      padding: '0.375rem 0.75rem',
      fontSize: 'var(--font-size-sm)',
      minHeight: '1.75rem',
    },
    md: {
      padding: '0.625rem 1rem',
      fontSize: 'var(--font-size-base)',
      minHeight: '2.25rem',
    },
    lg: {
      padding: '0.75rem 1.5rem',
      fontSize: 'var(--font-size-lg)',
      minHeight: '2.75rem',
    },
  };

  return sizeStyles[size];
};

/**
 * Button Component
 *
 * A flexible button component that supports multiple variants and sizes,
 * with built-in loading state support and theming via CSS variables.
 *
 * @example
 * ```tsx
 * <Button variant="primary" size="md" onClick={handleClick}>
 *   Click me
 * </Button>
 *
 * <Button variant="danger" isLoading={isSubmitting} disabled={isSubmitting}>
 *   Delete
 * </Button>
 * ```
 */
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      children,
      disabled = false,
      isLoading = false,
      loadingIndicator = 'Loading...',
      fullWidth = false,
      className = '',
      style = {},
      onMouseEnter,
      onMouseLeave,
      ...props
    },
    ref
  ) => {
    const [isHovered, setIsHovered] = useState(false);

    const handleMouseEnter = useCallback(
      (e: React.MouseEvent<HTMLButtonElement>) => {
        setIsHovered(true);
        onMouseEnter?.(e);
      },
      [onMouseEnter]
    );

    const handleMouseLeave = useCallback(
      (e: React.MouseEvent<HTMLButtonElement>) => {
        setIsHovered(false);
        onMouseLeave?.(e);
      },
      [onMouseLeave]
    );

    const isDisabled = disabled || isLoading;

    const buttonStyles: CSSProperties = {
      ...getBaseStyles(isDisabled, fullWidth),
      ...getSizeStyles(size),
      ...getVariantStyles(variant, isHovered && !isDisabled),
      ...style,
    };

    return (
      <button
        ref={ref}
        style={buttonStyles}
        disabled={isDisabled}
        className={className}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        {...props}
      >
        {isLoading ? loadingIndicator : children}
      </button>
    );
  }
);

Button.displayName = 'Button';
