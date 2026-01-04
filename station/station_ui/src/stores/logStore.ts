/**
 * Log state store.
 * Manages real-time log entries from WebSocket.
 */

import { create } from 'zustand';
import type { LogEntry, LogLevel } from '../types';

interface LogFilter {
  batchId?: string;
  level?: LogLevel;
  search?: string;
}

interface LogState {
  // State
  logs: LogEntry[];
  maxLogs: number;
  filters: LogFilter;
  autoScroll: boolean;

  // Actions
  addLog: (log: LogEntry) => void;
  addLogs: (logs: LogEntry[]) => void;
  clearLogs: () => void;
  setFilters: (filters: LogFilter) => void;
  setAutoScroll: (autoScroll: boolean) => void;
  setMaxLogs: (maxLogs: number) => void;

  // Selectors
  getFilteredLogs: () => LogEntry[];
}

export const useLogStore = create<LogState>((set, get) => ({
  // Initial state
  logs: [],
  maxLogs: 1000,
  filters: {},
  autoScroll: true,

  // Actions
  addLog: (log) =>
    set((state) => {
      const newLogs = [...state.logs, log];
      // Keep only the last maxLogs entries
      if (newLogs.length > state.maxLogs) {
        return { logs: newLogs.slice(-state.maxLogs) };
      }
      return { logs: newLogs };
    }),

  addLogs: (logs) =>
    set((state) => {
      const newLogs = [...state.logs, ...logs];
      if (newLogs.length > state.maxLogs) {
        return { logs: newLogs.slice(-state.maxLogs) };
      }
      return { logs: newLogs };
    }),

  clearLogs: () => set({ logs: [] }),

  setFilters: (filters) => set({ filters }),

  setAutoScroll: (autoScroll) => set({ autoScroll }),

  setMaxLogs: (maxLogs) => set({ maxLogs }),

  // Selectors
  getFilteredLogs: () => {
    const { logs, filters } = get();

    return logs.filter((log) => {
      if (filters.batchId && log.batchId !== filters.batchId) {
        return false;
      }
      if (filters.level && log.level !== filters.level) {
        return false;
      }
      if (filters.search && !log.message.toLowerCase().includes(filters.search.toLowerCase())) {
        return false;
      }
      return true;
    });
  },
}));
