import React, { useEffect, useRef } from 'react';
import { createChart, IChartApi, ISeriesApi, HistogramData } from 'lightweight-charts';

interface VolumeChartProps {
  data: HistogramData[];
  height?: number;
}

export const VolumeChart: React.FC<VolumeChartProps> = ({ data, height = 200 }) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height,
      layout: {
        background: { type: 'solid', color: 'var(--chart-background)' },
        textColor: 'var(--chart-textColor)',
      },
      grid: {
        vertLines: { color: 'var(--chart-gridColor)' },
        horzLines: { color: 'var(--chart-gridColor)' },
      },
      timeScale: {
        borderColor: 'var(--chart-borderColor)',
      },
      rightPriceScale: {
        borderColor: 'var(--chart-borderColor)',
      },
    });

    // Add volume series
    const volumeSeries = chart.addHistogramSeries({
      color: 'var(--chart-volumeColor)',
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: 'volume',
    });

    chartRef.current = chart;
    volumeSeriesRef.current = volumeSeries;

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [height]);

  useEffect(() => {
    if (volumeSeriesRef.current && data.length > 0) {
      volumeSeriesRef.current.setData(data);
    }
  }, [data]);

  return <div ref={chartContainerRef} className="volume-chart" />;
};
