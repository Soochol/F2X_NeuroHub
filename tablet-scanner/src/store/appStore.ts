/**
 * Zustand Store for App State
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type {
  User,
  Process,
  AppSettings,
  ScanResult,
  TodayStatistics
} from '@/types';

interface AppState {
  // Auth
  user: User | null;
  isAuthenticated: boolean;

  // Settings
  settings: AppSettings;

  // Process
  processes: Process[];
  selectedProcessId: number | null;

  // Statistics
  todayStats: TodayStatistics;

  // Scan history (last 10)
  scanHistory: ScanResult[];

  // UI State
  isLoading: boolean;
  error: string | null;

  // Actions
  setUser: (user: User | null) => void;
  logout: () => void;
  setSettings: (settings: Partial<AppSettings>) => void;
  setProcesses: (processes: Process[]) => void;
  setSelectedProcess: (processId: number | null) => void;
  setTodayStats: (stats: TodayStatistics) => void;
  addScanResult: (result: ScanResult) => void;
  clearScanHistory: () => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

const defaultSettings: AppSettings = {
  workerId: '',
  workerName: '',
  equipmentId: '',
  lineId: '',
  apiBaseUrl: '/api/v1',
};

const defaultStats: TodayStatistics = {
  started: 0,
  completed: 0,
  passed: 0,
  failed: 0,
};

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // Initial state
      user: null,
      isAuthenticated: false,
      settings: defaultSettings,
      processes: [],
      selectedProcessId: null,
      todayStats: defaultStats,
      scanHistory: [],
      isLoading: false,
      error: null,

      // Actions
      setUser: (user) => set({
        user,
        isAuthenticated: !!user,
        settings: user ? {
          ...defaultSettings,
          workerId: user.username,
          workerName: user.full_name,
        } : defaultSettings,
      }),

      logout: () => {
        localStorage.removeItem('access_token');
        set({
          user: null,
          isAuthenticated: false,
          scanHistory: [],
          todayStats: defaultStats,
        });
      },

      setSettings: (newSettings) => set((state) => ({
        settings: { ...state.settings, ...newSettings },
      })),

      setProcesses: (processes) => set({ processes }),

      setSelectedProcess: (processId) => set({ selectedProcessId: processId }),

      setTodayStats: (stats) => set({ todayStats: stats }),

      addScanResult: (result) => set((state) => ({
        scanHistory: [result, ...state.scanHistory].slice(0, 10),
        // Update stats on successful scan
        todayStats: result.success ? {
          ...state.todayStats,
          started: result.action === 'start'
            ? state.todayStats.started + 1
            : state.todayStats.started,
          completed: result.action === 'complete'
            ? state.todayStats.completed + 1
            : state.todayStats.completed,
        } : state.todayStats,
      })),

      clearScanHistory: () => set({ scanHistory: [] }),

      setLoading: (loading) => set({ isLoading: loading }),

      setError: (error) => set({ error }),
    }),
    {
      name: 'tablet-scanner-storage',
      partialize: (state) => ({
        settings: state.settings,
        selectedProcessId: state.selectedProcessId,
      }),
    }
  )
);
