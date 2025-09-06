import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface ChartState {
  currentSymbol: string;
  timeframe: string;
  chartType: 'candlestick' | 'line' | 'heikinashi' | 'renko';
  indicators: string[];
  isLoading: boolean;
  data: any[];
  volume: any[];
  selectedRange: { start: string; end: string } | null;
}

const initialState: ChartState = {
  currentSymbol: 'NIFTY',
  timeframe: '1d',
  chartType: 'candlestick',
  indicators: [],
  isLoading: false,
  data: [],
  volume: [],
  selectedRange: null,
};

const chartSlice = createSlice({
  name: 'chart',
  initialState,
  reducers: {
    setSymbol: (state, action: PayloadAction<string>) => {
      state.currentSymbol = action.payload;
      state.data = [];
      state.volume = [];
    },
    setTimeframe: (state, action: PayloadAction<string>) => {
      state.timeframe = action.payload;
      state.data = [];
      state.volume = [];
    },
    setChartType: (state, action: PayloadAction<ChartState['chartType']>) => {
      state.chartType = action.payload;
    },
    addIndicator: (state, action: PayloadAction<string>) => {
      if (!state.indicators.includes(action.payload)) {
        state.indicators.push(action.payload);
      }
    },
    removeIndicator: (state, action: PayloadAction<string>) => {
      state.indicators = state.indicators.filter(ind => ind !== action.payload);
    },
    setChartData: (state, action: PayloadAction<{ data: any[]; volume: any[] }>) => {
      state.data = action.payload.data;
      state.volume = action.payload.volume;
      state.isLoading = false;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setSelectedRange: (state, action: PayloadAction<{ start: string; end: string } | null>) => {
      state.selectedRange = action.payload;
    },
  },
});

export const {
  setSymbol,
  setTimeframe,
  setChartType,
  addIndicator,
  removeIndicator,
  setChartData,
  setLoading,
  setSelectedRange,
} = chartSlice.actions;

export default chartSlice.reducer;
