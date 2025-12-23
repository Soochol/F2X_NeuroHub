/**
 * Workflow State Slice
 *
 * 작업 흐름 관련 상태 관리
 * - 현재 WIP
 * - 선택된 프로세스
 * - 최근 작업 이력
 * - 배치 모드
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { WIPTrace, Process } from '@/types';

interface WorkflowState {
  // Current work context
  currentWip: WIPTrace | null;
  selectedProcessId: number | null;
  pendingAction: 'start' | 'complete' | null;

  // Process list
  processes: Process[];

  // Quick access
  recentWipIds: string[]; // Last 10 WIP IDs
  favoriteProcessIds: number[];

  // Batch mode
  batchMode: boolean;
  batchQueue: string[];

  // Actions
  setCurrentWip: (wip: WIPTrace | null) => void;
  setSelectedProcess: (processId: number | null) => void;
  setPendingAction: (action: 'start' | 'complete' | null) => void;
  setProcesses: (processes: Process[]) => void;

  // Quick access actions
  addToRecentWips: (wipId: string) => void;
  clearRecentWips: () => void;
  toggleFavoriteProcess: (processId: number) => void;

  // Batch mode actions
  toggleBatchMode: () => void;
  addToBatchQueue: (wipId: string) => void;
  removeFromBatchQueue: (wipId: string) => void;
  clearBatchQueue: () => void;

  // Computed
  canStart: () => boolean;
  canComplete: () => boolean;
  getNextProcess: () => Process | null;

  // Reset
  resetWorkflow: () => void;
}

const MAX_RECENT_WIPS = 10;

export const useWorkflowStore = create<WorkflowState>()(
  persist(
    (set, get) => ({
      // Initial state
      currentWip: null,
      selectedProcessId: null,
      pendingAction: null,
      processes: [],
      recentWipIds: [],
      favoriteProcessIds: [],
      batchMode: false,
      batchQueue: [],

      // Actions
      setCurrentWip: (wip) => {
        set({ currentWip: wip, pendingAction: null });

        // Add to recent if not null
        if (wip?.wip_id) {
          get().addToRecentWips(wip.wip_id);
        }
      },

      setSelectedProcess: (processId) =>
        set({ selectedProcessId: processId }),

      setPendingAction: (action) => set({ pendingAction: action }),

      setProcesses: (processes) => set({ processes }),

      // Quick access
      addToRecentWips: (wipId) =>
        set((state) => {
          const filtered = state.recentWipIds.filter((id) => id !== wipId);
          return {
            recentWipIds: [wipId, ...filtered].slice(0, MAX_RECENT_WIPS),
          };
        }),

      clearRecentWips: () => set({ recentWipIds: [] }),

      toggleFavoriteProcess: (processId) =>
        set((state) => {
          const isFavorite = state.favoriteProcessIds.includes(processId);
          return {
            favoriteProcessIds: isFavorite
              ? state.favoriteProcessIds.filter((id) => id !== processId)
              : [...state.favoriteProcessIds, processId],
          };
        }),

      // Batch mode
      toggleBatchMode: () =>
        set((state) => ({
          batchMode: !state.batchMode,
          batchQueue: state.batchMode ? [] : state.batchQueue,
        })),

      addToBatchQueue: (wipId) =>
        set((state) => {
          if (state.batchQueue.includes(wipId)) return state;
          return { batchQueue: [...state.batchQueue, wipId] };
        }),

      removeFromBatchQueue: (wipId) =>
        set((state) => ({
          batchQueue: state.batchQueue.filter((id) => id !== wipId),
        })),

      clearBatchQueue: () => set({ batchQueue: [] }),

      // Computed (as functions)
      canStart: () => {
        const { currentWip, selectedProcessId, processes } = get();
        if (!currentWip || !selectedProcessId) return false;

        // Find the selected process
        const selectedProcess = processes.find((p) => p.id === selectedProcessId);
        if (!selectedProcess) return false;

        // Check if this process has already been started/completed
        const processHistory = currentWip.process_history?.find(
          (ph) => ph.process_number === selectedProcess.process_number
        );

        // Can start if not yet started (no history or no start_time)
        return !processHistory || !processHistory.start_time;
      },

      canComplete: () => {
        const { currentWip, selectedProcessId, processes } = get();
        if (!currentWip || !selectedProcessId) return false;

        // Find the selected process
        const selectedProcess = processes.find((p) => p.id === selectedProcessId);
        if (!selectedProcess) return false;

        // Check process history
        const processHistory = currentWip.process_history?.find(
          (ph) => ph.process_number === selectedProcess.process_number
        );

        // Can complete if started but not completed
        return !!processHistory?.start_time && !processHistory.complete_time;
      },

      getNextProcess: () => {
        const { currentWip, processes } = get();
        if (!currentWip || !processes.length) return null;

        // Find completed process numbers
        const completedProcessNumbers =
          currentWip.process_history
            ?.filter((ph) => ph.result === 'PASS' || ph.result === 'FAIL')
            .map((ph) => ph.process_number) || [];

        // Sort processes by process_number
        const sortedProcesses = [...processes].sort(
          (a, b) => a.process_number - b.process_number
        );

        return (
          sortedProcesses.find(
            (p) => !completedProcessNumbers.includes(p.process_number)
          ) || null
        );
      },

      // Reset
      resetWorkflow: () =>
        set({
          currentWip: null,
          selectedProcessId: null,
          pendingAction: null,
          batchMode: false,
          batchQueue: [],
        }),
    }),
    {
      name: 'workflow-storage',
      partialize: (state) => ({
        recentWipIds: state.recentWipIds,
        favoriteProcessIds: state.favoriteProcessIds,
        selectedProcessId: state.selectedProcessId,
      }),
    }
  )
);

export default useWorkflowStore;
