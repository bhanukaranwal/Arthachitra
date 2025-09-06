import { useState, useEffect, useCallback } from 'react';
import { useWebSocket } from './useWebSocket';
import { api } from '../utils/api';

interface MarketDataHook {
  quote: any;
  orderBook: any;
  isConnected: boolean;
  error: string | null;
  subscribe: (symbol: string) => void;
  unsubscribe: () => void;
}

export const useMarketData = (initialSymbol?: string): MarketDataHook => {
  const [quote, setQuote] = useState<any>(null);
  const [orderBook, setOrderBook] = useState<any>(null);
  const [currentSymbol, setCurrentSymbol] = useState<string | null>(initialSymbol || null);
  const [error, setError] = useState<string | null>(null);

  const { data, isConnected, send } = useWebSocket(
    currentSymbol ? `ws://localhost:8000/ws/market/${currentSymbol}` : '',
    {
      onConnect: () => setError(null),
      onError: () => setError('WebSocket connection failed'),
    }
  );

  useEffect(() => {
    if (data) {
      try {
        if (data.type === 'quote') {
          setQuote(data.data);
        } else if (data.type === 'orderbook') {
          setOrderBook(data.data);
        }
      } catch (err) {
        setError('Failed to parse market data');
      }
    }
  }, [data]);

  const subscribe = useCallback(async (symbol: string) => {
    setCurrentSymbol(symbol);
    setError(null);
    
    try {
      // Get initial data
      const [quoteResponse, orderBookResponse] = await Promise.all([
        api.get(`/market/quote/${symbol}`),
        api.get(`/market/orderbook/${symbol}`)
      ]);
      
      setQuote(quoteResponse.data);
      setOrderBook(orderBookResponse.data);
    } catch (err) {
      setError('Failed to fetch initial market data');
    }
  }, []);

  const unsubscribe = useCallback(() => {
    setCurrentSymbol(null);
    setQuote(null);
    setOrderBook(null);
    setError(null);
  }, []);

  return {
    quote,
    orderBook,
    isConnected,
    error,
    subscribe,
    unsubscribe,
  };
};
