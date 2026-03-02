# Architecture Documentation

## System Overview

The Autonomous Data Analyst frontend is a modern React + TypeScript application built with Next.js 16, designed to be fully decoupled from its backend. This document outlines the architectural decisions, component hierarchy, data flow, and integration patterns.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js 16)                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           React Components (Pages + UI)              │   │
│  └──────────────┬───────────────────────────────────────┘   │
│                 │                                             │
│  ┌──────────────▼───────────────────────────────────────┐   │
│  │     Zustand State Management (Dataset/Query/UI)      │   │
│  └──────────────┬───────────────────────────────────────┘   │
│                 │                                             │
│  ┌──────────────▼───────────────────────────────────────┐   │
│  │   Custom Hooks (useWebSocket, useDatasetUpload)      │   │
│  └──────────────┬───────────────────────────────────────┘   │
│                 │                                             │
│  ┌──────────────▼───────────────────────────────────────┐   │
│  │   API Client (Axios with TypeScript types)           │   │
│  └──────────────┬───────────────────────────────────────┘   │
└─────────────────┼──────────────────────────────────────────┘
                  │
        ┌─────────▼──────────┐
        │  Network Layer     │
        │  (HTTP + WebSocket)│
        └─────────┬──────────┘
                  │
     ┌────────────┴─────────────┐
     │                          │
  ┌──▼──────┐            ┌─────▼─────┐
  │ Mock BE │            │ Real BE    │
  │ (Dev)   │            │(Production)│
  └─────────┘            └────────────┘
```

## State Management Architecture

We use Zustand for lightweight, decentralized state management with three core stores:

### 1. DatasetStore (`lib/store/dataset.store.ts`)
Manages dataset-related state across the upload → profile → cleaning workflow.

```typescript
{
  currentDataset: Dataset | null,
  currentProfile: ProfileResponse | null,
  currentCleaningPlan: CleaningPlanResponse | null,
  appliedCleaningSteps: Set<string>,
  uploadState: { file, metadata, preview, isLoading, error },
  
  // Methods
  setCurrentDataset,
  setCurrentProfile,
  setCurrentCleaningPlan,
  toggleCleaningStep,
  resetAll
}
```

**Design Decisions**:
- Cleaning steps stored as a `Set<string>` (stepIds) for O(1) lookup on toggle
- Upload state includes file, metadata, AND preview to avoid re-fetching
- All setters are immutable for React optimizer compatibility
- Persists to localStorage (except file blobs) via Zustand middleware

### 2. QueryStore (`lib/store/query.store.ts`)
Manages agent query state and execution trace.

```typescript
{
  question: string,
  mode: 'auto' | 'dry_run',
  runId: string | undefined,
  plan: AgentPlanStep[],
  steps: Map<string, AgentStepExecution>,
  isExecuting: boolean,
  error: string | null,
  result: QueryResult | undefined,
  runHistory: RunHistory[]
}
```

**Design Decisions**:
- Steps stored as a Map for efficient updates by stepId
- Plan is separate from steps to allow showing pending steps before execution
- Run history limited to 100 last runs for memory efficiency
- Full step execution details stored for trace visualizer

### 3. UIStore (`lib/store/ui.store.ts`)
Manages UI state: navigation, modals, theme, settings.

```typescript
{
  sidebarOpen: boolean,
  currentPage: string,
  currentProjectId: string | null,
  currentDatasetId: string | null,
  modals: { settingsOpen, helpOpen, confirmOpen },
  theme: 'light' | 'dark' | 'auto',
  settings: AppSettings,
  notificationQueue: Notification[]
}
```

**Design Decisions**:
- Notification queue auto-removes after 5s (unless duration: 0)
- Settings persisted to localStorage with warning about token storage
- Theme controlled by next-themes (respects system preference)

## Data Flow

### 1. File Upload Flow

```
FileUpload Component
    ↓
  [User selects file]
    ↓
FileUpload.handleFile()
    ├─ Validate type & size
    ├─ Parse CSV with PapaParse
    ├─ Extract metadata (rows, columns, types)
    └─ Generate preview (first 10 rows)
    ↓
onFileSelected() callback
    ↓
UploadPage.handleFileSelected()
    ├─ Update local state (selectedFile, metadata, preview)
    └─ Display PreviewTable
    ↓
  [User clicks "Upload Dataset"]
    ↓
UploadPage.handleUpload()
    ├─ Call api.uploadFile(file, metadata)
    ├─ Show progress bar
    └─ Store response in DatasetStore
    ↓
useDatasetStore.setCurrentDataset()
    ├─ Update global state
    └─ Redirect to profile page
```

### 2. Profile Analysis Flow

```
ProfilePage mounts
    ↓
useEffect → loadProfile()
    ↓
api.getProfile(datasetId)
    ├─ Simulates 1.5s delay (mock backend)
    └─ Returns ProfileResponse
    ↓
setProfile() + setCurrentProfile()
    ├─ Update local state
    └─ Update global store
    ↓
ProfileDashboard renders
    ├─ Displays quality score
    ├─ Lists data quality risks
    └─ Grid of ColumnCard components
    ↓
ColumnCard (for each column)
    ├─ Shows distribution histogram
    ├─ Displays min/max/mean/median
    └─ Highlights null percentage
```

### 3. Cleaning Execution Flow

```
CleaningPage mounts
    ↓
useEffect → generateCleaningPlan()
    ↓
api.generateCleaningPlan(datasetId)
    ├─ Simulates auto-detection
    └─ Returns CleaningPlanResponse
    ↓
useDatasetStore.setCurrentCleaningPlan()
    ├─ Initialize all steps as enabled
    └─ Show CleaningEditor
    ↓
[User toggles steps / clicks "Apply"]
    ↓
handleExecute(enabledStepIds)
    ├─ Show before/after preview
    ├─ Stream step results
    └─ Update audit log
    ↓
api.executeCleaning(planId, enabledSteps)
    ├─ Streams NDJSON results
    └─ Shows progress for each step
    ↓
displayResults()
    ├─ Show before/after samples
    ├─ List affected rows
    └─ Display rationale text
    ↓
Redirect to query page
```

### 4. Agent Query Flow

```
QueryPage mounts
    ↓
[User enters question + selects mode]
    ↓
handleSubmitQuery()
    ├─ Call api.submitQuery(question, mode)
    └─ Receive runId + plan
    ↓
QueryStore.setRunId() + setPlan()
    ├─ Show plan steps in sidebar
    └─ Initialize trace visualizer
    ↓
connectWebSocket(runId)
    ├─ Listen for step:* events
    └─ Reconnect on disconnect
    ↓
[Backend executes query]
    ↓
WebSocket events stream in:
  ├─ step_started → show step running
  ├─ step_prompt → display LLM prompt
  ├─ step_tool_call → show tool name + input
  ├─ step_tool_result → show tool output
  ├─ step_model_output → display response text
  └─ execution_completed → show final result
    ↓
QueryStore.updateStepExecution()
    ├─ Add to steps Map
    └─ Trace visualizer re-renders
    ↓
Final result received
    ├─ QueryStore.setResult()
    └─ Display ResultsPanel (charts + tables)
```

## Component Hierarchy

```
RootLayout (providers: Zustand, Toaster, ThemeProvider)
├─ Landing Page
│  └─ Feature cards
│  └─ CTA sections
├─ ProjectsPage
│  └─ ProjectCard (x N)
├─ [ProjectId] Layout
│  └─ UploadPage
│     ├─ FileUpload
│     └─ PreviewTable
│  └─ ProfilePage
│     └─ ProfileDashboard
│        └─ ColumnCard (x N columns)
│  └─ CleaningPage
│     └─ CleaningEditor
│        ├─ CleaningStepItem (x N steps)
│        └─ AuditLog
│  └─ QueryPage
│     ├─ QueryInput
│     ├─ PlanPanel
│     ├─ TraceVisualizer
│     │  └─ StepDetail (x N steps)
│     └─ ResultsPanel
│        ├─ ChartGallery
│        ├─ TableResults
│        ├─ SummaryCard
│        └─ RecommendationsPanel
└─ AuditPage
   └─ ActivityLog
      └─ RunDetail
```

## API Client Design

The `ApiClient` class in `lib/api.ts` is the single source of truth for all backend communication:

```typescript
class ApiClient {
  private client: AxiosInstance;
  private baseUrl: string;
  private token?: string;

  // Auto retry on 5xx with exponential backoff
  // Request interceptor: adds auth token
  // Response interceptor: converts errors to ApiErrorClass
  
  // Methods group by domain:
  // - Projects: createProject, listProjects, getProject
  // - Datasets: listDatasets, getDataset
  // - Upload: uploadFile (with progress callback)
  // - Profiling: getProfile
  // - Cleaning: generateCleaningPlan, executeCleaning
  // - Query: submitQuery
  // - Audit: getAuditLog, listRunHistory
  // - Health: healthCheck
}

// Singleton pattern
getApiClient(baseUrl?, token?): ApiClient
resetApiClient(): void
```

**Design Rationale**:
- Single endpoint configuration point
- Type-safe request/response contracts
- Error handling standardized
- Mock/real backend switch just changes baseUrl
- Interceptors for cross-cutting concerns (auth, retry)

## Type System

All types are defined in `lib/types.ts` for:
- Type safety across frontend
- Serving as API contract documentation
- Mock data generation based on types

Key type hierarchies:
- `Project` → `Dataset` → `FileMetadata` + `PreviewRow`
- `ProfileResponse` → `ColumnProfile` → `Histogram`
- `CleaningPlanResponse` → `CleaningStep` → parameters
- `AgentQueryInitResponse` → `AgentPlanStep` + streamed `AgentStreamEvent`
- `QueryResult` → `ChartSpec` + `TableResult`
- `AuditLog` → `PromptRecord` + `ToolCallRecord` + `ModelOutputRecord`

## Real-Time Communication

### WebSocket Integration

The `useWebSocket` custom hook encapsulates Socket.IO with:
- Auto-reconnection with exponential backoff
- Event listener management
- Error handling and fallback to polling
- Lifecycle cleanup

```typescript
const socket = useWebSocket({
  url: 'http://localhost:3001',
  autoConnect: true,
  reconnection: true,
  reconnectionDelayMax: 5000,
  reconnectionAttempts: 10
});

// Usage
socket.on('step:started', (event) => updateUI(event));
socket.send('subscribe', { runId });
```

**Event Format** (per API_CONTRACT.md):
```json
{
  "type": "step_started|step_prompt|step_tool_call|step_tool_result|step_model_output|execution_completed",
  "runId": "run-xxx",
  "stepId": "plan-step-2",
  "timestamp": "2024-01-20T12:06:00Z",
  // type-specific fields...
}
```

## Error Handling

Errors flow through a consistent pipeline:

```
HTTP/Network Error
    ↓
Axios interceptor catches
    ↓
Convert to ApiErrorClass
    ├─ code (e.g., "INVALID_REQUEST")
    ├─ message (e.g., "Dataset not found")
    ├─ details (optional context)
    └─ timestamp (ISO string)
    ↓
Component catch block
    ├─ Show toast.error(message)
    ├─ Update UI error state
    └─ Log to console for debugging
    ↓
User sees friendly error message
    ├─ (not raw stack trace)
    └─ Option to retry
```

## Performance Optimizations

1. **Code Splitting**: Next.js automatic route splitting
2. **Image Optimization**: next/image component
3. **Component Memoization**: React.memo on expensive visualizations
4. **Virtual Scrolling**: For large tables (todo: implement)
5. **Lazy Loading**: Dynamic imports for heavy charts
6. **Zustand Selectors**: Only re-render on state slice changes
7. **Pagination**: PreviewTable / ActivityLog paginated by default

## Testing Strategy

### Unit Tests (Jest + RTL)
- Component rendering with various props
- User interactions (click, type, select)
- State mutations via store
- API client methods
- Custom hook logic

### E2E Tests (Cypress)
- Full user journey: upload → profile → clean → ask
- Mock backend fixtures for deterministic results
- Visual assertions on results
- Error scenarios and edge cases

### Test Coverage Targets
- Components: 80%+
- Hooks: 90%+
- Stores: 85%+
- API client: 95%+

## Deployment Considerations

### Environment Separation
```bash
# Development
NEXT_PUBLIC_API_URL=http://localhost:3001/api
NODE_ENV=development

# Staging
NEXT_PUBLIC_API_URL=https://api.staging.dataanalyst.ai/api
NODE_ENV=production

# Production
NEXT_PUBLIC_API_URL=https://api.dataanalyst.ai/api
NODE_ENV=production
```

### Build Optimization
- Next.js static generation for landing page
- ISR (Incremental Static Regeneration) for project list
- Client-side rendering for interactive features
- Bundle analysis via @next/bundle-analyzer

### Monitoring
- Sentry for error tracking
- LogRocket for session replay
- Vercel Analytics for performance metrics
- Custom events for user interactions

## Future Architectural Improvements

1. **GraphQL API**: Reduce over-fetching with GraphQL queries
2. **Offline Support**: Service Workers + IndexedDB
3. **Real-time Collaboration**: Y.js / CRDT for multi-user editing
4. **Streaming UI**: Suspense + Server Components for AI responses
5. **Plugin System**: Custom cleaning steps and visualizations
6. **Caching Strategy**: React Query for server state
7. **Monorepo**: Shared types/components with backend (Nx/Turborepo)

## Security Architecture

1. **Authentication**: Bearer token in Authorization header
2. **HTTPS Only**: All production traffic encrypted
3. **CSP Headers**: Restrict script/style sources
4. **CORS**: Backend validates origin
5. **Input Validation**: Zod schemas for all user input
6. **XSS Prevention**: React escapes content by default
7. **PII Handling**: Optional redaction in previews

## Mock Backend Architecture

The mock backend in `mock-backend/server.js` provides realistic responses:
- 500-1500ms delays to simulate processing
- Realistic data distributions in profiles
- Streaming responses for cleaning/query
- Error scenarios for testing error boundaries
- CORS enabled for frontend dev

**Not a production system** - designed for:
- Offline development without real backend
- Testing UI without backend availability
- Demo purposes and presentations
- Understanding API contract

For production, implement backend following `API_CONTRACT.md`.
