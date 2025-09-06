// Market Data Types
export interface OHLCV {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface Quote {
  symbol: string;
  price: number;
  bid: number;
  ask: number;
  volume: number;
  change: number;
  changePercent: number;
  timestamp: string;
}

export interface OrderBookLevel {
  price: number;
  size: number;
  orders?: number;
}

export interface OrderBook {
  symbol: string;
  bids: OrderBookLevel[];
  asks: OrderBookLevel[];
  spread: number;
  timestamp: string;
}

// Trading Types
export interface Order {
  id: string;
  symbol: string;
  side: 'BUY' | 'SELL';
  quantity: number;
  price?: number;
  type: 'MARKET' | 'LIMIT' | 'STOP' | 'STOP_LIMIT';
  status: 'PENDING' | 'FILLED' | 'CANCELLED' | 'PARTIAL';
  timestamp: string;
}

export interface Position {
  symbol: string;
  quantity: number;
  averagePrice: number;
  currentPrice: number;
  pnl: number;
  pnlPercent: number;
}

export interface Portfolio {
  totalValue: number;
  cash: number;
  equity: number;
  dayPnl: number;
  totalPnl: number;
  positions: Position[];
}

// Theme Types
export interface Theme {
  name: string;
  colors: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
    surface: string;
    text: string;
    textSecondary: string;
    border: string;
    success: string;
    error: string;
    warning: string;
  };
  chart: {
    background: string;
    gridColor: string;
    textColor: string;
    borderColor: string;
    upColor: string;
    downColor: string;
    volumeColor: string;
    crosshairColor: string;
  };
  orderbook: {
    bidColor: string;
    askColor: string;
    bidTextColor: string;
    askTextColor: string;
    spreadColor: string;
  };
}

export interface ThemeConfig {
  name: string;
  theme: Theme;
}

// User Types
export interface User {
  id: string;
  username: string;
  email: string;
  fullName?: string;
  isVerified: boolean;
  subscriptionTier: 'free' | 'premium' | 'pro';
  createdAt: string;
}

// WebSocket Types
export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
}

export interface ChartData {
  symbol: string;
  timeframe: string;
  candles: OHLCV[];
  volume: Array<{ time: string; value: number }>;
}
