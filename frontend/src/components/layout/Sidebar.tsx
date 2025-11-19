/**
 * Sidebar Navigation Component
 */

import { Link, useLocation } from 'react-router-dom';
import { UserRole } from '@/types/api';
import { useAuth } from '@/contexts/AuthContext';

interface NavItem {
  path: string;
  label: string;
  icon?: string;
  roles?: UserRole[];
}

const navItems: NavItem[] = [
  { path: '/', label: 'Dashboard', icon: '📊' },
  { path: '/lots', label: 'LOT Management', icon: '📦' },
  { path: '/serials', label: 'Serial Tracking', icon: '🔍' },
  { path: '/quality', label: 'Quality', icon: '✓' },
  { path: '/analytics', label: 'Analytics', icon: '📈' },
  { path: '/alerts', label: 'Alerts', icon: '🔔' },
  { path: '/admin', label: 'Admin', icon: '⚙️', roles: [UserRole.ADMIN, UserRole.MANAGER] },
];

export const Sidebar = () => {
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
      width: '240px',
      backgroundColor: '#2c3e50',
      color: 'white',
      display: 'flex',
      flexDirection: 'column',
      padding: '20px 0',
    }}>
      <div style={{ padding: '0 20px', marginBottom: '30px' }}>
        <h1 style={{ fontSize: '20px', fontWeight: 'bold', margin: 0 }}>F2X NeuroHub</h1>
        <p style={{ fontSize: '12px', color: '#95a5a6', margin: '5px 0 0 0' }}>MES System</p>
      </div>

      <nav style={{ flex: 1 }}>
        {navItems.filter(canAccess).map((item) => (
          <Link
            key={item.path}
            to={item.path}
            style={{
              display: 'flex',
              alignItems: 'center',
              padding: '12px 20px',
              textDecoration: 'none',
              color: isActive(item.path) ? '#3498db' : '#ecf0f1',
              backgroundColor: isActive(item.path) ? '#34495e' : 'transparent',
              borderLeft: isActive(item.path) ? '4px solid #3498db' : '4px solid transparent',
              transition: 'all 0.2s',
            }}
          >
            <span style={{ marginRight: '10px', fontSize: '18px' }}>{item.icon}</span>
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>

      {user && (
        <div style={{
          padding: '20px',
          borderTop: '1px solid #34495e',
          fontSize: '14px',
        }}>
          <div style={{ fontWeight: 'bold' }}>{user.full_name}</div>
          <div style={{ color: '#95a5a6', fontSize: '12px', marginTop: '5px' }}>{user.role}</div>
        </div>
      )}
    </aside>
  );
};
