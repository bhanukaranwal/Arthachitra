import React, { useMemo } from 'react';
import clsx from 'clsx';

interface Level {
  price: number;
  quantity: number;
  orders?: number;
  total?: number;
}

interface HeatmapProps {
  bids: Level[];
  asks: Level[];
  height?: number;
}

export const Heatmap: React.FC<HeatmapProps> = ({ 
  bids, 
  asks, 
  height = 200 
}) => {
  const { maxQuantity, heatmapData } = useMemo(() => {
    const allLevels = [...bids, ...asks];
    const maxQty = Math.max(...allLevels.map(level => level.quantity));
    
    // Create heatmap visualization data
    const data = {
      bids: bids.map(level => ({
        ...level,
        intensity: (level.quantity / maxQty) * 100
      })),
      asks: asks.map(level => ({
        ...level,
        intensity: (level.quantity / maxQty) * 100
      }))
    };
    
    return { maxQuantity: maxQty, heatmapData: data };
  }, [bids, asks]);

  const getHeatmapColor = (intensity: number, type: 'bid' | 'ask') => {
    const opacity = Math.max(intensity / 100, 0.1);
    
    if (type === 'bid') {
      return `rgba(34, 197, 94, ${opacity})`; // Green for bids
    } else {
      return `rgba(239, 68, 68, ${opacity})`; // Red for asks
    }
  };

  return (
    <div className="heatmap">
      <div className="mb-2">
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Liquidity Heatmap
        </h4>
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Darker colors indicate higher volume concentration
        </p>
      </div>
      
      <div 
        className="heatmap-container flex rounded border border-gray-200 dark:border-gray-700 overflow-hidden"
        style={{ height: `${height}px` }}
      >
        {/* Bids Side */}
        <div className="heatmap-bids flex-1 flex flex-col-reverse justify-end">
          {heatmapData.bids.map((level, index) => (
            <div
              key={level.price}
              className={clsx(
                'heatmap-bar transition-all duration-200 hover:opacity-80 cursor-pointer',
                'border-r border-gray-200 dark:border-gray-600'
              )}
              style={{
                backgroundColor: getHeatmapColor(level.intensity, 'bid'),
                height: `${Math.max((level.intensity / 100) * height, 2)}px`,
                minHeight: '2px'
              }}
              title={`Price: ${level.price.toFixed(2)}, Quantity: ${level.quantity.toLocaleString()}`}
            />
          ))}
        </div>

        {/* Center Line */}
        <div className="w-px bg-gray-400 dark:bg-gray-500" />

        {/* Asks Side */}
        <div className="heatmap-asks flex-1 flex flex-col-reverse justify-end">
          {heatmapData.asks.slice().reverse().map((level, index) => (
            <div
              key={level.price}
              className={clsx(
                'heatmap-bar transition-all duration-200 hover:opacity-80 cursor-pointer',
                'border-l border-gray-200 dark:border-gray-600'
              )}
              style={{
                backgroundColor: getHeatmapColor(level.intensity, 'ask'),
                height: `${Math.max((level.intensity / 100) * height, 2)}px`,
                minHeight: '2px'
              }}
              title={`Price: ${level.price.toFixed(2)}, Quantity: ${level.quantity.toLocaleString()}`}
            />
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="heatmap-legend flex justify-between items-center mt-2 text-xs text-gray-500 dark:text-gray-400">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 rounded bg-green-500 opacity-50"></div>
          <span>Bids</span>
        </div>
        
        <div className="text-center">
          <div>Max Volume: {maxQuantity.toLocaleString()}</div>
        </div>
        
        <div className="flex items-center space-x-2">
          <span>Asks</span>
          <div className="w-3 h-3 rounded bg-red-500 opacity-50"></div>
        </div>
      </div>
    </div>
  );
};
