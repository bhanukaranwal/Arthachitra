import React, { useState, useCallback } from 'react';
import clsx from 'clsx';

interface OrderEntryProps {
  symbol: string;
  currentPrice?: number;
  onSubmit: (order: {
    symbol: string;
    side: 'BUY' | 'SELL';
    orderType: string;
    quantity: number;
    price?: number;
    stopPrice?: number;
  }) => void;
  className?: string;
}

export const OrderEntry: React.FC<OrderEntryProps> = ({ 
  symbol, 
  currentPrice = 0, 
  onSubmit, 
  className 
}) => {
  const [side, setSide] = useState<'BUY' | 'SELL'>('BUY');
  const [orderType, setOrderType] = useState<'MARKET' | 'LIMIT' | 'STOP' | 'STOP_LIMIT'>('MARKET');
  const [quantity, setQuantity] = useState<number>(1);
  const [price, setPrice] = useState<number>(currentPrice);
  const [stopPrice, setStopPrice] = useState<number>(currentPrice);

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    
    if (quantity <= 0) {
      alert('Please enter a valid quantity');
      return;
    }
    
    if ((orderType === 'LIMIT' || orderType === 'STOP_LIMIT') && price <= 0) {
      alert('Please enter a valid price');
      return;
    }
    
    if ((orderType === 'STOP' || orderType === 'STOP_LIMIT') && stopPrice <= 0) {
      alert('Please enter a valid stop price');
      return;
    }

    onSubmit({
      symbol,
      side,
      orderType,
      quantity,
      price: (orderType === 'LIMIT' || orderType === 'STOP_LIMIT') ? price : undefined,
      stopPrice: (orderType === 'STOP' || orderType === 'STOP_LIMIT') ? stopPrice : undefined,
    });
  }, [symbol, side, orderType, quantity, price, stopPrice, onSubmit]);

  const estimatedValue = quantity * (price || currentPrice);

  return (
    <div className={clsx('order-entry bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700', className)}>
      <div className="order-entry-header mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Place Order - {symbol}
        </h3>
        {currentPrice > 0 && (
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Current Price: ₹{currentPrice.toFixed(2)}
          </p>
        )}
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Buy/Sell Toggle */}
        <div className="grid grid-cols-2 gap-2">
          <button
            type="button"
            onClick={() => setSide('BUY')}
            className={clsx(
              'py-3 px-4 rounded font-medium transition-colors',
              side === 'BUY'
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            )}
          >
            BUY
          </button>
          <button
            type="button"
            onClick={() => setSide('SELL')}
            className={clsx(
              'py-3 px-4 rounded font-medium transition-colors',
              side === 'SELL'
                ? 'bg-red-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            )}
          >
            SELL
          </button>
        </div>

        {/* Order Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Order Type
          </label>
          <select
            value={orderType}
            onChange={(e) => setOrderType(e.target.value as any)}
            className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="MARKET">Market Order</option>
            <option value="LIMIT">Limit Order</option>
            <option value="STOP">Stop Order</option>
            <option value="STOP_LIMIT">Stop Limit Order</option>
          </select>
        </div>

        {/* Quantity */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Quantity
          </label>
          <input
            type="number"
            min="1"
            value={quantity}
            onChange={(e) => setQuantity(parseInt(e.target.value) || 0)}
            className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Enter quantity"
          />
        </div>

        {/* Price (for limit orders) */}
        {(orderType === 'LIMIT' || orderType === 'STOP_LIMIT') && (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Price (₹)
            </label>
            <input
              type="number"
              step="0.05"
              min="0"
              value={price}
              onChange={(e) => setPrice(parseFloat(e.target.value) || 0)}
              className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter price"
            />
          </div>
        )}

        {/* Stop Price (for stop orders) */}
        {(orderType === 'STOP' || orderType === 'STOP_LIMIT') && (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Stop Price (₹)
            </label>
            <input
              type="number"
              step="0.05"
              min="0"
              value={stopPrice}
              onChange={(e) => setStopPrice(parseFloat(e.target.value) || 0)}
              className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter stop price"
            />
          </div>
        )}

        {/* Order Summary */}
        <div className="bg-gray-50 dark:bg-gray-700 rounded p-3">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600 dark:text-gray-400">Estimated Value:</span>
            <span className="font-medium text-gray-900 dark:text-white">
              ₹{estimatedValue.toLocaleString()}
            </span>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          className={clsx(
            'w-full py-3 px-4 rounded font-medium text-white transition-colors',
            side === 'BUY'
              ? 'bg-green-600 hover:bg-green-700'
              : 'bg-red-600 hover:bg-red-700'
          )}
        >
          {side} {quantity} {symbol}
        </button>
      </form>
    </div>
  );
};
