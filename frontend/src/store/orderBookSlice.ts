import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface OrderBookLevel {
  price: number;
  size: number;
  orders?: number;
}

interface OrderBookState {
  symbol: string;
  bids: OrderBookLevel[];
  asks: OrderBookLevel[];
  spread: number;
  spreadPercent: number;
  isConnected: boolean;
  lastUpdate: string | null;
}

const initialState: OrderBookState = {
  symbol: '',
  bids: [],
  asks: [],
  spread: 0,
  spreadPercent: 0,
  isConnected: false,
  lastUpdate: null,
};

const orderBookSlice = createSlice({
  name: 'orderBook',
  initialState,
  reducers: {
    setOrderBookData: (state, action: PayloadAction<{
      symbol: string;
      bids: OrderBookLevel[];
      asks: OrderBookLevel[];
    }>) => {
      state.symbol = action.payload.symbol;
      state.bids = action.payload.bids;
      state.asks = action.payload.asks;
      
      const bestBid = action.payload.bids[0]?.price || 0;
      const bestAsk = action.payload.asks[0]?.price || 0;
      state.spread = bestAsk - bestBid;
      state.spreadPercent = bestBid > 0 ? (state.spread / bestBid) * 100 : 0;
      state.lastUpdate = new Date().toISOString();
    },
    setConnectionStatus: (state, action: PayloadAction<boolean>) => {
      state.isConnected = action.payload;
    },
    clearOrderBook: (state) => {
      state.bids = [];
      state.asks = [];
      state.spread = 0;
      state.spreadPercent = 0;
      state.lastUpdate = null;
    },
  },
});

export const { setOrderBookData, setConnectionStatus, clearOrderBook } = orderBookSlice.actions;
export default orderBookSlice.reducer;
