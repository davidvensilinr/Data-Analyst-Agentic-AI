# Autonomous Data Analyst - Frontend

A production-quality React + TypeScript frontend for an autonomous data analysis platform. Upload datasets, analyze data quality, apply intelligent cleaning, and interact with AI agents that show you exactly how they work.

## Features

- **📊 Smart Data Profiling**: Automatic column statistics, quality scores, missing data heatmaps, and data quality risk detection
- **🧹 Intelligent Data Cleaning**: Auto-detect cleaning steps, preview before/after transformations, track audit logs
- **🤖 Agent Transparency**: Watch AI agents execute step-by-step with full visibility into prompts, tool calls, and model outputs
- **📈 Rich Visualizations**: Interactive charts and tables with zoom, export, and tooltip support
- **🔍 Full Audit Trail**: Immutable logs of every decision with timestamps, prompts, and execution details
- **🌓 Dark Mode**: Full light/dark theme support with next-themes
- **📱 Responsive Design**: Mobile-optimized interface that works on all devices
- **♿ Accessible**: WCAG-compliant components with keyboard navigation and screen reader support

## Architecture

### Frontend Stack
- **Framework**: Next.js 16 + React 19
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: Zustand
- **Charts**: Recharts
- **Real-time**: Socket.IO client (WebSocket with fallback)
- **Form Parsing**: PapaParse (CSV), XLSX (Excel)
- **Testing**: Jest + React Testing Library (unit), Cypress (E2E)

### Backend Stack (Mock)
- **Server**: Express.js
- **Port**: 3001
- **Endpoints**: 8 RESTful APIs + WebSocket for streaming
- **File Upload**: Multer with 100MB file size limit

### Project Structure

```
├── app/                              # Next.js App Router
│   ├── layout.tsx                    # Root layout with providers
│   ├── page.tsx                      # Landing page
│   ├── providers.tsx                 # Zustand + theme providers
│   ├── projects/                     # Project management
│   │   ├── page.tsx                  # Project selector
│   │   └── [id]/                     # Project detail routes
│   │       └── datasets/             # Dataset management
│   │           └── [datasetId]/      # Dataset operations
│   │               ├── profile/      # Data profiling
│   │               ├── clean/        # Data cleaning
│   │               └── query/        # Query/agent
│   └── api/                          # Route handlers (if needed)
├── components/                       # React components
│   ├── dataset/                      # Upload, preview, metadata
│   ├── profiling/                    # Column cards, dashboards, stats
│   ├── cleaning/                     # Cleaning steps, diffs, audit logs
│   ├── query/                        # Query input, results, trace visualizer
│   ├── audit/                        # Activity logs, run history
│   └── ui/                           # shadcn/ui components
├── lib/                              # Shared utilities
│   ├── api.ts                        # Axios-based API client
│   ├── types.ts                      # TypeScript type definitions
│   ├── mock-data.ts                  # Mock response generators
│   ├── store/                        # Zustand stores
│   │   ├── dataset.store.ts
│   │   ├── query.store.ts
│   │   └── ui.store.ts
│   └── hooks/                        # Custom React hooks
│       └── useWebSocket.ts
├── mock-backend/                     # Express mock server
│   ├── server.js                     # Main server
│   └── sample-datasets/              # Example CSV files
├── __tests__/                        # Unit tests
├── e2e/                              # Cypress E2E tests
├── Dockerfile                        # Frontend container
├── docker-compose.yml                # Full stack setup
└── API_CONTRACT.md                   # Detailed API documentation
```

## Quick Start

### Prerequisites
- Node.js 18+ (LTS recommended)
- pnpm (or npm/yarn)
- Docker & Docker Compose (optional, for containerized setup)

### Local Development (with Mock Backend)

1. **Install dependencies**
```bash
pnpm install
```

2. **Start frontend + mock backend in parallel**
```bash
pnpm run dev:full
```

This starts:
- Frontend: `http://localhost:3000`
- Mock Backend: `http://localhost:3001`

Or run separately:
```bash
# Terminal 1 - Frontend
pnpm run dev

# Terminal 2 - Mock Backend
pnpm run mock-backend
```

3. **Open in browser**
```
http://localhost:3000
```

### Docker Setup (Recommended for Full Stack)

```bash
# Build and start everything
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

Access:
- Frontend: `http://localhost:3000`
- Mock Backend: `http://localhost:3001`

## Usage

### 1. Create a Project
- Navigate to "Projects" page
- Enter project name and description
- Click "Create"

### 2. Upload Dataset
- Click "New Dataset" on a project
- Upload a CSV, JSON, or Parquet file
- View preview and metadata
- Enter dataset name
- Click "Upload Dataset"

### 3. Profile Dataset
- Automatically profiles on upload
- View column statistics, histograms, and quality metrics
- Review data quality risks
- Click "Next: Clean Data"

### 4. Clean Data
- Review auto-detected cleaning steps
- Toggle steps on/off
- Review parameters and rationale
- Click "Apply Selected Steps"
- Watch transformation progress

### 5. Query with Agent
- Navigate to "Query" tab
- Ask questions in natural language: *"What are our top 5 products by region?"*
- Choose "Auto" (execute) or "Dry Run" (just plan)
- Watch agent execute step-by-step with full transparency
- Review results: charts, tables, summary, recommendations

### 6. Audit & Export
- View all past runs in "Activity" panel
- Click on any run to see full audit log
- Download audit logs as JSON
- Review all prompts, tool calls, and model outputs

## API Integration

### Connecting to Real Backend

The frontend is fully decoupled from the mock backend. To connect to a real backend:

1. **Set API Base URL** via environment variable:
```bash
NEXT_PUBLIC_API_URL=https://api.your-backend.com/api
```

Or configure in Settings panel at runtime.

2. **Implement Backend Endpoints** following `API_CONTRACT.md`:
   - `POST /api/projects`
   - `GET /api/projects`
   - `POST /api/upload`
   - `GET /api/profile`
   - `POST /api/clean/plan`
   - `POST /api/clean/execute`
   - `POST /api/ask`
   - `GET /api/audit/:id`
   - `GET /api/health`

3. **WebSocket for Streaming** (optional):
   - Connect to `/socket.io` namespace
   - Listen for `step:*` events during agent execution
   - Frontend automatically handles reconnection with exponential backoff

See `API_CONTRACT.md` for detailed request/response schemas with examples.

## Configuration

### Environment Variables

```bash
# Frontend (Next.js)
NEXT_PUBLIC_API_URL=http://localhost:3001/api     # Backend API
NEXT_PUBLIC_APP_NAME=DataAnalyst AI               # App title

# Mock Backend
PORT=3001                                          # Backend port
NODE_ENV=development                               # Environment
```

### Settings Panel

Users can configure at runtime:
- API endpoint URL
- Authentication token
- File upload size limit (MB)
- Sandbox mode toggle
- PII redaction toggle
- Theme preference

## Testing

### Unit Tests
```bash
# Run all tests
pnpm test

# Watch mode
pnpm run test:watch

# Coverage report
pnpm run test:coverage
```

### End-to-End Tests
```bash
# Open Cypress test runner
pnpm run e2e

# Run headless
pnpm run e2e:run
```

## Performance Optimization

- ✅ **Code Splitting**: Automatic route-based splitting with Next.js
- ✅ **Image Optimization**: next/image component
- ✅ **Bundle Analysis**: Use `@next/bundle-analyzer` to profile
- ✅ **Memoization**: React.memo on expensive components
- ✅ **Virtual Scrolling**: For large data tables
- ✅ **Lazy Loading**: Chart components load on demand

## Accessibility

- ✅ WCAG 2.1 Level AA compliance
- ✅ Semantic HTML and ARIA labels
- ✅ Keyboard navigation (Tab, Enter, Escape)
- ✅ Screen reader support with skip links
- ✅ Color contrast ratios ≥4.5:1
- ✅ Focus visible indicators
- ✅ Form field labels and error messages

Run accessibility audit:
```bash
# Using axe DevTools browser extension
# Or automated in tests with jest-axe
```

## Security & Privacy

- 🔒 **No Token Persistence**: Auth tokens are not stored in localStorage (use secure HttpOnly cookies)
- 🔒 **CSP Headers**: Content Security Policy configured
- 🔒 **HTTPS**: All production traffic should use HTTPS
- 🔒 **PII Redaction**: Option to redact sensitive data in previews
- 🔒 **Sandbox Mode**: Demo mode with read-only badge

## Deployment

### Vercel (Recommended)
```bash
# Push to GitHub, connect to Vercel
# Automatic deployments on push
# Environment variables in Vercel dashboard
```

### Docker
```bash
# Build image
docker build -t dataanalyst-frontend .

# Run container
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=https://api.example.com/api \
  dataanalyst-frontend
```

### Manual (Node.js)
```bash
# Build
pnpm run build

# Start production server
pnpm run start

# Port 3000 (configurable with PORT env var)
```

## File Upload

### Supported Formats
- CSV (with auto-detection of headers, delimiters)
- JSON (flat objects, arrays)
- Parquet (via arrow-js)
- Excel files (XLSX, XLS)

### Client-Side Features
- Drag & drop support
- File size validation (100MB max)
- Format validation
- Progress indicator
- Real-time preview (first 1000 rows)
- Column type hints (date, number, text)

### Large Files
For files > 50MB, consider:
- Chunked upload on backend
- Streaming parser (rows processed incrementally)
- Progress callback tracking
- Timeout configuration (default 30s)

## Troubleshooting

### Backend Connection Failed
- Check mock backend is running: `http://localhost:3001/api/health`
- Verify `NEXT_PUBLIC_API_URL` environment variable
- Check CORS configuration on backend
- Look for network errors in browser console

### File Upload Errors
- Ensure file is under 100MB
- Verify CSV is UTF-8 encoded
- Check for special characters in column names
- Review PapaParse console warnings

### WebSocket Disconnections
- Backend issue: verify `/socket.io` endpoint
- Network issue: check firewall rules
- Browser compatibility: ensure WebSocket support
- Fallback to polling if WebSocket unavailable

### Memory Issues on Large Datasets
- Use pagination for data previews
- Implement virtual scrolling for tables
- Process file in chunks on backend
- Consider streaming responses

## Project Structure Conventions

- **components/**: Reusable UI components (organize by feature)
- **app/**: Next.js pages and layouts (app router)
- **lib/**: Utilities, types, API clients, stores
- **hooks/**: Custom React hooks
- **__tests__/**: Jest unit tests
- **e2e/**: Cypress integration tests
- **public/**: Static assets

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Follow component structure conventions
3. Add unit tests for new components
4. Add E2E tests for user workflows
5. Run linter: `pnpm lint`
6. Format code: `pnpm prettier --write .`
7. Submit PR with description

## License

MIT License - See LICENSE.md for details

## Support

- 📖 **Documentation**: See `API_CONTRACT.md` and `ARCHITECTURE.md`
- 🐛 **Bug Reports**: Create GitHub issue with reproduction steps
- 💬 **Discussions**: Use GitHub Discussions for questions
- 📧 **Email**: support@dataanalyst.ai

## Roadmap

- [ ] Multi-step workflows (schedule runs)
- [ ] Real-time collaboration (multiple users editing)
- [ ] Advanced filtering and search
- [ ] Export to multiple formats (PDF, Excel, Parquet)
- [ ] Custom cleaning step templates
- [ ] Performance profiling and optimization
- [ ] GraphQL API option
- [ ] Mobile app (React Native)

## Acknowledgments

- Built with [Next.js](https://nextjs.org/)
- Components from [shadcn/ui](https://ui.shadcn.com/)
- Charts with [Recharts](https://recharts.org/)
- State management with [Zustand](https://github.com/pmndrs/zustand)
- Real-time with [Socket.IO](https://socket.io/)

---

**Status**: Production Ready ✅

Latest build: 2024-01-20  
Version: 1.0.0
