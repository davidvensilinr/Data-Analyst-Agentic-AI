import axios, { AxiosInstance, AxiosError } from 'axios';
import { io, Socket } from 'socket.io-client';

// Types for the autonomous data analyst backend
export interface Dataset {
  id: string;
  name: string;
  description?: string;
  file_path: string;
  file_size?: number;
  file_type: string;
  schema_info?: Record<string, any>;
  profile_info?: Record<string, any>;
  owner_id: string;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export interface Run {
  id: string;
  question: string;
  plan?: Plan;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result?: Record<string, any>;
  metrics?: Record<string, any>;
  user_id: string;
  dataset_id: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  steps?: RunStep[];
}

export interface Plan {
  steps: StepSpec[];
  estimated_duration?: number;
  confidence?: number;
}

export interface StepSpec {
  step_id: string;
  step_type: 'profile' | 'clean' | 'sql' | 'analysis' | 'visualization' | 'anomaly' | 'recommendation';
  spec: Record<string, any>;
  dependencies?: string[];
}

export interface RunStep {
  id: string;
  run_id: string;
  step_id: string;
  step_type: string;
  spec: Record<string, any>;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result?: Record<string, any>;
  error_message?: string;
  model_prompt?: string;
  model_output?: string;
  tool_call?: Record<string, any>;
  tool_result?: Record<string, any>;
  rationale?: string;
  confidence?: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

export interface AuditLog {
  id: string;
  run_id: string;
  event_type: string;
  timestamp: string;
  data: Record<string, any>;
  content_hash: string;
  user_id: string;
}

export interface WebSocketEvent {
  run_id: string;
  timestamp: string;
  event_type: 'run_started' | 'run_completed' | 'run_failed' | 'step_started' | 'step_completed' | 'step_failed' | 'plan_updated';
  step_id?: string;
  data?: Record<string, any>;
}

export interface SystemMetrics {
  active_runs: number;
  total_runs: number;
  success_rate: number;
  average_duration: number;
  uptime_seconds: number;
}

/**
 * Real API Client for Autonomous Data Analyst Backend
 */
export class RealApiClient {
  private client: AxiosInstance;
  private baseUrl: string;
  private wsUrl: string;
  private token?: string;
  private socket?: Socket;

  constructor(
    baseUrl: string = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    wsUrl: string = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000',
    token?: string
  ) {
    this.baseUrl = baseUrl;
    this.wsUrl = wsUrl;
    this.token = token;

    this.client = axios.create({
      baseURL: baseUrl,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor for authentication
    this.client.interceptors.request.use((config) => {
      if (this.token) {
        config.headers.Authorization = `Bearer ${this.token}`;
      }
      return config;
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        const errorData = error.response?.data as any;
        console.error('API Error:', errorData);
        throw new Error(
          errorData?.detail?.message || errorData?.message || error.message || 'An error occurred'
        );
      }
    );
  }

  /**
   * Set or update authentication token
   */
  setToken(token: string): void {
    this.token = token;
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string; version: string }> {
    const { data } = await this.client.get('/health');
    return data;
  }

  /**
   * Dataset Management
   */
  async uploadDataset(
    file: File,
    name: string,
    description?: string,
    isPublic: boolean = false,
    onUploadProgress?: (progress: number) => void
  ): Promise<{ dataset_id: string; name: string; file_type: string; file_size: number }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', name);
    if (description) formData.append('description', description);
    formData.append('is_public', isPublic.toString());

    const { data } = await this.client.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onUploadProgress?.(progress);
        }
      },
    });

    return data;
  }

  async listDatasets(skip: number = 0, limit: number = 50): Promise<Dataset[]> {
    const { data } = await this.client.get<Dataset[]>('/api/datasets', {
      params: { skip, limit },
    });
    return data;
  }

  async getDataset(datasetId: string): Promise<Dataset> {
    const { data } = await this.client.get<Dataset>(`/api/datasets/${datasetId}`);
    return data;
  }

  /**
   * Data Profiling
   */
  async getDatasetProfile(datasetId: string): Promise<Record<string, any>> {
    const { data } = await this.client.get(`/api/profile/${datasetId}`);
    return data.profile_info;
  }

  /**
   * Data Cleaning
   */
  async createCleaningPlan(
    datasetId: string,
    cleaningGoals?: string[]
  ): Promise<{ plan: Plan; rationale: string }> {
    const { data } = await this.client.post('/api/clean/plan', {
      dataset_id: datasetId,
      cleaning_goals: cleaningGoals,
    });
    return data;
  }

  async executeCleaningPlan(
    datasetId: string,
    plan: Plan,
    applyChanges: boolean = false
  ): Promise<{ run_id: string; cleaned_dataset_id?: string; changes_applied: boolean }> {
    const { data } = await this.client.post('/api/clean/execute', {
      dataset_id: datasetId,
      plan: plan,
      apply_changes: applyChanges,
    });
    return data;
  }

  /**
   * Analysis / Query
   */
  async askQuestion(
    question: string,
    datasetId: string,
    dryRun: boolean = false
  ): Promise<{ run_id: string; plan: Plan }> {
    const { data } = await this.client.post('/api/ask', {
      question: question,
      dataset_id: datasetId,
      dry_run: dryRun,
    });
    return data;
  }

  /**
   * Run Management
   */
  async getRun(runId: string): Promise<Run> {
    const { data } = await this.client.get<Run>(`/api/run/${runId}`);
    return data;
  }

  async getRunWithDetails(runId: string): Promise<Run> {
    const { data } = await this.client.get<Run>(`/api/run/${runId}`);
    return data;
  }

  /**
   * Audit Logs
   */
  async getAuditLogs(runId: string): Promise<AuditLog[]> {
    const { data } = await this.client.get<AuditLog[]>(`/api/audit/${runId}`);
    return data;
  }

  /**
   * System Metrics
   */
  async getSystemMetrics(): Promise<SystemMetrics> {
    const { data } = await this.client.get<SystemMetrics>('/api/metrics');
    return data;
  }

  /**
   * WebSocket connection for real-time updates
   */
  connectWebSocket(runId: string): Socket {
    if (this.socket) {
      this.socket.disconnect();
    }

    this.socket = io(`${this.wsUrl}/ws/runs/${runId}`, {
      transports: ['websocket'],
    });

    return this.socket;
  }

  disconnectWebSocket(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = undefined;
    }
  }

  /**
   * Subscribe to run events
   */
  subscribeToRunEvents(
    runId: string,
    onEvent: (event: WebSocketEvent) => void
  ): Socket {
    const socket = this.connectWebSocket(runId);

    socket.on('connect', () => {
      console.log('Connected to WebSocket for run:', runId);
    });

    socket.on('message', (data: WebSocketEvent) => {
      onEvent(data);
    });

    socket.on('disconnect', () => {
      console.log('Disconnected from WebSocket for run:', runId);
    });

    socket.on('error', (error) => {
      console.error('WebSocket error:', error);
    });

    return socket;
  }

  /**
   * Execute a complete analysis workflow
   */
  async executeAnalysis(
    question: string,
    datasetId: string,
    onProgress?: (event: WebSocketEvent) => void
  ): Promise<{ run: Run; events: WebSocketEvent[] }> {
    // Start the analysis
    const { run_id, plan } = await this.askQuestion(question, datasetId);
    
    const events: WebSocketEvent[] = [];
    
    // Subscribe to real-time events
    if (onProgress) {
      const socket = this.subscribeToRunEvents(run_id, (event) => {
        events.push(event);
        onProgress(event);
      });

      // Wait for completion
      return new Promise((resolve, reject) => {
        const checkCompletion = async () => {
          try {
            const run = await this.getRunWithDetails(run_id);
            if (run.status === 'completed') {
              socket.disconnect();
              resolve({ run, events });
            } else if (run.status === 'failed') {
              socket.disconnect();
              reject(new Error('Analysis failed'));
            } else {
              setTimeout(checkCompletion, 1000);
            }
          } catch (error) {
            socket.disconnect();
            reject(error);
          }
        };

        checkCompletion();
      });
    } else {
      // Simple polling without real-time updates
      const checkCompletion = async (): Promise<{ run: Run; events: WebSocketEvent[] }> => {
        const run = await this.getRunWithDetails(run_id);
        if (run.status === 'completed') {
          return { run, events };
        } else if (run.status === 'failed') {
          throw new Error('Analysis failed');
        } else {
          await new Promise(resolve => setTimeout(resolve, 1000));
          return checkCompletion();
        }
      };

      return checkCompletion();
    }
  }
}

// Singleton instance
let realApiClientInstance: RealApiClient | null = null;

/**
 * Get or create the real API client singleton
 */
export function getRealApiClient(
  baseUrl?: string,
  wsUrl?: string,
  token?: string
): RealApiClient {
  if (!realApiClientInstance) {
    realApiClientInstance = new RealApiClient(baseUrl, wsUrl, token);
  }
  return realApiClientInstance;
}

/**
 * Reset real API client (useful for testing)
 */
export function resetRealApiClient(): void {
  if (realApiClientInstance) {
    realApiClientInstance.disconnectWebSocket();
  }
  realApiClientInstance = null;
}
