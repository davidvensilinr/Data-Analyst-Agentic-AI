import {
  UploadResponse,
  ProfileResponse,
  CleaningPlanResponse,
  CleaningExecutionResponse,
  AgentQueryInitResponse,
  AuditLog,
  Dataset,
  Project,
  RunHistory,
  PreviewRow,
  ColumnProfile,
  Histogram,
  CleaningStep,
  CleaningStepResult,
  AgentPlanStep,
  QueryResult,
  ChartSpec,
  TableResult,
} from './types';

/**
 * Mock Projects
 */
export const mockProjects: Project[] = [
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
];

/**
 * Mock Datasets
 */
export const mockDataset: Dataset = {
  id: 'ds-001',
  name: 'Sales Transactions Q4',
  projectId: 'proj-001',
  fileName: 'sales_q4_2024.csv',
  fileSize: 2458624,
  rowsEstimated: 45230,
  columnsCount: 12,
  columns: ['order_id', 'date', 'customer_id', 'product', 'quantity', 'price', 'region', 'status', 'notes', 'created_at', 'updated_at', 'deleted'],
  uploadedAt: '2024-01-20T12:00:00Z',
  updatedAt: '2024-01-20T15:30:00Z',
  profiledAt: '2024-01-20T12:05:00Z',
};

/**
 * Mock Preview Data
 */
export function generateMockPreview(rows: number = 10): PreviewRow[] {
  const products = ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones'];
  const regions = ['North', 'South', 'East', 'West'];
  const statuses = ['completed', 'pending', 'failed', 'processing'];

  return Array.from({ length: rows }).map((_, i) => ({
    order_id: `ORD-${String(i + 1).padStart(6, '0')}`,
    date: new Date(2024, Math.random() * 11, Math.floor(Math.random() * 28) + 1).toISOString().split('T')[0],
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

/**
 * Mock Upload Response
 */
export function generateMockUploadResponse(datasetId: string = 'ds-001'): UploadResponse {
  return {
    datasetId,
    dataset: mockDataset,
    preview: generateMockPreview(20),
    metadata: {
      fileName: 'sales_q4_2024.csv',
      fileSize: 2458624,
      rowsEstimated: 45230,
      columnsCount: 12,
      columns: mockDataset.columns,
      mimeType: 'text/csv',
    },
  };
}

/**
 * Mock Column Profile
 */
function generateMockColumnProfile(name: string, type: string): ColumnProfile {
  const profiles: Record<string, ColumnProfile> = {
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
    date: {
      name: 'date',
      type: 'date',
      nullPercent: 0.2,
      uniqueCount: 91,
      uniquePercent: 0.2,
      sampleValues: ['2024-01-01', '2024-01-02', '2024-01-03'],
      histogram: {
        bins: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
        counts: [11307, 11230, 11456, 11237],
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
    status: {
      name: 'status',
      type: 'string',
      nullPercent: 0.3,
      uniqueCount: 4,
      uniquePercent: 0.01,
      sampleValues: ['completed', 'pending', 'failed'],
      histogram: {
        bins: ['completed', 'pending', 'failed', 'processing'],
        counts: [38000, 5000, 1500, 730],
      },
    },
  };

  return (
    profiles[name] || {
      name,
      type: type as any,
      nullPercent: Math.random() * 10,
      uniqueCount: Math.floor(Math.random() * 1000),
      uniquePercent: Math.random() * 100,
      sampleValues: [],
      histogram: {
        bins: [],
        counts: [],
      },
    }
  );
}

/**
 * Mock Profile Response
 */
export function generateMockProfileResponse(datasetId: string = 'ds-001'): ProfileResponse {
  return {
    datasetId,
    columnsCount: 12,
    rowsCount: 45230,
    columns: [
      generateMockColumnProfile('order_id', 'string'),
      generateMockColumnProfile('date', 'date'),
      generateMockColumnProfile('customer_id', 'string'),
      generateMockColumnProfile('product', 'string'),
      generateMockColumnProfile('quantity', 'number'),
      generateMockColumnProfile('price', 'number'),
      generateMockColumnProfile('region', 'string'),
      generateMockColumnProfile('status', 'string'),
      generateMockColumnProfile('notes', 'string'),
      generateMockColumnProfile('created_at', 'date'),
      generateMockColumnProfile('updated_at', 'date'),
      generateMockColumnProfile('deleted', 'string'),
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
      matrix: Array.from({ length: 10 }).map(() =>
        Array.from({ length: 4 }).map(() => Math.random() * 100)
      ),
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
  };
}

/**
 * Mock Cleaning Plan Response
 */
export function generateMockCleaningPlanResponse(datasetId: string = 'ds-001'): CleaningPlanResponse {
  const steps: CleaningStep[] = [
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
    {
      stepId: 'step-005',
      type: 'trim-whitespace',
      description: 'Trim whitespace in text columns',
      parameters: { columns: ['product', 'region', 'notes', 'status'] },
      enabled: true,
      estimatedRowImpact: 156,
      rationale: 'Leading/trailing whitespace found in categorical columns',
    },
  ];

  return {
    planId: `plan-${Date.now()}`,
    datasetId,
    steps,
  };
}

/**
 * Mock Cleaning Execution Response
 */
export function generateMockCleaningExecutionResponse(planId: string): CleaningExecutionResponse {
  const steps: CleaningStepResult[] = [
    {
      stepId: 'step-001',
      status: 'success',
      beforeSample: generateMockPreview(3),
      afterSample: generateMockPreview(3),
      rowsAffected: 45,
      rationale: 'Removed 45 duplicate rows',
      timestamp: new Date().toISOString(),
    },
    {
      stepId: 'step-002',
      status: 'success',
      beforeSample: generateMockPreview(3),
      afterSample: generateMockPreview(3),
      rowsAffected: 232,
      rationale: 'Imputed 232 missing price values with median $999.99',
      timestamp: new Date(Date.now() + 2000).toISOString(),
    },
  ];

  return {
    cleanedDatasetId: `ds-${Date.now()}`,
    auditLogId: `audit-${Date.now()}`,
    steps,
  };
}

/**
 * Mock Agent Query Response
 */
export function generateMockQueryInitResponse(datasetId: string = 'ds-001'): AgentQueryInitResponse {
  const steps: AgentPlanStep[] = [
    {
      stepId: 'plan-step-1',
      type: 'query',
      description: 'Parse question and identify analysis objectives',
    },
    {
      stepId: 'plan-step-2',
      type: 'analysis',
      description: 'Analyze sales trends across regions',
    },
    {
      stepId: 'plan-step-3',
      type: 'visualization',
      description: 'Generate trend chart and summary statistics',
    },
    {
      stepId: 'plan-step-4',
      type: 'recommendation',
      description: 'Formulate recommendations based on findings',
    },
  ];

  return {
    runId: `run-${Date.now()}`,
    plan: steps,
  };
}

/**
 * Mock Query Result
 */
export function generateMockQueryResult(runId: string, question: string = 'What are our top selling products by region?'): QueryResult {
  const chartData = [
    { region: 'North', Laptop: 12000, Mouse: 5000, Keyboard: 3500, Monitor: 8000, Headphones: 2500 },
    { region: 'South', Laptop: 10500, Mouse: 4800, Keyboard: 3200, Monitor: 7500, Headphones: 2300 },
    { region: 'East', Laptop: 15000, Mouse: 6200, Keyboard: 4100, Monitor: 9500, Headphones: 3000 },
    { region: 'West', Laptop: 11000, Mouse: 5200, Keyboard: 3800, Monitor: 8200, Headphones: 2700 },
  ];

  const charts: ChartSpec[] = [
    {
      id: 'chart-1',
      type: 'bar',
      title: 'Sales by Product and Region',
      description: 'Grouped bar chart showing revenue distribution',
      xAxis: { dataKey: 'region', label: 'Region' },
      yAxis: { dataKey: 'value', label: 'Revenue ($)' },
      data: chartData,
    },
    {
      id: 'chart-2',
      type: 'line',
      title: 'Revenue Trend',
      description: 'Monthly revenue progression',
      data: [
        { month: 'Jan', revenue: 145000 },
        { month: 'Feb', revenue: 152000 },
        { month: 'Mar', revenue: 148000 },
        { month: 'Apr', revenue: 161000 },
        { month: 'May', revenue: 158000 },
        { month: 'Jun', revenue: 172000 },
      ],
    },
  ];

  const tables: TableResult[] = [
    {
      id: 'table-1',
      title: 'Top Products by Revenue',
      columns: [
        { key: 'rank', label: 'Rank', type: 'number' },
        { key: 'product', label: 'Product', type: 'string' },
        { key: 'totalRevenue', label: 'Total Revenue', type: 'number' },
        { key: 'unitsSold', label: 'Units Sold', type: 'number' },
        { key: 'avgPrice', label: 'Avg Price', type: 'number' },
      ],
      rows: [
        { rank: 1, product: 'Monitor', totalRevenue: 33200, unitsSold: 412, avgPrice: 805.83 },
        { rank: 2, product: 'Laptop', totalRevenue: 48500, unitsSold: 4050, avgPrice: 1197.53 },
        { rank: 3, product: 'Keyboard', totalRevenue: 14600, unitsSold: 2920, avgPrice: 50.0 },
        { rank: 4, product: 'Mouse', totalRevenue: 21200, unitsSold: 4240, avgPrice: 5.0 },
        { rank: 5, product: 'Headphones', totalRevenue: 10500, unitsSold: 3500, avgPrice: 30.0 },
      ],
    },
  ];

  return {
    runId,
    datasetId: 'ds-001',
    question,
    charts,
    tables,
    summary:
      'Our analysis of Q4 2024 sales data reveals strong performance across all regions. The East region leads with $43.8M in revenue, followed by North with $31.0M. Laptops and Monitors are our top revenue drivers, accounting for 67% of total sales.',
    recommendations: [
      'Expand Monitor inventory in the East region where demand is highest',
      'Launch targeted keyboard bundle promotions to increase attachment rates',
      'Investigate lower headphone sales in South and West regions for market opportunities',
      'Consider region-specific pricing strategies to optimize margin per region',
    ],
    confidenceScore: 0.94,
    executionTimeMs: 2450,
  };
}

/**
 * Mock Audit Log
 */
export function generateMockAuditLog(runId: string): AuditLog {
  return {
    id: `audit-${runId}`,
    runId,
    timestamp: new Date().toISOString(),
    type: 'query',
    datasetId: 'ds-001',
    userId: 'user-123',
    prompts: [
      {
        stepId: 'plan-step-2',
        modelName: 'gpt-4',
        prompt: 'Analyze the sales data for trends across regions. Focus on identifying top products and growth patterns.',
        timestamp: new Date().toISOString(),
      },
    ],
    toolCalls: [
      {
        stepId: 'plan-step-2',
        toolName: 'sql_query',
        input: {
          query: 'SELECT region, product, SUM(quantity * price) as revenue FROM sales GROUP BY region, product',
        },
        output: { rows: 20, columns: 3 },
        timestamp: new Date().toISOString(),
      },
    ],
    modelOutputs: [
      {
        stepId: 'plan-step-2',
        modelName: 'gpt-4',
        output: 'The analysis shows strong regional variations in product preferences...',
        timestamp: new Date().toISOString(),
      },
    ],
    steps: [],
    hash: `hash-${Date.now()}`,
  };
}

/**
 * Mock Run History
 */
export function generateMockRunHistory(datasetId: string = 'ds-001'): RunHistory[] {
  return [
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
    {
      id: 'run-3',
      timestamp: new Date(Date.now() - 259200000).toISOString(),
      datasetId,
      datasetName: 'Sales Q4 2024',
      question: 'Identify customer segments by purchasing behavior',
      confidenceScore: 0.72,
      executionTimeMs: 3450,
      status: 'success',
    },
  ];
}
