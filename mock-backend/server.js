/**
 * Mock Backend Server for Autonomous Data Analyst
 * Implements all API endpoints with simulated responses
 * Runs on port 3001 by default
 */

const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ limit: '50mb', extended: true }));

// Configure multer for file uploads
const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 100 * 1024 * 1024 }, // 100MB
});

// ============================================================================
// Mock Data Generators
// ============================================================================

function generateMockPreview(rows = 10) {
  const products = ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones'];
  const regions = ['North', 'South', 'East', 'West'];
  const statuses = ['completed', 'pending', 'failed', 'processing'];

  return Array.from({ length: rows }).map((_, i) => ({
    order_id: `ORD-${String(i + 1).padStart(6, '0')}`,
    date: new Date(2024, Math.floor(Math.random() * 11), Math.floor(Math.random() * 28) + 1)
      .toISOString()
      .split('T')[0],
    customer_id: `CUST-${String(Math.floor(Math.random() * 10000)).padStart(5, '0')}`,
    product: products[Math.floor(Math.random() * products.length)],
    quantity: Math.floor(Math.random() * 10) + 1,
    price: (Math.random() * 5000 + 100).toFixed(2),
    region: regions[Math.floor(Math.random() * regions.length)],
    status: statuses[Math.floor(Math.random() * statuses.length)],
    notes: ['High value', 'Rush order', 'VIP', 'Standard', ''][Math.floor(Math.random() * 5)],
    created_at: new Date(Date.now() - Math.random() * 7776000000).toISOString(),
    updated_at: new Date(Date.now() - Math.random() * 3888000000).toISOString(),
    deleted: Math.random() > 0.95 ? 'true' : 'false',
  }));
}

function generateMockColumnProfile(name, type) {
  const profiles = {
    order_id: {
      name: 'order_id',
      type: 'string',
      nullPercent: 0,
      uniqueCount: 45200,
      uniquePercent: 99.93,
      sampleValues: ['ORD-000001', 'ORD-000002', 'ORD-000003'],
      histogram: {
        bins: ['ORD-0-10k', 'ORD-10k-20k', 'ORD-20k-30k', 'ORD-30k-40k', 'ORD-40k+'],
        counts: [9000, 9200, 9100, 8900, 9030],
      },
    },
    quantity: {
      name: 'quantity',
      type: 'number',
      nullPercent: 0.1,
      uniqueCount: 15,
      uniquePercent: 0.03,
      sampleValues: [1, 5, 3, 7, 2],
      min: 1,
      max: 15,
      mean: 5.2,
      median: 5,
      stdDev: 3.1,
      histogram: {
        bins: ['1-3', '4-6', '7-9', '10-12', '13-15'],
        counts: [8954, 12123, 15023, 6213, 2917],
      },
    },
    price: {
      name: 'price',
      type: 'number',
      nullPercent: 0.5,
      uniqueCount: 12000,
      uniquePercent: 26.5,
      sampleValues: [299.99, 1299.99, 79.99, 199.99, 89.99],
      min: 50,
      max: 5999.99,
      mean: 1250.5,
      median: 999.99,
      stdDev: 1200.3,
      histogram: {
        bins: ['$0-1k', '$1k-2k', '$2k-3k', '$3k-4k', '$4k+'],
        counts: [15000, 18000, 8000, 3000, 1230],
      },
    },
    region: {
      name: 'region',
      type: 'string',
      nullPercent: 0,
      uniqueCount: 4,
      uniquePercent: 0.01,
      sampleValues: ['North', 'South', 'East', 'West'],
      histogram: {
        bins: ['North', 'South', 'East', 'West'],
        counts: [11230, 11500, 11200, 11300],
      },
    },
  };

  return (
    profiles[name] || {
      name,
      type: type || 'string',
      nullPercent: Math.random() * 10,
      uniqueCount: Math.floor(Math.random() * 1000),
      uniquePercent: Math.random() * 100,
      sampleValues: [],
      histogram: { bins: [], counts: [] },
    }
  );
}

// ============================================================================
// API Routes
// ============================================================================

/**
 * Health Check
 */
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

/**
 * Projects
 */
app.post('/api/projects', (req, res) => {
  const { name, description } = req.body;
  res.json({
    id: `proj-${uuidv4()}`,
    name,
    description,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    datasetCount: 0,
  });
});

app.get('/api/projects', (req, res) => {
  res.json([
    {
      id: 'proj-001',
      name: 'Sales Analytics',
      description: 'Q4 2024 sales data analysis',
      createdAt: '2024-01-15T10:00:00Z',
      updatedAt: '2024-01-20T15:30:00Z',
      datasetCount: 3,
    },
    {
      id: 'proj-002',
      name: 'Customer Analytics',
      description: 'Customer behavior and segmentation',
      createdAt: '2024-01-10T09:00:00Z',
      updatedAt: '2024-01-18T14:20:00Z',
      datasetCount: 2,
    },
  ]);
});

app.get('/api/projects/:projectId', (req, res) => {
  res.json({
    id: req.params.projectId,
    name: 'Sample Project',
    description: 'A sample project',
    createdAt: new Date(Date.now() - 86400000).toISOString(),
    updatedAt: new Date().toISOString(),
    datasetCount: 1,
  });
});

/**
 * Datasets
 */
app.get('/api/datasets', (req, res) => {
  const { projectId } = req.query;
  res.json([
    {
      id: 'ds-001',
      name: 'Sales Transactions Q4',
      projectId: projectId || 'proj-001',
      fileName: 'sales_q4_2024.csv',
      fileSize: 2458624,
      rowsEstimated: 45230,
      columnsCount: 12,
      columns: ['order_id', 'date', 'customer_id', 'product', 'quantity', 'price', 'region', 'status', 'notes', 'created_at', 'updated_at', 'deleted'],
      uploadedAt: '2024-01-20T12:00:00Z',
      updatedAt: '2024-01-20T15:30:00Z',
      profiledAt: '2024-01-20T12:05:00Z',
    },
  ]);
});

app.get('/api/datasets/:datasetId', (req, res) => {
  res.json({
    id: req.params.datasetId,
    name: 'Sample Dataset',
    projectId: 'proj-001',
    fileName: 'sample.csv',
    fileSize: 1024000,
    rowsEstimated: 10000,
    columnsCount: 8,
    columns: ['id', 'name', 'value', 'date', 'category', 'region', 'status', 'notes'],
    uploadedAt: new Date(Date.now() - 86400000).toISOString(),
    updatedAt: new Date().toISOString(),
  });
});

/**
 * File Upload
 */
app.post('/api/upload', upload.single('file'), (req, res) => {
  const { datasetName, projectId, schemaHints } = req.body;
  const file = req.file;

  if (!file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }

  // Simulate file parsing
  const datasetId = `ds-${Date.now()}`;
  const rowsEstimated = Math.floor(Math.random() * 50000) + 1000;
  const columns = ['order_id', 'date', 'customer_id', 'product', 'quantity', 'price', 'region', 'status', 'notes', 'created_at', 'updated_at', 'deleted'];

  // Simulate processing delay
  setTimeout(() => {
    res.json({
      datasetId,
      dataset: {
        id: datasetId,
        name: datasetName,
        projectId,
        fileName: file.originalname,
        fileSize: file.size,
        rowsEstimated,
        columnsCount: columns.length,
        columns,
        uploadedAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
      preview: generateMockPreview(20),
      metadata: {
        fileName: file.originalname,
        fileSize: file.size,
        rowsEstimated,
        columnsCount: columns.length,
        columns,
        mimeType: file.mimetype,
      },
    });
  }, 1000);
});

/**
 * Data Profiling
 */
app.get('/api/profile', (req, res) => {
  const { datasetId } = req.query;

  // Simulate processing delay
  setTimeout(() => {
    res.json({
      datasetId,
      columnsCount: 12,
      rowsCount: 45230,
      columns: [
        generateMockColumnProfile('order_id', 'string'),
        generateMockColumnProfile('date', 'date'),
        { name: 'customer_id', type: 'string', nullPercent: 0.1, uniqueCount: 8234, uniquePercent: 18.2, sampleValues: ['CUST-00001', 'CUST-00002'], histogram: { bins: ['Low', 'Medium', 'High'], counts: [15000, 20000, 10230] } },
        { name: 'product', type: 'string', nullPercent: 0, uniqueCount: 5, uniquePercent: 0.01, sampleValues: ['Laptop', 'Mouse'], histogram: { bins: ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones'], counts: [9230, 8500, 9100, 10000, 8400] } },
        generateMockColumnProfile('quantity', 'number'),
        generateMockColumnProfile('price', 'number'),
        generateMockColumnProfile('region', 'string'),
        { name: 'status', type: 'string', nullPercent: 0.3, uniqueCount: 4, uniquePercent: 0.01, sampleValues: ['completed', 'pending'], histogram: { bins: ['completed', 'pending', 'failed', 'processing'], counts: [38000, 5000, 1500, 730] } },
        { name: 'notes', type: 'string', nullPercent: 15.2, uniqueCount: 12000, uniquePercent: 26.5, sampleValues: [], histogram: { bins: ['Present', 'Missing'], counts: [38300, 6930] } },
        { name: 'created_at', type: 'date', nullPercent: 0, uniqueCount: 45230, uniquePercent: 100, sampleValues: [], histogram: { bins: ['Week 1', 'Week 2', 'Week 3', 'Week 4'], counts: [11230, 11200, 11500, 11300] } },
        { name: 'updated_at', type: 'date', nullPercent: 0.2, uniqueCount: 44800, uniquePercent: 99.05, sampleValues: [], histogram: { bins: ['Week 1', 'Week 2', 'Week 3', 'Week 4'], counts: [11150, 11180, 11400, 11500] } },
        { name: 'deleted', type: 'string', nullPercent: 0, uniqueCount: 2, uniquePercent: 0.004, sampleValues: ['true', 'false'], histogram: { bins: ['false', 'true'], counts: [43968, 1262] } },
      ],
      qualityScore: 82.5,
      qualityMetrics: {
        completeness: 99.2,
        uniqueness: 89.3,
        consistency: 92.1,
        timeliness: 100,
      },
      missingHeatmap: {
        rows: Array.from({ length: 10 }).map((_, i) => i * 4523),
        columns: ['date', 'price', 'notes', 'status'],
        matrix: Array.from({ length: 10 }).map(() => Array.from({ length: 4 }).map(() => Math.random() * 100)),
      },
      topRisks: [
        {
          level: 'high',
          issue: 'Missing values in price column',
          column: 'price',
          affectedRows: 232,
          recommendation: 'Consider mean/median imputation or drop rows',
        },
        {
          level: 'medium',
          issue: 'Inconsistent date formats',
          column: 'date',
          affectedRows: 450,
          recommendation: 'Normalize to ISO 8601 format',
        },
        {
          level: 'medium',
          issue: 'Outliers detected in quantity',
          column: 'quantity',
          affectedRows: 89,
          recommendation: 'Review and filter extreme values',
        },
      ],
    });
  }, 1500);
});

/**
 * Cleaning Plan
 */
app.post('/api/clean/plan', (req, res) => {
  const { datasetId, autoDetect } = req.body;

  setTimeout(() => {
    res.json({
      planId: `plan-${Date.now()}`,
      datasetId,
      steps: [
        {
          stepId: 'step-001',
          type: 'drop-duplicates',
          description: 'Remove duplicate order IDs',
          parameters: { subset: ['order_id'], keep: 'first' },
          enabled: true,
          estimatedRowImpact: 45,
          rationale: 'Found 45 exact duplicate rows based on order_id',
        },
        {
          stepId: 'step-002',
          type: 'impute-missing',
          description: 'Impute missing prices with median',
          parameters: { column: 'price', method: 'median' },
          enabled: true,
          estimatedRowImpact: 232,
          rationale: 'Missing values in price column (0.5%) will be filled with median value $999.99',
        },
        {
          stepId: 'step-003',
          type: 'normalize-dates',
          description: 'Normalize all dates to ISO 8601',
          parameters: { columns: ['date', 'created_at', 'updated_at'], format: 'YYYY-MM-DD' },
          enabled: true,
          estimatedRowImpact: 450,
          rationale: 'Inconsistent date formats detected; standardizing to ISO 8601',
        },
        {
          stepId: 'step-004',
          type: 'remove-outliers',
          description: 'Remove quantity outliers (IQR method)',
          parameters: { column: 'quantity', method: 'iqr', multiplier: 1.5 },
          enabled: false,
          estimatedRowImpact: 89,
          rationale: 'Quantity values > 15 detected as outliers; disabled by default for review',
        },
      ],
    });
  }, 800);
});

/**
 * Clean Execution
 */
app.post('/api/clean/execute', (req, res) => {
  const { planId, apply } = req.body;

  // Set headers for streaming
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Transfer-Encoding', 'chunked');

  const stepIds = ['step-001', 'step-002', 'step-003'];
  let stepIndex = 0;

  const streamStep = () => {
    if (stepIndex < stepIds.length) {
      const stepId = stepIds[stepIndex];
      res.write(
        JSON.stringify({
          stepId,
          status: 'success',
          beforeSample: generateMockPreview(3),
          afterSample: generateMockPreview(3),
          rowsAffected: Math.floor(Math.random() * 500) + 10,
          rationale: `Applied cleaning transformation for ${stepId}`,
          timestamp: new Date().toISOString(),
        }) + '\n'
      );
      stepIndex++;
      setTimeout(streamStep, 1000);
    } else {
      // Final response
      res.write(
        JSON.stringify({
          cleanedDatasetId: `ds-${Date.now()}`,
          auditLogId: `audit-${Date.now()}`,
          completed: true,
        }) + '\n'
      );
      res.end();
    }
  };

  setTimeout(streamStep, 500);
});

/**
 * Query / Agent
 */
app.post('/api/ask', (req, res) => {
  const { datasetId, question, mode, userId } = req.body;
  const runId = `run-${Date.now()}`;

  // Initial response with plan
  res.json({
    runId,
    plan: [
      { stepId: 'plan-step-1', type: 'query', description: 'Parse question and identify analysis objectives' },
      { stepId: 'plan-step-2', type: 'analysis', description: 'Analyze sales trends across regions' },
      { stepId: 'plan-step-3', type: 'visualization', description: 'Generate trend chart and summary statistics' },
      { stepId: 'plan-step-4', type: 'recommendation', description: 'Formulate recommendations based on findings' },
    ],
  });

  // Store runId for later use in WebSocket events
  res.locals.runId = runId;
});

/**
 * Audit Log
 */
app.get('/api/audit/:auditLogId', (req, res) => {
  const { auditLogId } = req.params;

  setTimeout(() => {
    res.json({
      id: auditLogId,
      runId: `run-${Date.now()}`,
      timestamp: new Date().toISOString(),
      type: 'query',
      datasetId: 'ds-001',
      userId: 'user-123',
      prompts: [
        {
          stepId: 'plan-step-2',
          modelName: 'gpt-4',
          prompt: 'Analyze the sales data for trends across regions.',
          timestamp: new Date().toISOString(),
        },
      ],
      toolCalls: [
        {
          stepId: 'plan-step-2',
          toolName: 'sql_query',
          input: { query: 'SELECT region, SUM(price * quantity) as revenue FROM sales GROUP BY region' },
          output: { rows: 4, columns: 2 },
          timestamp: new Date().toISOString(),
        },
      ],
      modelOutputs: [
        {
          stepId: 'plan-step-2',
          modelName: 'gpt-4',
          output: 'The analysis shows strong regional variations...',
          timestamp: new Date().toISOString(),
        },
      ],
      steps: [],
      hash: `hash-${Date.now()}`,
    });
  }, 500);
});

/**
 * Run History
 */
app.get('/api/history', (req, res) => {
  const { datasetId, limit = 50, offset = 0 } = req.query;

  res.json([
    {
      id: 'run-1',
      timestamp: new Date(Date.now() - 86400000).toISOString(),
      datasetId,
      datasetName: 'Sales Q4 2024',
      question: 'What are the top 5 products by revenue?',
      confidenceScore: 0.95,
      executionTimeMs: 1250,
      status: 'success',
    },
    {
      id: 'run-2',
      timestamp: new Date(Date.now() - 172800000).toISOString(),
      datasetId,
      datasetName: 'Sales Q4 2024',
      question: 'Which regions have the highest growth rate?',
      confidenceScore: 0.88,
      executionTimeMs: 2100,
      status: 'success',
    },
  ]);
});

// ============================================================================
// Error Handling
// ============================================================================

app.use((err, req, res, next) => {
  console.error('[Mock Backend] Error:', err);
  res.status(500).json({
    code: 'INTERNAL_ERROR',
    message: err.message,
    timestamp: new Date().toISOString(),
  });
});

// ============================================================================
// Server Start
// ============================================================================

app.listen(PORT, () => {
  console.log(`\n[Mock Backend] Server running on http://localhost:${PORT}`);
  console.log(`[Mock Backend] Endpoints ready for testing`);
  console.log(`[Mock Backend] CORS enabled for frontend at http://localhost:3000\n`);
});

module.exports = app;
