'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Loader2, Server, Database, AlertCircle, CheckCircle } from 'lucide-react';
import { useBackendSwitch, BackendMode } from '@/hooks/useBackendSwitch';

export function BackendSwitcher() {
  const {
    mode,
    isAvailable,
    isChecking,
    error,
    switchBackend,
    checkBackendAvailability,
    getBackendStatus,
    getBackendColor,
  } = useBackendSwitch();

  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleSwitch = async (newMode: BackendMode) => {
    if (newMode === mode) return;
    
    const success = await switchBackend(newMode);
    if (success) {
      // Show success notification (you could integrate with your toast system)
      console.log(`Successfully switched to ${newMode} backend`);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await checkBackendAvailability(mode);
    setIsRefreshing(false);
  };

  const getBackendIcon = () => {
    if (isChecking || isRefreshing) {
      return <Loader2 className="h-4 w-4 animate-spin" />;
    }
    
    if (error) {
      return <AlertCircle className="h-4 w-4" />;
    }
    
    if (mode === 'real') {
      return <Database className="h-4 w-4" />;
    }
    
    return <Server className="h-4 w-4" />;
  };

  const getBackendBadgeVariant = () => {
    if (error) return 'destructive';
    if (mode === 'real') return 'default';
    return 'secondary';
  };

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Backend Configuration</CardTitle>
          <div className="flex items-center gap-2">
            {getBackendIcon()}
            <Badge variant={getBackendBadgeVariant()}>
              {mode === 'real' ? 'Real' : 'Mock'}
            </Badge>
          </div>
        </div>
        <CardDescription>
          Switch between mock and real autonomous data analyst backend
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Status */}
        <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
          <span className="text-sm font-medium">Status:</span>
          <span className="text-sm text-muted-foreground">
            {isChecking || isRefreshing ? 'Checking...' : getBackendStatus()}
          </span>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Backend Switch */}
        <div className="flex items-center justify-between p-3 border rounded-lg">
          <div className="space-y-1">
            <Label htmlFor="backend-switch" className="text-sm font-medium">
              Use Real Backend
            </Label>
            <p className="text-xs text-muted-foreground">
              Enable the autonomous data analyst backend for advanced features
            </p>
          </div>
          <Switch
            id="backend-switch"
            checked={mode === 'real'}
            onCheckedChange={(checked) => handleSwitch(checked ? 'real' : 'mock')}
            disabled={isChecking || isRefreshing}
          />
        </div>

        {/* Backend Information */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium">Backend Information</h4>
          
          {mode === 'real' ? (
            <div className="space-y-2 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-3 w-3 text-green-500" />
                <span>LLM-powered analysis planning</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="h-3 w-3 text-green-500" />
                <span>Real-time WebSocket streaming</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="h-3 w-3 text-green-500" />
                <span>Immutable audit logging</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="h-3 w-3 text-green-500" />
                <span>Advanced ML models</span>
              </div>
            </div>
          ) : (
            <div className="space-y-2 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <Server className="h-3 w-3" />
                <span>Mock responses for development</span>
              </div>
              <div className="flex items-center gap-2">
                <Server className="h-3 w-3" />
                <span>Fast and reliable</span>
              </div>
              <div className="flex items-center gap-2">
                <Server className="h-3 w-3" />
                <span>No external dependencies</span>
              </div>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={isChecking || isRefreshing}
            className="flex-1"
          >
            {isRefreshing ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Database className="h-4 w-4 mr-2" />
            )}
            Check Connection
          </Button>
          
          {mode === 'real' && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => window.open('http://localhost:8000/docs', '_blank')}
              className="flex-1"
            >
              <Server className="h-4 w-4 mr-2" />
              API Docs
            </Button>
          )}
        </div>

        {/* Quick Start Guide */}
        <div className="text-xs text-muted-foreground border-t pt-3">
          <p className="font-medium mb-1">Quick Start:</p>
          <ul className="space-y-1">
            {mode === 'real' ? (
              <>
                <li>• Ensure the real backend is running on port 8000</li>
                <li>• Run: <code className="bg-muted px-1 rounded">npm run backend:real</code></li>
                <li>• Or use Docker: <code className="bg-muted px-1 rounded">npm run full:docker</code></li>
              </>
            ) : (
              <>
                <li>• Mock backend is automatically available</li>
                <li>• Run: <code className="bg-muted px-1 rounded">npm run dev:mock</code></li>
                <li>• Perfect for development and testing</li>
              </>
            )}
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}
