'use client';

import React, { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { CleaningPlanResponse, PreviewRow, CleaningStep } from '@/lib/types';
import { ChevronDown, ChevronUp, Eye } from 'lucide-react';
import PreviewTable from '../dataset/PreviewTable';

interface CleaningEditorProps {
  plan: CleaningPlanResponse;
  beforeSample: PreviewRow[];
  columns: string[];
  onExecute: (enabledStepIds: Set<string>) => void;
  isExecuting?: boolean;
}

export default function CleaningEditor({
  plan,
  beforeSample,
  columns,
  onExecute,
  isExecuting = false,
}: CleaningEditorProps) {
  const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set());
  const [enabledSteps, setEnabledSteps] = useState<Set<string>>(
    new Set(plan.steps.filter((s) => s.enabled).map((s) => s.stepId))
  );

  const toggleStepExpanded = (stepId: string) => {
    const newExpanded = new Set(expandedSteps);
    if (newExpanded.has(stepId)) {
      newExpanded.delete(stepId);
    } else {
      newExpanded.add(stepId);
    }
    setExpandedSteps(newExpanded);
  };

  const toggleStep = (stepId: string) => {
    const newEnabled = new Set(enabledSteps);
    if (newEnabled.has(stepId)) {
      newEnabled.delete(stepId);
    } else {
      newEnabled.add(stepId);
    }
    setEnabledSteps(newEnabled);
  };

  const totalRowsAffected = plan.steps
    .filter((s) => enabledSteps.has(s.stepId))
    .reduce((sum, s) => sum + s.estimatedRowImpact, 0);

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="grid md:grid-cols-3 gap-4">
        <Card className="p-4 border border-slate-200 dark:border-slate-700">
          <p className="text-sm text-slate-600 dark:text-slate-400">Total Steps</p>
          <p className="text-2xl font-bold text-slate-900 dark:text-white">{plan.steps.length}</p>
        </Card>
        <Card className="p-4 border border-slate-200 dark:border-slate-700">
          <p className="text-sm text-slate-600 dark:text-slate-400">Enabled Steps</p>
          <p className="text-2xl font-bold text-blue-600">{enabledSteps.size}</p>
        </Card>
        <Card className="p-4 border border-slate-200 dark:border-slate-700">
          <p className="text-sm text-slate-600 dark:text-slate-400">Affected Rows</p>
          <p className="text-2xl font-bold text-amber-600">{totalRowsAffected.toLocaleString()}</p>
        </Card>
      </div>

      {/* Steps */}
      <div className="space-y-3">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Cleaning Steps</h3>
        {plan.steps.map((step) => (
          <Card
            key={step.stepId}
            className="p-4 border border-slate-200 dark:border-slate-700 hover:border-blue-300 dark:hover:border-blue-700 transition-colors"
          >
            <div className="flex items-start gap-4">
              {/* Checkbox */}
              <Checkbox
                id={`step-${step.stepId}`}
                checked={enabledSteps.has(step.stepId)}
                onCheckedChange={() => toggleStep(step.stepId)}
                disabled={isExecuting}
                className="mt-1"
              />

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-4 mb-2">
                  <div>
                    <label
                      htmlFor={`step-${step.stepId}`}
                      className="text-base font-semibold text-slate-900 dark:text-white cursor-pointer"
                    >
                      {step.description}
                    </label>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="outline">{step.type}</Badge>
                      <span className="text-sm text-slate-600 dark:text-slate-400">
                        ~{step.estimatedRowImpact.toLocaleString()} rows
                      </span>
                    </div>
                  </div>

                  {/* Expand Button */}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => toggleStepExpanded(step.stepId)}
                    disabled={isExecuting}
                  >
                    {expandedSteps.has(step.stepId) ? (
                      <ChevronUp className="h-4 w-4" />
                    ) : (
                      <ChevronDown className="h-4 w-4" />
                    )}
                  </Button>
                </div>

                {/* Expanded Details */}
                {expandedSteps.has(step.stepId) && (
                  <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700 space-y-3">
                    <div>
                      <p className="text-sm font-medium text-slate-900 dark:text-white mb-1">Rationale</p>
                      <p className="text-sm text-slate-600 dark:text-slate-400">{step.rationale}</p>
                    </div>

                    {Object.keys(step.parameters).length > 0 && (
                      <div>
                        <p className="text-sm font-medium text-slate-900 dark:text-white mb-2">Parameters</p>
                        <div className="bg-slate-50 dark:bg-slate-800 p-3 rounded font-mono text-xs text-slate-600 dark:text-slate-400 overflow-x-auto">
                          {JSON.stringify(step.parameters, null, 2)}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 pt-6 border-t border-slate-200 dark:border-slate-700">
        <Button
          onClick={() => onExecute(enabledSteps)}
          disabled={isExecuting || enabledSteps.size === 0}
          className="bg-blue-600 hover:bg-blue-700 flex-1"
          size="lg"
        >
          {isExecuting ? 'Applying...' : 'Apply Selected Steps'}
        </Button>

        <Button
          variant="outline"
          onClick={() => setEnabledSteps(new Set(plan.steps.map((s) => s.stepId)))}
          disabled={isExecuting}
        >
          Enable All
        </Button>

        <Button
          variant="outline"
          onClick={() => setEnabledSteps(new Set())}
          disabled={isExecuting}
        >
          Disable All
        </Button>
      </div>
    </div>
  );
}
