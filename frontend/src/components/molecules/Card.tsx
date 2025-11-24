/**
 * Reusable Card Component with CSS Variable Theming
 *
 * Supports:
 * - Theme-aware colors using CSS variables
 * - Multiple variants (default, elevated)
 * - Flexible padding options
 * - Optional header with title
 */

import { type ReactNode, type CSSProperties } from 'react';

type CardVariant = 'default' | 'elevated';
type PaddingSize = 'sm' | 'md' | 'lg';

interface CardProps {
  children: ReactNode;
  title?: ReactNode;
  variant?: CardVariant;
  padding?: PaddingSize;
  style?: CSSProperties;
  headerStyle?: CSSProperties;
  contentStyle?: CSSProperties;
}

const paddingMap: Record<PaddingSize, { header: string; content: string }> = {
  sm: { header: 'var(--spacing-3) var(--spacing-4)', content: 'var(--spacing-4)' },
  md: { header: 'var(--spacing-4) var(--spacing-5)', content: 'var(--spacing-5)' },
  lg: { header: 'var(--spacing-5) var(--spacing-6)', content: 'var(--spacing-6)' },
};

const variantStyles: Record<CardVariant, CSSProperties> = {
  default: {
    backgroundColor: 'var(--color-card-bg)',
    borderRadius: 'var(--radius-lg)',
    boxShadow: 'var(--shadow-base)',
    border: '1px solid var(--color-card-border)',
  },
  elevated: {
    backgroundColor: 'var(--color-bg-elevated)',
    borderRadius: 'var(--radius-lg)',
    boxShadow: 'var(--shadow-md)',
    border: '1px solid var(--color-card-border)',
  },
};

export const Card = ({
  children,
  title,
  variant = 'default',
  padding = 'md',
  style,
  headerStyle,
  contentStyle,
}: CardProps) => {
  const paddingValues = paddingMap[padding];
  const baseStyle = variantStyles[variant];

  return (
    <div
      style={{
        ...baseStyle,
        overflow: 'hidden',
        ...style,
      }}
    >
      {title && (
        <div
          style={{
            padding: paddingValues.header,
            borderBottom: '1px solid var(--color-card-border)',
            fontWeight: 'var(--font-weight-semibold)',
            fontSize: 'var(--font-size-base)',
            color: 'var(--color-text-primary)',
            ...headerStyle,
          }}
        >
          {title}
        </div>
      )}
      <div
        style={{
          padding: paddingValues.content,
          color: 'var(--color-text-primary)',
          ...contentStyle,
        }}
      >
        {children}
      </div>
    </div>
  );
};
