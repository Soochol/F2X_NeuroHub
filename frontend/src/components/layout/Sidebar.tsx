/**
 * Sidebar Navigation Component
 *
 * Collapsible sidebar with grouped menu items, search bar, and user profile
 */

import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { UserRole } from '@/types/api';
import { useAuth } from '@/contexts/AuthContext';
import {
  LayoutDashboard,
  Package,
  Search,
  Bell,
  Settings,
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
  Activity,
  PanelLeft,
  PanelLeftClose,
  LogOut,
  Server,
  type LucideIcon
} from 'lucide-react';

interface NavItem {
  path: string;
  label: string;
  icon: LucideIcon;
  roles?: UserRole[];
  badge?: number;
}

interface NavGroup {
  id: string;
  label: string;
  icon: LucideIcon;
  items: NavItem[];
  roles?: UserRole[];
}

interface NavSection {
  sectionLabel: string;
  items: (NavItem | NavGroup)[];
}

const navSections: NavSection[] = [
  {
    sectionLabel: 'MAIN',
    items: [
      { path: '/', label: 'Dashboard', icon: LayoutDashboard },
      { path: '/lots', label: 'LOT Issuance', icon: Package, roles: [UserRole.ADMIN, UserRole.MANAGER, UserRole.OPERATOR] },
    ]
  },
  {
    sectionLabel: 'PRODUCTION',
    items: [
      {
        id: 'wip',
        label: 'WIP',
        icon: Layers,
        items: [
          { path: '/wip/generate', label: 'WIP Generation', icon: PackagePlus },
          { path: '/wip/tracking', label: 'WIP Tracking', icon: Scan },
          { path: '/wip/list', label: 'WIP List by LOT', icon: Package },
        ]
      },
      {
        id: 'serial',
        label: 'Serial',
        icon: Box,
        items: [
          { path: '/serials/generate', label: 'Serial Generation', icon: PackagePlus, roles: [UserRole.ADMIN, UserRole.MANAGER] },
          { path: '/serials/tracking', label: 'Serial Tracking', icon: Search },
          { path: '/serials/list', label: 'Serial List by LOT', icon: Package },
        ]
      },
    ]
  },
  {
    sectionLabel: 'MONITORING',
    items: [
      { path: '/stations', label: 'Station Monitor', icon: Server },
    ]
  },
  {
    sectionLabel: 'QUALITY',
    items: [
      { path: '/quality/defect-rate', label: 'Defect Analysis', icon: BarChart3, roles: [UserRole.ADMIN, UserRole.MANAGER] },
      { path: '/quality/measurements', label: 'Measurements', icon: Activity, roles: [UserRole.ADMIN, UserRole.MANAGER] },
    ]
  },
  {
    sectionLabel: 'ADMIN',
    items: [
      {
        id: 'admin',
        label: 'Settings',
        icon: Settings,
        roles: [UserRole.ADMIN],
        items: [
          { path: '/admin/users', label: 'Users', icon: Users, roles: [UserRole.ADMIN] },
          { path: '/admin/processes', label: 'Processes', icon: Cog, roles: [UserRole.ADMIN] },
          { path: '/admin/products', label: 'Products', icon: Package, roles: [UserRole.ADMIN] },
          { path: '/admin/production-lines', label: 'Production Lines', icon: Factory, roles: [UserRole.ADMIN] },
          { path: '/admin/equipment', label: 'Equipment', icon: Wrench, roles: [UserRole.ADMIN] },
        ]
      },
      { path: '/admin/serial-inspector', label: 'Serial Inspector', icon: Search, roles: [UserRole.ADMIN] },
      { path: '/admin/lot-monitor', label: 'LOT Monitor', icon: Monitor, roles: [UserRole.ADMIN] },
    ]
  },
  {
    sectionLabel: 'OTHERS',
    items: [
      { path: '/alerts', label: 'Notifications', icon: Bell },
    ]
  },
];

interface SidebarProps {
  isCollapsed: boolean;
  onToggle: () => void;
}

const isNavGroup = (item: NavItem | NavGroup): item is NavGroup => {
  return 'id' in item && 'items' in item;
};

const getInitialExpandedGroups = (pathname: string): Set<string> => {
  const stored = localStorage.getItem('sidebar-expanded-groups');
  const storedGroups = stored ? new Set<string>(JSON.parse(stored)) : new Set<string>();

  // Auto-expand group containing current route
  for (const section of navSections) {
    for (const item of section.items) {
      if (isNavGroup(item)) {
        if (item.items.some(child =>
          pathname === child.path ||
          (child.path !== '/' && pathname.startsWith(child.path))
        )) {
          storedGroups.add(item.id);
        }
      }
    }
  }

  return storedGroups;
};

export const Sidebar = ({ isCollapsed, onToggle }: SidebarProps) => {
  const location = useLocation();
  const { user, logout } = useAuth();
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(() =>
    getInitialExpandedGroups(location.pathname)
  );
  const [searchQuery, setSearchQuery] = useState('');

  // Update expanded groups when route changes - only add if not already expanded
  useEffect(() => {
    for (const section of navSections) {
      for (const item of section.items) {
        if (isNavGroup(item)) {
          if (item.items.some(child =>
            location.pathname === child.path ||
            (child.path !== '/' && location.pathname.startsWith(child.path))
          )) {
            // eslint-disable-next-line react-hooks/set-state-in-effect -- Intentional: expanding sidebar group on route change
            setExpandedGroups(prev => {
              if (prev.has(item.id)) return prev;
              const next = new Set(prev);
              next.add(item.id);
              return next;
            });
          }
        }
      }
    }
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
    if (location.pathname === path) return true;
    if (path !== '/' && location.pathname.startsWith(path + '/')) return true;
    return false;
  };

  const canAccess = (item: NavItem | NavGroup) => {
    if (!item.roles) return true;
    return user && item.roles.includes(user.role);
  };

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const renderNavItem = (item: NavItem, isChild = false) => {
    const itemActive = isActive(item.path);

    return (
      <Link
        key={item.path}
        to={item.path}
        title={isCollapsed ? item.label : undefined}
        className="sidebar-nav-item"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: isCollapsed ? 'center' : 'flex-start',
          padding: isCollapsed ? '12px' : isChild ? '10px 16px 10px 44px' : '10px 16px',
          textDecoration: 'none',
          color: itemActive ? 'var(--color-text-inverse)' : 'var(--color-text-primary)',
          backgroundColor: itemActive ? 'var(--color-brand)' : 'transparent',
          borderRadius: '8px',
          margin: isCollapsed ? '4px 8px' : '2px 12px',
          transition: 'all 0.2s ease',
          fontSize: '14px',
          fontWeight: itemActive ? '500' : '400',
          gap: '12px',
        }}
      >
        <item.icon size={18} style={{ flexShrink: 0, opacity: itemActive ? 1 : 0.8 }} />
        {!isCollapsed && (
          <>
            <span style={{ flex: 1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {item.label}
            </span>
            {item.badge && (
              <span style={{
                backgroundColor: 'var(--color-bg-tertiary)',
                color: 'var(--color-text-secondary)',
                fontSize: '12px',
                padding: '2px 8px',
                borderRadius: '10px',
                fontWeight: '500',
              }}>
                {item.badge}
              </span>
            )}
          </>
        )}
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
          className="sidebar-nav-group"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: isCollapsed ? 'center' : 'space-between',
            padding: isCollapsed ? '12px' : '10px 16px',
            cursor: isCollapsed ? 'default' : 'pointer',
            color: hasActiveChild ? 'var(--color-brand)' : 'var(--color-text-primary)',
            borderRadius: '8px',
            margin: isCollapsed ? '4px 8px' : '2px 12px',
            transition: 'all 0.2s ease',
            fontSize: '14px',
            fontWeight: '500',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <group.icon size={18} style={{ flexShrink: 0, opacity: hasActiveChild ? 1 : 0.8 }} />
            {!isCollapsed && (
              <span style={{ whiteSpace: 'nowrap' }}>{group.label}</span>
            )}
          </div>
          {!isCollapsed && (
            isExpanded ?
              <ChevronUp size={16} style={{ flexShrink: 0, opacity: 0.6 }} /> :
              <ChevronDown size={16} style={{ flexShrink: 0, opacity: 0.6 }} />
          )}
        </div>

        {!isCollapsed && isExpanded && (
          <div style={{ overflow: 'hidden' }}>
            {group.items.filter(canAccess).map(item => renderNavItem(item, true))}
          </div>
        )}
      </div>
    );
  };

  const renderSection = (section: NavSection) => {
    const visibleItems = section.items.filter(canAccess);
    if (visibleItems.length === 0) return null;

    return (
      <div key={section.sectionLabel} style={{ marginBottom: '16px' }}>
        {/* Section Label */}
        <div style={{
          padding: isCollapsed ? '8px 0' : '8px 16px',
          fontSize: '11px',
          fontWeight: '600',
          color: 'var(--color-text-tertiary)',
          textTransform: 'uppercase',
          letterSpacing: '0.5px',
          textAlign: isCollapsed ? 'center' : 'left',
          marginLeft: isCollapsed ? 0 : '12px',
        }}>
          {isCollapsed ? section.sectionLabel.charAt(0) : section.sectionLabel}
        </div>

        {/* Section Items */}
        {visibleItems.map(item => {
          if (isNavGroup(item)) {
            return renderNavGroup(item);
          }
          return renderNavItem(item);
        })}
      </div>
    );
  };

  return (
    <aside
      className="sidebar"
      style={{
        width: isCollapsed ? '72px' : '260px',
        backgroundColor: 'var(--color-bg-primary)',
        display: 'flex',
        flexDirection: 'column',
        borderRight: '1px solid var(--color-border)',
        transition: 'width 0.3s ease',
        overflow: 'hidden',
        height: '100vh',
      }}
    >
      {/* Logo and Toggle */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '16px',
        borderBottom: '1px solid var(--color-border)',
        minHeight: '64px',
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
        }}>
          {/* Logo Icon */}
          <div style={{
            width: '36px',
            height: '36px',
            backgroundColor: 'var(--color-brand)',
            borderRadius: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontWeight: 'bold',
            fontSize: '16px',
            flexShrink: 0,
          }}>
            F2
          </div>
          {!isCollapsed && (
            <span style={{
              fontWeight: '600',
              fontSize: '16px',
              color: 'var(--color-text-primary)',
              whiteSpace: 'nowrap',
            }}>
              NeuroHub
            </span>
          )}
        </div>

        {/* Toggle Button */}
        <button
          onClick={onToggle}
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            padding: '8px',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--color-text-secondary)',
            transition: 'all 0.2s',
            flexShrink: 0,
          }}
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? <PanelLeft size={20} /> : <PanelLeftClose size={20} />}
        </button>
      </div>

      {/* Search Bar */}
      {!isCollapsed && (
        <div style={{ padding: '16px 16px 8px' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            backgroundColor: 'var(--color-bg-secondary)',
            borderRadius: '8px',
            padding: '10px 12px',
            gap: '8px',
            border: '1px solid var(--color-border)',
          }}>
            <Search size={16} style={{ color: 'var(--color-text-tertiary)', flexShrink: 0 }} />
            <input
              type="text"
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                background: 'none',
                border: 'none',
                outline: 'none',
                flex: 1,
                fontSize: '14px',
                color: 'var(--color-text-primary)',
              }}
            />
          </div>
        </div>
      )}

      {/* Search Icon Only (Collapsed) */}
      {isCollapsed && (
        <div style={{
          padding: '12px 0',
          display: 'flex',
          justifyContent: 'center',
        }}>
          <div style={{
            width: '40px',
            height: '40px',
            backgroundColor: 'var(--color-bg-secondary)',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
          }}>
            <Search size={18} style={{ color: 'var(--color-text-tertiary)' }} />
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav style={{
        flex: 1,
        overflowY: 'auto',
        overflowX: 'hidden',
        padding: '8px 0',
      }}>
        {navSections.map(renderSection)}
      </nav>

      {/* User Profile */}
      {user && (
        <div style={{
          borderTop: '1px solid var(--color-border)',
          padding: '16px',
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: isCollapsed ? '0' : '8px',
            backgroundColor: 'var(--color-bg-secondary)',
            borderRadius: '10px',
            justifyContent: isCollapsed ? 'center' : 'flex-start',
          }}>
            {/* Avatar */}
            <div style={{
              width: '36px',
              height: '36px',
              borderRadius: '50%',
              backgroundColor: 'var(--color-brand)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontWeight: '600',
              fontSize: '14px',
              flexShrink: 0,
            }}>
              {user.full_name?.charAt(0).toUpperCase() || 'U'}
            </div>

            {!isCollapsed && (
              <>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{
                    fontWeight: '500',
                    fontSize: '14px',
                    color: 'var(--color-text-primary)',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                  }}>
                    {user.full_name}
                  </div>
                  <div style={{
                    fontSize: '12px',
                    color: 'var(--color-text-tertiary)',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                  }}>
                    {user.email || user.role}
                  </div>
                </div>

                {/* Logout Button */}
                <button
                  onClick={handleLogout}
                  title="Logout"
                  style={{
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    padding: '8px',
                    borderRadius: '6px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'var(--color-text-secondary)',
                    transition: 'all 0.2s',
                  }}
                >
                  <LogOut size={18} />
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </aside>
  );
};
