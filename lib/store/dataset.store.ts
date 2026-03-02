import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import {
  Dataset,
  FileMetadata,
  PreviewRow,
  ProfileResponse,
  CleaningPlanResponse,
  CleaningStep,
  UploadState,
} from '../types';

interface DatasetState {
  // Current dataset being worked on
  currentDataset: Dataset | null;
  currentProfile: ProfileResponse | null;
  currentCleaningPlan: CleaningPlanResponse | null;
  appliedCleaningSteps: Set<string>; // Set of enabled step IDs

  // Upload state
  uploadState: UploadState;

  // Actions
  setCurrentDataset: (dataset: Dataset | null) => void;
  setCurrentProfile: (profile: ProfileResponse | null) => void;
  setCurrentCleaningPlan: (plan: CleaningPlanResponse | null) => void;
  toggleCleaningStep: (stepId: string) => void;
  resetCleaningSteps: () => void;
  setUploadState: (state: Partial<UploadState>) => void;
  resetUploadState: () => void;
  resetAll: () => void;
}

const initialUploadState: UploadState = {
  file: null,
  metadata: null,
  preview: [],
  isLoading: false,
  error: null,
};

export const useDatasetStore = create<DatasetState>()(
  devtools(
    persist(
      (set) => ({
        currentDataset: null,
        currentProfile: null,
        currentCleaningPlan: null,
        appliedCleaningSteps: new Set<string>(),
        uploadState: initialUploadState,

        setCurrentDataset: (dataset) =>
          set({ currentDataset: dataset }),

        setCurrentProfile: (profile) =>
          set({ currentProfile: profile }),

        setCurrentCleaningPlan: (plan) => {
          // When setting a new plan, initialize all steps as enabled
          const enabledSteps = new Set(
            plan?.steps.map((step) => step.stepId) || []
          );
          set({
            currentCleaningPlan: plan,
            appliedCleaningSteps: enabledSteps,
          });
        },

        toggleCleaningStep: (stepId) =>
          set((state) => {
            const newSteps = new Set(state.appliedCleaningSteps);
            if (newSteps.has(stepId)) {
              newSteps.delete(stepId);
            } else {
              newSteps.add(stepId);
            }
            return { appliedCleaningSteps: newSteps };
          }),

        resetCleaningSteps: () =>
          set((state) => ({
            appliedCleaningSteps: new Set(
              state.currentCleaningPlan?.steps.map((s) => s.stepId) || []
            ),
          })),

        setUploadState: (state) =>
          set((current) => ({
            uploadState: { ...current.uploadState, ...state },
          })),

        resetUploadState: () =>
          set({ uploadState: initialUploadState }),

        resetAll: () =>
          set({
            currentDataset: null,
            currentProfile: null,
            currentCleaningPlan: null,
            appliedCleaningSteps: new Set<string>(),
            uploadState: initialUploadState,
          }),
      }),
      {
        name: 'dataset-store',
        partialize: (state) => ({
          // Only persist non-sensitive data
          currentDataset: state.currentDataset,
          uploadState: {
            ...state.uploadState,
            file: null, // Don't persist file object
          },
        }),
      }
    )
  )
);
