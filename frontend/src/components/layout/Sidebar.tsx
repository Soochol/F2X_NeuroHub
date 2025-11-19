/**
 * Sidebar Navigation Component
 */

import { Link, useLocation } from 'react-router-dom';
import { UserRole } from '@/types/api';
import { useAuth } from '@/contexts/AuthContext';
import {
  LayoutDashboard,
  Package,
  Search,
  CheckCircle,
  TrendingUp,
  Bell,
  Settings,
  type LucideIcon
} from 'lucide-react';

interface NavItem {
  path: string;
  label: string;
  icon: LucideIcon;
  roles?: UserRole[];
}

const navItems: NavItem[] = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/lots', label: 'LOT Management', icon: Package },
  { path: '/serials', label: 'Serial Tracking', icon: Search },
  { path: '/quality', label: 'Quality', icon: CheckCircle },
  { path: '/analytics', label: 'Analytics', icon: TrendingUp },
  { path: '/alerts', label: 'Alerts', icon: Bell },
  { path: '/admin', label: 'Admin', icon: Settings, roles: [UserRole.ADMIN, UserRole.MANAGER] },
];

interface SidebarProps {
  isCollapsed?: boolean;
}

export const Sidebar = ({ isCollapsed = false }: SidebarProps) => {
  const location = useLocation();
  const { user } = useAuth();

  const isActive = (path: string) => {
    return location.pathname === path || (path !== '/' && location.pathname.startsWith(path));
  };

  const canAccess = (item: NavItem) => {
    if (!item.roles) return true;
    return user && item.roles.includes(user.role);
  };

  return (
    <aside style={{
      width: isCollapsed ? '70px' : '240px',
      backgroundColor: 'var(--color-bg-primary)',
      color: 'var(--color-text-primary)',
      display: 'flex',
      flexDirection: 'column',
      padding: '20px 0',
      borderRight: '1px solid var(--color-border)',
      transition: 'width 0.3s ease',
      overflow: 'hidden',
    }}>
      <div style={{ padding: isCollapsed ? '0 10px' : '0 20px', marginBottom: '30px', textAlign: isCollapsed ? 'center' : 'left' }}>
        <h1 style={{ fontSize: isCollapsed ? '16px' : '20px', fontWeight: 'bold', margin: 0, color: 'var(--color-brand)', whiteSpace: 'nowrap' }}>
          {isCollapsed ? 'F2X' : 'F2X NeuroHub'}
        </h1>
        {!isCollapsed && (
          <p style={{ fontSize: '12px', color: 'var(--color-text-secondary)', margin: '5px 0 0 0' }}>MES System</p>
        )}
      </div>

      <nav style={{ flex: 1 }}>
        {navItems.filter(canAccess).map((item) => (
          <Link
            key={item.path}
            to={item.path}
            title={isCollapsed ? item.label : undefined}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: isCollapsed ? 'center' : 'flex-start',
              padding: isCollapsed ? '12px' : '12px 20px',
              textDecoration: 'none',
              color: isActive(item.path) ? 'var(--color-brand)' : 'var(--color-text-primary)',
              backgroundColor: isActive(item.path) ? 'var(--color-bg-tertiary)' : 'transparent',
              borderLeft: isActive(item.path) ? '4px solid var(--color-brand)' : '4px solid transparent',
              transition: 'all 0.2s',
            }}
          >
            <item.icon size={18} style={{ marginRight: isCollapsed ? '0' : '10px', flexShrink: 0 }} />
            {!isCollapsed && <span style={{ whiteSpace: 'nowrap' }}>{item.label}</span>}
          </Link>
        ))}
      </nav>

      {user && !isCollapsed && (
        <div style={{
          padding: '20px',
          borderTop: '1px solid var(--color-border)',
          fontSize: '14px',
        }}>
          <div style={{ fontWeight: 'bold' }}>{user.full_name}</div>
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '12px', marginTop: '5px' }}>{user.role}</div>
        </div>
      )}
    </aside>
  );
};
