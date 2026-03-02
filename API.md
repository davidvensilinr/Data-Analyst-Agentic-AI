# API Documentation

Complete API reference for Autonomous Data Analyst backend.

## Base URL

```
Development: http://localhost:3001/api
Production: https://api.yourdomain.com/api
```

## Authentication

All endpoints (except health check) require authentication via Bearer token:

```
Authorization: Bearer <token>
```

## Error Response Format

All errors follow this format:

```json
{
  "code": "ERROR_CODE",
  "message": "Human readable error message",
  "details": {
    "field": "additional context"
  },
  "timestamp": "2024-03-02T10:30:00Z"
}
```

## Project Endpoints

### Create Project
```
POST /projects
Content-Type: application/json

{
  "name": "Q1 Sales Analysis",
  "description": "Sales data for Q1 2024"
}

Response: 201
{
  "id": "proj_123abc",
  "name": "Q1 Sales Analysis",
  "description": "Sales data for Q1 2024",
  "createdAt": "2024-03-02T10:30:00Z",
  "updatedAt": "2024-03-02T10:30:00Z",
  "datasetCount": 0
}
```

### List Projects
```
GET /projects

Response: 200
[
  {
    "id": "proj_123abc",
    "name": "Q1 Sales Analysis",
    "description": "Sales data for Q1 2024",
    "createdAt": "2024-03-02T10:30:00Z",
    "updatedAt": "2024-03-02T10:30:00Z",
    "datasetCount": 5
  }
]
```

### Get Project
```
GET /projects/:projectId

Response: 200
{
  "id": "proj_123abc",
  "name": "Q1 Sales Analysis",
  "description": "Sales data for Q1 2024",
  "createdAt": "2024-03-02T10:30:00Z",
  "updatedAt": "2024-03-02T10:30:00Z",
  "datasetCount": 5
}
```

## Dataset Endpoints

### List Datasets
```
GET /datasets?projectId=proj_123abc

Response: 200
[
  {
    "id": "ds_456def",
    "name": "Sales Data",
    "projectId": "proj_123abc",
    "fileName": "sales.csv",
    "fileSize": 1048576,
    "rowsEstimated": 10000,
    "columnsCount": 12,
    "columns": ["id", "date", "product", "quantity", "price", ...],
    "uploadedAt": "2024-03-02T10:30:00Z",
    "updatedAt": "2024-03-02T10:30:00Z",
    "profiledAt": "2024-03-02T10:35:00Z"
  }
]
```

### Get Dataset
```
GET /datasets/:datasetId

Response: 200
{
  "id": "ds_456def",
  "name": "Sales Data",
  "projectId": "proj_123abc",
  "fileName": "sales.csv",
  "fileSize": 1048576,
  "rowsEstimated": 10000,
  "columnsCount": 12,
  "columns": ["id", "date", "product", "quantity", "price", ...],
  "uploadedAt": "2024-03-02T10:30:00Z",
  "updatedAt": "2024-03-02T10:30:00Z",
  "profiledAt": "2024-03-02T10:35:00Z"
}
```

## Upload Endpoint

### Upload File
```
POST /upload
Content-Type: multipart/form-data

Fields:
- file: File (required) - CSV, Excel, JSON, etc.
- datasetName: string (required) - Human readable name
- projectId: string (required) - Project ID
- schemaHints: JSON (optional) - {"columnName": "number"|"date"|"text"|"boolean"}

Response: 200
{
  "datasetId": "ds_456def",
  "dataset": {
    "id": "ds_456def",
    "name": "Sales Data",
    "projectId": "proj_123abc",
    "fileName": "sales.csv",
    "fileSize": 1048576,
    "rowsEstimated": 10000,
    "columnsCount": 12,
    "columns": ["id", "date", "product", "quantity", "price", ...],
    "uploadedAt": "2024-03-02T10:30:00Z",
    "updatedAt": "2024-03-02T10:30:00Z"
  },
  "preview": [
    {
      "id": "1",
      "date": "2024-01-01",
      "product": "Laptop",
      "quantity": 5,
      "price": 1200.00
    }
  ],
  "metadata": {
    "fileName": "sales.csv",
    "fileSize": 1048576,
    "rowsEstimated": 10000,
    "columnsCount": 12,
    "columns": ["id", "date", "product", "quantity", "price", ...],
    "mimeType": "text/csv"
  }
}
```

## Profiling Endpoints

### Get Profile
```
GET /profile?datasetId=ds_456def

Response: 200
{
  "datasetId": "ds_456def",
  "columnsCount": 12,
  "rowsCount": 10000,
  "columns": [
    {
      "name": "id",
      "type": "number",
      "nullPercent": 0,
      "uniqueCount": 10000,
      "uniquePercent": 100,
      "sampleValues": [1, 2, 3, 4, 5],
      "min": 1,
      "max": 10000,
      "mean": 5000.5,
      "median": 5000.5,
      "stdDev": 2886.75,
      "histogram": {
        "bins": [1, 1001, 2001, 3001, ...],
        "counts": [1000, 1000, 1000, 1000, ...]
      }
    },
    {
      "name": "date",
      "type": "date",
      "nullPercent": 0,
      "uniqueCount": 365,
      "uniquePercent": 3.65,
      "sampleValues": ["2024-01-01", "2024-01-02", ...]
    }
  ],
  "qualityScore": 0.92,
  "qualityMetrics": {
    "completeness": 0.98,
    "uniqueness": 0.89,
    "consistency": 0.95,
    "timeliness": 0.90
  },
  "missingHeatmap": {
    "rows": [0, 100, 200, 300],
    "columns": ["id", "date", "product"],
    "matrix": [[0, 0, 5], [0, 2, 8], [0, 0, 3], [0, 1, 4]]
  },
  "correlationMatrix": {
    "columns": ["quantity", "price", "revenue"],
    "matrix": [
      [1.0, 0.45, 0.89],
      [0.45, 1.0, 0.76],
      [0.89, 0.76, 1.0]
    ]
  },
  "topRisks": [
    {
      "level": "high",
      "issue": "Missing values in shipping_date",
      "column": "shipping_date",
      "affectedRows": 523,
      "recommendation": "Impute with median or investigate source"
    }
  ]
}
```

## Cleaning Endpoints

### Generate Cleaning Plan
```
POST /clean/plan
Content-Type: application/json

{
  "datasetId": "ds_456def",
  "requestedChanges": "Remove outliers and normalize dates",
  "autoDetect": true
}

Response: 200
{
  "planId": "plan_789ghi",
  "datasetId": "ds_456def",
  "steps": [
    {
      "stepId": "step_1",
      "type": "normalize-dates",
      "description": "Normalize date columns to YYYY-MM-DD format",
      "parameters": {
        "columns": ["date", "created_at"],
        "format": "YYYY-MM-DD",
        "timezone": "UTC"
      },
      "enabled": true,
      "estimatedRowImpact": 0,
      "rationale": "Standardize date formats across dataset"
    },
    {
      "stepId": "step_2",
      "type": "remove-outliers",
      "description": "Remove statistical outliers from numeric columns",
      "parameters": {
        "columns": ["price", "quantity"],
        "method": "iqr",
        "threshold": 1.5
      },
      "enabled": true,
      "estimatedRowImpact": 47,
      "rationale": "Remove anomalous values that don't represent normal business data"
    }
  ]
}
```

### Execute Cleaning
```
POST /clean/execute
Content-Type: application/json

{
  "planId": "plan_789ghi",
  "apply": true
}

Response: 200
{
  "cleanedDatasetId": "ds_456def_cleaned",
  "auditLogId": "audit_101jkl",
  "steps": [
    {
      "stepId": "step_1",
      "status": "success",
      "beforeSample": [
        {"date": "01-02-24", "created_at": "2024-01-02 10:30:00"}
      ],
      "afterSample": [
        {"date": "2024-01-02", "created_at": "2024-01-02T10:30:00Z"}
      ],
      "rowsAffected": 0,
      "rationale": "Normalized 9,847 date values",
      "timestamp": "2024-03-02T10:35:00Z"
    },
    {
      "stepId": "step_2",
      "status": "success",
      "beforeSample": [
        {"price": 15000.00, "quantity": 500}
      ],
      "afterSample": [],
      "rowsAffected": 47,
      "rationale": "Removed 47 outlier records",
      "timestamp": "2024-03-02T10:36:00Z"
    }
  ]
}
```

## Query Endpoints

### Submit Query
```
POST /ask
Content-Type: application/json

{
  "datasetId": "ds_456def",
  "question": "What are the top 10 products by revenue?",
  "mode": "auto"
}

Response: 200
{
  "runId": "run_202mnop",
  "plan": [
    {
      "stepId": "plan_step_1",
      "type": "query",
      "description": "Execute SQL query to analyze product revenue",
      "estimatedTime": 2000
    },
    {
      "stepId": "plan_step_2",
      "type": "visualization",
      "description": "Create bar chart visualization",
      "estimatedTime": 1000
    }
  ]
}
```

### WebSocket: Real-time Execution (Optional)

```javascript
// Connect to WebSocket for real-time updates
const socket = new WebSocket('ws://localhost:3001/ws');

socket.on('message', (event) => {
  const data = JSON.parse(event.data);
  
  // Possible event types:
  // - step_started
  // - step_prompt
  // - step_tool_call
  // - step_tool_result
  // - step_model_output
  // - step_completed
  // - execution_completed
});
```

## Audit Endpoints

### Get Audit Log
```
GET /audit/:auditLogId

Response: 200
{
  "id": "audit_101jkl",
  "runId": "run_202mnop",
  "timestamp": "2024-03-02T10:30:00Z",
  "type": "query",
  "datasetId": "ds_456def",
  "userId": "user_123",
  "prompts": [
    {
      "stepId": "plan_step_1",
      "modelName": "gpt-4",
      "prompt": "Given this dataset with columns..., answer: What are the top 10 products?",
      "timestamp": "2024-03-02T10:30:01Z"
    }
  ],
  "toolCalls": [
    {
      "stepId": "plan_step_1",
      "toolName": "sql_query",
      "input": {
        "query": "SELECT product, SUM(price*quantity) as revenue FROM sales GROUP BY product ORDER BY revenue DESC LIMIT 10"
      },
      "output": [
        {"product": "Laptop", "revenue": 48500},
        {"product": "Monitor", "revenue": 33200}
      ],
      "timestamp": "2024-03-02T10:30:02Z"
    }
  ],
  "modelOutputs": [
    {
      "stepId": "plan_step_1",
      "modelName": "gpt-4",
      "output": "Based on the data, Laptops are the top revenue generator with $48,500...",
      "metadata": {
        "tokens_used": 245,
        "finish_reason": "stop"
      },
      "timestamp": "2024-03-02T10:30:03Z"
    }
  ],
  "steps": [
    {
      "id": "entry_1",
      "timestamp": "2024-03-02T10:30:00Z",
      "type": "query",
      "dataset": {
        "id": "ds_456def",
        "name": "Sales Data"
      },
      "action": "Execute query",
      "userId": "user_123",
      "details": {
        "question": "What are the top 10 products?",
        "resultsCount": 10
      },
      "status": "success"
    }
  ],
  "hash": "sha256:abc123def456..."
}
```

### List Run History
```
GET /history?datasetId=ds_456def&limit=50&offset=0

Response: 200
[
  {
    "id": "run_202mnop",
    "timestamp": "2024-03-02T10:30:00Z",
    "datasetId": "ds_456def",
    "datasetName": "Sales Data",
    "question": "What are the top 10 products by revenue?",
    "confidenceScore": 0.92,
    "executionTimeMs": 3500,
    "status": "success",
    "result": {
      "runId": "run_202mnop",
      "datasetId": "ds_456def",
      "question": "What are the top 10 products by revenue?",
      "charts": [
        {
          "id": "chart_1",
          "type": "bar",
          "title": "Top 10 Products by Revenue",
          "data": [
            {"product": "Laptop", "revenue": 48500},
            {"product": "Monitor", "revenue": 33200}
          ]
        }
      ],
      "tables": [
        {
          "id": "table_1",
          "title": "Product Revenue Breakdown",
          "columns": [
            {"key": "rank", "label": "Rank", "type": "number"},
            {"key": "product", "label": "Product", "type": "string"},
            {"key": "revenue", "label": "Revenue", "type": "number"}
          ],
          "rows": [
            {"rank": 1, "product": "Laptop", "revenue": 48500}
          ]
        }
      ],
      "summary": "Laptops are the top revenue generator...",
      "recommendations": ["Increase inventory...", "Create bundles..."],
      "confidenceScore": 0.92,
      "executionTimeMs": 3500
    }
  }
]
```

## Health Check

### Health Status
```
GET /health

Response: 200
{
  "status": "ok",
  "timestamp": "2024-03-02T10:30:00Z",
  "version": "1.0.0"
}
```

## Rate Limiting

Rate limits apply to protect the backend:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1709385000
```

Default limits:
- 100 requests per minute per IP
- 1000 requests per hour per user

## Pagination

List endpoints support pagination:

```
GET /datasets?projectId=proj_123&limit=20&offset=0

Query Parameters:
- limit: number of items (default: 50, max: 100)
- offset: number of items to skip (default: 0)

Response includes:
- total: total number of items
- limit: items per page
- offset: items skipped
- items: array of results
```

## Webhooks (Optional)

Register webhooks for events:

```
POST /webhooks
Content-Type: application/json

{
  "url": "https://yourapp.com/webhook",
  "events": ["query.completed", "cleaning.completed", "error"]
}

Response: 201
{
  "id": "webhook_123",
  "url": "https://yourapp.com/webhook",
  "events": ["query.completed", "cleaning.completed", "error"],
  "secret": "whsk_...",
  "createdAt": "2024-03-02T10:30:00Z"
}
```

## SDKs

Official SDKs available:
- JavaScript: `npm install @ada/sdk`
- Python: `pip install ada-sdk`
- Go: `go get github.com/ada/sdk`

## Changelog

### v1.0.0 (2024-03-02)
- Initial release
- Project management
- Dataset upload and profiling
- Data cleaning
- AI-powered querying
- Audit logging

---

For integration examples, see `ARCHITECTURE.md`.
For client library usage, see `lib/api.ts`.
