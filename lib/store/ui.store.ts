import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { AppSettings } from '../types';

interface UIState {
  // Navigation
  sidebarOpen: boolean;
  currentPage: 'landing' | 'projects' | 'upload' | 'profile' | 'clean' | 'query' | 'audit' | 'settings';
  currentProjectId: string | null;
  currentDatasetId: string | null;

  // Modals
  modals: {
    settingsOpen: boolean;
    helpOpen: boolean;
    confirmOpen: boolean;
  };

  // Theme
  theme: 'light' | 'dark' | 'auto';

  // Settings
  settings: AppSettings;

  // UI state
  notificationQueue: Array<{
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    message: string;
    duration?: number;
  }>;

  // Actions
  toggleSidebar: () => void;
  setCurrentPage: (page: UIState['currentPage']) => void;
  setCurrentProject: (projectId: string | null) => void;
  setCurrentDataset: (datasetId: string | null) => void;
  setTheme: (theme: 'light' | 'dark' | 'auto') => void;
  setSettings: (settings: Partial<AppSettings>) => void;
  openModal: (modal: keyof UIState['modals']) => void;
  closeModal: (modal: keyof UIState['modals']) => void;
  addNotification: (notification: Omit<typeof UIState.prototype.notificationQueue[0], 'id'>) => string;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
  reset: () => void;
}

const defaultSettings: AppSettings = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001/api',
  uploadSizeLimit: 100, // MB
  sandboxMode: false,
  redactPii: false,
  theme: 'auto',
};

export const useUIStore = create<UIState>()(
  devtools(
    persist(
      (set, get) => ({
        sidebarOpen: true,
        currentPage: 'landing',
        currentProjectId: null,
        currentDatasetId: null,
        modals: {
          settingsOpen: false,
          helpOpen: false,
          confirmOpen: false,
        },
        theme: 'auto',
        settings: defaultSettings,
        notificationQueue: [],

        toggleSidebar: () =>
          set((state) => ({ sidebarOpen: !state.sidebarOpen })),

        setCurrentPage: (page) => set({ currentPage: page }),

        setCurrentProject: (projectId) =>
          set({ currentProjectId: projectId }),

        setCurrentDataset: (datasetId) =>
          set({ currentDatasetId: datasetId }),

        setTheme: (theme) => set({ theme }),

        setSettings: (settings) =>
          set((state) => ({
            settings: { ...state.settings, ...settings },
          })),

        openModal: (modal) =>
          set((state) => ({
            modals: { ...state.modals, [modal]: true },
          })),

        closeModal: (modal) =>
          set((state) => ({
            modals: { ...state.modals, [modal]: false },
          })),

        addNotification: (notification) => {
          const id = `notification-${Date.now()}-${Math.random()}`;
          set((state) => ({
            notificationQueue: [
              ...state.notificationQueue,
              { ...notification, id },
            ],
          }));

          // Auto-remove after duration
          if (notification.duration !== 0) {
            setTimeout(() => {
              get().removeNotification(id);
            }, notification.duration || 5000);
          }

          return id;
        },

        removeNotification: (id) =>
          set((state) => ({
            notificationQueue: state.notificationQueue.filter(
              (n) => n.id !== id
            ),
          })),

        clearNotifications: () =>
          set({ notificationQueue: [] }),

        reset: () =>
          set({
            sidebarOpen: true,
            currentPage: 'landing',
            currentProjectId: null,
            currentDatasetId: null,
            modals: {
              settingsOpen: false,
              helpOpen: false,
              confirmOpen: false,
            },
            notificationQueue: [],
          }),
      }),
      {
        name: 'ui-store',
        partialize: (state) => ({
          sidebarOpen: state.sidebarOpen,
          theme: state.theme,
          settings: state.settings,
        }),
      }
    )
  )
);
