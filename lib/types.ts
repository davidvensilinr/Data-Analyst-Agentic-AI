// ============================================================================
// Core Domain Types & API Contracts
// ============================================================================

/**
 * Project Management
 */
export interface Project {
  id: string;
  name: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
  datasetCount: number;
}

/**
 * Dataset Management
 */
export interface Dataset {
  id: string;
  name: string;
  projectId: string;
  fileName: string;
  fileSize: number;
  rowsEstimated: number;
  columnsCount: number;
  columns: string[];
  uploadedAt: string;
  updatedAt: string;
  profiledAt?: string;
}

export interface FileMetadata {
  fileName: string;
  fileSize: number;
  rowsEstimated: number;
  columnsCount: number;
  columns: string[];
  mimeType: string;
}

export interface PreviewRow {
  [key: string]: any;
}

/**
 * POST /api/upload
 */
export interface UploadRequest {
  file: File;
  datasetName: string;
  schemaHints?: Record<string, 'date' | 'number' | 'text' | 'boolean'>;
  projectId: string;
}

export interface UploadResponse {
  datasetId: string;
  dataset: Dataset;
  preview: PreviewRow[];
  metadata: FileMetadata;
}

/**
 * Data Profiling
 */
export interface ColumnProfile {
  name: string;
  type: 'string' | 'number' | 'date' | 'boolean' | 'unknown';
  nullPercent: number;
  uniqueCount: number;
  uniquePercent: number;
  sampleValues: any[];
  histogram?: Histogram;
  // Numeric stats
  min?: number;
  max?: number;
  mean?: number;
  median?: number;
  stdDev?: number;
  // String stats
  minLength?: number;
  maxLength?: number;
  avgLength?: number;
}

export interface Histogram {
  bins: (number | string)[];
  counts: number[];
  labels?: string[];
}

export interface MissingHeatmap {
  rows: number[];
  columns: string[];
  matrix: number[][];
}

export interface ProfileResponse {
  datasetId: string;
  columnsCount: number;
  rowsCount: number;
  columns: ColumnProfile[];
  qualityScore: number;
  qualityMetrics: {
    completeness: number;
    uniqueness: number;
    consistency: number;
    timeliness: number;
  };
  missingHeatmap: MissingHeatmap;
  correlationMatrix?: {
    columns: string[];
    matrix: number[][];
  };
  topRisks: DataQualityRisk[];
}

export interface DataQualityRisk {
  level: 'high' | 'medium' | 'low';
  issue: string;
  column?: string;
  affectedRows: number;
  recommendation: string;
}

/**
 * Data Cleaning
 */
export type CleaningStepType =
  | 'normalize-dates'
  | 'impute-missing'
  | 'drop-duplicates'
  | 'remove-outliers'
  | 'trim-whitespace'
  | 'standardize-text'
  | 'convert-type'
  | 'rename-column'
  | 'drop-column'
  | 'custom';

export interface CleaningStepParameter {
  name: string;
  type: 'string' | 'number' | 'enum' | 'boolean';
  value: any;
  options?: any[];
  description?: string;
}

export interface CleaningStep {
  stepId: string;
  type: CleaningStepType;
  description: string;
  parameters: Record<string, any>;
  enabled: boolean;
  estimatedRowImpact: number;
  rationale: string;
}

export interface CleaningPlanRequest {
  datasetId: string;
  requestedChanges?: string;
  autoDetect?: boolean;
}

export interface CleaningPlanResponse {
  planId: string;
  datasetId: string;
  steps: CleaningStep[];
}

export interface CleaningStepResult {
  stepId: string;
  status: 'running' | 'success' | 'failed' | 'skipped';
  beforeSample: PreviewRow[];
  afterSample: PreviewRow[];
  rowsAffected: number;
  rationale: string;
  timestamp: string;
  error?: string;
}

export interface CleaningExecutionRequest {
  planId: string;
  apply: boolean;
}

export interface CleaningExecutionResponse {
  cleanedDatasetId: string;
  auditLogId: string;
  steps: CleaningStepResult[];
}

/**
 * Agent Query & Execution
 */
export type AgentStepType =
  | 'query'
  | 'cleaning'
  | 'analysis'
  | 'visualization'
  | 'validation'
  | 'recommendation';

export interface AgentPlanStep {
  stepId: string;
  type: AgentStepType;
  description: string;
  estimatedTime?: number;
}

export interface AgentQueryRequest {
  datasetId: string;
  question: string;
  mode: 'auto' | 'dry_run';
  userId?: string;
}

export interface AgentQueryInitResponse {
  runId: string;
  plan: AgentPlanStep[];
}

export type AgentStreamEvent = {
  runId: string;
  timestamp: string;
} & (
  | {
      type: 'step_started';
      stepId: string;
      stepType: AgentStepType;
      stepDescription: string;
    }
  | {
      type: 'step_prompt';
      stepId: string;
      prompt: string;
    }
  | {
      type: 'step_tool_call';
      stepId: string;
      toolName: string;
      toolInput: Record<string, any>;
    }
  | {
      type: 'step_tool_result';
      stepId: string;
      toolName: string;
      result: any;
    }
  | {
      type: 'step_model_output';
      stepId: string;
      modelName: string;
      output: string;
      metadata?: Record<string, any>;
    }
  | {
      type: 'step_completed';
      stepId: string;
      status: 'success' | 'failed';
      output?: any;
      error?: string;
    }
  | {
      type: 'execution_completed';
      result: QueryResult;
    }
);

export interface QueryResult {
  runId: string;
  datasetId: string;
  question: string;
  charts: ChartSpec[];
  tables: TableResult[];
  summary: string;
  recommendations: string[];
  confidenceScore: number;
  executionTimeMs: number;
}

export interface ChartSpec {
  id: string;
  type: 'bar' | 'line' | 'scatter' | 'pie' | 'area' | 'heatmap';
  title: string;
  description?: string;
  xAxis?: {
    dataKey: string;
    label?: string;
  };
  yAxis?: {
    dataKey: string;
    label?: string;
  };
  data: Record<string, any>[];
  config?: Record<string, any>;
}

export interface TableResult {
  id: string;
  title: string;
  description?: string;
  columns: {
    key: string;
    label: string;
    type?: 'string' | 'number' | 'date' | 'boolean';
  }[];
  rows: Record<string, any>[];
  pageSize?: number;
}

/**
 * Audit & Activity
 */
export interface AuditLogEntry {
  id: string;
  timestamp: string;
  type: 'upload' | 'profile' | 'clean' | 'query';
  dataset: {
    id: string;
    name: string;
  };
  action: string;
  userId?: string;
  details: Record<string, any>;
  status: 'success' | 'failed';
}

export interface AuditLog {
  id: string;
  runId: string;
  timestamp: string;
  type: 'query' | 'cleaning';
  datasetId: string;
  userId?: string;
  prompts: PromptRecord[];
  toolCalls: ToolCallRecord[];
  modelOutputs: ModelOutputRecord[];
  steps: AuditLogEntry[];
  hash: string; // For immutability verification
}

export interface PromptRecord {
  stepId: string;
  modelName: string;
  prompt: string;
  timestamp: string;
}

export interface ToolCallRecord {
  stepId: string;
  toolName: string;
  input: Record<string, any>;
  output: any;
  timestamp: string;
}

export interface ModelOutputRecord {
  stepId: string;
  modelName: string;
  output: string;
  metadata?: Record<string, any>;
  timestamp: string;
}

export interface RunHistory {
  id: string;
  timestamp: string;
  datasetId: string;
  datasetName: string;
  question: string;
  confidenceScore: number;
  executionTimeMs: number;
  status: 'success' | 'failed';
  result?: QueryResult;
}

/**
 * Settings & Configuration
 */
export interface AppSettings {
  apiBaseUrl: string;
  apiToken?: string;
  uploadSizeLimit: number; // MB
  sandboxMode: boolean;
  redactPii: boolean;
  theme: 'light' | 'dark' | 'auto';
}

/**
 * Error Handling
 */
export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
}

export class ApiErrorClass extends Error implements ApiError {
  code: string;
  details?: Record<string, any>;
  timestamp: string;

  constructor(code: string, message: string, details?: Record<string, any>) {
    super(message);
    this.code = code;
    this.details = details;
    this.timestamp = new Date().toISOString();
    Object.setPrototypeOf(this, ApiErrorClass.prototype);
  }
}

/**
 * UI State Types
 */
export interface UploadState {
  file: File | null;
  metadata: FileMetadata | null;
  preview: PreviewRow[];
  isLoading: boolean;
  error: string | null;
}

export interface QueryState {
  question: string;
  mode: 'auto' | 'dry_run';
  runId?: string;
  plan: AgentPlanStep[];
  steps: Map<string, AgentStepExecution>;
  isExecuting: boolean;
  error: string | null;
  result?: QueryResult;
}

export interface AgentStepExecution {
  stepId: string;
  stepType?: AgentStepType;
  status: 'pending' | 'running' | 'completed' | 'failed';
  prompt?: string;
  toolCalls?: ToolCallRecord[];
  modelOutput?: string;
  output?: any;
  error?: string;
  startTime?: string;
  endTime?: string;
}

export interface PlanStep {
  stepId: string;
  type: AgentStepType;
  description: string;
  estimatedTime?: number;
}
