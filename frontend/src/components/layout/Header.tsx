/**
 * Header Component
 *
 * Top bar with alerts notification and user menu
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { alertsApi } from '@/api';

export const Header = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [unreadCount, setUnreadCount] = useState(0);
  const [showUserMenu, setShowUserMenu] = useState(false);

  // Poll for unread alerts every 30 seconds
  useEffect(() => {
    const fetchUnreadCount = async () => {
      try {
        const count = await alertsApi.getUnreadCount();
        setUnreadCount(count);
      } catch (error) {
        console.error('Failed to fetch unread alerts:', error);
      }
    };

    fetchUnreadCount();
    const interval = setInterval(fetchUnreadCount, 30000);

    return () => clearInterval(interval);
  }, []);

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return (
    <header style={{
      height: '60px',
      backgroundColor: 'white',
      borderBottom: '1px solid #e0e0e0',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'flex-end',
      padding: '0 20px',
      gap: '20px',
    }}>
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
        }}
      >
        🔔
        {unreadCount > 0 && (
          <span style={{
            position: 'absolute',
            top: '0',
            right: '0',
            backgroundColor: '#e74c3c',
            color: 'white',
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
      <div style={{ position: 'relative' }}>
        <button
          onClick={() => setShowUserMenu(!showUserMenu)}
          style={{
            background: 'none',
            border: '1px solid #e0e0e0',
            borderRadius: '4px',
            padding: '8px 12px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          <span>👤</span>
          <span>{user?.full_name}</span>
          <span style={{ fontSize: '12px' }}>▼</span>
        </button>

        {showUserMenu && (
          <div style={{
            position: 'absolute',
            top: '100%',
            right: 0,
            marginTop: '5px',
            backgroundColor: 'white',
            border: '1px solid #e0e0e0',
            borderRadius: '4px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
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
                color: '#e74c3c',
              }}
            >
              Logout
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
