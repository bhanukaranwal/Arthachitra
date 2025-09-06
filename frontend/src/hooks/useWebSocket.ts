import { useState, useEffect, useRef, useCallback } from 'react';

interface WebSocketOptions {
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
}

interface UseWebSocketReturn {
  data: any;
  isConnected: boolean;
  error: string | null;
  send: (data: any) => void;
  reconnect: () => void;
}

export const useWebSocket = (
  url: string,
  options: WebSocketOptions = {}
): UseWebSocketReturn => {
  const [data, setData] = useState<any>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const ws = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  const reconnectTimer = useRef<NodeJS.Timeout | null>(null);
  
  const {
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
    onConnect,
    onDisconnect,
    onError
  } = options;

  const connect = useCallback(() => {
    try {
      ws.current = new WebSocket(url);
      
      ws.current.onopen = () => {
        console.log(`WebSocket connected to ${url}`);
        setIsConnected(true);
        setError(null);
        reconnectAttempts.current = 0;
        onConnect?.();
      };
      
      ws.current.onmessage = (event) => {
        try {
          const parsedData = JSON.parse(event.data);
          setData(parsedData);
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
          setData(event.data);
        }
      };
      
      ws.current.onclose = (event) => {
        console.log(`WebSocket disconnected from ${url}`, event.code, event.reason);
        setIsConnected(false);
        onDisconnect?.();
        
        // Attempt to reconnect if not a manual close
        if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
          reconnectTimer.current = setTimeout(() => {
            reconnectAttempts.current++;
            console.log(`Reconnecting... Attempt ${reconnectAttempts.current}`);
            connect();
          }, reconnectInterval);
        }
      };
      
      ws.current.onerror = (event) => {
        console.error(`WebSocket error on ${url}:`, event);
        setError('WebSocket connection error');
        onError?.(event);
      };
      
    } catch (err) {
      console.error('Failed to create WebSocket connection:', err);
      setError('Failed to create WebSocket connection');
    }
  }, [url, reconnectInterval, maxReconnectAttempts, onConnect, onDisconnect, onError]);

  const disconnect = useCallback(() => {
    if (reconnectTimer.current) {
      clearTimeout(reconnectTimer.current);
      reconnectTimer.current = null;
    }
    
    if (ws.current) {
      ws.current.close(1000, 'Manual disconnect');
      ws.current = null;
    }
  }, []);

  const send = useCallback((data: any) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      const message = typeof data === 'string' ? data : JSON.stringify(data);
      ws.current.send(message);
    } else {
      console.warn('WebSocket is not connected. Cannot send message:', data);
    }
  }, []);

  const reconnect = useCallback(() => {
    disconnect();
    setTimeout(connect, 100);
  }, [connect, disconnect]);

  useEffect(() => {
    connect();
    
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    data,
    isConnected,
    error,
    send,
    reconnect
  };
};
