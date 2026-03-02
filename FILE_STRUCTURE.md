# Project File Structure

## Directory Layout

```
autonomous-data-analyst-frontend/
├── app/                           # Next.js App Router
│   ├── page.tsx                  # Landing page
│   ├── layout.tsx                # Root layout with providers
│   ├── providers.tsx             # App providers (Zustand, theme)
│   ├── globals.css               # Global Tailwind styles
│   ├── projects/
│   │   ├── page.tsx              # Project selector/dashboard
│   │   ├── [id]/
│   │   │   ├── datasets/
│   │   │   │   ├── page.tsx      # Dataset list for project
│   │   │   │   ├── [datasetId]/
│   │   │   │   │   ├── profile/
│   │   │   │   │   │   └── page.tsx      # Data profiling dashboard
│   │   │   │   │   ├── cleaning/
│   │   │   │   │   │   └── page.tsx      # Data cleaning editor
│   │   │   │   │   └── query/
│   │   │   │   │       └── page.tsx      # Query/analysis interface
│   │   │   └── upload/
│   │   │       └── page.tsx      # Dataset upload page
│
├── components/                     # Reusable React components
│   ├── ui/                        # shadcn/ui components (pre-generated)
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── badge.tsx
│   │   ├── input.tsx
│   │   ├── textarea.tsx
│   │   └── ... (other UI components)
│   │
│   ├── dataset/                   # Dataset-related components
│   │   ├── FileUpload.tsx         # File upload with drag-drop
│   │   └── PreviewTable.tsx       # Data preview table
│   │
│   ├── profiling/                 # Data profiling components
│   │   ├── ColumnCard.tsx         # Single column statistics
│   │   ├── ProfileDashboard.tsx   # Main profiling dashboard
│   │   └── HistogramChart.tsx     # Distribution visualizations
│   │
│   ├── cleaning/                  # Data cleaning components
│   │   ├── CleaningEditor.tsx     # Main cleaning interface
│   │   ├── StepToggle.tsx         # Step enable/disable
│   │   └── DiffView.tsx           # Before/after comparison
│   │
│   ├── agent/                     # Agent/query components
│   │   ├── StepTraceVisualizer.tsx # Step execution timeline
│   │   ├── PlanPanel.tsx          # Plan visualization
│   │   └── ChainOfThought.tsx     # Agent reasoning display
│   │
│   ├── query/                     # Query result components
│   │   ├── ResultsDisplay.tsx     # Charts, tables, summary
│   │   ├── ChartRenderer.tsx      # Dynamic chart rendering
│   │   └── TableViewer.tsx        # Interactive table display
│   │
│   └── audit/                     # Audit log components
│       └── AuditLog.tsx           # Immutable activity log
│
├── lib/                            # Utility functions and config
│   ├── api.ts                     # API client wrapper
│   ├── config.ts                  # App configuration
│   ├── types.ts                   # TypeScript type definitions
│   ├── mock-data.ts               # Mock data generators
│   ├── utils.ts                   # Utility functions
│   │
│   ├── store/                     # Zustand stores
│   │   ├── dataset.store.ts       # Dataset state
│   │   ├── query.store.ts         # Query/analysis state
│   │   └── ui.store.ts            # UI state (theme, modals)
│   │
│   └── hooks/                     # Custom React hooks
│       ├── useWebSocket.ts        # WebSocket connection hook
│       └── useDatasetUpload.ts    # Upload management hook
│
├── mock-backend/                   # Mock backend server
│   ├── server.js                  # Express.js API server
│   ├── sample-datasets/
│   │   ├── sales_messy.csv        # Example dataset
│   │   ├── customers.json         # Example JSON data
│   │   └── products.parquet       # Example Parquet file
│   └── routes/                    # Mock API routes (in server.js)
│
├── public/                         # Static assets
│   ├── icon.svg
│   ├── icon-light-32x32.png
│   └── icon-dark-32x32.png
│
├── __tests__/                      # Test files
│   ├── components/
│   │   ├── FileUpload.test.tsx
│   │   └── ProfileDashboard.test.tsx
│   ├── hooks/
│   │   └── useWebSocket.test.ts
│   └── lib/
│       └── api.test.ts
│
├── cypress/                        # E2E tests
│   ├── e2e/
│   │   └── full-flow.cy.ts        # Complete workflow tests
│   ├── support/
│   │   ├── commands.ts
│   │   └── e2e.ts
│   └── fixtures/                  # Test data
│
├── config/                         # Configuration files
│   ├── next.config.mjs            # Next.js configuration
│   ├── tailwind.config.ts         # Tailwind CSS config
│   ├── tsconfig.json              # TypeScript configuration
│   └── postcss.config.js          # PostCSS configuration
│
├── docker/                         # Docker configurations
│   ├── Dockerfile                 # Frontend Dockerfile
│   ├── Dockerfile.backend         # Backend Dockerfile
│   └── docker-compose.yml         # Docker Compose configuration
│
├── Documentation files
│   ├── README.md                  # Getting started guide
│   ├── GETTING_STARTED.md         # Detailed setup instructions
│   ├── ARCHITECTURE.md            # System architecture
│   ├── API_CONTRACT.md            # API specifications
│   ├── API.md                     # API documentation
│   ├── INTEGRATION_GUIDE.md       # Backend integration
│   ├── DEPLOYMENT.md              # Deployment guide
│   └── FILE_STRUCTURE.md          # This file
│
├── Configuration files
│   ├── .env.example               # Environment variable template
│   ├── .env.local                 # Local environment (git ignored)
│   ├── .env.production            # Production environment
│   ├── .gitignore                 # Git ignore rules
│   ├── .prettierrc                # Prettier formatting
│   ├── .eslintrc.json             # ESLint rules
│   ├── jest.config.js             # Jest test configuration
│   ├── jest.setup.js              # Jest setup file
│   ├── cypress.config.ts          # Cypress configuration
│   ├── package.json               # NPM dependencies & scripts
│   └── package-lock.json          # Locked dependencies
│
└── Postman/API files
    └── postman-collection.json    # API test collection
```

## Key File Descriptions

### Frontend Pages

| File | Purpose | Route |
|------|---------|-------|
| `app/page.tsx` | Landing page with CTA | `/` |
| `app/projects/page.tsx` | Project selector/dashboard | `/projects` |
| `app/projects/[id]/datasets/page.tsx` | Datasets in project | `/projects/:id/datasets` |
| `app/projects/[id]/upload/page.tsx` | Upload new dataset | `/projects/:id/upload` |
| `app/projects/[id]/datasets/[datasetId]/profile/page.tsx` | Data profiling | `/projects/:id/datasets/:datasetId/profile` |
| `app/projects/[id]/datasets/[datasetId]/cleaning/page.tsx` | Data cleaning | `/projects/:id/datasets/:datasetId/cleaning` |
| `app/projects/[id]/datasets/[datasetId]/query/page.tsx` | Query interface | `/projects/:id/datasets/:datasetId/query` |

### Core Libraries

| File | Purpose |
|------|---------|
| `lib/api.ts` | All API endpoint abstractions |
| `lib/types.ts` | TypeScript interface definitions |
| `lib/config.ts` | Configuration constants |
| `lib/mock-data.ts` | Data generation functions |

### State Management (Zustand)

| Store | Purpose |
|-------|---------|
| `dataset.store.ts` | Dataset state & metadata |
| `query.store.ts` | Query execution & results state |
| `ui.store.ts` | Theme, modals, UI state |

### Components

| Component | Purpose |
|-----------|---------|
| `FileUpload.tsx` | File upload with preview |
| `PreviewTable.tsx` | Data preview before upload |
| `ProfileDashboard.tsx` | Column statistics dashboard |
| `CleaningEditor.tsx` | Cleaning steps editor |
| `StepTraceVisualizer.tsx` | Agent step execution timeline |
| `ResultsDisplay.tsx` | Results (charts, tables, summary) |
| `AuditLog.tsx` | Activity & audit trail |

### Testing

| File | Purpose |
|------|---------|
| `__tests__/components/*.test.tsx` | Component unit tests |
| `__tests__/hooks/*.test.ts` | Hook unit tests |
| `cypress/e2e/*.cy.ts` | End-to-end tests |

### Backend

| File | Purpose |
|------|---------|
| `mock-backend/server.js` | Full mock API server |
| `mock-backend/sample-datasets/` | Example data files |

### Configuration

| File | Purpose |
|------|---------|
| `.env.example` | Template for environment variables |
| `docker-compose.yml` | Docker container orchestration |
| `postman-collection.json` | API testing collection |

## Environment Variables

```
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXT_PUBLIC_WS_URL=ws://localhost:3001

# Authentication
API_TOKEN=your-token-here

# Feature Flags
NEXT_PUBLIC_SANDBOX_MODE=true
NEXT_PUBLIC_ENABLE_PII_REDACTION=true

# Upload Configuration
NEXT_PUBLIC_MAX_UPLOAD_MB=100
NEXT_PUBLIC_ALLOWED_FILE_TYPES=csv,json,parquet

# Theme
NEXT_PUBLIC_THEME=light|dark|system
```

## Component Hierarchy

```
<RootLayout>
  ├── <Providers>
  │   ├── Theme Provider
  │   └── Zustand Stores
  │
  └── <Page Routes>
      ├── Landing
      │   └── Projects Dashboard
      │       ├── Upload Dataset
      │       │   └── FileUpload
      │       │       └── PreviewTable
      │       ├── Data Profiling
      │       │   └── ProfileDashboard
      │       │       └── ColumnCard[]
      │       ├── Data Cleaning
      │       │   └── CleaningEditor
      │       │       └── StepToggle[]
      │       └── Query Interface
      │           ├── QueryInput
      │           ├── StepTraceVisualizer
      │           └── ResultsDisplay
      │               ├── ChartRenderer
      │               ├── TableViewer
      │               └── AuditLog
```

## Data Flow

```
User Upload
    ↓
[FileUpload] → api.uploadDataset() → Backend
    ↓
[dataset.store] ← Response with dataset_id
    ↓
[PreviewTable] displays preview
    ↓
User navigates to Profile
    ↓
[ProfileDashboard] → api.getProfile() → Backend
    ↓
[ProfileDashboard] renders with stats
    ↓
User submits Query
    ↓
[QueryInput] → api.submitQuery() → Backend
    ↓
WebSocket connection established
    ↓
[StepTraceVisualizer] streams steps from WS
    ↓
[query.store] updated with step results
    ↓
[ResultsDisplay] renders final results
    ↓
[AuditLog] records the activity
```

## Scripts Reference

```bash
# Development
npm run dev                # Start frontend (port 3000)
npm run mock-backend       # Start mock backend (port 3001)
npm run dev:full           # Start both frontend and backend

# Testing
npm run test               # Run unit tests
npm run test:watch        # Watch mode for tests
npm run test:coverage     # Coverage report
npm run e2e               # Open Cypress
npm run e2e:run           # Run Cypress headlessly

# Production
npm run build              # Build for production
npm run start              # Start production server
npm run lint               # Run ESLint

# Code Quality
npx prettier --write .     # Format code
npx eslint --fix .         # Fix linting issues
```

## Docker Usage

```bash
# Build and run everything
docker-compose up --build

# Frontend only
docker build -f Dockerfile -t frontend .
docker run -p 3000:3000 frontend

# Backend only
docker build -f Dockerfile.backend -t backend .
docker run -p 3001:3001 backend
```
