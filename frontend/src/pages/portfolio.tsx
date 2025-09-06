import React, { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import { fetchPortfolio } from '../store/portfolioSlice';
import { Header } from '../components/ui/Header';
import { Sidebar } from '../components/ui/Sidebar';

const PortfolioPage: React.FC = () => {
  const dispatch = useAppDispatch();
  const { totalValue, cash, equity, dayPnl, positions, isLoading } = useAppSelector(
    (state) => state.portfolio
  );

  useEffect(() => {
    dispatch(fetchPortfolio());
  }, [dispatch]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="flex h-screen">
          <Sidebar />
          <div className="flex-1 flex flex-col overflow-hidden">
            <Header />
            <main className="flex-1 overflow-auto">
              <div className="flex items-center justify-center h-full">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span className="ml-2">Loading portfolio...</span>
              </div>
            </main>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="flex h-screen">
        <Sidebar />
        
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header />
          
          <main className="flex-1 overflow-auto p-6">
            {/* Portfolio Summary */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
              <div className="card">
                <div className="card-body">
                  <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Total Value
                  </h3>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    ₹{totalValue.toLocaleString()}
                  </p>
                </div>
              </div>
              
              <div className="card">
                <div className="card-body">
                  <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Cash Balance
                  </h3>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    ₹{cash.toLocaleString()}
                  </p>
                </div>
              </div>
              
              <div className="card">
                <div className="card-body">
                  <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Equity Value
                  </h3>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    ₹{equity.toLocaleString()}
                  </p>
                </div>
              </div>
              
              <div className="card">
                <div className="card-body">
                  <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Day P&L
                  </h3>
                  <p className={`text-2xl font-bold ${
                    dayPnl >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {dayPnl >= 0 ? '+' : ''}₹{dayPnl.toLocaleString()}
                  </p>
                </div>
              </div>
            </div>

            {/* Positions Table */}
            <div className="card">
              <div className="card-header">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Current Positions
                </h2>
              </div>
              <div className="card-body">
                <div className="overflow-x-auto" data-testid="positions-table">
                  <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                    <thead className="bg-gray-50 dark:bg-gray-800">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                          Symbol
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                          Quantity
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                          Avg Price
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                          Current Price
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                          P&L
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                          P&L %
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                      {positions.map((position) => (
                        <tr key={position.id}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                            {position.symbol}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                            {position.quantity}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                            ₹{position.averagePrice.toFixed(2)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                            ₹{position.currentPrice.toFixed(2)}
                          </td>
                          <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${
                            position.pnl >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {position.pnl >= 0 ? '+' : ''}₹{position.pnl.toFixed(2)}
                          </td>
                          <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${
                            position.pnlPercent >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {position.pnlPercent >= 0 ? '+' : ''}{position.pnlPercent.toFixed(2)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                
                {positions.length === 0 && (
                  <div className="text-center py-8">
                    <p className="text-gray-500 dark:text-gray-400">No positions found</p>
                  </div>
                )}
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
};

export default PortfolioPage;
