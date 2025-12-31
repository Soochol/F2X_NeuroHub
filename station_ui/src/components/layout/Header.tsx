/**
 * Header Component
 *
 * Minimal header bar for sidebar layout
 */

import { useLocation } from 'react-router-dom';
import { Bell, Moon, Sun } from 'lucide-react';
import { useUIStore, useNotificationStore } from '../../stores';
import { NotificationPanel } from './NotificationPanel';

// Page title mapping
const pageTitles: Record<string, string> = {
  '/': 'Dashboard',
  '/ui': 'Dashboard',
  '/ui/': 'Dashboard',
  '/ui/batches': 'Batches',
  '/ui/sequences': 'Sequences',
  '/ui/manual': 'Manual Control',
  '/ui/logs': 'Logs',
  '/ui/settings': 'Settings',
};

export function Header() {
  const location = useLocation();
  const { theme, toggleTheme } = useUIStore();
  const { isOpen, togglePanel, getUnreadCount } = useNotificationStore();
  const isDark = theme === 'dark';
  const unreadCount = getUnreadCount();

  // Get page title from current path
  const pageTitle = pageTitles[location.pathname] || 'Station UI';

  return (
    <header
      className="flex items-center justify-between h-[60px] px-5 border-b transition-colors"
      style={{
        backgroundColor: 'var(--color-bg-secondary)',
        borderColor: 'var(--color-border-default)',
      }}
    >
      {/* Page Title */}
      <h1
        className="text-lg font-semibold"
        style={{ color: 'var(--color-text-primary)' }}
      >
        {pageTitle}
      </h1>

      {/* Right side controls */}
      <div className="flex items-center gap-3">
        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg transition-colors"
          style={{
            color: 'var(--color-text-secondary)',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = 'var(--color-bg-tertiary)';
            e.currentTarget.style.color = 'var(--color-text-primary)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'transparent';
            e.currentTarget.style.color = 'var(--color-text-secondary)';
          }}
          title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>

        {/* Notifications */}
        <div className="relative">
          <button
            data-notification-trigger
            onClick={togglePanel}
            className="p-2 rounded-lg transition-colors relative"
            style={{
              color: isOpen ? 'var(--color-text-primary)' : 'var(--color-text-secondary)',
              backgroundColor: isOpen ? 'var(--color-bg-tertiary)' : 'transparent',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = 'var(--color-bg-tertiary)';
              e.currentTarget.style.color = 'var(--color-text-primary)';
            }}
            onMouseLeave={(e) => {
              if (!isOpen) {
                e.currentTarget.style.backgroundColor = 'transparent';
                e.currentTarget.style.color = 'var(--color-text-secondary)';
              }
            }}
            title="Notifications"
          >
            <Bell className="w-5 h-5" />
            {unreadCount > 0 && (
              <span
                className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] flex items-center justify-center text-[10px] font-bold rounded-full px-1"
                style={{
                  backgroundColor: 'var(--color-status-error)',
                  color: 'white',
                }}
              >
                {unreadCount > 99 ? '99+' : unreadCount}
              </span>
            )}
          </button>
          <NotificationPanel />
        </div>
      </div>
    </header>
  );
}
