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
        backgroundColor: isActive ? '#d5f4e6' : '#fee',
        color: isActive ? '#27ae60' : '#e74c3c',
      }}
    >
      {isActive ? 'Active' : 'Inactive'}
    </span>
  );
};
