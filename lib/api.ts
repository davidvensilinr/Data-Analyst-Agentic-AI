import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  UploadRequest,
  UploadResponse,
  ProfileResponse,
  CleaningPlanRequest,
  CleaningPlanResponse,
  CleaningExecutionRequest,
  CleaningExecutionResponse,
  AgentQueryRequest,
  AgentQueryInitResponse,
  AuditLog,
  ApiErrorClass,
  RunHistory,
  Dataset,
  Project,
} from './types';

/**
 * API Client for Autonomous Data Analyst
 * Provides type-safe methods for all backend endpoints
 */
export class ApiClient {
  private client: AxiosInstance;
  private baseUrl: string;
  private token?: string;

  constructor(baseUrl: string = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001/api', token?: string) {
    this.baseUrl = baseUrl;
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
        throw new ApiErrorClass(
          errorData?.code || error.code || 'UNKNOWN_ERROR',
          errorData?.message || error.message || 'An error occurred',
          errorData?.details
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
   * Update base URL (useful for switching between mock and real backend)
   */
  setBaseUrl(baseUrl: string): void {
    this.baseUrl = baseUrl;
    this.client.defaults.baseURL = baseUrl;
  }

  /**
   * Project Management
   */
  async createProject(name: string, description?: string): Promise<Project> {
    const { data } = await this.client.post<Project>('/projects', {
      name,
      description,
    });
    return data;
  }

  async listProjects(): Promise<Project[]> {
    const { data } = await this.client.get<Project[]>('/projects');
    return data;
  }

  async getProject(projectId: string): Promise<Project> {
    const { data } = await this.client.get<Project>(`/projects/${projectId}`);
    return data;
  }

  /**
   * Dataset Management
   */
  async listDatasets(projectId: string): Promise<Dataset[]> {
    const { data } = await this.client.get<Dataset[]>('/datasets', {
      params: { projectId },
    });
    return data;
  }

  async getDataset(datasetId: string): Promise<Dataset> {
    const { data } = await this.client.get<Dataset>(`/datasets/${datasetId}`);
    return data;
  }

  /**
   * File Upload with streaming progress
   */
  async uploadFile(
    file: File,
    datasetName: string,
    projectId: string,
    schemaHints?: Record<string, string>,
    onUploadProgress?: (progress: number) => void
  ): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('datasetName', datasetName);
    formData.append('projectId', projectId);
    if (schemaHints) {
      formData.append('schemaHints', JSON.stringify(schemaHints));
    }

    const { data } = await this.client.post<UploadResponse>('/upload', formData, {
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

  /**
   * Data Profiling
   */
  async getProfile(datasetId: string): Promise<ProfileResponse> {
    const { data } = await this.client.get<ProfileResponse>('/profile', {
      params: { datasetId },
    });
    return data;
  }

  /**
   * Data Cleaning
   */
  async generateCleaningPlan(request: CleaningPlanRequest): Promise<CleaningPlanResponse> {
    const { data } = await this.client.post<CleaningPlanResponse>('/clean/plan', request);
    return data;
  }

  async executeCleaning(request: CleaningExecutionRequest): Promise<CleaningExecutionResponse> {
    const { data } = await this.client.post<CleaningExecutionResponse>('/clean/execute', request);
    return data;
  }

  /**
   * Query / Agent
   */
  async submitQuery(request: AgentQueryRequest): Promise<AgentQueryInitResponse> {
    const { data } = await this.client.post<AgentQueryInitResponse>('/ask', request);
    return data;
  }

  /**
   * Audit & Activity
   */
  async getAuditLog(auditLogId: string): Promise<AuditLog> {
    const { data } = await this.client.get<AuditLog>(`/audit/${auditLogId}`);
    return data;
  }

  async listRunHistory(datasetId: string, limit: number = 50, offset: number = 0): Promise<RunHistory[]> {
    const { data } = await this.client.get<RunHistory[]>('/history', {
      params: { datasetId, limit, offset },
    });
    return data;
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<boolean> {
    try {
      const { data } = await this.client.get('/health');
      return data?.status === 'ok';
    } catch {
      return false;
    }
  }
}

// Singleton instance
let apiClientInstance: ApiClient | null = null;

/**
 * Get or create the API client singleton
 */
export function getApiClient(baseUrl?: string, token?: string): ApiClient {
  if (!apiClientInstance) {
    apiClientInstance = new ApiClient(baseUrl, token);
  }
  return apiClientInstance;
}

/**
 * Reset API client (useful for testing)
 */
export function resetApiClient(): void {
  apiClientInstance = null;
}
