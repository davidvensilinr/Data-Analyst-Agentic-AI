# Quick Start Guide

## 30-Second Setup

```bash
# Clone and install
git clone <repo>
cd autonomous-data-analyst-frontend
npm install

# Start everything
npm run dev:full

# Open http://localhost:3000 in your browser
```

Done! Frontend and mock backend are running.

---

## 3 Ways to Run

### 1️⃣ Docker (Recommended) - 1 Command

```bash
docker-compose up --build
```

Then visit: `http://localhost:3000`

### 2️⃣ Local with NPM - Frontend + Backend

```bash
npm install
npm run dev:full
```

Frontend: `http://localhost:3000`  
Backend: `http://localhost:3001`

### 3️⃣ Frontend Only + Real Backend

```bash
# Create .env.local
echo "NEXT_PUBLIC_API_URL=https://your-backend.com" > .env.local

npm install
npm run dev
```

Then visit: `http://localhost:3000`

---

## Common Commands

```bash
# Development
npm run dev              # Frontend only (port 3000)
npm run mock-backend     # Backend only (port 3001)
npm run dev:full         # Both together

# Testing
npm run test             # Run unit tests
npm run e2e              # Open Cypress (interactive)
npm run e2e:run          # Run tests headless

# Building
npm run build            # Production build
npm run start            # Run production build

# Code Quality
npm run lint             # Check for issues
npx prettier --write .   # Format code

# Docker
docker-compose up        # Start all services
docker-compose down      # Stop all services
```

---

## First Steps to Try

1. **Landing Page** → Visit `http://localhost:3000`
2. **Create Project** → Click "Get Started" button
3. **Upload Data** → Click "Upload Dataset"
4. **Choose File** → Sample dataset: `mock-backend/sample-datasets/sales_messy.csv`
5. **View Profile** → Click "View Profile" to see data analysis
6. **Ask Question** → Go to "Query" tab, ask "What is the average sales by region?"
7. **See Results** → Watch the agent trace and view results

---

## Understanding the Trace

When you submit a query, you'll see:

```
Step Trace
├── 📋 Plan Step 1: Parse question
├── 🔵 Analysis Step 2: Running analysis...
│   - Shows prompt being used
│   - Shows tool calls
│   - Shows model output
├── 🟢 Visualization Step 3: Complete
└── 📊 Results displayed with charts and tables
```

Click any step to expand and see details.

---

## Testing the API

### Using Postman

1. Open `postman-collection.json` in Postman
2. Choose an endpoint (e.g., "Upload Dataset")
3. Click "Send"
4. See response

OR use curl:

```bash
# Upload a file
curl -X POST http://localhost:3001/api/upload \
  -F "file=@mock-backend/sample-datasets/sales_messy.csv" \
  -F "dataset_name=Test Dataset"

# Get profile
curl http://localhost:3001/api/profile?dataset_id=demo-dataset-1
```

---

## File Locations

```
Frontend:     http://localhost:3000
Backend:      http://localhost:3001
Sample Data:  mock-backend/sample-datasets/
API Docs:     API_CONTRACT.md, API.md
Tests:        __tests__/, cypress/
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find and kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Then try again
npm run dev:full
```

### Dependencies Not Installing

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Docker Issues

```bash
# Clean rebuild
docker-compose down
docker-compose up --build

# Or manually
docker build -f Dockerfile -t frontend .
docker run -p 3000:3000 frontend
```

### WebSocket Connection Failed

This is expected if using mock backend. Check:
1. Backend is running on port 3001
2. Check browser console for errors
3. Ensure `NEXT_PUBLIC_WS_URL` is set correctly

---

## Environment Variables

Create `.env.local`:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXT_PUBLIC_WS_URL=ws://localhost:3001

# Feature Flags
NEXT_PUBLIC_SANDBOX_MODE=true
NEXT_PUBLIC_ENABLE_PII_REDACTION=true

# Upload Settings
NEXT_PUBLIC_MAX_UPLOAD_MB=100
NEXT_PUBLIC_ALLOWED_FILE_TYPES=csv,json,parquet
```

---

## Production Deployment

See `DEPLOYMENT.md` for full guide. Quick version:

```bash
# Build
npm run build

# Test build locally
npm run start

# Deploy to Vercel, AWS, or your hosting
# (Push code to GitHub, connect to hosting service)
```

---

## Next: Backend Integration

Once ready to use a real backend:

1. Read `INTEGRATION_GUIDE.md`
2. Update `NEXT_PUBLIC_API_URL` to your backend
3. Implement the 6 endpoints (see `API_CONTRACT.md`)
4. Test with Postman collection
5. Run E2E tests against real backend

---

## Documentation

| Quick Links | Purpose |
|------------|---------|
| `README.md` | Overview |
| `GETTING_STARTED.md` | Detailed setup (3 methods) |
| `API_CONTRACT.md` | API specifications |
| `INTEGRATION_GUIDE.md` | Backend integration |
| `FEATURES.md` | Complete feature list |
| `ARCHITECTURE.md` | System design |

---

## Key URLs When Running

```
Frontend:              http://localhost:3000
Mock Backend API:      http://localhost:3001
API Documentation:     API_CONTRACT.md (in repo)
Postman Collection:    postman-collection.json (in repo)
```

---

## Success Indicators

✅ You've succeeded when:
- Frontend loads at http://localhost:3000
- You can upload a CSV file
- Profile dashboard shows data statistics
- You can submit a query and see results
- Step trace shows agent execution

---

## Getting Help

1. Check `README.md` for overview
2. See `FILE_STRUCTURE.md` for project layout
3. Read relevant documentation
4. Check test files for examples (`cypress/e2e/`)
5. Review mock backend for API implementation (`mock-backend/server.js`)

---

## Time Estimates

- Getting started: **< 5 minutes** ⚡
- First data upload: **< 10 minutes** ⚡
- Understanding architecture: **30 minutes** 📚
- Backend integration: **2-3 days** 🔧
- Production deployment: **1 day** 🚀

---

**Ready? Let's go!** 🚀

```bash
npm install && npm run dev:full
```

Then visit: **http://localhost:3000**

---

*For detailed guides, see the documentation folder.*
