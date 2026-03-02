import { create } from 'zustand';
import { PlanStep, AgentStepExecution, QueryResult } from '@/lib/types';

interface QueryStoreState {
  runId: string | null;
  plan: PlanStep[];
  steps: Map<string, AgentStepExecution>;
  result: QueryResult | null;
  isExecuting: boolean;
  error: string | null;

  // Actions
  setRunId: (runId: string) => void;
  setPlan: (plan: PlanStep[]) => void;
  updateStepExecution: (stepId: string, execution: Partial<AgentStepExecution>) => void;
  setResult: (result: QueryResult) => void;
  setIsExecuting: (isExecuting: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

export const useQueryStore = create<QueryStoreState>((set) => ({
  runId: null,
  plan: [],
  steps: new Map(),
  result: null,
  isExecuting: false,
  error: null,

  setRunId: (runId) => set({ runId }),

  setPlan: (plan) => {
    const stepsMap = new Map<string, AgentStepExecution>();
    plan.forEach((step) => {
      stepsMap.set(step.stepId, {
        stepId: step.stepId,
        status: 'pending',
      });
    });
    set({ plan, steps: stepsMap, isExecuting: true });
  },

  updateStepExecution: (stepId, execution) =>
    set((state) => {
      const newSteps = new Map(state.steps);
      const existing = newSteps.get(stepId) || { stepId, status: 'pending' };
      newSteps.set(stepId, { ...existing, ...execution });
      return { steps: newSteps };
    }),

  setResult: (result) => set({ result, isExecuting: false }),

  setIsExecuting: (isExecuting) => set({ isExecuting }),

  setError: (error) => set({ error, isExecuting: false }),

  reset: () =>
    set({
      runId: null,
      plan: [],
      steps: new Map(),
      result: null,
      isExecuting: false,
      error: null,
    }),
}));
