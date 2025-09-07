import React, { useMemo } from 'react';
import { useOrderBook } from '../../hooks/useOrderBook';
import { OrderBookLevel } from './OrderBookLevel';
import { Heatmap } from './Heatmap';
import clsx from 'clsx';

interface Level {
  price: number;
  quantity: number;
  orders?: number;
  total?: number;
}

interface OrderBookProps {
  symbol: string;
  depth?: number;
  showHeatmap?: boolean;
  className?: string;
}

export const OrderBook: React.FC<OrderBookProps> = ({ 
  symbol, 
  depth = 10,
  showHeatmap = true,
  className 
}) => {
  const { bids, asks, spread, loading, error } = useOrderBook(symbol, depth);

  const maxQuantity = useMemo(() => {
    if (!bids.length && !asks.length) return 0;
    return Math.max(
      ...bids.map(level => level.quantity),
      ...asks.map(level => level.quantity)
    );
  }, [bids, asks]);

  if (loading) {
    return (
      <div className={clsx('orderbook loading', className)}>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600 dark:text-gray-400">Loading Order Book...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={clsx('orderbook error', className)}>
        <div className="text-center py-8 text-red-600 dark:text-red-400">
          Error loading order book: {error}
        </div>
      </div>
    );
  }

  return (
    <div className={clsx('orderbook bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700', className)}>
      {/* Header */}
      <div className="orderbook-header p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Order Book - {symbol}
          </h3>
          <div className="text-sm text-gray-600 dark:text-gray-400">
            Spread: <span className="font-mono text-orange-600">{spread?.toFixed(2)}</span>
          </div>
        </div>
        
        {/* Column Headers */}
        <div className="grid grid-cols-3 gap-4 mt-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
          <div className="text-right">Price</div>
          <div className="text-center">Size</div>
          <div className="text-left">Total</div>
        </div>
      </div>

      <div className="orderbook-content p-4">
        {/* Asks (Sell Orders) */}
        <div className="orderbook-asks mb-4">
          <div className="space-y-1">
            {asks.slice().reverse().map((level) => (
              <OrderBookLevel
                key={level.price}
                level={level}
                type="ask"
                maxQuantity={maxQuantity}
                showHeatmap={showHeatmap}
              />
            ))}
          </div>
        </div>

        {/* Spread Indicator */}
        <div className="spread-indicator bg-gray-100 dark:bg-gray-700 rounded px-3 py-2 my-2">
          <div className="text-center text-sm font-medium text-gray-700 dark:text-gray-300">
            Spread: {spread?.toFixed(2)} ({((spread || 0) / (bids[0]?.price || 1) * 100).toFixed(3)}%)
          </div>
        </div>

        {/* Bids (Buy Orders) */}
        <div className="orderbook-bids mt-4">
          <div className="space-y-1">
            {bids.map((level) => (
              <OrderBookLevel
                key={level.price}
                level={level}
                type="bid"
                maxQuantity={maxQuantity}
                showHeatmap={showHeatmap}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Heatmap Visualization */}
      {showHeatmap && (
        <div className="orderbook-heatmap border-t border-gray-200 dark:border-gray-700 p-4">
          <Heatmap bids={bids} asks={asks} />
        </div>
      )}
    </div>
  );
};
