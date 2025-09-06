import React, { useEffect, useRef } from 'react';
import { useWebSocket } from '../../hooks/useWebSocket';
import { useTheme } from '../../hooks/useTheme';

interface HeatmapData {
  price: number;
  volume: number;
  timestamp: number;
  side: 'buy' | 'sell';
}

interface HeatmapChartProps {
  symbol: string;
  height?: number;
}

export const HeatmapChart: React.FC<HeatmapChartProps> = ({
  symbol,
  height = 600
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const { theme } = useTheme();
  const { data } = useWebSocket(`ws://localhost:8000/ws/orderbook/${symbol}`);
  
  const [heatmapData, setHeatmapData] = React.useState<HeatmapData[]>([]);

  useEffect(() => {
    if (data && data.type === 'orderbook') {
      const newData: HeatmapData[] = [];
      
      // Process bid side
      data.bids.forEach((bid: any) => {
        newData.push({
          price: bid.price,
          volume: bid.size,
          timestamp: Date.now(),
          side: 'buy'
        });
      });
      
      // Process ask side
      data.asks.forEach((ask: any) => {
        newData.push({
          price: ask.price,
          volume: ask.size,
          timestamp: Date.now(),
          side: 'sell'
        });
      });
      
      setHeatmapData(prev => [...prev, ...newData].slice(-1000)); // Keep last 1000 points
    }
  }, [data]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      const maxVolume = Math.max(...heatmapData.map(d => d.volume));
      const minPrice = Math.min(...heatmapData.map(d => d.price));
      const maxPrice = Math.max(...heatmapData.map(d => d.price));
      
      heatmapData.forEach(point => {
        const x = ((point.timestamp - Date.now() + 60000) / 60000) * canvas.width;
        const y = ((maxPrice - point.price) / (maxPrice - minPrice)) * canvas.height;
        const intensity = point.volume / maxVolume;
        
        const alpha = Math.min(intensity, 1);
        const color = point.side === 'buy' 
          ? `rgba(34, 197, 94, ${alpha})` 
          : `rgba(239, 68, 68, ${alpha})`;
        
        ctx.fillStyle = color;
        ctx.fillRect(x - 2, y - 2, 4, 4);
      });
      
      animationRef.current = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [heatmapData]);

  return (
    <div className="relative">
      <div className="absolute top-2 left-2 bg-black bg-opacity-50 text-white p-2 rounded z-10">
        <h3 className="text-lg font-semibold">Order Flow Heatmap - {symbol}</h3>
        <div className="flex items-center space-x-4 mt-1">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-green-500 rounded"></div>
            <span>Buy Orders</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-red-500 rounded"></div>
            <span>Sell Orders</span>
          </div>
        </div>
      </div>
      <canvas
        ref={canvasRef}
        width={800}
        height={height}
        className="w-full border border-gray-300 dark:border-gray-600"
      />
    </div>
  );
};
