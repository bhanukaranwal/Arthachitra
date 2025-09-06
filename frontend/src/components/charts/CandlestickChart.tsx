import React, { useEffect, useRef, useState } from 'react';
import { createChart, IChartApi, ISeriesApi } from 'lightweight-charts';
import { useWebSocket } from '../../hooks/useWebSocket';
import { useTheme } from '../../hooks/useTheme';

interface CandlestickChartProps {
  symbol: string;
  timeframe: string;
  height?: number;
}

export const CandlestickChart: React.FC<CandlestickChartProps> = ({
  symbol,
  timeframe,
  height = 400
}) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null);
  
  const { theme } = useTheme();
  const { data, isConnected } = useWebSocket(`ws://localhost:8000/ws/market/${symbol}/${timeframe}`);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height,
      layout: {
        background: { color: theme.chart.background },
        textColor: theme.chart.textColor,
      },
      grid: {
        vertLines: { color: theme.chart.gridColor },
        horzLines: { color: theme.chart.gridColor },
      },
      crosshair: {
        mode: 1,
      },
      rightPriceScale: {
        borderColor: theme.chart.borderColor,
      },
      timeScale: {
        borderColor: theme.chart.borderColor,
        timeVisible: true,
        secondsVisible: false,
      },
    });

    const candlestickSeries = chart.addCandlestickSeries({
      upColor: theme.chart.upColor,
      downColor: theme.chart.downColor,
      borderUpColor: theme.chart.upColor,
      borderDownColor: theme.chart.downColor,
      wickUpColor: theme.chart.upColor,
      wickDownColor: theme.chart.downColor,
    });

    const volumeSeries = chart.addHistogramSeries({
      color: theme.chart.volumeColor,
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: '',
      scaleMargins: {
        top: 0.8,
        bottom: 0,
      },
    });

    chartRef.current = chart;
    candlestickSeriesRef.current = candlestickSeries;
    volumeSeriesRef.current = volumeSeries;

    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [theme, height]);

  useEffect(() => {
    if (data && candlestickSeriesRef.current && volumeSeriesRef.current) {
      if (data.type === 'historical') {
        candlestickSeriesRef.current.setData(data.candles);
        volumeSeriesRef.current.setData(data.volume);
      } else if (data.type === 'tick') {
        candlestickSeriesRef.current.update(data.candle);
        volumeSeriesRef.current.update(data.volume);
      }
    }
  }, [data]);

  return (
    <div className="relative">
      <div className="flex items-center justify-between p-2 bg-gray-100 dark:bg-gray-800">
        <div className="flex items-center space-x-4">
          <h3 className="text-lg font-semibold">{symbol}</h3>
          <span className={`px-2 py-1 rounded text-sm ${isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
            {isConnected ? 'Live' : 'Disconnected'}
          </span>
        </div>
        <div className="flex items-center space-x-2">
          <select className="px-2 py-1 border rounded">
            <option value="1m">1M</option>
            <option value="5m">5M</option>
            <option value="15m">15M</option>
            <option value="1h">1H</option>
            <option value="1d">1D</option>
          </select>
        </div>
      </div>
      <div ref={chartContainerRef} className="w-full" />
    </div>
  );
};
