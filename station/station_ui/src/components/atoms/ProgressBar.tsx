/**
 * Progress bar component.
 */

interface ProgressBarProps {
  value: number;
  max?: number;
  variant?: 'default' | 'success' | 'warning' | 'error';
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

const variantColors = {
  default: 'var(--color-brand-500)',
  success: '#22c55e',
  warning: '#f59e0b',
  error: '#ef4444',
};

const sizeClasses = {
  sm: 'h-1',
  md: 'h-2',
  lg: 'h-3',
};

export function ProgressBar({
  value,
  max = 100,
  variant = 'default',
  size = 'md',
  showLabel = false,
  className = '',
}: ProgressBarProps) {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));

  return (
    <div className={`w-full ${className}`}>
      <div
        className={`w-full rounded-full overflow-hidden ${sizeClasses[size]}`}
        style={{ backgroundColor: 'var(--color-border-default)' }}
      >
        <div
          className="h-full transition-all duration-300 ease-out"
          style={{
            width: `${percentage}%`,
            backgroundColor: variantColors[variant],
          }}
        />
      </div>
      {showLabel && (
        <div
          className="mt-1 text-xs text-right"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          {Math.round(percentage)}%
        </div>
      )}
    </div>
  );
}
