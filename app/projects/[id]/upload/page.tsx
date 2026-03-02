'use client';

import React, { useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle, ArrowLeft } from 'lucide-react';
import FileUpload from '@/components/dataset/FileUpload';
import PreviewTable from '@/components/dataset/PreviewTable';
import { useDatasetStore } from '@/lib/store/dataset.store';
import { useUIStore } from '@/lib/store/ui.store';
import { getApiClient } from '@/lib/api';
import { FileMetadata, PreviewRow } from '@/lib/types';
import Link from 'next/link';
import { toast } from 'sonner';

export default function UploadPage() {
  const router = useRouter();
  const params = useParams();
  const projectId = params?.id as string;

  const [datasetName, setDatasetName] = useState('');
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileMetadata, setFileMetadata] = useState<FileMetadata | null>(null);
  const [preview, setPreview] = useState<PreviewRow[]>([]);

  const setCurrentDataset = useDatasetStore((state) => state.setCurrentDataset);
  const setUploadState = useDatasetStore((state) => state.setUploadState);

  const handleFileSelected = (file: File, metadata: FileMetadata, previewData: PreviewRow[]) => {
    setSelectedFile(file);
    setFileMetadata(metadata);
    setPreview(previewData);
    setUploadError(null);
    setDatasetName(file.name.replace(/\.[^.]+$/, '')); // Remove extension
  };

  const handleError = (error: string) => {
    setUploadError(error);
    toast.error(error);
  };

  const handleUpload = async () => {
    if (!selectedFile || !fileMetadata || !datasetName.trim()) {
      setUploadError('Please select a file and enter a dataset name');
      return;
    }

    try {
      setIsUploading(true);
      setUploadError(null);

      const api = getApiClient();
      const response = await api.uploadFile(
        selectedFile,
        datasetName,
        projectId,
        undefined,
        (progress) => {
          console.log('[Upload] Progress:', progress);
        }
      );

      // Store dataset info
      setCurrentDataset(response.dataset);
      toast.success('Dataset uploaded successfully!');

      // Redirect to profile page
      router.push(`/projects/${projectId}/datasets/${response.datasetId}/profile`);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to upload dataset';
      setUploadError(message);
      toast.error(message);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white dark:bg-slate-900">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-slate-900 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Link href="/projects" className="inline-flex items-center gap-2 text-red-600 hover:text-red-700 mb-4">
            <ArrowLeft className="h-4 w-4" />
            Back to Projects
          </Link>
          <h1 className="text-3xl font-bold text-black dark:text-white">Upload Dataset</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Choose a CSV, JSON, or Parquet file to analyze
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Upload Form */}
        <Card className="p-8 mb-8 border border-gray-200 dark:border-gray-800 shadow-sm">
          <div className="space-y-6">
            {/* File Upload */}
            <div>
              <label className="block text-sm font-medium text-black dark:text-white mb-4">
                Upload File
              </label>
              <FileUpload
                onFileSelected={handleFileSelected}
                onError={handleError}
                disabled={isUploading}
              />
            </div>

            {/* Error Alert */}
            {uploadError && (
              <Alert className="border-red-600 dark:border-red-700 bg-red-50 dark:bg-red-950">
                <AlertCircle className="h-4 w-4 text-red-600 dark:text-red-400" />
                <AlertDescription className="text-red-800 dark:text-red-200">
                  {uploadError}
                </AlertDescription>
              </Alert>
            )}

            {/* File Metadata */}
            {fileMetadata && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-gray-50 dark:bg-gray-800 p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                  <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">File Size</p>
                  <p className="text-sm font-semibold text-black dark:text-white">
                    {(fileMetadata.fileSize / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
                <div className="bg-gray-50 dark:bg-gray-800 p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                  <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Columns</p>
                  <p className="text-sm font-semibold text-black dark:text-white">
                    {fileMetadata.columnsCount}
                  </p>
                </div>
                <div className="bg-gray-50 dark:bg-gray-800 p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                  <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Estimated Rows</p>
                  <p className="text-sm font-semibold text-black dark:text-white">
                    {fileMetadata.rowsEstimated.toLocaleString()}
                  </p>
                </div>
                <div className="bg-gray-50 dark:bg-gray-800 p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                  <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Type</p>
                  <p className="text-sm font-semibold text-black dark:text-white">
                    {fileMetadata.mimeType.split('/')[1].toUpperCase()}
                  </p>
                </div>
              </div>
            )}

            {/* Dataset Name */}
            <div>
              <label className="block text-sm font-medium text-black dark:text-white mb-2">
                Dataset Name
              </label>
              <Input
                type="text"
                placeholder="e.g., Q4 Sales Data"
                value={datasetName}
                onChange={(e) => setDatasetName(e.target.value)}
                disabled={isUploading}
                className="w-full border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950"
              />
            </div>

            {/* Upload Button */}
            <div className="flex gap-3 pt-4">
              <Button
                onClick={handleUpload}
                disabled={isUploading || !selectedFile || !datasetName.trim()}
                className="bg-red-600 hover:bg-red-700 text-white flex-1"
                size="lg"
              >
                {isUploading ? 'Uploading...' : 'Upload Dataset'}
              </Button>
              <Button
                variant="outline"
                disabled={isUploading}
                onClick={() => router.back()}
                className="border-gray-300 text-black dark:text-white dark:border-gray-700"
                size="lg"
              >
                Cancel
              </Button>
            </div>
          </div>
        </Card>

        {/* Preview */}
        {preview.length > 0 && (
          <Card className="p-8 border border-gray-200 dark:border-gray-800">
            <PreviewTable
              data={preview}
              columns={fileMetadata?.columns || []}
              title="Data Preview (First 10 rows)"
              pageSize={10}
            />
          </Card>
        )}
      </div>
    </div>
  );
}
