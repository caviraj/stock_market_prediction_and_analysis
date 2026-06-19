export interface OHLCVData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface StockLatest {
  ticker: string;
  price: number;
  change: number;
  change_pct: number;
  last_updated?: string;
}

export interface PredictionResult {
  ticker: string;
  forecast_7d: number[];
  forecast_30d: number[];
  signal: 'BUY' | 'HOLD' | 'SELL';
  confidence: number;
  last_trained: string;
}

export interface IndicatorResult {
  rsi: { value: number; status: string };
  macd: { macd: number; signal: number; histogram: number; trend: string };
  bollinger: { upper: number; middle: number; lower: number; current_price: number; position: string };
  atr: { atr: number; volatility_level: string };
  sma: { sma20: number; sma50: number; cross_signal: string };
  ema?: number;
}

export interface WatchlistItem {
  ticker: string;
  price: number;
  change: number;
  change_pct: number;
  signal?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    name: string;
    email: string;
  };
}

export interface IndexData {
  value: number;
  change: number;
  change_pct: number;
}

export interface MarketOverview {
  sensex: IndexData;
  nifty50: IndexData;
  bank_nifty: IndexData;
  top_gainers: StockLatest[];
  top_losers: StockLatest[];
}
