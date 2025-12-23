/**
 * UI State Slice
 *
 * UI 관련 상태 관리
 * - 모달/시트 상태
 * - 스캐너 모드
 * - 테마
 * - 토스트
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type ModalType =
  | 'measurement'
  | 'settings'
  | 'history'
  | 'camera'
  | 'offline-queue'
  | 'confirm'
  | null;

type ScannerMode = 'camera' | 'manual';

type StatusTheme = 'default' | 'success' | 'warning' | 'error';

export interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info' | 'loading';
  title: string;
  message?: string;
  duration?: number;
}

interface UIState {
  // Modals/Sheets
  activeModal: ModalType;
  modalData: Record<string, unknown> | null;
  bottomSheetOpen: boolean;
  bottomSheetContent: 'history' | 'settings' | 'queue' | null;

  // Scanner mode
  scannerMode: ScannerMode;
  selectedCameraId: string | null;
  scannerEnabled: boolean;

  // Theme
  statusTheme: StatusTheme;
  statusThemeTimeout: number | null;

  // Toasts
  toasts: Toast[];

  // Loading states
  isGlobalLoading: boolean;
  loadingMessage: string | null;

  // Sound & Vibration
  soundEnabled: boolean;
  vibrationEnabled: boolean;

  // Actions
  openModal: (modal: ModalType, data?: Record<string, unknown>) => void;
  closeModal: () => void;
  openBottomSheet: (content: 'history' | 'settings' | 'queue') => void;
  closeBottomSheet: () => void;

  // Scanner
  setScannerMode: (mode: ScannerMode) => void;
  setSelectedCamera: (cameraId: string | null) => void;
  toggleScanner: () => void;
  enableScanner: () => void;
  disableScanner: () => void;

  // Theme
  setStatusTheme: (theme: StatusTheme, duration?: number) => void;
  resetStatusTheme: () => void;

  // Toasts
  addToast: (toast: Omit<Toast, 'id'>) => string;
  removeToast: (id: string) => void;
  clearToasts: () => void;

  // Loading
  setGlobalLoading: (loading: boolean, message?: string) => void;

  // Sound & Vibration
  toggleSound: () => void;
  toggleVibration: () => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set, get) => ({
      // Initial state
      activeModal: null,
      modalData: null,
      bottomSheetOpen: false,
      bottomSheetContent: null,
      scannerMode: 'camera',
      selectedCameraId: null,
      scannerEnabled: true,
      statusTheme: 'default',
      statusThemeTimeout: null,
      toasts: [],
      isGlobalLoading: false,
      loadingMessage: null,
      soundEnabled: true,
      vibrationEnabled: true,

      // Modal actions
      openModal: (modal, data) =>
        set({
          activeModal: modal,
          modalData: data ?? null,
        }),

      closeModal: () =>
        set({
          activeModal: null,
          modalData: null,
        }),

      // Bottom sheet
      openBottomSheet: (content) =>
        set({
          bottomSheetOpen: true,
          bottomSheetContent: content,
        }),

      closeBottomSheet: () =>
        set({
          bottomSheetOpen: false,
          bottomSheetContent: null,
        }),

      // Scanner
      setScannerMode: (mode) => set({ scannerMode: mode }),

      setSelectedCamera: (cameraId) => set({ selectedCameraId: cameraId }),

      toggleScanner: () =>
        set((state) => ({ scannerEnabled: !state.scannerEnabled })),

      enableScanner: () => set({ scannerEnabled: true }),

      disableScanner: () => set({ scannerEnabled: false }),

      // Theme
      setStatusTheme: (theme, duration = 2000) => {
        const { statusThemeTimeout } = get();

        // Clear existing timeout
        if (statusThemeTimeout) {
          clearTimeout(statusThemeTimeout);
        }

        if (duration > 0) {
          const timeout = window.setTimeout(() => {
            set({ statusTheme: 'default', statusThemeTimeout: null });
          }, duration);

          set({ statusTheme: theme, statusThemeTimeout: timeout });
        } else {
          set({ statusTheme: theme, statusThemeTimeout: null });
        }
      },

      resetStatusTheme: () => {
        const { statusThemeTimeout } = get();
        if (statusThemeTimeout) {
          clearTimeout(statusThemeTimeout);
        }
        set({ statusTheme: 'default', statusThemeTimeout: null });
      },

      // Toasts
      addToast: (toast) => {
        const id = `toast_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
        const newToast: Toast = { ...toast, id };

        set((state) => ({
          toasts: [...state.toasts, newToast],
        }));

        // Auto remove after duration
        if (toast.duration && toast.duration > 0) {
          setTimeout(() => {
            get().removeToast(id);
          }, toast.duration);
        }

        return id;
      },

      removeToast: (id) =>
        set((state) => ({
          toasts: state.toasts.filter((t) => t.id !== id),
        })),

      clearToasts: () => set({ toasts: [] }),

      // Loading
      setGlobalLoading: (loading, message) =>
        set({
          isGlobalLoading: loading,
          loadingMessage: message ?? null,
        }),

      // Sound & Vibration
      toggleSound: () =>
        set((state) => ({ soundEnabled: !state.soundEnabled })),

      toggleVibration: () =>
        set((state) => ({ vibrationEnabled: !state.vibrationEnabled })),
    }),
    {
      name: 'ui-storage',
      partialize: (state) => ({
        scannerMode: state.scannerMode,
        selectedCameraId: state.selectedCameraId,
        soundEnabled: state.soundEnabled,
        vibrationEnabled: state.vibrationEnabled,
      }),
    }
  )
);

// Helper hooks for common operations
export const useModal = () => {
  const { activeModal, modalData, openModal, closeModal } = useUIStore();
  return { activeModal, modalData, openModal, closeModal };
};

export const useBottomSheet = () => {
  const {
    bottomSheetOpen,
    bottomSheetContent,
    openBottomSheet,
    closeBottomSheet,
  } = useUIStore();
  return {
    isOpen: bottomSheetOpen,
    content: bottomSheetContent,
    open: openBottomSheet,
    close: closeBottomSheet,
  };
};

export const useStatusTheme = () => {
  const { statusTheme, setStatusTheme, resetStatusTheme } = useUIStore();
  return { theme: statusTheme, setTheme: setStatusTheme, reset: resetStatusTheme };
};

export default useUIStore;
