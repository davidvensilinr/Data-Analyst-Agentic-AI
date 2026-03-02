'use client';

import React from 'react';
import { AgentStepExecution } from '@/lib/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ChevronDown, ChevronRight, AlertCircle, CheckCircle, Clock, Zap } from 'lucide-react';

interface StepTraceVisualizerProps {
  steps: AgentStepExecution[];
  isRunning?: boolean;
  selectedStepId?: string;
  onSelectStep?: (stepId: string) => void;
}

export const StepTraceVisualizer: React.FC<StepTraceVisualizerProps> = ({
  steps,
  isRunning = false,
  selectedStepId,
  onSelectStep,
}) => {
  const [expandedSteps, setExpandedSteps] = React.useState<Set<string>>(new Set());

  const toggleStep = (stepId: string) => {
    const newExpanded = new Set(expandedSteps);
    if (newExpanded.has(stepId)) {
      newExpanded.delete(stepId);
    } else {
      newExpanded.add(stepId);
    }
    setExpandedSteps(newExpanded);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'running':
        return <Zap className="w-5 h-5 text-blue-500 animate-pulse" />;
      case 'pending':
        return <Clock className="w-5 h-5 text-gray-400" />;
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-50 border-green-200';
      case 'running':
        return 'bg-blue-50 border-blue-200';
      case 'pending':
        return 'bg-gray-50 border-gray-200';
      case 'failed':
        return 'bg-red-50 border-red-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Step Trace {isRunning && '(Running...)'}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {steps.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No steps executed yet
            </div>
          ) : (
            steps.map((step, index) => (
              <div key={step.stepId} className="relative">
                {/* Timeline connector */}
                {index < steps.length - 1 && (
                  <div className="absolute left-6 top-12 w-1 h-8 bg-gray-200" />
                )}

                {/* Step card */}
                <div
                  className={`border rounded-lg p-4 cursor-pointer transition-all ${getStatusColor(step.status)} ${
                    selectedStepId === step.stepId ? 'ring-2 ring-blue-500' : ''
                  }`}
                  onClick={() => {
                    toggleStep(step.stepId);
                    onSelectStep?.(step.stepId);
                  }}
                >
                  <div className="flex items-start gap-3">
                    {/* Status icon */}
                    <div className="flex-shrink-0 mt-1">
                      {getStatusIcon(step.status)}
                    </div>

                    {/* Step info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-2 mb-1">
                        <div className="flex items-center gap-2">
                          <h4 className="font-semibold text-sm">{step.stepId}</h4>
                          {step.stepType && (
                            <Badge variant="outline" className="text-xs">
                              {step.stepType}
                            </Badge>
                          )}
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleStep(step.stepId);
                          }}
                          className="text-gray-500 hover:text-gray-700"
                        >
                          {expandedSteps.has(step.stepId) ? (
                            <ChevronDown className="w-4 h-4" />
                          ) : (
                            <ChevronRight className="w-4 h-4" />
                          )}
                        </button>
                      </div>
                      <p className="text-xs text-gray-600 mb-2">
                        Status: <Badge variant="secondary" className="text-xs ml-1">{step.status}</Badge>
                      </p>

                      {/* Expanded content */}
                      {expandedSteps.has(step.stepId) && (
                        <div className="mt-3 pt-3 border-t text-xs space-y-2">
                          {step.prompt && (
                            <div>
                              <p className="font-semibold text-gray-700 mb-1">Prompt:</p>
                              <pre className="bg-white p-2 rounded text-xs overflow-auto max-h-32 text-gray-600">
                                {step.prompt}
                              </pre>
                            </div>
                          )}
                          {step.toolCalls && step.toolCalls.length > 0 && (
                            <div>
                              <p className="font-semibold text-gray-700 mb-1">Tool Calls:</p>
                              {step.toolCalls.map((call, i) => (
                                <div key={i} className="bg-white p-2 rounded mb-1">
                                  <p className="font-mono text-blue-600">{call.toolName}</p>
                                  <pre className="text-xs text-gray-600 mt-1 overflow-auto max-h-24">
                                    {JSON.stringify(call.parameters, null, 2)}
                                  </pre>
                                </div>
                              ))}
                            </div>
                          )}
                          {step.modelOutput && (
                            <div>
                              <p className="font-semibold text-gray-700 mb-1">Model Output:</p>
                              <pre className="bg-white p-2 rounded text-xs overflow-auto max-h-32 text-gray-600">
                                {step.modelOutput}
                              </pre>
                            </div>
                          )}
                          {step.error && (
                            <div className="bg-red-100 border border-red-300 p-2 rounded">
                              <p className="font-semibold text-red-700">Error:</p>
                              <p className="text-red-600 text-xs mt-1">{step.error}</p>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
};
