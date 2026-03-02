# Backend Integration Guide

This document describes how to integrate the Autonomous Data Analyst frontend with a real backend service.

## Architecture Overview

The frontend is designed with a clean separation between API calls and business logic:

- **API Client** (`lib/api.ts`): All HTTP requests are abstracted here
- **Type Definitions** (`lib/types.ts`): Shared TypeScript interfaces for request/response contracts
- **Mock Backend** (`mock-backend/server.js`): Reference implementation for all endpoints
- **Stores** (`lib/store/*.ts`): Zustand stores for state management

## Step 1: Update API Base URL

In `.env.local`, set your backend URL:

```env
NEXT_PUBLIC_API_URL=https://your-backend-api.com
NEXT_PUBLIC_WS_URL=wss://your-backend-api.com
```

## Step 2: Update API Client Methods

Edit `lib/api.ts` to point to your actual endpoints:

```typescript
export const api = {
  async uploadDataset(file: File, datasetName: string, schemaHints?: any) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('dataset_name', datasetName);
    if (schemaHints) formData.append('schema_hints', JSON.stringify(schemaHints));

    const response = await axios.post(
      `${config.apiUrl}/upload`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
    return response.data;
  },
  // ... other methods
};
```

## Step 3: Implement Authentication

If your backend requires authentication:

```typescript
// lib/api.ts
const setupInterceptors = () => {
  axios.interceptors.request.use((config) => {
    const token = getAuthToken(); // Get from your auth system
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });
};

setupInterceptors();
```

## Step 4: Handle WebSocket Events

The frontend expects real-time step execution updates via WebSocket/SSE. Update `lib/hooks/useWebSocket.ts`:

```typescript
export const useWebSocket = (runId: string) => {
  useEffect(() => {
    const ws = new WebSocket(`${config.wsUrl}?run_id=${runId}`);
    
    ws.onmessage = (event) => {
      const step = JSON.parse(event.data);
      // Update store with step execution
      useQueryStore.setState((state) => ({
        steps: [...state.steps, step],
      }));
    };
  }, [runId]);
};
```

## Step 5: Error Handling

Your backend should return standard error responses. The frontend handles them in `lib/api.ts`:

```typescript
if (response.status >= 400) {
  throw new Error(response.data.message || 'API Error');
}
```

## Step 6: Data Type Mapping

Ensure your backend returns data matching the types in `lib/types.ts`. Example:

```typescript
// Your backend should return:
{
  dataset_id: "ds-123",
  rows_est: 45230,
  cols: 8,
  preview: [
    { order_id: "ORD-001", date: "2024-01-01", ... },
    // ...
  ]
}

// Maps to TypeScript type:
interface UploadResponse {
  dataset_id: string;
  rows_est: number;
  cols: number;
  preview: Record<string, any>[];
}
```

## Step 7: Testing Integration

1. Update `.env.local` with your backend URL
2. Run `npm run dev` to start the frontend
3. Use the Postman collection to test individual endpoints
4. Run E2E tests: `npm run e2e:run`

## Common Integration Patterns

### File Upload with Progress

```typescript
const handleUpload = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('dataset_name', fileName);

  try {
    const response = await axios.post('/api/upload', formData, {
      onUploadProgress: (progressEvent) => {
        const progress = (progressEvent.loaded / progressEvent.total) * 100;
        setUploadProgress(progress);
      },
    });
    return response.data;
  } catch (error) {
    handleError(error);
  }
};
```

### Streaming Responses

For long-running operations, use streaming:

```typescript
async function* streamQuery(question: string) {
  const response = await fetch('/api/ask', {
    method: 'POST',
    body: JSON.stringify({ question }),
  });

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { value, done } = await reader!.read();
    if (done) break;
    
    const text = decoder.decode(value);
    yield JSON.parse(text);
  }
}
```

### Error Recovery

```typescript
const apiCall = async (fn: () => Promise<any>, maxRetries = 3) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(r => setTimeout(r, 1000 * Math.pow(2, i)));
    }
  }
};
```

## Deployment Checklist

- [ ] Update API endpoints in `.env.production`
- [ ] Configure CORS on your backend for the frontend domain
- [ ] Set up SSL/TLS for production (HTTPS/WSS)
- [ ] Implement rate limiting on your API
- [ ] Set up logging and monitoring
- [ ] Test full workflows with real data
- [ ] Configure authentication tokens
- [ ] Set up data backup/recovery procedures

## Troubleshooting

### CORS Errors

Add your frontend domain to your backend's CORS whitelist:

```javascript
// Example: Node.js/Express
app.use(cors({
  origin: 'https://your-frontend-domain.com',
  credentials: true,
}));
```

### WebSocket Connection Failures

Ensure your backend supports WebSocket connections and the URL is correct:

```typescript
// lib/config.ts
export const config = {
  wsUrl: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:3001',
};
```

### Type Mismatches

Keep `lib/types.ts` synchronized with your backend's API schema. Use tools like:
- OpenAPI Generator
- ts-json-schema-generator
- Manual validation with runtime type checking

## Support

For questions about integration:
1. Check the API_CONTRACT.md for detailed endpoint specifications
2. Review mock-backend/server.js for reference implementation
3. Check the Postman collection for example requests
4. Review ARCHITECTURE.md for system design details
