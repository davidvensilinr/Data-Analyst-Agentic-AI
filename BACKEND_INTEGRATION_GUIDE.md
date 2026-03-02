# Backend Integration Guide

This guide explains how to integrate the autonomous data analyst backend with the frontend and switch between mock and real backends.

## 🏗️ Architecture Overview

```
Frontend (Next.js) ←→ API Adapter ←→ Mock Backend / Real Backend
     ↓                    ↓                ↓
  React Components    Type-safe API    Express Server / FastAPI
  WebSocket Client    Interface         Python Backend
```

## 🔄 Backend Modes

### Mock Backend (Development)
- **Purpose**: Fast development without dependencies
- **Features**: Predefined responses, no external services
- **Usage**: Perfect for UI development, testing, demos
- **Port**: 3001
- **Command**: `npm run dev:mock`

### Real Backend (Production)
- **Purpose**: Full autonomous data analysis capabilities
- **Features**: LLM-powered planning, real ML models, audit logging
- **Usage**: Production, advanced analysis, real-time features
- **Port**: 8000
- **Command**: `npm run dev:real`

## 🚀 Quick Start

### Option 1: Mock Backend (Recommended for Development)

```bash
# Start frontend with mock backend
npm run dev:mock

# Access:
# Frontend: http://localhost:3000
# Mock API: http://localhost:3001/api
```

### Option 2: Real Backend (Full Features)

```bash
# Start Python backend first
cd autonomous_data_analyst
python main.py

# In another terminal, start frontend
cd ..
npm run dev:real

# Access:
# Frontend: http://localhost:3000
# Real API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 3: Docker (Recommended for Production)

```bash
# Start everything with Docker
npm run full:docker

# Access:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Grafana: http://localhost:3001 (if monitoring enabled)
```

## 🔧 Configuration

### Environment Variables

Create `.env.local` in the frontend root:

```env
# Backend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Backend Mode (true = real, false = mock)
NEXT_PUBLIC_USE_REAL_BACKEND=false

# Feature Flags
NEXT_PUBLIC_ENABLE_WEBSOCKET=true
NEXT_PUBLIC_ENABLE_AUDIT_LOGS=true
NEXT_PUBLIC_ENABLE_REAL_TIME_UPDATES=true
```

### Backend Configuration

Create `.env` in the `autonomous_data_analyst` directory:

```env
# Database
DATABASE_URL=sqlite:///./data/analyst.db

# LLM (optional, defaults to mock)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Settings
MOCK_LLM_MODE=true
REQUIRE_HUMAN_APPROVAL=false
MAX_FILE_SIZE=104857600
```

## 📱 Frontend Integration

### Using the API Adapter

```typescript
import { useApiClient } from '@/hooks/useBackendSwitch';

function MyComponent() {
  const apiClient = useApiClient();

  const uploadDataset = async (file: File) => {
    try {
      const result = await apiClient.uploadDataset(file, 'My Dataset');
      console.log('Dataset uploaded:', result.dataset_id);
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  return <button onClick={() => uploadDataset(file)}>Upload</button>;
}
```

### Real-time Updates

```typescript
import { useApiClient } from '@/hooks/useBackendSwitch';

function AnalysisComponent() {
  const apiClient = useApiClient();

  const runAnalysis = async (question: string, datasetId: string) => {
    // Execute with real-time updates
    const { run, events } = await apiClient.executeAnalysis(
      question,
      datasetId,
      (event) => {
        console.log('Progress:', event.event_type, event.data);
      }
    );

    console.log('Analysis completed:', run.result);
  };

  return <button onClick={runAnalysis}>Analyze</button>;
}
```

### Backend Switcher Component

```typescript
import { BackendSwitcher } from '@/components/BackendSwitcher';

function SettingsPage() {
  return (
    <div>
      <h1>Settings</h1>
      <BackendSwitcher />
    </div>
  );
}
```

## 🔌 API Compatibility

### Mock vs Real API Mapping

| Feature | Mock Backend | Real Backend |
|---------|--------------|--------------|
| Dataset Upload | ✅ Predefined response | ✅ Actual file processing |
| Data Profiling | ✅ Mock statistics | ✅ Real statistical analysis |
| Data Cleaning | ✅ Mock cleaning steps | ✅ ML-based cleaning |
| Analysis | ✅ Mock insights | ✅ LLM-powered analysis |
| WebSocket | ❌ Not supported | ✅ Real-time streaming |
| Audit Logs | ❌ Not implemented | ✅ Immutable logging |
| ML Models | ❌ Not available | ✅ Real ML execution |

### Response Format Differences

The API Adapter automatically converts between formats:

```typescript
// Mock API Response
{
  datasetId: "123",
  dataset: { name: "Test", ... },
  metadata: { mimeType: "text/csv", ... }
}

// Automatically converted to Real API Format
{
  dataset_id: "123",
  name: "Test",
  file_type: "csv",
  file_size: 1024,
  ...
}
```

## 🧪 Testing

### Unit Tests

```typescript
import { getApiAdapter } from '@/lib/api.adapter';

// Test with mock backend
const mockAdapter = getApiAdapter();
mockAdapter.setBackendMode(false);

// Test with real backend
const realAdapter = getApiAdapter();
realAdapter.setBackendMode(true);
```

### Integration Tests

```bash
# Test with mock backend
npm run test

# Test with real backend (requires backend running)
NEXT_PUBLIC_USE_REAL_BACKEND=true npm run test
```

## 🐛 Troubleshooting

### Common Issues

1. **Real backend not available**
   ```bash
   # Check if backend is running
   curl http://localhost:8000/health
   
   # Start backend
   cd autonomous_data_analyst && python main.py
   ```

2. **WebSocket connection failed**
   ```bash
   # Check WebSocket URL
   echo $NEXT_PUBLIC_WS_URL
   
   # Ensure real backend is running
   ```

3. **API endpoint not found**
   ```bash
   # Check API URL
   echo $NEXT_PUBLIC_API_URL
   
   # Verify backend mode
   # Mock: http://localhost:3001/api
   # Real: http://localhost:8000/api
   ```

4. **File upload failed**
   ```bash
   # Check file size limit
   grep MAX_FILE_SIZE autonomous_data_analyst/.env
   
   # Check upload directory permissions
   ls -la autonomous_data_analyst/data/uploads
   ```

### Debug Mode

Enable debug logging:

```typescript
// In development
if (process.env.NODE_ENV === 'development') {
  console.log('Backend mode:', apiAdapter.getBackendMode());
  console.log('API URL:', process.env.NEXT_PUBLIC_API_URL);
}
```

## 📊 Performance

### Mock Backend
- **Response Time**: < 50ms
- **Memory Usage**: Minimal
- **Dependencies**: None

### Real Backend
- **Response Time**: 1-10s (depends on analysis complexity)
- **Memory Usage**: Higher (ML models, data processing)
- **Dependencies**: Python, ML libraries

### Optimization Tips

1. **Use mock backend for UI development**
2. **Switch to real backend for integration testing**
3. **Enable caching for repeated analyses**
4. **Use WebSocket for long-running analyses**

## 🔒 Security

### Authentication

```typescript
// Set API key for real backend
apiClient.setToken('your-api-key');

// Mock backend ignores authentication
```

### Data Privacy

- **Mock Backend**: No data persistence
- **Real Backend**: Immutable audit logs, configurable retention

### Rate Limiting

```typescript
// Real backend has built-in rate limiting
// Mock backend has no limits
```

## 🚀 Production Deployment

### Docker Deployment

```bash
# Build and deploy everything
docker-compose -f docker-compose.full.yml up -d

# With monitoring
docker-compose -f docker-compose.full.yml --profile monitoring up -d
```

### Environment Configuration

```env
# Production
NODE_ENV=production
NEXT_PUBLIC_USE_REAL_BACKEND=true
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com
```

### Monitoring

- **Health Checks**: `/health` endpoint
- **Metrics**: `/api/metrics` (Prometheus)
- **Logs**: Structured logging with audit trails

## 📚 Advanced Usage

### Custom API Methods

```typescript
// Extend the API adapter for custom endpoints
class ExtendedApiClient extends ApiAdapter {
  async customMethod(params: any) {
    // Custom implementation
  }
}
```

### WebSocket Events

```typescript
// Subscribe to specific events
socket.on('step_completed', (event) => {
  if (event.step_id === 'analysis') {
    // Handle analysis completion
  }
});
```

### Error Handling

```typescript
try {
  const result = await apiClient.askQuestion('What are the trends?', datasetId);
} catch (error) {
  if (error.message.includes('backend not available')) {
    // Fallback to mock backend
    apiAdapter.setBackendMode(false);
    // Retry with mock
  }
}
```

## 🔄 Migration Guide

### From Mock to Real

1. **Start real backend**
2. **Update environment variables**
3. **Test API compatibility**
4. **Enable WebSocket features**
5. **Configure authentication**

### From Real to Mock

1. **Stop real backend**
2. **Update environment variables**
3. **Test with mock responses**
4. **Disable real-time features**

## 📞 Support

- **Documentation**: See `/docs` folder
- **API Reference**: http://localhost:8000/docs (real backend)
- **Issues**: Create GitHub issue
- **Discussions**: Use GitHub Discussions

---

*This guide covers the integration between the frontend and autonomous data analyst backend. For more detailed information, see the individual component documentation.*
