'use client';

import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, CheckCircle, AlertTriangle, Info } from 'lucide-react';
import { ProfileResponse, DataQualityRisk } from '@/lib/types';
import ColumnCard from './ColumnCard';

interface ProfileDashboardProps {
  profile: ProfileResponse;
}

export default function ProfileDashboard({ profile }: ProfileDashboardProps) {
  const getQualityColor = (score: number) => {
    if (score >= 90) return { bg: 'bg-green-100 dark:bg-green-900', text: 'text-green-800 dark:text-green-200', icon: <CheckCircle className="h-5 w-5" /> };
    if (score >= 70) return { bg: 'bg-amber-100 dark:bg-amber-900', text: 'text-amber-800 dark:text-amber-200', icon: <AlertTriangle className="h-5 w-5" /> };
    return { bg: 'bg-red-100 dark:bg-red-900', text: 'text-red-800 dark:text-red-200', icon: <AlertCircle className="h-5 w-5" /> };
  };

  const qualityColor = getQualityColor(profile.qualityScore);

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'high':
        return 'border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950';
      case 'medium':
        return 'border-amber-200 dark:border-amber-900 bg-amber-50 dark:bg-amber-950';
      case 'low':
        return 'border-blue-200 dark:border-blue-900 bg-blue-50 dark:bg-blue-950';
      default:
        return 'border-slate-200 dark:border-slate-700';
    }
  };

  return (
    <div className="space-y-8">
      {/* Overview Cards */}
      <div className="grid md:grid-cols-4 gap-4">
        {/* Quality Score */}
        <Card className={`p-6 border ${qualityColor.bg}`}>
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs text-slate-600 dark:text-slate-400 mb-1">Data Quality Score</p>
              <p className={`text-3xl font-bold ${qualityColor.text}`}>{profile.qualityScore.toFixed(1)}</p>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-2">out of 100</p>
            </div>
            <div className={`${qualityColor.text}`}>{qualityColor.icon}</div>
          </div>
        </Card>

        {/* Completeness */}
        <Card className="p-6 border border-slate-200 dark:border-slate-700">
          <p className="text-xs text-slate-600 dark:text-slate-400 mb-1">Completeness</p>
          <p className="text-3xl font-bold text-slate-900 dark:text-white">
            {profile.qualityMetrics.completeness.toFixed(1)}%
          </p>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-2">Missing values present</p>
        </Card>

        {/* Consistency */}
        <Card className="p-6 border border-slate-200 dark:border-slate-700">
          <p className="text-xs text-slate-600 dark:text-slate-400 mb-1">Consistency</p>
          <p className="text-3xl font-bold text-slate-900 dark:text-white">
            {profile.qualityMetrics.consistency.toFixed(1)}%
          </p>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-2">Format compliance</p>
        </Card>

        {/* Dataset Size */}
        <Card className="p-6 border border-slate-200 dark:border-slate-700">
          <p className="text-xs text-slate-600 dark:text-slate-400 mb-1">Dataset Size</p>
          <p className="text-3xl font-bold text-slate-900 dark:text-white">
            {(profile.rowsCount / 1000).toFixed(1)}K
          </p>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-2">rows × {profile.columnsCount} columns</p>
        </Card>
      </div>

      {/* Top Risks */}
      {profile.topRisks && profile.topRisks.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-4">Data Quality Issues</h2>
          <div className="space-y-3">
            {profile.topRisks.map((risk, index) => (
              <Card key={index} className={`p-4 border-l-4 ${getRiskColor(risk.level)}`}>
                <div className="flex items-start gap-4">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <Badge
                        className={
                          risk.level === 'high'
                            ? 'bg-red-600 dark:bg-red-700'
                            : risk.level === 'medium'
                              ? 'bg-amber-600 dark:bg-amber-700'
                              : 'bg-blue-600 dark:bg-blue-700'
                        }
                      >
                        {risk.level.toUpperCase()}
                      </Badge>
                      {risk.column && (
                        <span className="text-sm font-mono text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-800 px-2 py-1 rounded">
                          {risk.column}
                        </span>
                      )}
                    </div>
                    <p className="text-sm font-medium text-slate-900 dark:text-white mb-1">{risk.issue}</p>
                    <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">{risk.recommendation}</p>
                    <p className="text-xs text-slate-500 dark:text-slate-500">
                      Affects {risk.affectedRows.toLocaleString()} rows
                    </p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Column Profiles */}
      <div>
        <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-4">Column Profiles</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {profile.columns.map((column) => (
            <ColumnCard key={column.name} column={column} />
          ))}
        </div>
      </div>
    </div>
  );
}
