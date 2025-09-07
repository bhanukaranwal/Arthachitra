import React, { useState } from 'react';
import { OrderEntry } from './OrderEntry';
import { PositionTracker } from './PositionTracker';
import clsx from 'clsx';

interface Position {
  id: string;
  symbol: string;
  quantity: number;
  averagePrice: number;
  currentPrice: number;
  pnl: number;
  pnlPercent: number;
  unrealizedPnl: number;
  marketValue: number;
}

interface TradingPanelProps {
  symbol: string;
  currentPrice?: number;
  positions: Position[];
  onPlaceOrder: (order: {
    symbol: string;
    side: 'BUY' | 'SELL';
    orderType: string;
    quantity: number;
    price?: number;
    stopPrice?: number;
  }) => void;
  className?: string;
}

export const TradingPanel: React.FC<TradingPanelProps> = ({
  symbol,
  currentPrice,
  positions,
  onPlaceOrder,
  className
}) => {
  const [activeTab, setActiveTab] = useState<'order' | 'positions'>('order');

  return (
    <div className={clsx('trading-panel', className)}>
      {/* Tab Navigation */}
      <div className="mb-4">
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('order')}
              className={clsx(
                'py-2 px-1 border-b-2 font-medium text-sm transition-colors',
                activeTab === 'order'
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300'
              )}
            >
              Place Order
            </button>
            <button
              onClick={() => setActiveTab('positions')}
              className={clsx(
                'py-2 px-1 border-b-2 font-medium text-sm transition-colors',
                activeTab === 'positions'
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300'
              )}
            >
              Positions ({positions.length})
            </button>
          </nav>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'order' && (
        <OrderEntry
          symbol={symbol}
          currentPrice={currentPrice}
          onSubmit={onPlaceOrder}
        />
      )}

      {activeTab === 'positions' && (
        <PositionTracker positions={positions} />
      )}
    </div>
  );
};
