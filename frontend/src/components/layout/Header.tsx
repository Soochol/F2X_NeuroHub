/**
 * Header Component
 *
 * Top bar with alerts notification, theme toggle, and user menu
 */

import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { alertsApi } from '@/api';
import { ThemeToggleIcon } from '@/components/atoms';
import { Bell, User, ChevronDown } from 'lucide-react';
import Logger from '@/utils/logger';

export const Header = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [unreadCount, setUnreadCount] = useState(0);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);

  // Poll for unread alerts every 30 seconds
  useEffect(() => {
    const fetchUnreadCount = async () => {
      try {
        const count = await alertsApi.getUnreadCount();
        setUnreadCount(count);
      } catch (error) {
        Logger.error('Failed to fetch unread alerts:', error);
      }
    };

    fetchUnreadCount();
    const interval = setInterval(fetchUnreadCount, 30000);

    return () => clearInterval(interval);
  }, []);

  // Close user menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setShowUserMenu(false);
      }
    };

    if (showUserMenu) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showUserMenu]);

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      Logger.error('Logout error:', error);
    }
  };

  return (
    <header style={{
      height: '60px',
      backgroundColor: 'var(--color-bg-primary)',
      borderBottom: '1px solid var(--color-border)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'flex-end',
      padding: '0 20px',
    }}>
      {/* Right side controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {/* Theme Toggle */}
        <ThemeToggleIcon />

        {/* Alerts Bell */}
        <button
          onClick={() => navigate('/alerts')}
          style={{
            position: 'relative',
            background: 'none',
            border: 'none',
            fontSize: '24px',
            cursor: 'pointer',
            padding: '5px',
            color: 'var(--color-text-primary)',
          }}
        >
          <Bell size={24} />
          {unreadCount > 0 && (
            <span style={{
              position: 'absolute',
              top: '0',
              right: '0',
              backgroundColor: 'var(--color-error)',
              color: 'var(--color-text-inverse)',
              fontSize: '12px',
              fontWeight: 'bold',
              borderRadius: '50%',
              width: '20px',
              height: '20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}>
              {unreadCount > 99 ? '99+' : unreadCount}
            </span>
          )}
        </button>

        {/* User Menu */}
        <div style={{ position: 'relative' }} ref={userMenuRef}>
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            style={{
              background: 'none',
              border: '1px solid var(--color-border)',
              borderRadius: '4px',
              padding: '8px 12px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              color: 'var(--color-text-primary)',
            }}
          >
            <User size={16} />
            <span>{user?.full_name}</span>
            <ChevronDown size={12} />
          </button>

          {showUserMenu && (
            <div style={{
              position: 'absolute',
              top: '100%',
              right: 0,
              marginTop: '5px',
              backgroundColor: 'var(--color-bg-secondary)',
              border: '1px solid var(--color-border)',
              borderRadius: '4px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
              minWidth: '150px',
              zIndex: 1000,
            }}>
              <button
                onClick={handleLogout}
                style={{
                  width: '100%',
                  padding: '10px 15px',
                  background: 'none',
                  border: 'none',
                  textAlign: 'left',
                  cursor: 'pointer',
                  color: 'var(--color-error)',
                }}
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
