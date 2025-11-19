/**
 * RoleBadge Component - Displays user role with color coding
 */

import { UserRole } from '@/types/api';

interface RoleBadgeProps {
  role: UserRole;
}

export const RoleBadge = ({ role }: RoleBadgeProps) => {
  const getRoleBadgeColor = (role: UserRole) => {
    switch (role) {
      case UserRole.ADMIN:
        return { backgroundColor: 'var(--color-error)', color: 'var(--color-text-inverse)' };
      case UserRole.MANAGER:
        return { backgroundColor: 'var(--color-warning)', color: 'var(--color-text-inverse)' };
      case UserRole.OPERATOR:
        return { backgroundColor: 'var(--color-info)', color: 'var(--color-text-inverse)' };
      default:
        return { backgroundColor: 'var(--color-text-tertiary)', color: 'var(--color-text-inverse)' };
    }
  };

  const colors = getRoleBadgeColor(role);

  return (
    <span
      style={{
        padding: '4px 12px',
        borderRadius: '12px',
        fontSize: '12px',
        fontWeight: '500',
        ...colors,
      }}
    >
      {role}
    </span>
  );
};
