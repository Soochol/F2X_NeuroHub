/**
 * Sync State Slice
 *
 * 동기화 및 오프라인 상태 관리
 * - 온라인/오프라인 상태
 * - WebSocket 연결 상태
 * - 오프라인 큐
 * - 동기화 진행률
 */
import { create } from 'zustand';

export interface QueueItem {
  id: string;
  type: 'start' | 'complete';
  data: {
    wip_id: string;
    process_id: number;
    result?: string;
    measurements?: Record<string, unknown>;
  };
  timestamp: number;
  status: 'pending' | 'syncing' | 'failed';
  retryCount: number;
  error?: string;
}

interface SyncState {
  // Connection status
  isOnline: boolean;
  websocketConnected: boolean;
  lastSyncTime: number | null;
  lastHeartbeat: number | null;

  // Queue visualization
  queueItems: QueueItem[];
  syncProgress: number; // 0-100
  currentlySyncing: string | null;

  // Sync statistics
  totalSynced: number;
  totalFailed: number;

  // Actions
  setOnline: (isOnline: boolean) => void;
  setWebsocketConnected: (connected: boolean) => void;
  updateLastSync: () => void;
  updateHeartbeat: () => void;

  // Queue actions
  addToQueue: (item: Omit<QueueItem, 'id' | 'timestamp' | 'status' | 'retryCount'>) => string;
  updateQueueItem: (id: string, updates: Partial<QueueItem>) => void;
  removeFromQueue: (id: string) => void;
  clearQueue: () => void;
  markAsSyncing: (id: string) => void;
  markAsFailed: (id: string, error: string) => void;
  markAsSynced: (id: string) => void;

  // Sync progress
  setSyncProgress: (progress: number) => void;
  setCurrentlySyncing: (id: string | null) => void;

  // Computed
  getPendingCount: () => number;
  getFailedCount: () => number;
  hasOfflineItems: () => boolean;
}

export const useSyncStore = create<SyncState>()((set, get) => ({
  // Initial state
  isOnline: typeof navigator !== 'undefined' ? navigator.onLine : true,
  websocketConnected: false,
  lastSyncTime: null,
  lastHeartbeat: null,
  queueItems: [],
  syncProgress: 0,
  currentlySyncing: null,
  totalSynced: 0,
  totalFailed: 0,

  // Actions
  setOnline: (isOnline) => set({ isOnline }),

  setWebsocketConnected: (connected) =>
    set({ websocketConnected: connected }),

  updateLastSync: () => set({ lastSyncTime: Date.now() }),

  updateHeartbeat: () => set({ lastHeartbeat: Date.now() }),

  // Queue actions
  addToQueue: (item) => {
    const id = `queue_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
    const newItem: QueueItem = {
      ...item,
      id,
      timestamp: Date.now(),
      status: 'pending',
      retryCount: 0,
    };

    set((state) => ({
      queueItems: [...state.queueItems, newItem],
    }));

    return id;
  },

  updateQueueItem: (id, updates) =>
    set((state) => ({
      queueItems: state.queueItems.map((item) =>
        item.id === id ? { ...item, ...updates } : item
      ),
    })),

  removeFromQueue: (id) =>
    set((state) => ({
      queueItems: state.queueItems.filter((item) => item.id !== id),
    })),

  clearQueue: () =>
    set({
      queueItems: [],
      syncProgress: 0,
      currentlySyncing: null,
    }),

  markAsSyncing: (id) =>
    set((state) => ({
      queueItems: state.queueItems.map((item) =>
        item.id === id ? { ...item, status: 'syncing' } : item
      ),
      currentlySyncing: id,
    })),

  markAsFailed: (id, error) =>
    set((state) => ({
      queueItems: state.queueItems.map((item) =>
        item.id === id
          ? {
              ...item,
              status: 'failed',
              error,
              retryCount: item.retryCount + 1,
            }
          : item
      ),
      currentlySyncing: null,
      totalFailed: state.totalFailed + 1,
    })),

  markAsSynced: (id) =>
    set((state) => {
      const newQueue = state.queueItems.filter((item) => item.id !== id);
      const progress =
        newQueue.length > 0
          ? ((state.queueItems.length - newQueue.length) /
              state.queueItems.length) *
            100
          : 100;

      return {
        queueItems: newQueue,
        currentlySyncing: null,
        syncProgress: progress,
        totalSynced: state.totalSynced + 1,
        lastSyncTime: Date.now(),
      };
    }),

  // Sync progress
  setSyncProgress: (progress) => set({ syncProgress: progress }),
  setCurrentlySyncing: (id) => set({ currentlySyncing: id }),

  // Computed
  getPendingCount: () =>
    get().queueItems.filter((item) => item.status === 'pending').length,

  getFailedCount: () =>
    get().queueItems.filter((item) => item.status === 'failed').length,

  hasOfflineItems: () => get().queueItems.length > 0,
}));

// Online/Offline listener setup
if (typeof window !== 'undefined') {
  window.addEventListener('online', () => {
    useSyncStore.getState().setOnline(true);
  });

  window.addEventListener('offline', () => {
    useSyncStore.getState().setOnline(false);
  });
}

export default useSyncStore;
