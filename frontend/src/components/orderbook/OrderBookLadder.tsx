import React, { useEffect, useState, useRef } from 'react';
import { useWebSocket } from '../../hooks/useWebSocket';
import { useTheme } from '../../hooks/useTheme';

interface OrderBookLevel {
  price: number;
  size: number;
  orders: number;
}

interface OrderBookData {
  bids: OrderBookLevel[];
  asks: OrderBookLevel[];
  spread: number;
  spreadPercent: number;
}

interface OrderBookLadderProps {
  symbol: string;
  precision?: number;
  levels?: number;
  onPriceClick?: (price: number, side: 'buy' | 'sell') => void;
}

export const OrderBookLadder: React.FC<OrderBookLadderProps> = ({
  symbol,
  precision = 2,
  levels = 20,
  onPriceClick
}) => {
  const { theme } = useTheme();
  const { data } = useWebSocket(`ws://localhost:8000/ws/orderbook/${symbol}`);
  const [orderBook, setOrderBook] = useState<OrderBookData>({
    bids: [],
    asks: [],
    spread: 0,
    spreadPercent: 0
  });
  
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (data && data.type === 'orderbook') {
      const bids = data.bids.slice(0, levels).sort((a: any, b: any) => b.price - a.price);
      const asks = data.asks.slice(0, levels).sort((a: any, b: any) => a.price - b.price);
      
      const bestBid = bids[0]?.price || 0;
      const bestAsk = asks[0]?.price || 0;
      const spread = bestAsk - bestBid;
      const spreadPercent = bestBid > 0 ? (spread / bestBid) * 100 : 0;
      
      setOrderBook({
        bids,
        asks,
        spread,
        spreadPercent
      });
    }
  }, [data, levels]);

  const formatPrice = (price: number) => price.toFixed(precision);
  const formatSize = (size: number) => {
    if (size >= 1000000) {
      return `${(size / 1000000).toFixed(1)}M`;
    } else if (size >= 1000) {
      return `${(size / 1000).toFixed(1)}K`;
    }
    return size.toString();
  };

  const getVolumeBarWidth = (size: number, maxSize: number) => {
    return Math.max((size / maxSize) * 100, 2);
  };

  const maxBidSize = Math.max(...orderBook.bids.map(b => b.size), 1);
  const maxAskSize = Math.max(...orderBook.asks.map(a => a.size), 1);
  const maxSize = Math.max(maxBidSize, maxAskSize);

  return (
    <div ref={containerRef} className="flex flex-col h-full bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg">
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Order Book - {symbol}
        </h3>
        <div className="text-sm text-gray-600 dark:text-gray-400">
          Spread: {formatPrice(orderBook.spread)} ({orderBook.spreadPercent.toFixed(3)}%)
        </div>
      </div>

      {/* Column Headers */}
      <div className="flex text-xs font-semibold text-gray-600 dark:text-gray-400 p-2 border-b border-gray-200 dark:border-gray-700">
        <div className="flex-1 text-left">Size</div>
        <div className="flex-1 text-center">Price</div>
        <div className="flex-1 text-right">Size</div>
      </div>

      {/* Order Book Levels */}
      <div className="flex-1 overflow-y-auto">
        {/* Asks (Sell Orders) */}
        <div className="flex flex-col-reverse">
          {orderBook.asks.map((ask, index) => (
            <div
              key={`ask-${ask.price}-${index}`}
              className="relative flex items-center h-6 hover:bg-red-50 dark:hover:bg-red-900/20 cursor-pointer"
              onClick={() => onPriceClick?.(ask.price, 'sell')}
            >
              {/* Volume Bar */}
              <div
                className="absolute right-0 h-full bg-red-100 dark:bg-red-900/30"
                style={{ width: `${getVolumeBarWidth(ask.size, maxSize)}%` }}
              />
              
              {/* Content */}
              <div className="relative flex w-full px-2 text-xs">
                <div className="flex-1 text-left text-gray-600 dark:text-gray-400">
                  {/* Empty space for asks */}
                </div>
                <div className="flex-1 text-center font-mono text-red-600 dark:text-red-400">
                  {formatPrice(ask.price)}
                </div>
                <div className="flex-1 text-right text-red-600 dark:text-red-400">
                  {formatSize(ask.size)}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Spread Indicator */}
        <div className="flex items-center justify-center h-8 bg-yellow-50 dark:bg-yellow-900/20 border-y border-yellow-200 dark:border-yellow-800">
          <span className="text-xs font-semibold text-yellow-800 dark:text-yellow-400">
            Spread: {formatPrice(orderBook.spread)}
          </span>
        </div>

        {/* Bids (Buy Orders) */}
        <div>
          {orderBook.bids.map((bid, index) => (
            <div
              key={`bid-${bid.price}-${index}`}
              className="relative flex items-center h-6 hover:bg-green-50 dark:hover:bg-green-900/20 cursor-pointer"
              onClick={() => onPriceClick?.(bid.price, 'buy')}
            >
              {/* Volume Bar */}
              <div
                className="absolute left-0 h-full bg-green-100 dark:bg-green-900/30"
                style={{ width: `${getVolumeBarWidth(bid.size, maxSize)}%` }}
              />
              
              {/* Content */}
              <div className="relative flex w-full px-2 text-xs">
                <div className="flex-1 text-left text-green-600 dark:text-green-400">
                  {formatSize(bid.size)}
                </div>
                <div className="flex-1 text-center font-mono text-green-600 dark:text-green-400">
                  {formatPrice(bid.price)}
                </div>
                <div className="flex-1 text-right text-gray-600 dark:text-gray-400">
                  {/* Empty space for bids */}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Market Info */}
      <div className="p-2 border-t border-gray-200 dark:border-gray-700 text-xs text-gray-600 dark:text-gray-400">
        <div className="flex justify-between">
          <span>Best Bid: {orderBook.bids[0] ? formatPrice(orderBook.bids[0].price) : 'N/A'}</span>
          <span>Best Ask: {orderBook.asks[0] ? formatPrice(orderBook.asks[0].price) : 'N/A'}</span>
        </div>
      </div>
    </div>
  );
};
