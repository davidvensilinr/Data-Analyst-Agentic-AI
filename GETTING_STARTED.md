# Getting Started with Autonomous Data Analyst

This guide walks you through setting up and running the Autonomous Data Analyst application.

## Quick Start (Development Mode)

### Prerequisites
- Node.js 18+ or higher
- npm, yarn, or pnpm

### 1. Installation

```bash
# Install dependencies
pnpm install
# or
npm install
```

### 2. Environment Setup

```bash
# Copy the example environment file
cp .env.example .env.local
```

The default configuration uses:
- `NEXT_PUBLIC_API_URL=http://localhost:3001/api` (mock backend)
- `NEXT_PUBLIC_MOCK_MODE=true` (simulates API responses)

### 3. Run Development Server

```bash
# Run Next.js frontend only
pnpm dev

# Open http://localhost:3000 in your browser
```

### 4. (Optional) Run with Mock Backend

The mock backend server simulates API responses for development and testing:

```bash
# Terminal 1: Start frontend
pnpm dev

# Terminal 2: Start mock backend
pnpm mock-backend

# Or run both simultaneously
pnpm dev:full
```

The mock backend runs on `http://localhost:3001` and provides realistic data and simulations.

## Features Overview

### 1. Project Management
- **Create Projects**: Organize your datasets by project
- **Navigate Projects**: Select and manage multiple projects simultaneously
- **Project Dashboard**: View all datasets in a project

### 2. Data Upload & Profiling
- **Upload Files**: CSV, Excel (.xlsx), and other formats
- **Automatic Profiling**: Get instant insights into your data:
  - Data types and distributions
  - Missing value analysis
  - Quality metrics (completeness, uniqueness, consistency)
  - Risk identification and recommendations
  - Correlation matrices for numeric data

### 3. Data Cleaning
- **Smart Cleaning Plans**: AI-generated cleaning suggestions
- **Multiple Operations**: Normalization, imputation, deduplication, outlier detection, type conversion, and more
- **Before/After Comparison**: See exactly what changes will be made
- **Audit Logging**: Complete history of all cleaning operations

### 4. Intelligent Querying
- **Natural Language Questions**: Ask questions about your data in plain English
- **Automated Analysis**: Watch the AI agent work step-by-step
- **Multi-Step Execution**: 
  - Data querying and aggregation
  - Analysis and insights generation
  - Visualization creation
  - Recommendation generation
- **Trace Visualizer**: See exactly what tools were called and what they returned

### 5. Results & Visualizations
- **Interactive Charts**: Bar charts, line charts, scatter plots, and more
- **Data Tables**: Sortable, pageable table views
- **Confidence Scores**: Understand the reliability of results
- **Recommendations**: Actionable insights from your data analysis

## Usage Examples

### Example 1: Upload and Profile Data

1. Go to **Projects** → Select a project
2. Click **New Dataset**
3. Upload a CSV file (e.g., sales data, customer data)
4. Wait for automatic profiling
5. Review data quality metrics and risks
6. Click **Profile** to see detailed analysis

### Example 2: Clean Your Data

1. Go to **Projects** → **Datasets** → Select dataset
2. Click **Clean** (available on dataset card)
3. Review suggested cleaning steps
4. Adjust parameters if needed
5. Preview before/after samples
6. Apply changes to create a cleaned version

### Example 3: Query Your Data

1. Go to **Projects** → **Datasets** → Select dataset
2. Click **Query**
3. Ask a question:
   - "What are the top 10 products by revenue?"
   - "Show me sales trends by region over time"
   - "Which customers have the highest lifetime value?"
4. Watch the agent execute the analysis
5. Review results, charts, and recommendations

## Project Structure

```
autonomous-data-analyst/
├── app/                          # Next.js App Router
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Landing page
│   ├── projects/                # Project routes
│   │   ├── page.tsx            # Projects list
│   │   └── [id]/               # Individual project
│   │       ├── datasets/        # Dataset management
│   │       ├── upload/          # Upload page
│   │       └── settings/        # Project settings
│   └── api/                      # API routes (backend)
│
├── components/                   # React components
│   ├── ui/                      # shadcn/ui components
│   ├── profile/                 # Profiling components
│   ├── cleaning/                # Cleaning UI components
│   └── query/                   # Query UI components
│
├── lib/                         # Utilities and store
│   ├── api.ts                   # API client
│   ├── types.ts                 # TypeScript types
│   ├── store/                   # Zustand stores
│   │   ├── ui.store.ts
│   │   ├── dataset.store.ts
│   │   ├── cleaning.store.ts
│   │   └── query.store.ts
│   └── mock-data.ts             # Mock data for development
│
├── mock-backend/                # Backend server (optional)
│   └── server.js
│
├── public/                       # Static assets
├── styles/                       # Global styles
│
├── ARCHITECTURE.md              # Detailed architecture docs
├── GETTING_STARTED.md          # This file
└── README.md                    # Project overview
```

## Configuration

### API Configuration

Edit `.env.local` to change backend configuration:

```env
# Default (mock backend)
NEXT_PUBLIC_API_URL=http://localhost:3001/api

# Production
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api
```

### Mock Mode

The app includes mock mode for development. To use it:

```env
NEXT_PUBLIC_MOCK_MODE=true
```

When enabled, API calls return realistic simulated data without needing a real backend.

## Development Workflows

### Adding a New Feature

1. Define types in `lib/types.ts`
2. Add API methods in `lib/api.ts`
3. Add mock data in `lib/mock-data.ts`
4. Create components in `components/`
5. Create page in `app/`
6. Add store in `lib/store/` if needed

### Running Tests

```bash
# Run all tests
pnpm test

# Run tests in watch mode
pnpm test:watch

# Generate coverage report
pnpm test:coverage
```

### Running E2E Tests

```bash
# Open Cypress UI
pnpm e2e

# Run Cypress headless
pnpm e2e:run
```

## Troubleshooting

### "Cannot GET /" Error
- Make sure you're visiting `http://localhost:3000` (not port 3001)
- Check that the frontend is running with `pnpm dev`

### "Failed to connect to API" Error
- Verify the mock backend is running (if using it): `pnpm mock-backend`
- Check `NEXT_PUBLIC_API_URL` in `.env.local` matches your backend
- Ensure your backend is accessible on that URL

### Port Already in Use
- Frontend uses port 3000, backend uses port 3001
- If these ports are in use, you can:
  - Change `PORT` environment variable
  - Kill the process using the port
  - Use `lsof -i :3000` (Mac/Linux) to find the process

### Build Errors
- Clear `.next` folder: `rm -rf .next`
- Reinstall dependencies: `rm -rf node_modules && pnpm install`
- Check Node.js version: `node --version` (should be 18+)

## Next Steps

1. **Explore the UI**: Upload a test CSV file and try the different features
2. **Review Architecture**: Read `ARCHITECTURE.md` for detailed technical design
3. **Customize**: Modify colors, fonts, and layouts in `tailwind.config.ts`
4. **Integrate Backend**: Replace mock data with real API calls when backend is ready
5. **Deploy**: Use the deployment guide in `README.md`

## Support

For issues or questions:
1. Check this guide and `ARCHITECTURE.md`
2. Review the code comments and type definitions
3. Look at example usage in the demo pages
4. Check browser console for error messages

## Performance Tips

- Use mock mode for initial development
- Enable caching for repeated queries
- Optimize large file uploads with compression
- Monitor bundle size with `npm run build`

## Security Notes

- Never commit `.env.local` files with real credentials
- Always validate user input on the backend
- Use HTTPS in production
- Keep dependencies updated with `npm audit`

---

Happy analyzing! For detailed technical information, see `ARCHITECTURE.md`.
