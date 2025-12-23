/**
 * Badge Component
 *
 * Status badges for displaying process states
 */
import { cn } from '@/lib/cn';

export interface BadgeProps {
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'neutral';
  size?: 'sm' | 'md';
  children: React.ReactNode;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  variant = 'neutral',
  size = 'md',
  children,
  className,
}) => {
  const variants = {
    success: 'bg-success-50 text-success-600 border-success-200',
    warning: 'bg-warning-50 text-warning-600 border-warning-200',
    danger: 'bg-danger-50 text-danger-600 border-danger-200',
    info: 'bg-primary-50 text-primary-600 border-primary-200',
    neutral: 'bg-neutral-100 text-neutral-600 border-neutral-200',
  };

  const sizes = {
    sm: 'px-1.5 py-0.5 text-xs',
    md: 'px-2 py-0.5 text-sm',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center',
        'font-medium rounded-full border',
        variants[variant],
        sizes[size],
        className
      )}
    >
      {children}
    </span>
  );
};

// Status-specific badge presets
export const StatusBadge: React.FC<{
  status: 'completed' | 'in-progress' | 'pending' | 'pass' | 'fail';
  size?: 'sm' | 'md';
}> = ({ status, size = 'md' }) => {
  const config = {
    completed: { variant: 'success' as const, label: '완료' },
    'in-progress': { variant: 'warning' as const, label: '진행중' },
    pending: { variant: 'neutral' as const, label: '대기' },
    pass: { variant: 'success' as const, label: 'PASS' },
    fail: { variant: 'danger' as const, label: 'FAIL' },
  };

  const { variant, label } = config[status];

  return (
    <Badge variant={variant} size={size}>
      {label}
    </Badge>
  );
};
