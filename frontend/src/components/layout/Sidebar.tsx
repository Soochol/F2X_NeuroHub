/**
 * Sidebar Navigation Component with Nested Menu Groups
 */

import { useState, useEffect } from 'react';
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
  AlertTriangle,
  PackagePlus,
  Layers,
  Scan,
  Box,
  BarChart3,
  ChevronDown,
  ChevronUp,
  Monitor,
  Users,
  Cog,
  Factory,
  Wrench,
  FileText,
  type LucideIcon
} from 'lucide-react';

interface NavItem {
  path: string;
  label: string;
  icon: LucideIcon;
  roles?: UserRole[];
}

interface NavGroup {
  id: string;
  label: string;
  icon: LucideIcon;
  items: NavItem[];
  roles?: UserRole[];
}

type NavConfig = (NavItem | NavGroup)[];

const navConfig: NavConfig = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/lots', label: 'LOT Issuance', icon: Package, roles: [UserRole.ADMIN, UserRole.MANAGER, UserRole.OPERATOR] },

  {
    id: 'wip',
    label: 'WIP',
    icon: Layers,
    items: [
      { path: '/wip-generation', label: 'WIP Generation', icon: PackagePlus },
      { path: '/wip-tracking', label: 'WIP Tracking', icon: Scan },
    ]
  },

  {
    id: 'serial',
    label: 'Serial',
    icon: Box,
    items: [
      { path: '/serials/generate', label: 'Serial Generation', icon: PackagePlus, roles: [UserRole.ADMIN, UserRole.MANAGER] },
      { path: '/serials', label: 'Serial Tracking', icon: Search },
    ]
  },

  {
    id: 'reports',
    label: 'Reports & Analytics',
    icon: BarChart3,
    roles: [UserRole.ADMIN, UserRole.MANAGER],
    items: [
      { path: '/quality', label: 'Quality', icon: CheckCircle, roles: [UserRole.ADMIN, UserRole.MANAGER] },
      { path: '/analytics', label: 'Analytics', icon: TrendingUp, roles: [UserRole.ADMIN, UserRole.MANAGER] },
    ]
  },

  {
    id: 'system',
    label: 'System',
    icon: FileText,
    roles: [UserRole.ADMIN, UserRole.MANAGER],
    items: [
      { path: '/alerts', label: 'Alerts', icon: Bell, roles: [UserRole.ADMIN, UserRole.MANAGER] },
      { path: '/error-dashboard', label: 'Error Dashboard', icon: AlertTriangle, roles: [UserRole.ADMIN] },
    ]
  },

  {
    id: 'admin',
    label: 'Admin',
    icon: Settings,
    roles: [UserRole.ADMIN],
    items: [
      { path: '/admin/users', label: 'Users', icon: Users, roles: [UserRole.ADMIN] },
      { path: '/admin/processes', label: 'Processes', icon: Cog, roles: [UserRole.ADMIN] },
      { path: '/admin/products', label: 'Products', icon: Package, roles: [UserRole.ADMIN] },
      { path: '/admin/production-lines', label: 'Production Lines', icon: Factory, roles: [UserRole.ADMIN] },
      { path: '/admin/equipment', label: 'Equipment', icon: Wrench, roles: [UserRole.ADMIN] },
      { path: '/admin/serial-inspector', label: 'Serial Inspector', icon: Search, roles: [UserRole.ADMIN] },
      { path: '/admin/lot-monitor', label: 'LOT Management', icon: Monitor, roles: [UserRole.ADMIN] },
    ]
  },
];

interface SidebarProps {
  isCollapsed?: boolean;
}

const isNavGroup = (item: NavItem | NavGroup): item is NavGroup => {
  return 'id' in item && 'items' in item;
};

export const Sidebar = ({ isCollapsed = false }: SidebarProps) => {
  const location = useLocation();
  const { user } = useAuth();
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set());

  // Initialize expanded groups from localStorage and current route
  useEffect(() => {
    const stored = localStorage.getItem('sidebar-expanded-groups');
    const storedGroups = stored ? new Set<string>(JSON.parse(stored)) : new Set<string>();

    // Auto-expand group containing current route
    const currentGroup = navConfig.find(item => {
      if (isNavGroup(item)) {
        return item.items.some(child =>
          location.pathname === child.path ||
          (child.path !== '/' && location.pathname.startsWith(child.path))
        );
      }
      return false;
    });

    if (currentGroup && isNavGroup(currentGroup)) {
      storedGroups.add(currentGroup.id);
    }

    setExpandedGroups(storedGroups);
  }, [location.pathname]);

  // Save to localStorage when expanded groups change
  useEffect(() => {
    localStorage.setItem('sidebar-expanded-groups', JSON.stringify([...expandedGroups]));
  }, [expandedGroups]);

  const toggleGroup = (groupId: string) => {
    setExpandedGroups(prev => {
      const next = new Set(prev);
      if (next.has(groupId)) {
        next.delete(groupId);
      } else {
        next.add(groupId);
      }
      return next;
    });
  };

  const isActive = (path: string) => {
    // Exact match first
    if (location.pathname === path) return true;

    // For non-root paths, only activate if it's a true parent path
    if (path !== '/' && location.pathname.startsWith(path + '/')) {
      return true;
    }

    return false;
  };

  const canAccess = (item: NavItem | NavGroup) => {
    if (!item.roles) return true;
    return user && item.roles.includes(user.role);
  };

  const renderNavItem = (item: NavItem, isChild = false) => {
    const itemActive = location.pathname === item.path;

    return (
      <Link
        key={item.path}
        to={item.path}
        title={isCollapsed ? item.label : undefined}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: isCollapsed ? 'center' : 'flex-start',
          padding: isCollapsed ? '12px' : isChild ? '10px 20px 10px 50px' : '12px 20px',
          textDecoration: 'none',
          color: itemActive ? 'var(--color-brand)' : 'var(--color-text-primary)',
          backgroundColor: itemActive ? 'var(--color-bg-tertiary)' : 'transparent',
          borderLeft: itemActive ? '4px solid var(--color-brand)' : '4px solid transparent',
          transition: 'all 0.2s',
          fontSize: isChild ? '13px' : '14px',
        }}
      >
        <item.icon size={16} style={{ marginRight: isCollapsed ? '0' : '10px', flexShrink: 0 }} />
        {!isCollapsed && <span style={{ whiteSpace: 'nowrap' }}>{item.label}</span>}
      </Link>
    );
  };

  const renderNavGroup = (group: NavGroup) => {
    const isExpanded = expandedGroups.has(group.id);
    const hasActiveChild = group.items.some(item => isActive(item.path));

    return (
      <div key={group.id}>
        <div
          onClick={() => !isCollapsed && toggleGroup(group.id)}
          title={isCollapsed ? group.label : undefined}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: isCollapsed ? 'center' : 'space-between',
            padding: isCollapsed ? '12px' : '12px 20px',
            cursor: isCollapsed ? 'default' : 'pointer',
            color: hasActiveChild ? 'var(--color-brand)' : 'var(--color-text-primary)',
            backgroundColor: hasActiveChild && !isExpanded ? 'var(--color-bg-tertiary)' : 'transparent',
            borderLeft: hasActiveChild && !isExpanded ? '4px solid var(--color-brand)' : '4px solid transparent',
            fontWeight: '500',
            transition: 'all 0.2s',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <group.icon size={18} style={{ marginRight: isCollapsed ? '0' : '10px', flexShrink: 0 }} />
            {!isCollapsed && <span style={{ whiteSpace: 'nowrap' }}>{group.label}</span>}
          </div>
          {!isCollapsed && (
            isExpanded ?
              <ChevronUp size={16} style={{ flexShrink: 0 }} /> :
              <ChevronDown size={16} style={{ flexShrink: 0 }} />
          )}
        </div>

        {!isCollapsed && isExpanded && (
          <div style={{
            overflow: 'hidden',
            transition: 'max-height 0.3s ease-in-out',
          }}>
            {group.items.filter(canAccess).map(item => renderNavItem(item, true))}
          </div>
        )}
      </div>
    );
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

      <nav style={{ flex: 1, overflowY: 'auto' }}>
        {navConfig.filter(canAccess).map(item => {
          if (isNavGroup(item)) {
            return renderNavGroup(item);
          }
          return renderNavItem(item);
        })}
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
