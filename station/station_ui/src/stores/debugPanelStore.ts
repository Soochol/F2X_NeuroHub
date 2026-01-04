/**
 * Batch Details Panel state store.
 * Manages the state of the batch details panel in BatchDetailPage.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { LogLevel } from '../types';

export type DebugPanelTab = 'logs' | 'data' | 'params' | 'config';

interface DebugPanelState {
  // Panel visibility & sizing
  isCollapsed: boolean;
  panelWidth: number;

  // Tab selection
  activeTab: DebugPanelTab;

  // Filters
  selectedStep: string | null;
  logLevel: LogLevel | null;
  searchQuery: string;

  // Scroll behavior
  autoScroll: boolean;

  // Actions
  toggleCollapsed: () => void;
  setCollapsed: (collapsed: boolean) => void;
  setPanelWidth: (width: number) => void;
  setActiveTab: (tab: DebugPanelTab) => void;
  setSelectedStep: (step: string | null) => void;
  setLogLevel: (level: LogLevel | null) => void;
  setSearchQuery: (query: string) => void;
  setAutoScroll: (auto: boolean) => void;
  clearFilters: () => void;
}

const MIN_PANEL_WIDTH = 280;
const MAX_PANEL_WIDTH = 600;
const DEFAULT_PANEL_WIDTH = 380;

export const useDebugPanelStore = create<DebugPanelState>()(
  persist(
    (set) => ({
      // Initial state
      isCollapsed: false,
      panelWidth: DEFAULT_PANEL_WIDTH,
      activeTab: 'logs',
      selectedStep: null,
      logLevel: null,
      searchQuery: '',
      autoScroll: true,

      // Actions
      toggleCollapsed: () => set((state) => ({ isCollapsed: !state.isCollapsed })),

      setCollapsed: (isCollapsed) => set({ isCollapsed }),

      setPanelWidth: (width) =>
        set({ panelWidth: Math.min(MAX_PANEL_WIDTH, Math.max(MIN_PANEL_WIDTH, width)) }),

      setActiveTab: (activeTab) => set({ activeTab }),

      setSelectedStep: (selectedStep) => set({ selectedStep }),

      setLogLevel: (logLevel) => set({ logLevel }),

      setSearchQuery: (searchQuery) => set({ searchQuery }),

      setAutoScroll: (autoScroll) => set({ autoScroll }),

      clearFilters: () =>
        set({
          selectedStep: null,
          logLevel: null,
          searchQuery: '',
        }),
    }),
    {
      name: 'debug-panel-state',
      partialize: (state) => ({
        // Only persist these fields
        isCollapsed: state.isCollapsed,
        panelWidth: state.panelWidth,
        activeTab: state.activeTab,
        autoScroll: state.autoScroll,
      }),
    }
  )
);
