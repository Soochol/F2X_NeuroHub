/**
 * Sidebar Navigation Component
 *
 * Collapsible sidebar with grouped menu items and station info
 */

import { useState, useEffect } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Layers,
  GitBranch,
  Wrench,
  FileText,
  Settings,
  Search,
  PanelLeft,
  PanelLeftClose,
  Activity,
  ClipboardList,
  type LucideIcon,
} from 'lucide-react';
import { ROUTES } from '../../constants';
import { useConnectionStore } from '../../stores/connectionStore';

interface NavItem {
  path: string;
  label: string;
  icon: LucideIcon;
}

interface NavSection {
  sectionLabel: string;
  items: NavItem[];
}

const navSections: NavSection[] = [
  {
    sectionLabel: 'MAIN',
    items: [
      { path: ROUTES.DASHBOARD, label: 'Dashboard', icon: LayoutDashboard },
      { path: ROUTES.BATCHES, label: 'Batches', icon: Layers },
    ],
  },
  {
    sectionLabel: 'OPERATIONS',
    items: [
      { path: ROUTES.SEQUENCES, label: 'Sequences', icon: GitBranch },
      { path: ROUTES.MANUAL, label: 'Manual Control', icon: Wrench },
      { path: ROUTES.RESULTS, label: 'Results', icon: ClipboardList },
    ],
  },
  {
    sectionLabel: 'SYSTEM',
    items: [
      { path: ROUTES.LOGS, label: 'Logs', icon: FileText },
      { path: ROUTES.MONITOR, label: 'Monitor', icon: Activity },
      { path: ROUTES.SETTINGS, label: 'Settings', icon: Settings },
    ],
  },
];

interface SidebarProps {
  isCollapsed: boolean;
  onToggle: () => void;
  stationId: string;
  stationName: string;
}

export function Sidebar({ isCollapsed, onToggle, stationId, stationName }: SidebarProps) {
  const location = useLocation();
  const [searchQuery, setSearchQuery] = useState('');
  const websocketStatus = useConnectionStore((state) => state.websocketStatus);

  // Save collapsed state to localStorage
  useEffect(() => {
    localStorage.setItem('station-sidebar-collapsed', JSON.stringify(isCollapsed));
  }, [isCollapsed]);

  const isActive = (path: string) => {
    if (location.pathname === path) return true;
    if (path !== '/' && location.pathname.startsWith(path)) return true;
    return false;
  };

  const renderNavItem = (item: NavItem) => {
    const itemActive = isActive(item.path);

    return (
      <NavLink
        key={item.path}
        to={item.path}
        title={isCollapsed ? item.label : undefined}
        className={`sidebar-nav-item flex items-center gap-3 px-4 py-2.5 mx-3 rounded-lg text-sm font-medium transition-all duration-200 ${
          isCollapsed ? 'justify-center mx-2 px-3' : ''
        }`}
        style={{
          backgroundColor: itemActive ? 'var(--color-brand-500)' : 'transparent',
          color: itemActive ? '#ffffff' : 'var(--color-text-secondary)',
        }}
        onMouseEnter={(e) => {
          if (!itemActive) {
            e.currentTarget.style.backgroundColor = 'var(--color-bg-tertiary)';
            e.currentTarget.style.color = 'var(--color-text-primary)';
          }
        }}
        onMouseLeave={(e) => {
          if (!itemActive) {
            e.currentTarget.style.backgroundColor = 'transparent';
            e.currentTarget.style.color = 'var(--color-text-secondary)';
          }
        }}
      >
        <item.icon className={`w-[18px] h-[18px] flex-shrink-0 ${itemActive ? 'opacity-100' : 'opacity-80'}`} />
        {!isCollapsed && (
          <span className="flex-1 whitespace-nowrap overflow-hidden text-ellipsis">
            {item.label}
          </span>
        )}
      </NavLink>
    );
  };

  const renderSection = (section: NavSection) => {
    return (
      <div key={section.sectionLabel} className="mb-4">
        {/* Section Label */}
        <div
          className={`px-4 py-2 text-[11px] font-semibold uppercase tracking-wide ${
            isCollapsed ? 'text-center px-0' : 'ml-3'
          }`}
          style={{ color: 'var(--color-text-tertiary)' }}
        >
          {isCollapsed ? section.sectionLabel.charAt(0) : section.sectionLabel}
        </div>

        {/* Section Items */}
        <div className="space-y-1">
          {section.items.map((item) => renderNavItem(item))}
        </div>
      </div>
    );
  };

  return (
    <aside
      className={`sidebar flex flex-col h-screen transition-all duration-300 ${
        isCollapsed ? 'w-[72px]' : 'w-[260px]'
      }`}
      style={{
        backgroundColor: 'var(--color-bg-secondary)',
        borderRight: '1px solid var(--color-border-default)',
      }}
    >
      {/* Logo and Toggle */}
      <div
        className="flex items-center justify-between p-4 min-h-[64px]"
        style={{ borderBottom: '1px solid var(--color-border-default)' }}
      >
        <div className="flex items-center gap-3">
          {/* Logo Icon */}
          <div
            className="w-9 h-9 rounded-[10px] flex items-center justify-center flex-shrink-0"
            style={{ backgroundColor: 'var(--color-brand-500)' }}
          >
            <Activity className="w-5 h-5 text-white" />
          </div>
          {!isCollapsed && (
            <span
              className="font-semibold whitespace-nowrap"
              style={{ color: 'var(--color-text-primary)' }}
            >
              Station UI
            </span>
          )}
        </div>

        {/* Toggle Button */}
        <button
          onClick={onToggle}
          className="p-2 rounded-lg transition-colors flex-shrink-0"
          style={{ color: 'var(--color-text-secondary)' }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = 'var(--color-bg-tertiary)';
            e.currentTarget.style.color = 'var(--color-text-primary)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'transparent';
            e.currentTarget.style.color = 'var(--color-text-secondary)';
          }}
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? <PanelLeft className="w-5 h-5" /> : <PanelLeftClose className="w-5 h-5" />}
        </button>
      </div>

      {/* Search Bar */}
      {!isCollapsed && (
        <div className="p-4 pb-2">
          <div
            className="flex items-center gap-2 rounded-lg px-3 py-2.5"
            style={{
              backgroundColor: 'var(--color-bg-tertiary)',
              border: '1px solid var(--color-border-default)',
            }}
          >
            <Search className="w-4 h-4 flex-shrink-0" style={{ color: 'var(--color-text-tertiary)' }} />
            <input
              type="text"
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-transparent border-none outline-none flex-1 text-sm"
              style={{ color: 'var(--color-text-primary)' }}
            />
          </div>
        </div>
      )}

      {/* Search Icon Only (Collapsed) */}
      {isCollapsed && (
        <div className="py-3 flex justify-center">
          <div
            className="w-10 h-10 rounded-lg flex items-center justify-center cursor-pointer transition-colors"
            style={{ backgroundColor: 'var(--color-bg-tertiary)' }}
          >
            <Search className="w-[18px] h-[18px]" style={{ color: 'var(--color-text-tertiary)' }} />
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto overflow-x-hidden py-2">
        {navSections.map(renderSection)}
      </nav>

      {/* Station Info */}
      <div className="p-4" style={{ borderTop: '1px solid var(--color-border-default)' }}>
        <div
          className={`flex items-center gap-3 p-2 rounded-[10px] ${
            isCollapsed ? 'justify-center' : ''
          }`}
          style={{ backgroundColor: 'var(--color-bg-tertiary)' }}
        >
          {/* Status Indicator */}
          <div
            className="w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0"
            style={{
              backgroundColor: websocketStatus === 'connected'
                ? 'rgba(62, 207, 142, 0.2)'
                : 'var(--color-bg-elevated)',
            }}
          >
            <div
              className={`w-3 h-3 rounded-full ${
                websocketStatus === 'connecting' ? 'animate-pulse' : ''
              }`}
              style={{
                backgroundColor: websocketStatus === 'connected'
                  ? 'var(--color-brand-500)'
                  : websocketStatus === 'connecting'
                  ? 'var(--color-warning)'
                  : 'var(--color-text-disabled)',
              }}
            />
          </div>

          {!isCollapsed && (
            <div className="flex-1 min-w-0">
              <div
                className="font-medium text-sm truncate"
                style={{ color: 'var(--color-text-primary)' }}
              >
                {stationName}
              </div>
              <div
                className="text-xs font-mono truncate"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                {stationId}
              </div>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
