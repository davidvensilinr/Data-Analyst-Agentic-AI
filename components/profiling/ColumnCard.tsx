'use client';

import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ColumnProfile } from '@/lib/types';
import { AlertCircle } from 'lucide-react';

interface ColumnCardProps {
  column: ColumnProfile;
}

export default function ColumnCard({ column }: ColumnCardProps) {
  const getTypeColor = (type: string) => {
    switch (type) {
      case 'number':
        return 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200';
      case 'string':
        return 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200';
      case 'date':
        return 'bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200';
      case 'boolean':
        return 'bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200';
      default:
        return 'bg-gray-100 dark:bg-gray-900 text-gray-800 dark:text-gray-200';
    }
  };

  const chartData = column.histogram
    ? column.histogram.bins.map((bin, index) => ({
        name: String(bin),
        count: column.histogram?.counts[index] || 0,
      }))
    : [];

  return (
    <Card className="p-6 border border-slate-200 dark:border-slate-700 hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{column.name}</h3>
          <Badge className={`mt-2 ${getTypeColor(column.type)}`}>{column.type}</Badge>
        </div>
        {column.nullPercent > 10 && (
          <AlertCircle className="h-5 w-5 text-amber-500" title="High missing values" />
        )}
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-3 mb-4 text-sm">
        <div>
          <p className="text-slate-600 dark:text-slate-400">Null %</p>
          <p className="font-semibold text-slate-900 dark:text-white">{column.nullPercent.toFixed(1)}%</p>
        </div>
        <div>
          <p className="text-slate-600 dark:text-slate-400">Unique</p>
          <p className="font-semibold text-slate-900 dark:text-white">{column.uniqueCount}</p>
        </div>

        {column.type === 'number' && (
          <>
            <div>
              <p className="text-slate-600 dark:text-slate-400">Min</p>
              <p className="font-semibold text-slate-900 dark:text-white">{column.min?.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-slate-600 dark:text-slate-400">Max</p>
              <p className="font-semibold text-slate-900 dark:text-white">{column.max?.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-slate-600 dark:text-slate-400">Mean</p>
              <p className="font-semibold text-slate-900 dark:text-white">{column.mean?.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-slate-600 dark:text-slate-400">Median</p>
              <p className="font-semibold text-slate-900 dark:text-white">{column.median?.toFixed(2)}</p>
            </div>
          </>
        )}

        {column.type === 'string' && (
          <>
            <div>
              <p className="text-slate-600 dark:text-slate-400">Min Length</p>
              <p className="font-semibold text-slate-900 dark:text-white">{column.minLength}</p>
            </div>
            <div>
              <p className="text-slate-600 dark:text-slate-400">Max Length</p>
              <p className="font-semibold text-slate-900 dark:text-white">{column.maxLength}</p>
            </div>
          </>
        )}
      </div>

      {/* Sample Values */}
      {column.sampleValues && column.sampleValues.length > 0 && (
        <div className="mb-4">
          <p className="text-xs text-slate-600 dark:text-slate-400 mb-2">Sample Values</p>
          <div className="flex flex-wrap gap-2">
            {column.sampleValues.slice(0, 3).map((value, index) => (
              <span
                key={index}
                className="px-2 py-1 text-xs bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 rounded truncate"
              >
                {String(value).substring(0, 20)}
              </span>
            ))}
            {column.sampleValues.length > 3 && (
              <span className="px-2 py-1 text-xs text-slate-500 dark:text-slate-400">
                +{column.sampleValues.length - 3} more
              </span>
            )}
          </div>
        </div>
      )}

      {/* Histogram */}
      {chartData.length > 0 && (
        <div className="mt-4">
          <p className="text-xs text-slate-600 dark:text-slate-400 mb-2">Distribution</p>
          <ResponsiveContainer width="100%" height={150}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.1} />
              <XAxis
                dataKey="name"
                tick={{ fontSize: 11 }}
                tickFormatter={(value) => String(value).substring(0, 10)}
              />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(15, 23, 42, 0.9)',
                  border: 'none',
                  borderRadius: '6px',
                  color: '#fff',
                }}
              />
              <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  );
}
