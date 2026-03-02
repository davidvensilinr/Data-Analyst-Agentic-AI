'use client';

import React, { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle, ArrowLeft, Loader } from 'lucide-react';
import { useDatasetStore } from '@/lib/store/dataset.store';
import { getApiClient } from '@/lib/api';
import ProfileDashboard from '@/components/profiling/ProfileDashboard';
import { ProfileResponse } from '@/lib/types';
import Link from 'next/link';
import { toast } from 'sonner';

export default function ProfilePage() {
  const router = useRouter();
  const params = useParams();
  const projectId = params?.id as string;
  const datasetId = params?.datasetId as string;

  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const currentDataset = useDatasetStore((state) => state.currentDataset);
  const setCurrentProfile = useDatasetStore((state) => state.setCurrentProfile);

  useEffect(() => {
    loadProfile();
  }, [datasetId]);

  const loadProfile = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const api = getApiClient();
      const data = await api.getProfile(datasetId);
      setProfile(data);
      setCurrentProfile(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load profile';
      setError(message);
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
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
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-black dark:text-white">
                {currentDataset?.name || 'Dataset'} Profile
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                Comprehensive data quality analysis and statistics
              </p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => loadProfile()} className="border-gray-300 text-black dark:text-white dark:border-gray-700 hover:border-red-300">
                Refresh
              </Button>
              <Link href={`/projects/${projectId}/datasets/${datasetId}/clean`}>
                <Button className="bg-red-600 hover:bg-red-700 text-white">
                  Next: Clean Data
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {isLoading ? (
          <div className="flex justify-center items-center py-12">
            <Loader className="h-6 w-6 animate-spin text-red-600" />
            <span className="ml-3 text-gray-600 dark:text-gray-400">Analyzing dataset...</span>
          </div>
        ) : error ? (
          <Alert className="border-red-600 dark:border-red-700 bg-red-50 dark:bg-red-950">
            <AlertCircle className="h-4 w-4 text-red-600 dark:text-red-400" />
            <AlertDescription className="text-red-800 dark:text-red-200">
              {error}
            </AlertDescription>
          </Alert>
        ) : profile ? (
          <ProfileDashboard profile={profile} />
        ) : (
          <Card className="p-8 text-center border border-gray-200 dark:border-gray-800">
            <p className="text-gray-600 dark:text-gray-400">No profile data available</p>
          </Card>
        )}
      </div>
    </div>
  );
}
