import React from 'react';
import clsx from 'clsx';

interface Level {
  price: number;
  quantity: number;
  orders?: number;
  total?: number;
}

interface OrderBookLevelProps {
  level: Level;
  type: 'bid' | 'ask';
  maxQuantity: number;
  showHeatmap?: boolean;
}

export const OrderBookLevel: React.FC<OrderBookLevelProps> = ({ 
  level, 
  type, 
  maxQuantity,
  showHeatmap = true 
}) => {
  const percentage = maxQuantity > 0 ? (level.quantity / maxQuantity) * 100 : 0;
  
  return (
    <div 
      className={clsx(
        'orderbook-level relative rounded px-2 py-1 transition-colors duration-200 hover:bg-opacity-20',
        type === 'bid' 
          ? 'hover:bg-green-100 dark:hover:bg-green-900' 
          : 'hover:bg-red-100 dark:hover:bg-red-900'
      )}
    >
      {/* Background bar for quantity visualization */}
      {showHeatmap && (
        <div
          className={clsx(
            'absolute inset-0 rounded opacity-20',
            type === 'bid' ? 'bg-green-500' : 'bg-red-500'
          )}
          style={{ 
            width: `${percentage}%`,
            right: type === 'bid' ? 0 : 'auto',
            left: type === 'ask' ? 0 : 'auto'
          }}
        />
      )}
      
      {/* Level Data */}
      <div className="relative grid grid-cols-3 gap-4 text-sm font-mono">
        <div className={clsx(
          'text-right font-medium',
          type === 'bid' 
            ? 'text-green-600 dark:text-green-400' 
            : 'text-red-600 dark:text-red-400'
        )}>
          {level.price.toFixed(2)}
        </div>
        
        <div className="text-center text-gray-900 dark:text-white">
          {level.quantity.toLocaleString()}
        </div>
        
        <div className="text-left text-gray-600 dark:text-gray-400">
          {(level.total || level.quantity).toLocaleString()}
          {level.orders && (
            <span className="text-xs ml-1">({level.orders})</span>
          )}
        </div>
      </div>
    </div>
  );
};
