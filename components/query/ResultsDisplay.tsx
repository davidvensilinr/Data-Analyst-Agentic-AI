'use client';

import React from 'react';
import { QueryResult } from '@/lib/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Download, Copy } from 'lucide-react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

interface ResultsDisplayProps {
  result: QueryResult;
  onExport?: () => void;
}

export const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ result, onExport }) => {
  const [copiedText, setCopiedText] = React.useState<string | null>(null);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedText(text);
    setTimeout(() => setCopiedText(null), 2000);
  };

  return (
    <div className="space-y-6 w-full">
      {/* Summary Section */}
      {result.summary && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Summary</span>
              <Badge variant="outline">
                Confidence: {Math.round(result.confidence * 100)}%
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 leading-relaxed">{result.summary}</p>
          </CardContent>
        </Card>
      )}

      {/* Charts Section */}
      {result.charts && result.charts.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Charts & Visualizations</h3>
          {result.charts.map((chart, index) => (
            <Card key={index}>
              <CardHeader>
                <CardTitle className="text-base">{chart.title || `Chart ${index + 1}`}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-80 w-full">
                  <ChartRenderer spec={chart} />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Tables Section */}
      {result.tables && result.tables.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Data Tables</h3>
          {result.tables.map((table, index) => (
            <Card key={index}>
              <CardHeader>
                <CardTitle className="text-base">{table.title || `Table ${index + 1}`}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm border-collapse">
                    <thead>
                      <tr className="border-b bg-gray-50">
                        {table.columns && table.columns.map((col) => (
                          <th key={col} className="text-left p-3 font-semibold">
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {table.rows && table.rows.map((row, rowIndex) => (
                        <tr key={rowIndex} className="border-b hover:bg-gray-50">
                          {table.columns && table.columns.map((col) => (
                            <td key={`${rowIndex}-${col}`} className="p-3">
                              {String(row[col] || '')}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  className="mt-4"
                  onClick={() => handleCopy(JSON.stringify(table.rows, null, 2))}
                >
                  <Copy className="w-4 h-4 mr-2" />
                  {copiedText === JSON.stringify(table.rows) ? 'Copied!' : 'Copy Data'}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Recommendations Section */}
      {result.recommendations && result.recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recommendations</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {result.recommendations.map((rec, index) => (
                <li key={index} className="flex gap-3">
                  <span className="text-blue-500 font-bold flex-shrink-0">{index + 1}.</span>
                  <span className="text-gray-700">{rec}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Export Button */}
      <Button onClick={onExport} className="w-full">
        <Download className="w-4 h-4 mr-2" />
        Export Results
      </Button>
    </div>
  );
};

interface ChartRendererProps {
  spec: any;
}

const ChartRenderer: React.FC<ChartRendererProps> = ({ spec }) => {
  if (!spec.data || spec.data.length === 0) {
    return <div className="text-center text-gray-500">No data to display</div>;
  }

  const chartType = spec.type || 'bar';
  const xKey = spec.x || Object.keys(spec.data[0])[0];
  const yKey = spec.y || Object.keys(spec.data[0])[1];

  try {
    if (chartType === 'line') {
      return (
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={spec.data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={xKey} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey={yKey} stroke="#8884d8" />
          </LineChart>
        </ResponsiveContainer>
      );
    } else {
      return (
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={spec.data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={xKey} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey={yKey} fill="#8884d8" />
          </BarChart>
        </ResponsiveContainer>
      );
    }
  } catch (error) {
    return <div className="text-center text-red-500">Error rendering chart</div>;
  }
};
