/**
 * NotificationPanel Component
 *
 * Dropdown panel for displaying notifications.
 * Shows recent notifications with read/unread status.
 */

import { useEffect, useRef } from 'react';
import { X, CheckCheck, Trash2, AlertCircle, CheckCircle, AlertTriangle, Info } from 'lucide-react';
import { useNotificationStore, type Notification, type NotificationType } from '../../stores';

const typeIcons: Record<NotificationType, React.ReactNode> = {
  info: <Info className="w-4 h-4" />,
  success: <CheckCircle className="w-4 h-4" />,
  warning: <AlertTriangle className="w-4 h-4" />,
  error: <AlertCircle className="w-4 h-4" />,
};

const typeColors: Record<NotificationType, string> = {
  info: 'var(--color-accent-blue)',
  success: 'var(--color-status-success)',
  warning: 'var(--color-status-warning)',
  error: 'var(--color-status-error)',
};

function formatTimestamp(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  return date.toLocaleDateString();
}

interface NotificationItemProps {
  notification: Notification;
  onMarkAsRead: (id: string) => void;
  onRemove: (id: string) => void;
}

function NotificationItem({ notification, onMarkAsRead, onRemove }: NotificationItemProps) {
  return (
    <div
      className="px-4 py-3 border-b transition-colors cursor-pointer"
      style={{
        backgroundColor: notification.read ? 'transparent' : 'var(--color-bg-tertiary)',
        borderColor: 'var(--color-border-default)',
      }}
      onClick={() => !notification.read && onMarkAsRead(notification.id)}
    >
      <div className="flex items-start gap-3">
        <div
          className="mt-0.5 flex-shrink-0"
          style={{ color: typeColors[notification.type] }}
        >
          {typeIcons[notification.type]}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <span
              className="font-medium text-sm truncate"
              style={{ color: 'var(--color-text-primary)' }}
            >
              {notification.title}
            </span>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onRemove(notification.id);
              }}
              className="p-1 rounded hover:bg-red-500/20 transition-colors flex-shrink-0"
              style={{ color: 'var(--color-text-tertiary)' }}
              title="Remove notification"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
          <p
            className="text-xs mt-1 line-clamp-2"
            style={{ color: 'var(--color-text-secondary)' }}
          >
            {notification.message}
          </p>
          <div className="flex items-center gap-2 mt-1.5">
            <span
              className="text-xs"
              style={{ color: 'var(--color-text-tertiary)' }}
            >
              {formatTimestamp(notification.timestamp)}
            </span>
            {!notification.read && (
              <span
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: 'var(--color-accent-blue)' }}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export function NotificationPanel() {
  const panelRef = useRef<HTMLDivElement>(null);
  const {
    notifications,
    isOpen,
    setIsOpen,
    markAsRead,
    markAllAsRead,
    removeNotification,
    clearAll,
    getUnreadCount,
  } = useNotificationStore();

  const unreadCount = getUnreadCount();

  // Close panel when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (panelRef.current && !panelRef.current.contains(event.target as Node)) {
        // Check if click is on the notification bell button
        const target = event.target as HTMLElement;
        if (target.closest('[data-notification-trigger]')) {
          return;
        }
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen, setIsOpen]);

  // Close on escape key
  useEffect(() => {
    function handleEscape(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen, setIsOpen]);

  if (!isOpen) return null;

  return (
    <div
      ref={panelRef}
      className="absolute top-full right-0 mt-2 w-80 max-h-[480px] rounded-lg shadow-xl overflow-hidden z-50"
      style={{
        backgroundColor: 'var(--color-bg-secondary)',
        border: '1px solid var(--color-border-default)',
      }}
    >
      {/* Header */}
      <div
        className="px-4 py-3 border-b flex items-center justify-between"
        style={{ borderColor: 'var(--color-border-default)' }}
      >
        <h3
          className="font-semibold text-sm"
          style={{ color: 'var(--color-text-primary)' }}
        >
          Notifications
          {unreadCount > 0 && (
            <span
              className="ml-2 px-1.5 py-0.5 text-xs rounded-full"
              style={{
                backgroundColor: 'var(--color-accent-blue)',
                color: 'white',
              }}
            >
              {unreadCount}
            </span>
          )}
        </h3>
        <div className="flex items-center gap-1">
          {unreadCount > 0 && (
            <button
              onClick={markAllAsRead}
              className="p-1.5 rounded transition-colors"
              style={{ color: 'var(--color-text-secondary)' }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--color-bg-tertiary)';
                e.currentTarget.style.color = 'var(--color-text-primary)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
                e.currentTarget.style.color = 'var(--color-text-secondary)';
              }}
              title="Mark all as read"
            >
              <CheckCheck className="w-4 h-4" />
            </button>
          )}
          {notifications.length > 0 && (
            <button
              onClick={clearAll}
              className="p-1.5 rounded transition-colors"
              style={{ color: 'var(--color-text-secondary)' }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--color-bg-tertiary)';
                e.currentTarget.style.color = 'var(--color-status-error)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
                e.currentTarget.style.color = 'var(--color-text-secondary)';
              }}
              title="Clear all notifications"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Notification List */}
      <div className="max-h-[400px] overflow-y-auto">
        {notifications.length === 0 ? (
          <div
            className="px-4 py-8 text-center"
            style={{ color: 'var(--color-text-tertiary)' }}
          >
            <Info className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No notifications</p>
          </div>
        ) : (
          notifications.map((notification) => (
            <NotificationItem
              key={notification.id}
              notification={notification}
              onMarkAsRead={markAsRead}
              onRemove={removeNotification}
            />
          ))
        )}
      </div>
    </div>
  );
}
