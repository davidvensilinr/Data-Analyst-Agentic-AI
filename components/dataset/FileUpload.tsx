'use client';

import React, { useCallback, useState } from 'react';
import { Upload, File, AlertCircle, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import Papa from 'papaparse';
import { FileMetadata, PreviewRow } from '@/lib/types';

interface FileUploadProps {
  onFileSelected: (file: File, metadata: FileMetadata, preview: PreviewRow[]) => void;
  onError: (error: string) => void;
  isLoading?: boolean;
  disabled?: boolean;
}

export default function FileUpload({
  onFileSelected,
  onError,
  isLoading = false,
  disabled = false,
}: FileUploadProps) {
  const [isDragActive, setIsDragActive] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const parseCSV = useCallback((file: File): Promise<{ metadata: FileMetadata; preview: PreviewRow[] }> => {
    return new Promise((resolve, reject) => {
      Papa.parse(file, {
        header: true,
        dynamicTyping: true,
        skipEmptyLines: true,
        preview: 1000, // Parse first 1000 rows to estimate
        complete: (results: any) => {
          try {
            const columns = results.meta.fields || [];
            const rows = results.data.filter((row: any) => Object.keys(row).some((key) => row[key] != null));

            const metadata: FileMetadata = {
              fileName: file.name,
              fileSize: file.size,
              rowsEstimated: rows.length,
              columnsCount: columns.length,
              columns,
              mimeType: file.type,
            };

            const preview = rows.slice(0, 10);

            resolve({ metadata, preview });
          } catch (err) {
            reject(new Error('Failed to parse CSV file'));
          }
        },
        error: (error: any) => {
          reject(new Error(`CSV parsing error: ${error.message}`));
        },
      });
    });
  }, []);

  const handleFile = useCallback(
    async (file: File) => {
      // Validate file type
      const validTypes = ['text/csv', 'application/vnd.ms-excel', 'application/json'];
      if (!validTypes.includes(file.type) && !file.name.endsWith('.csv') && !file.name.endsWith('.json')) {
        onError('Invalid file type. Please upload CSV or JSON files.');
        return;
      }

      // Validate file size (100MB limit)
      if (file.size > 100 * 1024 * 1024) {
        onError('File is too large. Maximum size is 100MB.');
        return;
      }

      try {
        setSelectedFile(file);
        setUploadProgress(0);

        // Simulate progress
        const progressInterval = setInterval(() => {
          setUploadProgress((prev) => Math.min(prev + 10, 90));
        }, 100);

        // Parse file
        const { metadata, preview } = await parseCSV(file);
        clearInterval(progressInterval);
        setUploadProgress(100);

        // Trigger callback
        onFileSelected(file, metadata, preview);

        // Reset after success
        setTimeout(() => {
          setSelectedFile(null);
          setUploadProgress(0);
        }, 1000);
      } catch (error) {
        setSelectedFile(null);
        setUploadProgress(0);
        onError(error instanceof Error ? error.message : 'Failed to process file');
      }
    },
    [parseCSV, onFileSelected, onError]
  );

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(e.type === 'dragenter' || e.type === 'dragover');
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragActive(false);

      const files = e.dataTransfer.files;
      if (files && files[0]) {
        handleFile(files[0]);
      }
    },
    [handleFile]
  );

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.currentTarget.files;
      if (files && files[0]) {
        handleFile(files[0]);
      }
    },
    [handleFile]
  );

  return (
    <div className="space-y-4">
      <Card
        className={`p-12 border-2 border-dashed border-slate-300 dark:border-slate-600 rounded-lg transition-colors ${
          isDragActive ? 'border-blue-400 bg-blue-50 dark:bg-blue-950' : ''
        } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:border-blue-400'}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-input"
          className="hidden"
          accept=".csv,.json,.xlsx,.xls"
          onChange={handleInputChange}
          disabled={disabled || isLoading}
        />

        <label htmlFor="file-input" className="block text-center cursor-pointer">
          <div className="flex justify-center mb-4">
            {selectedFile ? (
              <CheckCircle className="h-12 w-12 text-green-500" />
            ) : (
              <Upload className="h-12 w-12 text-slate-400" />
            )}
          </div>

          <p className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
            {selectedFile ? 'File selected' : 'Drag & drop your dataset'}
          </p>

          <p className="text-sm text-slate-600 dark:text-slate-400">
            {selectedFile ? (
              selectedFile.name
            ) : (
              <>or <span className="text-blue-600 dark:text-blue-400">click to browse</span> CSV, JSON, or Parquet files</>
            )}
          </p>

          <p className="text-xs text-slate-500 dark:text-slate-500 mt-2">
            Maximum file size: 100MB
          </p>
        </label>
      </Card>

      {uploadProgress > 0 && uploadProgress < 100 && (
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-slate-600 dark:text-slate-400">Parsing file...</span>
            <span className="text-slate-600 dark:text-slate-400">{uploadProgress}%</span>
          </div>
          <Progress value={uploadProgress} className="h-2" />
        </div>
      )}

      {uploadProgress === 100 && (
        <Alert className="border-green-200 dark:border-green-900 bg-green-50 dark:bg-green-950">
          <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
          <AlertDescription className="text-green-800 dark:text-green-200">
            File processed successfully! Ready to upload.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}
