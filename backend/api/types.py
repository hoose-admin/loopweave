from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Stock(BaseModel):
    symbol: str
    company_name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    forward_pe: Optional[float] = None
    ebitda: Optional[float] = None
    description: Optional[str] = None
    website: Optional[str] = None
    logo: Optional[str] = None

class TimeSeriesData(BaseModel):
    symbol: str
    date: str
    # FMP API fields from historical-price-eod/full endpoint (daily EOD data)
    open: float
    high: float
    low: float
    close: float
    volume: float
    unadjusted_close: Optional[float] = None
    unadjusted_volume: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    vwap: Optional[float] = None
    label: Optional[str] = None
    change_over_time: Optional[float] = None
    # Technical analysis metrics (calculated fields)
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    rsi: Optional[float] = None

class Pattern(BaseModel):
    pattern_id: str
    stock_symbol: str
    pattern_type: str
    start_time: str
    end_time: str
    confidence: Optional[float] = None

class Trade(BaseModel):
    trade_uuid: str
    pattern_uuid: Optional[str] = None
    pattern_name: Optional[str] = None
    prediction: Optional[str] = None
    result: Optional[str] = None  # "correct" or "incorrect"
    percent: Optional[float] = None
    stock_symbol: str
    position_type: Optional[str] = None  # "long" or "short"
    dt_open: str
    dt_close: Optional[str] = None
    stock_value_open: float
    stock_value_close: Optional[float] = None
