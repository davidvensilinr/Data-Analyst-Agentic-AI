'use client';

import React from 'react';
import { AuditLogEntry } from '@/lib/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Download, ChevronDown, ChevronRight } from 'lucide-react';
import { format } from 'date-fns';

interface AuditLogProps {
  entries: AuditLogEntry[];
  onDownload?: (entry: AuditLogEntry) => void;
}

export const AuditLog: React.FC<AuditLogProps> = ({ entries, onDownload }) => {
  const [expandedIds, setExpandedIds] = React.useState<Set<string>>(new Set());

  const toggleExpanded = (id: string) => {
    const newExpanded = new Set(expandedIds);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedIds(newExpanded);
  };

  const handleDownload = (entry: AuditLogEntry) => {
    const json = JSON.stringify(entry, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit-${entry.id}-${format(new Date(entry.timestamp), 'yyyy-MM-dd-HHmmss')}.json`;
    a.click();
    URL.revokeObjectURL(url);
    onDownload?.(entry);
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Activity & Audit Log</CardTitle>
      </CardHeader>
      <CardContent>
        {entries.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No activities recorded yet
          </div>
        ) : (
          <div className="space-y-3">
            {entries.map((entry) => (
              <div
                key={entry.id}
                className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h4 className="font-semibold">{entry.type}</h4>
                      <Badge variant="outline" className="text-xs">
                        {format(new Date(entry.timestamp), 'PPpp')}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{entry.description}</p>
                    <div className="flex items-center gap-4 text-xs text-gray-500 mb-2">
                      {entry.userId && <span>User: {entry.userId}</span>}
                      {entry.metadata?.datasetId && <span>Dataset: {entry.metadata.datasetId}</span>}
                      {entry.metadata?.runId && <span>Run: {entry.metadata.runId}</span>}
                    </div>

                    {/* Expanded content */}
                    {expandedIds.has(entry.id) && (
                      <div className="mt-4 pt-4 border-t space-y-3">
                        {entry.prompts && entry.prompts.length > 0 && (
                          <div>
                            <h5 className="font-semibold text-sm mb-2">Prompts</h5>
                            {entry.prompts.map((prompt, i) => (
                              <details key={i} className="text-xs mb-2">
                                <summary className="cursor-pointer font-mono text-blue-600 hover:underline">
                                  Prompt {i + 1}
                                </summary>
                                <pre className="bg-gray-100 p-2 rounded mt-1 overflow-auto max-h-32 text-xs text-gray-700">
                                  {prompt}
                                </pre>
                              </details>
                            ))}
                          </div>
                        )}

                        {entry.toolCalls && entry.toolCalls.length > 0 && (
                          <div>
                            <h5 className="font-semibold text-sm mb-2">Tool Calls</h5>
                            {entry.toolCalls.map((call, i) => (
                              <details key={i} className="text-xs mb-2">
                                <summary className="cursor-pointer font-mono text-green-600 hover:underline">
                                  {call.toolName}
                                </summary>
                                <pre className="bg-gray-100 p-2 rounded mt-1 overflow-auto max-h-32 text-xs text-gray-700">
                                  {JSON.stringify(call, null, 2)}
                                </pre>
                              </details>
                            ))}
                          </div>
                        )}

                        {entry.modelOutputs && entry.modelOutputs.length > 0 && (
                          <div>
                            <h5 className="font-semibold text-sm mb-2">Model Outputs</h5>
                            {entry.modelOutputs.map((output, i) => (
                              <details key={i} className="text-xs mb-2">
                                <summary className="cursor-pointer font-mono text-purple-600 hover:underline">
                                  Output {i + 1}
                                </summary>
                                <pre className="bg-gray-100 p-2 rounded mt-1 overflow-auto max-h-32 text-xs text-gray-700">
                                  {output}
                                </pre>
                              </details>
                            ))}
                          </div>
                        )}

                        {entry.metadata?.summary && (
                          <div>
                            <h5 className="font-semibold text-sm mb-2">Summary</h5>
                            <p className="text-xs text-gray-700 bg-gray-50 p-2 rounded">
                              {entry.metadata.summary}
                            </p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 flex-shrink-0">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleExpanded(entry.id)}
                    >
                      {expandedIds.has(entry.id) ? (
                        <ChevronDown className="w-4 h-4" />
                      ) : (
                        <ChevronRight className="w-4 h-4" />
                      )}
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDownload(entry)}
                    >
                      <Download className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
