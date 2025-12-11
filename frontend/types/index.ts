// Stock and pattern data types
export interface Stock {
  symbol: string;
  company_name: string;
  sector?: string;
  industry?: string;
  market_cap?: number;
  pe_ratio?: number;
  forward_pe?: number;
  ebitda?: number;
  description?: string;
  website?: string;
  logo?: string;
}

export interface TimeSeriesData {
  symbol: string;
  date: string;
  // FMP API fields from historical-price-eod/full endpoint (daily EOD data)
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  unadjusted_close?: number;
  unadjusted_volume?: number;
  change?: number;
  change_percent?: number;
  vwap?: number;
  label?: string;
  change_over_time?: number;
  // Technical analysis metrics (calculated fields)
  ema_12?: number;
  ema_26?: number;
  sma_50?: number;
  sma_200?: number;
  macd?: number;
  macd_signal?: number;
  macd_histogram?: number;
  rsi?: number;
}

export interface Pattern {
  pattern_id: string;
  stock_symbol: string;
  pattern_type: string;
  start_time: string;
  end_time: string;
  confidence?: number;
}

export interface User {
  uid: string;
  email?: string;
  username?: string;
  displayName?: string;
  favorites?: string[];
  subscriptionActive?: boolean;
  createdAt?: string;
  updatedAt?: string;
}

export type MetricType =
  | 'macd_crossover'
  | 'golden_cross'
  | 'death_cross'
  | 'rsi_extremes'
  | 'volume_spikes'
  | 'breakout_above'
  | 'breakout_below'
  | 'inverted_hammer'
  | 'bullish_engulfing'
  | 'morning_star'
  | 'three_white_soldiers'
  | 'three_black_crows'
  | 'bearish_engulfing'
  | 'shooting_star'
  | 'evening_star';

