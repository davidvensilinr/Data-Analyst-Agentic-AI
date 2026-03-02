from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class StepType(str, Enum):
    PROFILE = "profile"
    CLEAN = "clean"
    SQL = "sql"
    ANALYSIS = "analysis"
    VISUALIZATION = "visualization"
    ANOMALY = "anomaly"
    RECOMMENDATION = "recommendation"


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# Base schemas
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True


# User schemas
class UserBase(BaseSchema):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: str
    is_active: bool
    created_at: datetime


# Dataset schemas
class DatasetBase(BaseSchema):
    name: str
    description: Optional[str] = None
    is_public: bool = False


class DatasetCreate(DatasetBase):
    pass


class Dataset(DatasetBase):
    id: str
    file_path: str
    file_size: Optional[int]
    file_type: str
    schema_info: Optional[Dict[str, Any]]
    profile_info: Optional[Dict[str, Any]]
    owner_id: str
    created_at: datetime
    updated_at: datetime


# Step schemas
class StepSpec(BaseSchema):
    step_id: str
    step_type: StepType
    spec: Dict[str, Any]
    dependencies: Optional[List[str]] = []


class Plan(BaseSchema):
    steps: List[StepSpec]
    estimated_duration: Optional[int] = None
    confidence: Optional[float] = None


class StepResult(BaseSchema):
    step_id: str
    step_type: StepType
    status: StepStatus
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    model_prompt: Optional[str] = None
    model_output: Optional[str] = None
    tool_call: Optional[Dict[str, Any]] = None
    tool_result: Optional[Dict[str, Any]] = None
    rationale: Optional[str] = None
    confidence: Optional[float] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# Run schemas
class RunCreate(BaseSchema):
    question: str
    dataset_id: str
    dry_run: bool = False


class Run(BaseSchema):
    id: str
    question: str
    plan: Optional[Plan]
    status: RunStatus
    result: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    user_id: str
    dataset_id: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    steps: Optional[List[StepResult]] = None


class RunWithDetails(Run):
    dataset: Dataset
    steps: List[StepResult]


# API Request/Response schemas
class UploadResponse(BaseSchema):
    dataset_id: str
    name: str
    file_type: str
    file_size: int


class ProfileResponse(BaseSchema):
    dataset_id: str
    profile_info: Dict[str, Any]


class CleanPlanRequest(BaseSchema):
    dataset_id: str
    cleaning_goals: Optional[List[str]] = None


class CleanPlanResponse(BaseSchema):
    plan: Plan
    rationale: str


class CleanExecuteRequest(BaseSchema):
    dataset_id: str
    plan: Plan
    apply_changes: bool = False


class CleanExecuteResponse(BaseSchema):
    run_id: str
    cleaned_dataset_id: Optional[str] = None
    changes_applied: bool


class AskRequest(BaseSchema):
    question: str
    dataset_id: str
    dry_run: bool = False


class AskResponse(BaseSchema):
    run_id: str
    plan: Plan


# WebSocket Event schemas
class EventType(str, Enum):
    RUN_STARTED = "run_started"
    RUN_COMPLETED = "run_completed"
    RUN_FAILED = "run_failed"
    STEP_STARTED = "step_started"
    STEP_COMPLETED = "step_completed"
    STEP_FAILED = "step_failed"
    PLAN_UPDATED = "plan_updated"


class WebSocketEvent(BaseSchema):
    run_id: str
    timestamp: datetime
    event_type: EventType
    step_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


# Audit schemas
class AuditLogEntry(BaseSchema):
    id: str
    run_id: str
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]
    content_hash: str
    user_id: str


# Configuration schemas
class LLMConfig(BaseSchema):
    provider: str = "openai"
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 4000
    temperature: float = 0.1
    api_key: Optional[str] = None


class SafetyConfig(BaseSchema):
    require_human_approval: bool = True
    read_only_mode: bool = False
    sanitize_logs: bool = True
    sensitive_columns: List[str] = []
    max_query_rows: int = 100000
    query_timeout_seconds: int = 30


# Error schemas
class ErrorDetail(BaseSchema):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseSchema):
    error: ErrorDetail
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Visualization schemas
class ChartSpec(BaseSchema):
    type: str  # bar, line, scatter, etc.
    data: Dict[str, Any]
    config: Optional[Dict[str, Any]] = None
    title: Optional[str] = None
    description: Optional[str] = None


class AnalysisResult(BaseSchema):
    summary: str
    insights: List[str]
    recommendations: List[str]
    confidence: float
    charts: Optional[List[ChartSpec]] = None
    tables: Optional[List[Dict[str, Any]]] = None


# Metrics schemas
class RunMetrics(BaseSchema):
    total_duration_seconds: float
    step_durations: Dict[str, float]
    llm_tokens_used: int
    llm_api_calls: int
    queries_executed: int
    rows_processed: int
    memory_peak_mb: float


class SystemMetrics(BaseSchema):
    active_runs: int
    total_runs: int
    success_rate: float
    average_duration: float
    uptime_seconds: float
