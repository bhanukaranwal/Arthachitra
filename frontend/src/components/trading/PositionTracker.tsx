import React from 'react';
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

interface PositionTrackerProps {
  positions: Position[];
  className?: string;
}

export const PositionTracker: React.FC<PositionTrackerProps> = ({ 
  positions, 
  className 
}) => {
  const totalPnl = positions.reduce((sum, pos) => sum + pos.pnl, 0);
  const totalMarketValue = positions.reduce((sum, pos) => sum + pos.marketValue, 0);

  if (!positions.length) {
    return (
      <div className={clsx('position-tracker bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700', className)}>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Positions
        </h3>
        <div className="text-center text-gray-500 dark:text-gray-400 py-8">
          No active positions
        </div>
      </div>
    );
  }

  return (
    <div className={clsx('position-tracker bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700', className)}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Positions ({positions.length})
          </h3>
          <div className="text-right">
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Total Value: ₹{totalMarketValue.toLocaleString()}
            </div>
            <div className={clsx(
              'text-lg font-semibold',
              totalPnl >= 0 ? 'text-green-600' : 'text-red-600'
            )}>
              {totalPnl >= 0 ? '+' : ''}₹{totalPnl.toFixed(2)}
            </div>
          </div>
        </div>
      </div>

      {/* Positions Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Symbol
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Qty
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Avg Price
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Current Price
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                P&L
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                P&L %
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Market Value
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {positions.map((position) => (
              <tr 
                key={position.id}
                className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <td className="px-4 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="text-sm font-medium text-gray-900 dark:text-white">
                      {position.symbol}
                    </div>
                  </div>
                </td>
                
                <td className="px-4 py-4 whitespace-nowrap text-right">
                  <div className="text-sm text-gray-900 dark:text-white">
                    {position.quantity.toLocaleString()}
                  </div>
                </td>
                
                <td className="px-4 py-4 whitespace-nowrap text-right">
                  <div className="text-sm font-mono text-gray-900 dark:text-white">
                    ₹{position.averagePrice.toFixed(2)}
                  </div>
                </td>
                
                <td className="px-4 py-4 whitespace-nowrap text-right">
                  <div className="text-sm font-mono text-gray-900 dark:text-white">
                    ₹{position.currentPrice.toFixed(2)}
                  </div>
                </td>
                
                <td className="px-4 py-4 whitespace-nowrap text-right">
                  <div className={clsx(
                    'text-sm font-medium',
                    position.pnl >= 0 ? 'text-green-600' : 'text-red-600'
                  )}>
                    {position.pnl >= 0 ? '+' : ''}₹{position.pnl.toFixed(2)}
                  </div>
                </td>
                
                <td className="px-4 py-4 whitespace-nowrap text-right">
                  <div className={clsx(
                    'text-sm font-medium',
                    position.pnlPercent >= 0 ? 'text-green-600' : 'text-red-600'
                  )}>
                    {position.pnlPercent >= 0 ? '+' : ''}{position.pnlPercent.toFixed(2)}%
                  </div>
                </td>
                
                <td className="px-4 py-4 whitespace-nowrap text-right">
                  <div className="text-sm font-mono text-gray-900 dark:text-white">
                    ₹{position.marketValue.toLocaleString()}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
