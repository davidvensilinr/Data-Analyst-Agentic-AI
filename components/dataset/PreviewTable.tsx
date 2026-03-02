'use client';

import React, { useState, useMemo } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { PreviewRow } from '@/lib/types';

interface PreviewTableProps {
  data: PreviewRow[];
  columns: string[];
  title?: string;
  pageSize?: number;
}

export default function PreviewTable({
  data,
  columns,
  title = 'Data Preview',
  pageSize = 10,
}: PreviewTableProps) {
  const [currentPage, setCurrentPage] = useState(0);

  const paginatedData = useMemo(() => {
    const start = currentPage * pageSize;
    const end = start + pageSize;
    return data.slice(start, end);
  }, [data, currentPage, pageSize]);

  const totalPages = Math.ceil(data.length / pageSize);

  const formatValue = (value: any): string => {
    if (value === null || value === undefined) {
      return '—';
    }
    if (typeof value === 'object') {
      return JSON.stringify(value).substring(0, 50);
    }
    return String(value).substring(0, 100);
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{title}</h3>
        <span className="text-sm text-slate-600 dark:text-slate-400">
          {data.length} row{data.length !== 1 ? 's' : ''} • Page {currentPage + 1} of {totalPages}
        </span>
      </div>

      <Card className="overflow-x-auto border border-slate-200 dark:border-slate-700">
        <table className="w-full text-sm">
          <thead className="bg-slate-100 dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700">
            <tr>
              {columns.map((column) => (
                <th
                  key={column}
                  className="px-4 py-3 text-left text-xs font-semibold text-slate-700 dark:text-slate-300 whitespace-nowrap"
                >
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paginatedData.map((row, rowIndex) => (
              <tr
                key={rowIndex}
                className="border-b border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800"
              >
                {columns.map((column) => (
                  <td key={`${rowIndex}-${column}`} className="px-4 py-3 text-slate-900 dark:text-slate-100">
                    <div className="truncate max-w-xs" title={String(row[column])}>
                      {formatValue(row[column])}
                    </div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </Card>

      {totalPages > 1 && (
        <div className="flex justify-between items-center">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
            disabled={currentPage === 0}
          >
            <ChevronLeft className="h-4 w-4 mr-1" />
            Previous
          </Button>
          <div className="flex gap-1">
            {Array.from({ length: totalPages }).map((_, i) => (
              <Button
                key={i}
                variant={currentPage === i ? 'default' : 'outline'}
                size="sm"
                onClick={() => setCurrentPage(i)}
                className="min-w-10"
              >
                {i + 1}
              </Button>
            ))}
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentPage(Math.min(totalPages - 1, currentPage + 1))}
            disabled={currentPage === totalPages - 1}
          >
            Next
            <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        </div>
      )}
    </div>
  );
}
