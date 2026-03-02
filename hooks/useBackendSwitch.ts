import { useState, useEffect } from 'react';
import { getApiAdapter, ApiAdapter } from '../lib/api.adapter';

export type BackendMode = 'mock' | 'real';

interface BackendState {
  mode: BackendMode;
  isAvailable: boolean;
  isChecking: boolean;
  error?: string;
}

export function useBackendSwitch() {
  const [backendState, setBackendState] = useState<BackendState>({
    mode: 'mock',
    isAvailable: true,
    isChecking: false,
  });

  const apiAdapter = getApiAdapter();

  // Check backend availability
  const checkBackendAvailability = async (mode: BackendMode): Promise<boolean> => {
    try {
      setBackendState(prev => ({ ...prev, isChecking: true, error: undefined }));
      
      // Temporarily switch to check availability
      const originalMode = apiAdapter.getBackendMode();
      apiAdapter.setBackendMode(mode === 'real');
      
      const healthResult = await apiAdapter.healthCheck();
      const isAvailable = typeof healthResult === 'boolean' ? healthResult : healthResult.status === 'healthy';
      
      // Restore original mode
      apiAdapter.setBackendMode(originalMode === 'real');
      
      return isAvailable;
    } catch (error) {
      console.error(`Failed to check ${mode} backend availability:`, error);
      return false;
    } finally {
      setBackendState(prev => ({ ...prev, isChecking: false }));
    }
  };

  // Switch backend mode
  const switchBackend = async (mode: BackendMode) => {
    try {
      setBackendState(prev => ({ ...prev, isChecking: true, error: undefined }));
      
      // Check if backend is available
      const isAvailable = await checkBackendAvailability(mode);
      
      if (!isAvailable) {
        const error = mode === 'real' 
          ? 'Real backend is not available. Please start the autonomous data analyst backend.'
          : 'Mock backend is not available.';
        
        setBackendState(prev => ({
          ...prev,
          error,
          isChecking: false,
        }));
        return false;
      }

      // Switch the backend
      apiAdapter.setBackendMode(mode === 'real');
      
      setBackendState({
        mode,
        isAvailable: true,
        isChecking: false,
      });

      console.log(`Switched to ${mode} backend`);
      return true;
      
    } catch (error) {
      const errorMessage = `Failed to switch to ${mode} backend: ${error}`;
      console.error(errorMessage);
      
      setBackendState(prev => ({
        ...prev,
        error: errorMessage,
        isChecking: false,
      }));
      
      return false;
    }
  };

  // Auto-detect backend availability on mount
  useEffect(() => {
    const autoDetectBackend = async () => {
      // First check if real backend is available
      const realBackendAvailable = await checkBackendAvailability('real');
      
      if (realBackendAvailable) {
        await switchBackend('real');
      } else {
        // Fall back to mock backend
        await switchBackend('mock');
      }
    };

    autoDetectBackend();
  }, []);

  // Get backend status description
  const getBackendStatus = () => {
    if (backendState.isChecking) {
      return 'Checking backend availability...';
    }

    if (backendState.error) {
      return backendState.error;
    }

    if (backendState.mode === 'real') {
      return 'Using Autonomous Data Analyst Backend (Real)';
    } else {
      return 'Using Mock Backend (Development)';
    }
  };

  // Get backend color for UI
  const getBackendColor = () => {
    if (backendState.error) {
      return 'destructive';
    }
    
    if (backendState.mode === 'real') {
      return 'default';
    }
    
    return 'secondary';
  };

  return {
    mode: backendState.mode,
    isAvailable: backendState.isAvailable,
    isChecking: backendState.isChecking,
    error: backendState.error,
    switchBackend,
    checkBackendAvailability,
    getBackendStatus,
    getBackendColor,
    apiAdapter,
  };
}

// Hook for getting the current API client
export function useApiClient() {
  const { apiAdapter } = useBackendSwitch();
  return apiAdapter;
}
