import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { jest } from '@jest/globals';
import { CandlestickChart } from '../../src/components/charts/CandlestickChart';
import { ThemeProvider } from '../../src/components/themes/ThemeProvider';

// Mock lightweight-charts
jest.mock('lightweight-charts', () => ({
  createChart: jest.fn(() => ({
    addCandlestickSeries: jest.fn(() => ({
      setData: jest.fn(),
      update: jest.fn(),
    })),
    addHistogramSeries: jest.fn(() => ({
      setData: jest.fn(),
      update: jest.fn(),
    })),
    applyOptions: jest.fn(),
    remove: jest.fn(),
  })),
}));

// Mock WebSocket hook
jest.mock('../../src/hooks/useWebSocket', () => ({
  useWebSocket: jest.fn(() => ({
    data: null,
    isConnected: false,
  })),
}));

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider>
      {component}
    </ThemeProvider>
  );
};

describe('CandlestickChart', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders chart container', () => {
    renderWithTheme(
      <CandlestickChart symbol="NIFTY" timeframe="1d" />
    );

    expect(screen.getByText('NIFTY')).toBeInTheDocument();
    expect(screen.getByText('Disconnected')).toBeInTheDocument();
  });

  test('displays connection status', () => {
    const { useWebSocket } = require('../../src/hooks/useWebSocket');
    useWebSocket.mockReturnValue({
      data: null,
      isConnected: true,
    });

    renderWithTheme(
      <CandlestickChart symbol="NIFTY" timeframe="1d" />
    );

    expect(screen.getByText('Live')).toBeInTheDocument();
  });

  test('handles historical data', async () => {
    const mockData = {
      type: 'historical',
      candles: [
        { time: '2024-01-01', open: 100, high: 105, low: 95, close: 102 },
        { time: '2024-01-02', open: 102, high: 108, low: 98, close: 106 },
      ],
      volume: [
        { time: '2024-01-01', value: 1000 },
        { time: '2024-01-02', value: 1500 },
      ],
    };

    const { useWebSocket } = require('../../src/hooks/useWebSocket');
    useWebSocket.mockReturnValue({
      data: mockData,
      isConnected: true,
    });

    const { createChart } = require('lightweight-charts');
    const mockChart = createChart();
    const mockCandlestickSeries = mockChart.addCandlestickSeries();
    const mockVolumeSeries = mockChart.addHistogramSeries();

    renderWithTheme(
      <CandlestickChart symbol="NIFTY" timeframe="1d" />
    );

    await waitFor(() => {
      expect(mockCandlestickSeries.setData).toHaveBeenCalledWith(mockData.candles);
      expect(mockVolumeSeries.setData).toHaveBeenCalledWith(mockData.volume);
    });
  });

  test('handles tick updates', async () => {
    const mockTickData = {
      type: 'tick',
      candle: { time: '2024-01-03', open: 106, high: 110, low: 104, close: 108 },
      volume: { time: '2024-01-03', value: 2000 },
    };

    const { useWebSocket } = require('../../src/hooks/useWebSocket');
    useWebSocket.mockReturnValue({
      data: mockTickData,
      isConnected: true,
    });

    const { createChart } = require('lightweight-charts');
    const mockChart = createChart();
    const mockCandlestickSeries = mockChart.addCandlestickSeries();
    const mockVolumeSeries = mockChart.addHistogramSeries();

    renderWithTheme(
      <CandlestickChart symbol="NIFTY" timeframe="1d" />
    );

    await waitFor(() => {
      expect(mockCandlestickSeries.update).toHaveBeenCalledWith(mockTickData.candle);
      expect(mockVolumeSeries.update).toHaveBeenCalledWith(mockTickData.volume);
    });
  });

  test('applies theme correctly', () => {
    const { createChart } = require('lightweight-charts');

    renderWithTheme(
      <CandlestickChart symbol="NIFTY" timeframe="1d" />
    );

    expect(createChart).toHaveBeenCalledWith(
      expect.any(Element),
      expect.objectContaining({
        layout: expect.objectContaining({
          background: expect.any(Object),
          textColor: expect.any(String),
        }),
        grid: expect.objectContaining({
          vertLines: expect.any(Object),
          horzLines: expect.any(Object),
        }),
      })
    );
  });

  test('cleans up on unmount', () => {
    const { createChart } = require('lightweight-charts');
    const mockChart = createChart();

    const { unmount } = renderWithTheme(
      <CandlestickChart symbol="NIFTY" timeframe="1d" />
    );

    unmount();

    expect(mockChart.remove).toHaveBeenCalled();
  });
});
