import { getApiClient } from './api';
import { getRealApiClient, resetRealApiClient } from './api.real';
import { Dataset, Run, Plan, WebSocketEvent } from './api.real';

/**
 * API Adapter that provides a unified interface for both mock and real backends
 * Allows switching between mock and real backends seamlessly
 */
export class ApiAdapter {
  private useRealBackend: boolean;
  private realApiClient = getRealApiClient();
  private mockApiClient = getApiClient();

  constructor(useRealBackend: boolean = false) {
    this.useRealBackend = useRealBackend;
  }

  /**
   * Switch between mock and real backend
   */
  setBackendMode(useRealBackend: boolean): void {
    this.useRealBackend = useRealBackend;
  }

  /**
   * Get current backend mode
   */
  getBackendMode(): 'mock' | 'real' {
    return this.useRealBackend ? 'real' : 'mock';
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string; version: string } | boolean> {
    if (this.useRealBackend) {
      return await this.realApiClient.healthCheck();
    } else {
      return await this.mockApiClient.healthCheck();
    }
  }

  /**
   * Dataset Management
   */
  async uploadDataset(
    file: File,
    name: string,
    description?: string,
    isPublic?: boolean,
    onUploadProgress?: (progress: number) => void
  ): Promise<any> {
    if (this.useRealBackend) {
      return await this.realApiClient.uploadDataset(file, name, description, isPublic, onUploadProgress);
    } else {
      // Convert to mock API format
      const response = await this.mockApiClient.uploadFile(
        file,
        name,
        'default-project', // Mock project ID
        {},
        onUploadProgress
      );
      
      // Convert to real backend format
      return {
        dataset_id: response.datasetId,
        name: response.dataset.name,
        file_type: response.metadata.mimeType,
        file_size: response.metadata.fileSize,
      };
    }
  }

  async listDatasets(skip?: number, limit?: number): Promise<Dataset[]> {
    if (this.useRealBackend) {
      return await this.realApiClient.listDatasets(skip, limit);
    } else {
      // Get from mock backend and convert format
      const mockDatasets = await this.mockApiClient.listDatasets('default-project');
      
      return mockDatasets.map(dataset => ({
        id: dataset.id,
        name: dataset.name,
        description: '', // Mock API doesn't have description
        file_path: '', // Mock API doesn't have file path
        file_size: dataset.fileSize,
        file_type: 'csv', // Default type
        schema_info: { columns: dataset.columns },
        profile_info: undefined,
        owner_id: 'mock-user',
        is_public: false,
        created_at: dataset.uploadedAt,
        updated_at: dataset.updatedAt,
      }));
    }
  }

  async getDataset(datasetId: string): Promise<Dataset> {
    if (this.useRealBackend) {
      return await this.realApiClient.getDataset(datasetId);
    } else {
      const mockDataset = await this.mockApiClient.getDataset(datasetId);
      
      return {
        id: mockDataset.id,
        name: mockDataset.name,
        description: '', // Mock API doesn't have description
        file_path: '', // Mock API doesn't have file path
        file_size: mockDataset.fileSize,
        file_type: 'csv', // Default type
        schema_info: { columns: mockDataset.columns },
        profile_info: undefined,
        owner_id: 'mock-user',
        is_public: false,
        created_at: mockDataset.uploadedAt,
        updated_at: mockDataset.updatedAt,
      };
    }
  }

  /**
   * Data Profiling
   */
  async getDatasetProfile(datasetId: string): Promise<Record<string, any>> {
    if (this.useRealBackend) {
      return await this.realApiClient.getDatasetProfile(datasetId);
    } else {
      const response = await this.mockApiClient.getProfile(datasetId);
      return response;
    }
  }

  /**
   * Data Cleaning
   */
  async createCleaningPlan(
    datasetId: string,
    cleaningGoals?: string[]
  ): Promise<{ plan: Plan; rationale: string }> {
    if (this.useRealBackend) {
      return await this.realApiClient.createCleaningPlan(datasetId, cleaningGoals);
    } else {
      const response = await this.mockApiClient.generateCleaningPlan({
        datasetId,
        requestedChanges: cleaningGoals?.join(', '),
        autoDetect: true,
      });
      
      // Convert mock response to real format
      return {
        plan: {
          steps: response.steps.map(step => ({
            step_id: step.stepId,
            step_type: step.type as any,
            spec: step.parameters,
            dependencies: [],
          })),
          estimated_duration: response.steps.reduce((sum, step) => sum + 10, 0), // Default 10s per step
          confidence: 0.8,
        },
        rationale: `Generated ${response.steps.length} cleaning steps`,
      };
    }
  }

  async executeCleaningPlan(
    datasetId: string,
    plan: Plan,
    applyChanges?: boolean
  ): Promise<any> {
    if (this.useRealBackend) {
      return await this.realApiClient.executeCleaningPlan(datasetId, plan, applyChanges);
    } else {
      const response = await this.mockApiClient.executeCleaning({
        planId: plan.steps[0]?.step_id || 'clean-plan',
        apply: applyChanges || false,
      });
      
      return {
        run_id: response.auditLogId,
        cleaned_dataset_id: response.cleanedDatasetId,
        changes_applied: applyChanges || false,
      };
    }
  }

  /**
   * Analysis / Query
   */
  async askQuestion(
    question: string,
    datasetId: string,
    dryRun?: boolean
  ): Promise<{ run_id: string; plan: Plan }> {
    if (this.useRealBackend) {
      return await this.realApiClient.askQuestion(question, datasetId, dryRun);
    } else {
      const response = await this.mockApiClient.submitQuery({
        datasetId,
        question,
        mode: dryRun ? 'dry_run' : 'auto',
      });
      
      // Convert mock response to real format
      return {
        run_id: response.runId,
        plan: {
          steps: response.plan.map(step => ({
            step_id: step.stepId,
            step_type: step.type as any,
            spec: { description: step.description },
            dependencies: [],
          })),
          estimated_duration: response.plan.reduce((sum, step) => sum + (step.estimatedTime || 10), 0),
          confidence: 0.8,
        },
      };
    }
  }

  /**
   * Run Management
   */
  async getRun(runId: string): Promise<Run> {
    if (this.useRealBackend) {
      return await this.realApiClient.getRun(runId);
    } else {
      // Mock backend doesn't have run management, return a mock response
      return {
        id: runId,
        question: 'Mock question',
        status: 'completed',
        user_id: 'mock-user',
        dataset_id: 'mock-dataset',
        created_at: new Date().toISOString(),
        result: { summary: 'Mock analysis completed' },
      };
    }
  }

  /**
   * Audit Logs
   */
  async getAuditLogs(runId: string): Promise<any[]> {
    if (this.useRealBackend) {
      return await this.realApiClient.getAuditLogs(runId);
    } else {
      // Mock backend doesn't have audit logs
      return [];
    }
  }

  /**
   * System Metrics
   */
  async getSystemMetrics(): Promise<any> {
    if (this.useRealBackend) {
      return await this.realApiClient.getSystemMetrics();
    } else {
      // Mock metrics
      return {
        active_runs: 0,
        total_runs: 0,
        success_rate: 1.0,
        average_duration: 0,
        uptime_seconds: 0,
      };
    }
  }

  /**
   * WebSocket connection (only available with real backend)
   */
  subscribeToRunEvents(
    runId: string,
    onEvent: (event: WebSocketEvent) => void
  ): any {
    if (this.useRealBackend) {
      return this.realApiClient.subscribeToRunEvents(runId, onEvent);
    } else {
      // Mock backend doesn't support WebSocket
      console.warn('WebSocket events not available in mock mode');
      return null;
    }
  }

  /**
   * Execute complete analysis workflow
   */
  async executeAnalysis(
    question: string,
    datasetId: string,
    onProgress?: (event: WebSocketEvent) => void
  ): Promise<{ run: Run; events: WebSocketEvent[] }> {
    if (this.useRealBackend) {
      return await this.realApiClient.executeAnalysis(question, datasetId, onProgress);
    } else {
      // Mock execution
      const { run_id, plan } = await this.askQuestion(question, datasetId);
      
      // Simulate progress
      if (onProgress) {
        setTimeout(() => {
          onProgress({
            run_id,
            timestamp: new Date().toISOString(),
            event_type: 'run_started',
            data: { question, plan },
          });
        }, 100);

        setTimeout(() => {
          onProgress({
            run_id,
            timestamp: new Date().toISOString(),
            event_type: 'step_completed',
            step_id: 'mock_step',
            data: { result: 'Mock step completed' },
          });
        }, 1000);

        setTimeout(() => {
          onProgress({
            run_id,
            timestamp: new Date().toISOString(),
            event_type: 'run_completed',
            data: { result: { summary: 'Mock analysis completed' } },
          });
        }, 2000);
      }

      // Wait for completion
      await new Promise(resolve => setTimeout(resolve, 2500));
      
      const run = await this.getRun(run_id);
      return { run, events: [] };
    }
  }

  /**
   * Set authentication token
   */
  setToken(token: string): void {
    this.realApiClient.setToken(token);
    this.mockApiClient.setToken(token);
  }
}

// Global adapter instance
let apiAdapterInstance: ApiAdapter | null = null;

/**
 * Get or create the API adapter singleton
 */
export function getApiAdapter(useRealBackend?: boolean): ApiAdapter {
  if (!apiAdapterInstance) {
    // Determine backend mode from environment or parameter
    const useReal = useRealBackend ?? 
      (process.env.NEXT_PUBLIC_USE_REAL_BACKEND === 'true' || 
       process.env.NEXT_PUBLIC_API_URL?.includes('8000'));
    
    apiAdapterInstance = new ApiAdapter(useReal);
  }
  return apiAdapterInstance;
}

/**
 * Reset API adapter (useful for testing)
 */
export function resetApiAdapter(): void {
  if (apiAdapterInstance) {
    apiAdapterInstance = null;
  }
  resetRealApiClient();
}

/**
 * Hook for using the API adapter in React components
 */
export function useApiAdapter() {
  const adapter = getApiAdapter();
  
  const switchBackend = (useReal: boolean) => {
    adapter.setBackendMode(useReal);
  };
  
  return {
    api: adapter,
    backendMode: adapter.getBackendMode(),
    switchBackend,
  };
}
