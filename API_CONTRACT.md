# Autonomous Data Analyst - API Contract

This document defines the complete API contract between the frontend and backend. All endpoints are implemented with mock responses for development and testing.

## Base URL

- **Development (Mock)**: `http://localhost:3001/api`
- **Production**: `https://api.dataanalyst.example.com/api`

Environment variable: `NEXT_PUBLIC_API_URL`

## Authentication

All endpoints accept an optional `Authorization: Bearer <token>` header for authenticated requests.

```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Project Management

### POST /api/projects

Create a new project.

**Request**
```json
{
  "name": "Q4 Sales Analysis",
  "description": "Sales data for Q4 2024"
}
```

**Response** (201 Created)
```json
{
  "id": "proj-001",
  "name": "Q4 Sales Analysis",
  "description": "Sales data for Q4 2024",
  "createdAt": "2024-01-20T12:00:00Z",
  "updatedAt": "2024-01-20T12:00:00Z",
  "datasetCount": 0
}
```

### GET /api/projects

List all projects for the authenticated user.

**Response** (200 OK)
```json
[
  {
    "id": "proj-001",
    "name": "Q4 Sales Analysis",
    "description": "Sales data for Q4 2024",
    "createdAt": "2024-01-20T12:00:00Z",
    "updatedAt": "2024-01-20T12:00:00Z",
    "datasetCount": 3
  }
]
```

### GET /api/projects/:projectId

Get a specific project.

**Response** (200 OK)
```json
{
  "id": "proj-001",
  "name": "Q4 Sales Analysis",
  "description": "Sales data for Q4 2024",
  "createdAt": "2024-01-20T12:00:00Z",
  "updatedAt": "2024-01-20T12:00:00Z",
  "datasetCount": 3
}
```

---

## Dataset Management

### POST /api/upload

Upload and parse a dataset file.

**Request**
```
Content-Type: multipart/form-data

Form Data:
- file: File (CSV, JSON, or Parquet)
- datasetName: string (e.g., "Q4 Sales Data")
- projectId: string
- schemaHints?: Record<string, 'date' | 'number' | 'text' | 'boolean'>
```

**Response** (200 OK)
```json
{
  "datasetId": "ds-001",
  "dataset": {
    "id": "ds-001",
    "name": "Q4 Sales Data",
    "projectId": "proj-001",
    "fileName": "sales_q4.csv",
    "fileSize": 2458624,
    "rowsEstimated": 45230,
    "columnsCount": 12,
    "columns": ["order_id", "date", "customer_id", "product", "quantity", "price", "region", "status", "notes", "created_at", "updated_at", "deleted"],
    "uploadedAt": "2024-01-20T12:00:00Z",
    "updatedAt": "2024-01-20T12:00:00Z",
    "profiledAt": "2024-01-20T12:05:00Z"
  },
  "preview": [
    {
      "order_id": "ORD-000001",
      "date": "2024-01-01",
      "customer_id": "CUST-00001",
      "product": "Laptop",
      "quantity": 1,
      "price": 1299.99,
      "region": "North",
      "status": "completed",
      "notes": "High value",
      "created_at": "2024-01-01T08:30:00Z",
      "updated_at": "2024-01-01T08:45:00Z",
      "deleted": false
    }
  ],
  "metadata": {
    "fileName": "sales_q4.csv",
    "fileSize": 2458624,
    "rowsEstimated": 45230,
    "columnsCount": 12,
    "columns": ["order_id", "date", "customer_id", "product", "quantity", "price", "region", "status", "notes", "created_at", "updated_at", "deleted"],
    "mimeType": "text/csv"
  }
}
```

### GET /api/datasets

List datasets for a project.

**Query Parameters**
- `projectId`: string (required)
- `limit`: number (optional, default 50)
- `offset`: number (optional, default 0)

**Response** (200 OK)
```json
[
  {
    "id": "ds-001",
    "name": "Q4 Sales Data",
    "projectId": "proj-001",
    "fileName": "sales_q4.csv",
    "fileSize": 2458624,
    "rowsEstimated": 45230,
    "columnsCount": 12,
    "columns": [...],
    "uploadedAt": "2024-01-20T12:00:00Z",
    "updatedAt": "2024-01-20T12:00:00Z",
    "profiledAt": "2024-01-20T12:05:00Z"
  }
]
```

### GET /api/datasets/:datasetId

Get a specific dataset.

**Response** (200 OK)
```json
{
  "id": "ds-001",
  "name": "Q4 Sales Data",
  "projectId": "proj-001",
  "fileName": "sales_q4.csv",
  "fileSize": 2458624,
  "rowsEstimated": 45230,
  "columnsCount": 12,
  "columns": [...],
  "uploadedAt": "2024-01-20T12:00:00Z",
  "updatedAt": "2024-01-20T12:00:00Z",
  "profiledAt": "2024-01-20T12:05:00Z"
}
```

---

## Data Profiling

### GET /api/profile

Analyze dataset and return column statistics.

**Query Parameters**
- `datasetId`: string (required)

**Response** (200 OK)
```json
{
  "datasetId": "ds-001",
  "columnsCount": 12,
  "rowsCount": 45230,
  "columns": [
    {
      "name": "order_id",
      "type": "string",
      "nullPercent": 0,
      "uniqueCount": 45200,
      "uniquePercent": 99.93,
      "sampleValues": ["ORD-000001", "ORD-000002"],
      "histogram": {
        "bins": ["ORD-0-10k", "ORD-10k-20k", "ORD-20k-30k"],
        "counts": [9000, 9200, 9100]
      }
    },
    {
      "name": "price",
      "type": "number",
      "nullPercent": 0.5,
      "uniqueCount": 12000,
      "uniquePercent": 26.5,
      "sampleValues": [299.99, 1299.99, 79.99],
      "min": 50,
      "max": 5999.99,
      "mean": 1250.5,
      "median": 999.99,
      "stdDev": 1200.3,
      "histogram": {
        "bins": ["$0-1k", "$1k-2k", "$2k-3k"],
        "counts": [15000, 18000, 8000]
      }
    }
  ],
  "qualityScore": 82.5,
  "qualityMetrics": {
    "completeness": 99.2,
    "uniqueness": 89.3,
    "consistency": 92.1,
    "timeliness": 100
  },
  "missingHeatmap": {
    "rows": [0, 4523, 9046, 13569, 18092, 22615, 27138, 31661, 36184, 40707],
    "columns": ["date", "price", "notes", "status"],
    "matrix": [
      [0.5, 0.2, 1.2, 0.8],
      [0.3, 0.1, 0.9, 0.5]
    ]
  },
  "topRisks": [
    {
      "level": "high",
      "issue": "Missing values in price column",
      "column": "price",
      "affectedRows": 232,
      "recommendation": "Consider mean/median imputation or drop rows"
    }
  ]
}
```

---

## Data Cleaning

### POST /api/clean/plan

Generate a cleaning plan for a dataset.

**Request**
```json
{
  "datasetId": "ds-001",
  "requestedChanges": "Normalize dates and impute missing prices",
  "autoDetect": true
}
```

**Response** (200 OK)
```json
{
  "planId": "plan-1234567890",
  "datasetId": "ds-001",
  "steps": [
    {
      "stepId": "step-001",
      "type": "drop-duplicates",
      "description": "Remove duplicate order IDs",
      "parameters": {
        "subset": ["order_id"],
        "keep": "first"
      },
      "enabled": true,
      "estimatedRowImpact": 45,
      "rationale": "Found 45 exact duplicate rows based on order_id"
    },
    {
      "stepId": "step-002",
      "type": "impute-missing",
      "description": "Impute missing prices with median",
      "parameters": {
        "column": "price",
        "method": "median"
      },
      "enabled": true,
      "estimatedRowImpact": 232,
      "rationale": "Missing values in price column (0.5%) will be filled with median value $999.99"
    }
  ]
}
```

### POST /api/clean/execute

Execute cleaning steps and return results (streamed).

**Request**
```json
{
  "planId": "plan-1234567890",
  "apply": true
}
```

**Response** (200 OK - Streaming NDJSON)
```
{"stepId":"step-001","status":"success","beforeSample":[...],"afterSample":[...],"rowsAffected":45,"rationale":"Removed 45 duplicate rows","timestamp":"2024-01-20T12:05:00Z"}
{"stepId":"step-002","status":"success","beforeSample":[...],"afterSample":[...],"rowsAffected":232,"rationale":"Imputed 232 missing price values","timestamp":"2024-01-20T12:06:00Z"}
{"cleanedDatasetId":"ds-cleaned-001","auditLogId":"audit-001","completed":true}
```

---

## Query / Agent

### POST /api/ask

Submit a natural language question to the agent.

**Request**
```json
{
  "datasetId": "ds-001",
  "question": "What are our top selling products by region?",
  "mode": "auto",
  "userId": "user-123"
}
```

**Response** (200 OK)
```json
{
  "runId": "run-1234567890",
  "plan": [
    {
      "stepId": "plan-step-1",
      "type": "query",
      "description": "Parse question and identify analysis objectives"
    },
    {
      "stepId": "plan-step-2",
      "type": "analysis",
      "description": "Analyze sales trends across regions"
    },
    {
      "stepId": "plan-step-3",
      "type": "visualization",
      "description": "Generate trend chart and summary statistics"
    }
  ]
}
```

**WebSocket Events** (after POST response, connect to `/socket.io` with runId)

```json
{
  "type": "step_started",
  "runId": "run-1234567890",
  "stepId": "plan-step-2",
  "stepType": "analysis",
  "stepDescription": "Analyze sales trends across regions",
  "timestamp": "2024-01-20T12:06:00Z"
}
```

```json
{
  "type": "step_prompt",
  "runId": "run-1234567890",
  "stepId": "plan-step-2",
  "prompt": "Analyze the sales data for trends across regions...",
  "timestamp": "2024-01-20T12:06:01Z"
}
```

```json
{
  "type": "step_tool_call",
  "runId": "run-1234567890",
  "stepId": "plan-step-2",
  "toolName": "sql_query",
  "toolInput": {
    "query": "SELECT region, product, SUM(quantity * price) as revenue FROM sales GROUP BY region, product"
  },
  "timestamp": "2024-01-20T12:06:02Z"
}
```

```json
{
  "type": "step_tool_result",
  "runId": "run-1234567890",
  "stepId": "plan-step-2",
  "toolName": "sql_query",
  "result": {
    "rows": 20,
    "columns": 3,
    "data": [...]
  },
  "timestamp": "2024-01-20T12:06:03Z"
}
```

```json
{
  "type": "step_model_output",
  "runId": "run-1234567890",
  "stepId": "plan-step-2",
  "modelName": "gpt-4",
  "output": "The analysis shows strong regional variations in product preferences...",
  "timestamp": "2024-01-20T12:06:04Z"
}
```

```json
{
  "type": "execution_completed",
  "runId": "run-1234567890",
  "result": {
    "runId": "run-1234567890",
    "datasetId": "ds-001",
    "question": "What are our top selling products by region?",
    "charts": [
      {
        "id": "chart-1",
        "type": "bar",
        "title": "Sales by Product and Region",
        "data": [...]
      }
    ],
    "tables": [
      {
        "id": "table-1",
        "title": "Top Products by Revenue",
        "columns": [...],
        "rows": [...]
      }
    ],
    "summary": "Our analysis reveals...",
    "recommendations": ["Expand Monitor inventory in East region"],
    "confidenceScore": 0.94,
    "executionTimeMs": 2450
  },
  "timestamp": "2024-01-20T12:06:10Z"
}
```

---

## Audit & Activity

### GET /api/audit/:auditLogId

Retrieve full audit log for a query or cleaning run.

**Response** (200 OK)
```json
{
  "id": "audit-001",
  "runId": "run-1234567890",
  "timestamp": "2024-01-20T12:06:00Z",
  "type": "query",
  "datasetId": "ds-001",
  "userId": "user-123",
  "prompts": [
    {
      "stepId": "plan-step-2",
      "modelName": "gpt-4",
      "prompt": "Analyze the sales data for trends across regions...",
      "timestamp": "2024-01-20T12:06:01Z"
    }
  ],
  "toolCalls": [
    {
      "stepId": "plan-step-2",
      "toolName": "sql_query",
      "input": {
        "query": "SELECT region, SUM(quantity * price) as revenue FROM sales GROUP BY region"
      },
      "output": {
        "rows": 4,
        "columns": 2
      },
      "timestamp": "2024-01-20T12:06:02Z"
    }
  ],
  "modelOutputs": [
    {
      "stepId": "plan-step-2",
      "modelName": "gpt-4",
      "output": "The analysis shows strong regional variations...",
      "timestamp": "2024-01-20T12:06:04Z"
    }
  ],
  "steps": [],
  "hash": "sha256:abc123..."
}
```

### GET /api/history

Retrieve run history for a dataset.

**Query Parameters**
- `datasetId`: string (required)
- `limit`: number (optional, default 50)
- `offset`: number (optional, default 0)

**Response** (200 OK)
```json
[
  {
    "id": "run-1",
    "timestamp": "2024-01-20T12:00:00Z",
    "datasetId": "ds-001",
    "datasetName": "Q4 Sales Data",
    "question": "What are the top 5 products by revenue?",
    "confidenceScore": 0.95,
    "executionTimeMs": 1250,
    "status": "success"
  }
]
```

---

## Error Handling

All error responses follow this format:

```json
{
  "code": "INVALID_REQUEST",
  "message": "Dataset not found",
  "details": {
    "datasetId": "ds-invalid"
  },
  "timestamp": "2024-01-20T12:00:00Z"
}
```

**Common Error Codes**
- `INVALID_REQUEST` (400)
- `UNAUTHORIZED` (401)
- `NOT_FOUND` (404)
- `CONFLICT` (409)
- `INTERNAL_ERROR` (500)

---

## Health Check

### GET /api/health

Check backend service health.

**Response** (200 OK)
```json
{
  "status": "ok",
  "timestamp": "2024-01-20T12:00:00Z"
}
```

---

## Rate Limiting

All endpoints are rate-limited to:
- 100 requests per minute for authenticated users
- 10 requests per minute for unauthenticated requests

Response headers include:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1705760400
```
