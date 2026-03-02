'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Plus, ArrowRight, Database, Clock, Trash2 } from 'lucide-react';
import { useUIStore } from '@/lib/store/ui.store';
import { getApiClient } from '@/lib/api';
import { Project } from '@/lib/types';

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [newProjectName, setNewProjectName] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const setCurrentProjectId = useUIStore((state) => state.setCurrentProject);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setIsLoading(true);
      const api = getApiClient();
      const data = await api.listProjects();
      setProjects(data);
    } catch (error) {
      console.error('[ProjectsPage] Error loading projects:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateProject = async () => {
    if (!newProjectName.trim()) return;

    try {
      setIsCreating(true);
      const api = getApiClient();
      const newProject = await api.createProject(newProjectName);
      setProjects([...projects, newProject]);
      setNewProjectName('');
    } catch (error) {
      console.error('[ProjectsPage] Error creating project:', error);
    } finally {
      setIsCreating(false);
    }
  };

  const handleSelectProject = (projectId: string) => {
    setCurrentProjectId(projectId);
  };

  return (
    <div className="min-h-screen bg-white dark:bg-slate-900">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-slate-900 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-black dark:text-white">Projects</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Manage your data analysis projects
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Create New Project */}
        <Card className="p-6 mb-8 border border-gray-200 dark:border-gray-800 shadow-sm">
          <h2 className="text-lg font-semibold text-black dark:text-white mb-4">
            Create New Project
          </h2>
          <div className="flex gap-2">
            <Input
              type="text"
              placeholder="Project name (e.g., Q4 Sales Analysis)"
              value={newProjectName}
              onChange={(e) => setNewProjectName(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleCreateProject();
                }
              }}
              disabled={isCreating}
              className="flex-1 border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950"
            />
            <Button
              onClick={handleCreateProject}
              disabled={isCreating || !newProjectName.trim()}
              className="bg-red-600 hover:bg-red-700 text-white"
            >
              <Plus className="h-4 w-4 mr-2" />
              Create
            </Button>
          </div>
        </Card>

        {/* Projects Grid */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-gray-600 dark:text-gray-400">Loading projects...</div>
          </div>
        ) : projects.length === 0 ? (
          <div className="text-center py-12">
            <Database className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-black dark:text-white mb-2">
              No projects yet
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Create your first project to get started with data analysis
            </p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <Card
                key={project.id}
                className="p-6 border border-gray-200 dark:border-gray-800 hover:border-red-300 dark:hover:border-red-800 transition-all hover:shadow-md"
              >
                <h3 className="text-lg font-semibold text-black dark:text-white mb-2">
                  {project.name}
                </h3>
                {project.description && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    {project.description}
                  </p>
                )}

                <div className="flex items-center gap-4 mb-4 text-sm text-gray-600 dark:text-gray-400">
                  <div className="flex items-center gap-1">
                    <Database className="h-4 w-4" />
                    {project.datasetCount} dataset{project.datasetCount !== 1 ? 's' : ''}
                  </div>
                  <div className="flex items-center gap-1">
                    <Clock className="h-4 w-4" />
                    {new Date(project.updatedAt).toLocaleDateString()}
                  </div>
                </div>

                <div className="flex gap-2">
                  <Link href={`/projects/${project.id}/upload`} className="flex-1">
                    <Button
                      variant="outline"
                      className="w-full border-gray-300 text-black dark:text-white dark:border-gray-700 hover:border-red-300"
                      onClick={() => handleSelectProject(project.id)}
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      New Dataset
                    </Button>
                  </Link>
                  {project.datasetCount > 0 && (
                    <Link href={`/projects/${project.id}/datasets`} className="flex-1">
                      <Button
                        className="w-full bg-red-600 hover:bg-red-700 text-white"
                        onClick={() => handleSelectProject(project.id)}
                      >
                        Open
                        <ArrowRight className="h-4 w-4 ml-2" />
                      </Button>
                    </Link>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
