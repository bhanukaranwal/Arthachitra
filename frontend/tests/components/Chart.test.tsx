import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { CandlestickChart } from '../../src/components/charts/CandlestickChart';
import chartSlice from '../../src/store/chartSlice';

const mockStore = configureStore({
  reducer: {
    chart: chartSlice,
  },
});

const mockData = [
  { time: '2024-01-01', open: 100, high: 110, low: 95, close: 105, volume: 1000 },
  { time: '2024-01-02', open: 105, high: 115, low: 100, close: 108, volume: 1200 },
];

describe('CandlestickChart', () => {
  test('renders chart container', () => {
    render(
      <Provider store={mockStore}>
        <CandlestickChart symbol="NIFTY" timeframe="1d" />
      </Provider>
    );
    
    expect(screen.getByTestId('chart-container')).toBeInTheDocument();
  });

  test('displays loading state', () => {
    render(
      <Provider store={mockStore}>
        <CandlestickChart symbol="NIFTY" timeframe="1d" />
      </Provider>
    );
    
    // Initially should show loading
    expect(screen.getByTestId('chart-loading')).toBeInTheDocument();
  });

  test('handles symbol change', () => {
    const { rerender } = render(
      <Provider store={mockStore}>
        <CandlestickChart symbol="NIFTY" timeframe="1d" />
      </Provider>
    );

    rerender(
      <Provider store={mockStore}>
        <CandlestickChart symbol="RELIANCE" timeframe="1d" />
      </Provider>
    );

    // Should trigger new data fetch for RELIANCE
    expect(screen.getByTestId('chart-container')).toBeInTheDocument();
  });
});
