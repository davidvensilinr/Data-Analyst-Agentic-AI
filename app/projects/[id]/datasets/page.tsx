'use client';

import React, { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { ArrowLeft, Plus, Database, Calendar } from 'lucide-react';
import { useUIStore } from '@/lib/store/ui.store';
import { getApiClient } from '@/lib/api';
import { Dataset } from '@/lib/types';
import { toast } from 'sonner';

export default function DatasetsPage() {
  const router = useRouter();
  const params = useParams();
  const projectId = params?.id as string;

  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const setCurrentDatasetId = useUIStore((state) => state.setCurrentDataset);

  useEffect(() => {
    loadDatasets();
  }, [projectId]);

  const loadDatasets = async () => {
    try {
      setIsLoading(true);
      const api = getApiClient();
      const data = await api.listDatasets(projectId);
      setDatasets(data);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to load datasets';
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectDataset = (datasetId: string) => {
    setCurrentDatasetId(datasetId);
  };

  return (
    <div className="min-h-screen bg-white dark:bg-slate-900">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-slate-900 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Link href="/projects" className="inline-flex items-center gap-2 text-red-600 hover:text-red-700 mb-4">
            <ArrowLeft className="h-4 w-4" />
            Back to Projects
          </Link>
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-black dark:text-white">Datasets</h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                Select a dataset to analyze or upload a new one
              </p>
            </div>
            <Link href={`/projects/${projectId}/upload`}>
              <Button className="bg-red-600 hover:bg-red-700 text-white">
                <Plus className="h-4 w-4 mr-2" />
                New Dataset
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {isLoading ? (
          <div className="flex justify-center items-center py-12">
            <p className="text-gray-600 dark:text-gray-400">Loading datasets...</p>
          </div>
        ) : datasets.length === 0 ? (
          <Card className="p-12 text-center border border-gray-200 dark:border-gray-800">
            <Database className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-black dark:text-white mb-2">
              No datasets yet
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Upload your first dataset to get started with data analysis
            </p>
            <Link href={`/projects/${projectId}/upload`}>
              <Button className="bg-red-600 hover:bg-red-700 text-white">
                Upload Dataset
              </Button>
            </Link>
          </Card>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {datasets.map((dataset) => (
              <Card
                key={dataset.id}
                className="p-6 border border-gray-200 dark:border-gray-800 hover:border-red-300 dark:hover:border-red-800 transition-all hover:shadow-md"
              >
                <h3 className="text-lg font-semibold text-black dark:text-white truncate">
                  {dataset.name}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1 truncate">
                  {dataset.fileName}
                </p>

                <div className="grid grid-cols-2 gap-3 my-4 text-sm">
                  <div>
                    <p className="text-xs text-gray-600 dark:text-gray-400">Rows</p>
                    <p className="font-semibold text-black dark:text-white">
                      {dataset.rowsEstimated.toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600 dark:text-gray-400">Columns</p>
                    <p className="font-semibold text-black dark:text-white">{dataset.columnsCount}</p>
                  </div>
                  <div className="col-span-2">
                    <p className="text-xs text-gray-600 dark:text-gray-400 flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {new Date(dataset.uploadedAt).toLocaleDateString()}
                    </p>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Link
                    href={`/projects/${projectId}/datasets/${dataset.id}/profile`}
                    className="flex-1"
                    onClick={() => handleSelectDataset(dataset.id)}
                  >
                    <Button variant="outline" className="w-full border-gray-300 text-black dark:text-white dark:border-gray-700 hover:border-red-300" size="sm">
                      Profile
                    </Button>
                  </Link>
                  <Link
                    href={`/projects/${projectId}/datasets/${dataset.id}/query`}
                    className="flex-1"
                    onClick={() => handleSelectDataset(dataset.id)}
                  >
                    <Button className="w-full bg-red-600 hover:bg-red-700 text-white" size="sm">
                      Query
                    </Button>
                  </Link>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
