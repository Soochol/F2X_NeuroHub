/**
 * Notification state store.
 * Manages notification items for the header notification panel.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type NotificationType = 'info' | 'success' | 'warning' | 'error';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  batchId?: string;
}

interface NotificationState {
  // State
  notifications: Notification[];
  maxNotifications: number;
  isOpen: boolean;

  // Actions
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  removeNotification: (id: string) => void;
  clearAll: () => void;
  setIsOpen: (isOpen: boolean) => void;
  togglePanel: () => void;

  // Selectors
  getUnreadCount: () => number;
}

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

export const useNotificationStore = create<NotificationState>()(
  persist(
    (set, get) => ({
      // Initial state
      notifications: [],
      maxNotifications: 50,
      isOpen: false,

      // Actions
      addNotification: (notification) =>
        set((state) => {
          const newNotification: Notification = {
            ...notification,
            id: generateId(),
            timestamp: new Date(),
            read: false,
          };

          const newNotifications = [newNotification, ...state.notifications];
          // Keep only the last maxNotifications entries
          if (newNotifications.length > state.maxNotifications) {
            return { notifications: newNotifications.slice(0, state.maxNotifications) };
          }
          return { notifications: newNotifications };
        }),

      markAsRead: (id) =>
        set((state) => ({
          notifications: state.notifications.map((n) =>
            n.id === id ? { ...n, read: true } : n
          ),
        })),

      markAllAsRead: () =>
        set((state) => ({
          notifications: state.notifications.map((n) => ({ ...n, read: true })),
        })),

      removeNotification: (id) =>
        set((state) => ({
          notifications: state.notifications.filter((n) => n.id !== id),
        })),

      clearAll: () => set({ notifications: [] }),

      setIsOpen: (isOpen) => set({ isOpen }),

      togglePanel: () => set((state) => ({ isOpen: !state.isOpen })),

      // Selectors
      getUnreadCount: () => {
        const { notifications } = get();
        return notifications.filter((n) => !n.read).length;
      },
    }),
    {
      name: 'station-ui-notifications',
      partialize: (state) => ({
        notifications: state.notifications.map((n) => ({
          ...n,
          timestamp: n.timestamp.toISOString(),
        })),
      }),
      onRehydrateStorage: () => (state) => {
        // Convert ISO strings back to Date objects
        if (state?.notifications) {
          state.notifications = state.notifications.map((n: Notification & { timestamp: string | Date }) => ({
            ...n,
            timestamp: typeof n.timestamp === 'string' ? new Date(n.timestamp) : n.timestamp,
          }));
        }
      },
    }
  )
);
