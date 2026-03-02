'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';
import { ArrowLeft, Send, Loader, AlertCircle, CheckCircle, BarChart3, Table2 } from 'lucide-react';
import { useQueryStore } from '@/lib/store/query.store';
import { useDatasetStore } from '@/lib/store/dataset.store';
import { getApiClient } from '@/lib/api';
import { AgentStepExecution, QueryResult } from '@/lib/types';
import { toast } from 'sonner';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function QueryPage() {
  const router = useRouter();
  const params = useParams();
  const projectId = params?.id as string;
  const datasetId = params?.datasetId as string;

  const [question, setQuestion] = useState('');
  const [mode, setMode] = useState<'auto' | 'dry_run'>('auto');
  const [isLoading, setIsLoading] = useState(false);

  const currentDataset = useDatasetStore((state) => state.currentDataset);
  const { plan, steps, result, isExecuting } = useQueryStore();
  const { setPlan, setRunId, updateStepExecution, setResult, reset } = useQueryStore();

  const handleSubmitQuery = async () => {
    if (!question.trim()) {
      toast.error('Please enter a question');
      return;
    }

    try {
      setIsLoading(true);
      reset();

      const api = getApiClient();
      const response = await api.submitQuery({
        datasetId,
        question,
        mode,
      });

      setRunId(response.runId);
      setPlan(response.plan);

      // Simulate agent execution
      simulateAgentExecution(response.runId);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to submit query';
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const simulateAgentExecution = (runId: string) => {
    const mockSteps = [
      {
        stepId: 'plan-step-2',
        stepType: 'analysis' as const,
        prompt: 'Analyze the sales data and identify top selling products by region',
        toolCall: 'sql_query',
        toolInput: 'SELECT product, region, SUM(quantity * price) as revenue FROM sales GROUP BY product, region ORDER BY revenue DESC',
        output: '20 rows returned with regional breakdown',
      },
      {
        stepId: 'plan-step-3',
        stepType: 'visualization' as const,
        prompt: 'Create visualizations for the sales analysis',
        output: 'Generated bar and line charts',
      },
    ];

    let stepIndex = 0;

    const executeNextStep = () => {
      if (stepIndex < mockSteps.length) {
        const step = mockSteps[stepIndex];

        // Simulate step execution
        updateStepExecution(step.stepId, {
          status: 'running',
          stepType: step.stepType,
        });

        setTimeout(() => {
          updateStepExecution(step.stepId, {
            status: 'completed',
            prompt: step.prompt,
            output: step.output,
            toolCalls: [
              {
                stepId: step.stepId,
                toolName: step.toolCall,
                input: { query: step.toolInput },
                output: step.output,
                timestamp: new Date().toISOString(),
              },
            ],
          });

          stepIndex++;
          executeNextStep();
        }, 1500);
      } else {
        // Show results
        const mockResult: QueryResult = {
          runId,
          datasetId,
          question,
          charts: [
            {
              id: 'chart-1',
              type: 'bar',
              title: 'Sales by Product and Region',
              data: [
                { product: 'Laptop', North: 12000, South: 10500, East: 15000, West: 11000 },
                { product: 'Monitor', North: 8000, South: 7500, East: 9500, West: 8200 },
                { product: 'Mouse', North: 5000, South: 4800, East: 6200, West: 5200 },
              ],
            },
          ],
          tables: [
            {
              id: 'table-1',
              title: 'Top Products by Revenue',
              columns: [
                { key: 'rank', label: 'Rank', type: 'number' },
                { key: 'product', label: 'Product', type: 'string' },
                { key: 'revenue', label: 'Total Revenue', type: 'number' },
                { key: 'units', label: 'Units Sold', type: 'number' },
              ],
              rows: [
                { rank: 1, product: 'Laptop', revenue: 48500, units: 4050 },
                { rank: 2, product: 'Monitor', revenue: 33200, units: 412 },
                { rank: 3, product: 'Mouse', revenue: 21200, units: 4240 },
              ],
            },
          ],
          summary:
            'Based on the analysis of your sales data, Laptops are your top revenue generator across all regions, with the East region showing the highest demand. Monitors are the second-best product, particularly strong in the North and East regions.',
          recommendations: [
            'Increase Laptop inventory in East region where demand is strongest',
            'Create Mouse and Keyboard bundles to boost attachment rates',
            'Investigate opportunities in South and West regions for expansion',
          ],
          confidenceScore: 0.92,
          executionTimeMs: 2800,
        };

        setResult(mockResult);
      }
    };

    executeNextStep();
  };

  return (
    <div className="min-h-screen bg-white dark:bg-slate-900">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-slate-900 sticky top-0 z-40 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Link href={`/projects/${projectId}`} className="inline-flex items-center gap-2 text-red-600 hover:text-red-700 mb-4">
            <ArrowLeft className="h-4 w-4" />
            Back to Project
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-black dark:text-white">
              {currentDataset?.name || 'Dataset'} Query
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Ask questions and get intelligent answers powered by autonomous agents
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Query Input & Plan */}
          <div className="lg:col-span-1 space-y-6">
            <Card className="p-6 border border-gray-200 dark:border-gray-800 shadow-sm">
              <h2 className="text-lg font-semibold text-black dark:text-white mb-4">Ask a Question</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-black dark:text-white mb-2">
                    Your Question
                  </label>
                  <Input
                    placeholder="e.g., What are our top products by region?"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') handleSubmitQuery();
                    }}
                    disabled={isLoading || isExecuting}
                    className="border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-black dark:text-white mb-2">
                    Mode
                  </label>
                  <div className="flex gap-2">
                    <Button
                      variant={mode === 'auto' ? 'default' : 'outline'}
                      onClick={() => setMode('auto')}
                      className={mode === 'auto' ? 'flex-1 bg-red-600 hover:bg-red-700 text-white' : 'flex-1 border-gray-300 text-black dark:text-white dark:border-gray-700'}
                      disabled={isLoading || isExecuting}
                    >
                      Auto Execute
                    </Button>
                    <Button
                      variant={mode === 'dry_run' ? 'default' : 'outline'}
                      onClick={() => setMode('dry_run')}
                      className={mode === 'dry_run' ? 'flex-1 bg-red-600 hover:bg-red-700 text-white' : 'flex-1 border-gray-300 text-black dark:text-white dark:border-gray-700'}
                      disabled={isLoading || isExecuting}
                    >
                      Dry Run
                    </Button>
                  </div>
                </div>

                <Button
                  onClick={handleSubmitQuery}
                  disabled={isLoading || !question.trim() || isExecuting}
                  className="w-full bg-red-600 hover:bg-red-700 text-white"
                  size="lg"
                >
                  {isLoading || isExecuting ? (
                    <>
                      <Loader className="h-4 w-4 mr-2 animate-spin" />
                      Executing...
                    </>
                  ) : (
                    <>
                      <Send className="h-4 w-4 mr-2" />
                      Submit
                    </>
                  )}
                </Button>
              </div>
            </Card>

            {/* Execution Plan */}
            {plan.length > 0 && (
              <Card className="p-6 border border-gray-200 dark:border-gray-800 shadow-sm">
                <h3 className="text-lg font-semibold text-black dark:text-white mb-4">Execution Plan</h3>
                <div className="space-y-2">
                  {plan.map((step, index) => {
                    const stepExecution = steps.get(step.stepId);
                    const isComplete = stepExecution?.status === 'completed';
                    const isRunning = stepExecution?.status === 'running';

                    return (
                      <div key={step.stepId} className="flex items-start gap-3 pb-3 border-b border-slate-200 dark:border-slate-700 last:border-0">
                        <div className="flex-shrink-0 mt-0.5">
                          {isComplete ? (
                            <CheckCircle className="h-5 w-5 text-green-600" />
                          ) : isRunning ? (
                            <Loader className="h-5 w-5 text-blue-600 animate-spin" />
                          ) : (
                            <div className="h-5 w-5 rounded-full border-2 border-slate-300 dark:border-slate-600" />
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-slate-900 dark:text-white truncate">
                            {step.description}
                          </p>
                          <Badge variant="outline" className="text-xs mt-1">
                            {step.type}
                          </Badge>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </Card>
            )}
          </div>

          {/* Results */}
          <div className="lg:col-span-2">
            {result ? (
              <Tabs defaultValue="charts" className="w-full">
                <TabsList className="grid w-full grid-cols-4">
                  <TabsTrigger value="charts" className="flex items-center gap-1">
                    <BarChart3 className="h-4 w-4" />
                    <span className="hidden sm:inline">Charts</span>
                  </TabsTrigger>
                  <TabsTrigger value="tables" className="flex items-center gap-1">
                    <Table2 className="h-4 w-4" />
                    <span className="hidden sm:inline">Tables</span>
                  </TabsTrigger>
                  <TabsTrigger value="summary">Summary</TabsTrigger>
                  <TabsTrigger value="recommendations">Tips</TabsTrigger>
                </TabsList>

                <TabsContent value="charts" className="space-y-6 mt-6">
                  {result.charts.map((chart) => (
                    <Card key={chart.id} className="p-6 border border-slate-200 dark:border-slate-700">
                      <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">{chart.title}</h3>
                      <ResponsiveContainer width="100%" height={300}>
                        {chart.type === 'bar' ? (
                          <BarChart data={chart.data}>
                            <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.1} />
                            <XAxis dataKey="product" tick={{ fontSize: 12 }} />
                            <YAxis tick={{ fontSize: 12 }} />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="North" fill="#3b82f6" />
                            <Bar dataKey="South" fill="#ef4444" />
                            <Bar dataKey="East" fill="#10b981" />
                            <Bar dataKey="West" fill="#f59e0b" />
                          </BarChart>
                        ) : (
                          <LineChart data={chart.data}>
                            <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.1} />
                            <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                            <YAxis tick={{ fontSize: 12 }} />
                            <Tooltip />
                            <Legend />
                            <Line type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={2} />
                          </LineChart>
                        )}
                      </ResponsiveContainer>
                    </Card>
                  ))}
                </TabsContent>

                <TabsContent value="tables" className="space-y-6 mt-6">
                  {result.tables.map((table) => (
                    <Card key={table.id} className="p-6 border border-slate-200 dark:border-slate-700 overflow-x-auto">
                      <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">{table.title}</h3>
                      <table className="w-full text-sm">
                        <thead className="border-b border-slate-200 dark:border-slate-700">
                          <tr>
                            {table.columns.map((col) => (
                              <th key={col.key} className="text-left py-3 px-4 font-semibold text-slate-900 dark:text-white">
                                {col.label}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {table.rows.map((row, idx) => (
                            <tr key={idx} className="border-b border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800">
                              {table.columns.map((col) => (
                                <td key={`${idx}-${col.key}`} className="py-3 px-4 text-slate-600 dark:text-slate-400">
                                  {String(row[col.key])}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </Card>
                  ))}
                </TabsContent>

                <TabsContent value="summary" className="mt-6">
                  <Card className="p-6 border border-slate-200 dark:border-slate-700">
                    <div className="space-y-4">
                      <div>
                        <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">Confidence Score</p>
                        <div className="flex items-center gap-3">
                          <div className="h-2 bg-gradient-to-r from-blue-500 to-green-500 rounded-full" style={{ width: `${result.confidenceScore * 100}%` }} />
                          <span className="text-lg font-semibold text-slate-900 dark:text-white">
                            {(result.confidenceScore * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                      <div>
                        <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">Execution Time</p>
                        <p className="text-slate-900 dark:text-white">{(result.executionTimeMs / 1000).toFixed(2)}s</p>
                      </div>
                      <div>
                        <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">Summary</p>
                        <p className="text-slate-900 dark:text-white leading-relaxed">{result.summary}</p>
                      </div>
                    </div>
                  </Card>
                </TabsContent>

                <TabsContent value="recommendations" className="mt-6">
                  <Card className="p-6 border border-slate-200 dark:border-slate-700">
                    <div className="space-y-3">
                      {result.recommendations.map((rec, idx) => (
                        <div key={idx} className="flex gap-3 p-3 bg-blue-50 dark:bg-blue-950 rounded-lg border border-blue-200 dark:border-blue-900">
                          <span className="font-semibold text-blue-600 dark:text-blue-400 flex-shrink-0">💡</span>
                          <p className="text-slate-900 dark:text-white">{rec}</p>
                        </div>
                      ))}
                    </div>
                  </Card>
                </TabsContent>
              </Tabs>
            ) : plan.length === 0 ? (
              <Card className="p-12 text-center border border-slate-200 dark:border-slate-700">
                <BarChart3 className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
                  Ask a Question to Get Started
                </h3>
                <p className="text-slate-600 dark:text-slate-400">
                  Enter a natural language question above and the AI agent will analyze your data step-by-step
                </p>
              </Card>
            ) : (
              <Card className="p-12 text-center border border-slate-200 dark:border-slate-700">
                <Loader className="h-12 w-12 text-blue-600 animate-spin mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                  Analyzing Your Data
                </h3>
                <p className="text-slate-600 dark:text-slate-400 mt-1">
                  Watch the plan above as each step executes...
                </p>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
