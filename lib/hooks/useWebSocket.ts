import { useEffect, useState, useRef, useCallback } from 'react';
import io, { Socket } from 'socket.io-client';

interface UseWebSocketOptions {
  url: string;
  autoConnect?: boolean;
  reconnection?: boolean;
  reconnectionDelay?: number;
  reconnectionDelayMax?: number;
  reconnectionAttempts?: number;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
  send: (event: string, data: any) => void;
  on: (event: string, callback: (data: any) => void) => void;
  off: (event: string, callback?: (data: any) => void) => void;
  disconnect: () => void;
  reconnect: () => void;
}

/**
 * Custom hook for WebSocket connection management
 * Uses Socket.IO for enhanced reliability and fallback mechanisms
 */
export function useWebSocket(options: UseWebSocketOptions): UseWebSocketReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const socketRef = useRef<Socket | null>(null);

  const {
    url,
    autoConnect = true,
    reconnection = true,
    reconnectionDelay = 1000,
    reconnectionDelayMax = 5000,
    reconnectionAttempts = 10,
  } = options;

  // Initialize socket connection
  useEffect(() => {
    if (!autoConnect || socketRef.current?.connected) {
      return;
    }

    setIsConnecting(true);
    const socket = io(url, {
      reconnection,
      reconnectionDelay,
      reconnectionDelayMax,
      reconnectionAttempts,
      transports: ['websocket', 'polling'],
    });

    socket.on('connect', () => {
      console.log('[useWebSocket] Connected');
      setIsConnected(true);
      setIsConnecting(false);
      setError(null);
    });

    socket.on('disconnect', () => {
      console.log('[useWebSocket] Disconnected');
      setIsConnected(false);
    });

    socket.on('connect_error', (err) => {
      console.error('[useWebSocket] Connection error:', err);
      setError(err.message || 'Connection error');
    });

    socket.on('error', (err) => {
      console.error('[useWebSocket] Socket error:', err);
      setError(typeof err === 'string' ? err : JSON.stringify(err));
    });

    socketRef.current = socket;

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, [url, autoConnect, reconnection, reconnectionDelay, reconnectionDelayMax, reconnectionAttempts]);

  const send = useCallback((event: string, data: any) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit(event, data);
    } else {
      console.warn('[useWebSocket] Socket not connected, cannot send:', event);
    }
  }, []);

  const on = useCallback((event: string, callback: (data: any) => void) => {
    if (socketRef.current) {
      socketRef.current.on(event, callback);
    }
  }, []);

  const off = useCallback((event: string, callback?: (data: any) => void) => {
    if (socketRef.current) {
      if (callback) {
        socketRef.current.off(event, callback);
      } else {
        socketRef.current.off(event);
      }
    }
  }, []);

  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.disconnect();
      setIsConnected(false);
    }
  }, []);

  const reconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.connect();
    }
  }, []);

  return {
    isConnected,
    isConnecting,
    error,
    send,
    on,
    off,
    disconnect,
    reconnect,
  };
}

/**
 * Higher-level hook for listening to specific events with cleanup
 */
export function useWebSocketEvent(
  socket: ReturnType<typeof useWebSocket>,
  event: string,
  callback: (data: any) => void,
  enabled = true
) {
  useEffect(() => {
    if (!enabled) return;

    socket.on(event, callback);
    return () => {
      socket.off(event, callback);
    };
  }, [socket, event, callback, enabled]);
}
