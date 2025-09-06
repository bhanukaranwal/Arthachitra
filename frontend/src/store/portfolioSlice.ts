import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { api } from '../utils/api';

interface Position {
  id: string;
  symbol: string;
  quantity: number;
  averagePrice: number;
  currentPrice: number;
  pnl: number;
  pnlPercent: number;
}

interface PortfolioState {
  totalValue: number;
  cash: number;
  equity: number;
  dayPnl: number;
  totalPnl: number;
  positions: Position[];
  isLoading: boolean;
  error: string | null;
}

const initialState: PortfolioState = {
  totalValue: 0,
  cash: 0,
  equity: 0,
  dayPnl: 0,
  totalPnl: 0,
  positions: [],
  isLoading: false,
  error: null,
};

export const fetchPortfolio = createAsyncThunk('portfolio/fetch', async () => {
  const response = await api.get('/portfolio');
  return response.data;
});

export const fetchPositions = createAsyncThunk('portfolio/fetchPositions', async () => {
  const response = await api.get('/portfolio/positions');
  return response.data;
});

const portfolioSlice = createSlice({
  name: 'portfolio',
  initialState,
  reducers: {
    updatePosition: (state, action: PayloadAction<{
      symbol: string;
      currentPrice: number;
    }>) => {
      const position = state.positions.find(p => p.symbol === action.payload.symbol);
      if (position) {
        position.currentPrice = action.payload.currentPrice;
        position.pnl = (action.payload.currentPrice - position.averagePrice) * position.quantity;
        position.pnlPercent = ((action.payload.currentPrice - position.averagePrice) / position.averagePrice) * 100;
      }
      
      // Recalculate totals
      state.equity = state.positions.reduce((sum, pos) => sum + (pos.currentPrice * pos.quantity), 0);
      state.totalValue = state.cash + state.equity;
      state.dayPnl = state.positions.reduce((sum, pos) => sum + pos.pnl, 0);
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchPortfolio.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchPortfolio.fulfilled, (state, action) => {
        state.isLoading = false;
        state.totalValue = action.payload.total_value;
        state.cash = action.payload.cash_balance;
        state.equity = action.payload.equity_value;
        state.dayPnl = action.payload.day_pnl;
        state.totalPnl = action.payload.total_pnl;
        state.positions = action.payload.positions;
      })
      .addCase(fetchPortfolio.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to fetch portfolio';
      });
  },
});

export const { updatePosition, clearError } = portfolioSlice.actions;
export default portfolioSlice.reducer;
