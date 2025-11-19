/**
 * StatusBadge Component - Displays Active/Inactive status
 */

interface StatusBadgeProps {
  isActive: boolean;
}

export const StatusBadge = ({ isActive }: StatusBadgeProps) => {
  return (
    <span
      style={{
        padding: '4px 12px',
        borderRadius: '12px',
        fontSize: '12px',
        fontWeight: '500',
        backgroundColor: isActive ? 'var(--color-badge-success-bg)' : 'var(--color-badge-error-bg)',
        color: isActive ? 'var(--color-success)' : 'var(--color-error)',
      }}
    >
      {isActive ? 'Active' : 'Inactive'}
    </span>
  );
};
