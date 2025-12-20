import os
from typing import Dict, Any, List

import pandas as pd
import pandas_ta as ta

from utils.chart_patterns import calculate_all_chart_patterns
from utils.db import (
    execute_query_dataframe,
    update_timeseries_metrics,
    execute_insert,
)

# List of stocks to process
STOCKS = [
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "META",
    "TSLA",
    "NVDA",
    "JPM",
    "V",
    "JNJ",
    "WMT",
    "PG",
    "MA",
    "UNH",
    "HD",
    "DIS",
    "BAC",
    "ADBE",
    "NFLX",
    "CRM",
]


def _fetch_timeseries_from_table(symbol: str, table: str) -> pd.DataFrame:
    """Fetch timeseries data from a given Cloud SQL table."""
    query = """
    SELECT 
        date,
        open,
        high,
        low,
        close,
        volume,
        sma_20,
        sma_50,
        sma_200,
        ema_12,
        ema_20,
        ema_26,
        macd_line,
        macd_signal_line,
        macd_histogram,
        rsi,
        atr,
        bb_upper,
        bb_lower
    FROM {}
    WHERE symbol = %s
    ORDER BY date ASC
    """.format(table)
    
    df = execute_query_dataframe(query, (symbol,))
    
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)
    
    return df


def fetch_timeseries_data(symbol: str) -> pd.DataFrame:
    """Fetch daily timeseries data from Cloud SQL."""
    return _fetch_timeseries_from_table(symbol, "timeseries")


def fetch_timeseries_data_4h(symbol: str) -> pd.DataFrame:
    """Fetch 4‑hour timeseries data from Cloud SQL."""
    return _fetch_timeseries_from_table(symbol, "timeseries_4h")


def calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate technical analysis metrics using pandas-ta.
    
    Calculates all metrics needed for strategies and analysis:
    - Simple Moving Averages (SMA): 20, 50, 200
    - Exponential Moving Averages (EMA): 12, 20, 26
    - MACD: line, signal, histogram
    - RSI: 14-period
    - ATR: Average True Range
    - Bollinger Bands: upper, lower
    """
    if df.empty:
        return df

    # Simple Moving Averages
    df["sma_20"] = ta.sma(df["close"], length=20)
    df["sma_50"] = ta.sma(df["close"], length=50)
    df["sma_200"] = ta.sma(df["close"], length=200)
    
    # Exponential Moving Averages
    df["ema_12"] = ta.ema(df["close"], length=12)
    df["ema_20"] = ta.ema(df["close"], length=20)
    df["ema_26"] = ta.ema(df["close"], length=26)
    
    # MACD (12, 26, 9)
    macd = ta.macd(df["close"])
    if macd is not None and not macd.empty:
        df["macd_line"] = macd["MACD_12_26_9"]
        df["macd_signal_line"] = macd["MACDs_12_26_9"]
        df["macd_histogram"] = macd["MACDh_12_26_9"]
    else:
        df["macd_line"] = None
        df["macd_signal_line"] = None
        df["macd_histogram"] = None

    # RSI (14-period)
    df["rsi"] = ta.rsi(df["close"], length=14)

    # ATR (Average True Range) - 14 period default
    atr = ta.atr(df["high"], df["low"], df["close"], length=14)
    if atr is not None and not atr.empty:
        df["atr"] = atr
    else:
        df["atr"] = None

    # Bollinger Bands (20 period, 2 std dev)
    bb = ta.bbands(df["close"], length=20, std=2)
    if bb is not None and not bb.empty:
        df["bb_upper"] = bb["BBU_20_2.0"]
        df["bb_lower"] = bb["BBL_20_2.0"]
    else:
        df["bb_upper"] = None
        df["bb_lower"] = None
    
    return df


def _update_metrics_for_table(symbol: str, df: pd.DataFrame, table: str) -> None:
    """
    Update a timeseries table with all calculated metrics.
    
    Persists all technical indicators to Cloud SQL using batch updates.
    """
    if df.empty:
        return

    def _to_float_or_none(val):
        """Convert pandas value to float or None."""
        if pd.isna(val):
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    # Prepare metrics for batch update
    metrics_list = []
    for idx, row in df.iterrows():
        metric_row = {
            "symbol": symbol,
            "date": idx.to_pydatetime(),
            "sma_20": _to_float_or_none(row.get("sma_20")),
            "sma_50": _to_float_or_none(row.get("sma_50")),
            "sma_200": _to_float_or_none(row.get("sma_200")),
            "ema_12": _to_float_or_none(row.get("ema_12")),
            "ema_20": _to_float_or_none(row.get("ema_20")),
            "ema_26": _to_float_or_none(row.get("ema_26")),
            "macd_line": _to_float_or_none(row.get("macd_line")),
            "macd_signal_line": _to_float_or_none(row.get("macd_signal_line")),
            "macd_histogram": _to_float_or_none(row.get("macd_histogram")),
            "rsi": _to_float_or_none(row.get("rsi")),
            "atr": _to_float_or_none(row.get("atr")),
            "bb_upper": _to_float_or_none(row.get("bb_upper")),
            "bb_lower": _to_float_or_none(row.get("bb_lower")),
        }
        metrics_list.append(metric_row)

    try:
        update_timeseries_metrics(symbol, table, metrics_list)
    except Exception as e:
        print(f"Error updating metrics for {symbol} in {table}: {str(e)}")


def update_timeseries_metrics(symbol: str, df: pd.DataFrame) -> None:
    """Update daily timeseries table with calculated metrics."""
    _update_metrics_for_table(symbol, df, "timeseries")


def update_timeseries_metrics_4h(symbol: str, df: pd.DataFrame) -> None:
    """Update 4‑hour timeseries table with calculated metrics."""
    _update_metrics_for_table(symbol, df, "timeseries_4h")

def calculate_patterns(df: pd.DataFrame, symbol: str) -> List[Dict[str, Any]]:
    """
    Calculate chart patterns using scipy/numpy.
    
    Chart patterns are multi-candle patterns like head and shoulders, rectangles,
    triangles, channels, flags, etc.
    
    Args:
        df: DataFrame with OHLC data
        symbol: Stock symbol
    
    Returns:
        List of pattern dictionaries matching Cloud SQL schema
    """
    patterns = []
    
    if len(df) < 40:
        return patterns
    
    # Calculate chart patterns using scipy/numpy
    try:
        # Calculate all chart patterns
        df_with_chart_patterns = calculate_all_chart_patterns(df.copy())
        
        # Chart pattern names and their lookback periods (for determining start_time)
        chart_pattern_configs = {
            'head_and_shoulders': {'lookback': 60},
            'bullish_rectangle': {'lookback': 40},
            'bearish_rectangle': {'lookback': 40},
            'triple_top': {'lookback': 60},
            'triple_bottom': {'lookback': 60},
            'double_top': {'lookback': 50},
            'double_bottom': {'lookback': 50},
            'ascending_channel': {'lookback': 40},
            'descending_channel': {'lookback': 40},
            'ascending_triangle': {'lookback': 40},
            'descending_triangle': {'lookback': 40},
            'bull_flag': {'lookback': 30},
            'bear_flag': {'lookback': 30},
        }
        
        # Process each chart pattern
        for pattern_name, config in chart_pattern_configs.items():
            detected_col = f'{pattern_name}_detected'
            if detected_col not in df_with_chart_patterns.columns:
                continue
            
            # Find where pattern is detected (value = 1)
            pattern_occurrences = df_with_chart_patterns[df_with_chart_patterns[detected_col] == 1]
            
            for idx, row in pattern_occurrences.iterrows():
                # Chart patterns span multiple candles, so start_time is earlier than end_time
                lookback = config['lookback']
                pattern_end_idx = df_with_chart_patterns.index.get_loc(idx)
                pattern_start_idx = max(0, pattern_end_idx - lookback)
                pattern_start_time = df_with_chart_patterns.index[pattern_start_idx]
                
                patterns.append({
                    "pattern_id": f"{symbol}_{pattern_name}_{idx.isoformat()}",
                    "stock_symbol": symbol,
                    "pattern_type": pattern_name,
                    "start_time": pattern_start_time.isoformat(),
                    "end_time": idx.isoformat(),
                    "confidence": 1.0,  # Can be calculated based on pattern strength
                })
    except Exception as e:
        print(f"Error calculating chart patterns for {symbol}: {str(e)}")
    
    return patterns


def insert_patterns(patterns: List[Dict[str, Any]]):
    """Insert patterns into Cloud SQL patterns table."""
    if not patterns:
        return
    
    # Use ON CONFLICT to avoid duplicates
    on_conflict = "ON CONFLICT (pattern_id) DO NOTHING"
    execute_insert("patterns", patterns, on_conflict=on_conflict)

async def calculate_all_metrics() -> Dict[str, Any]:
    """Calculate TA metrics and patterns for all stocks (daily timeframe)."""
    stocks_processed = 0
    patterns_found = 0
    
    for symbol in STOCKS:
        try:
            # Fetch timeseries data
            df = fetch_timeseries_data(symbol)
            
            if df.empty:
                continue
            
            # Calculate metrics
            df_with_metrics = calculate_metrics(df)
            
            # Update BigQuery with metrics
            update_timeseries_metrics(symbol, df_with_metrics)
            
            # Calculate patterns
            patterns = calculate_patterns(df_with_metrics, symbol)
            
            # Insert patterns into BigQuery
            if patterns:
                insert_patterns(patterns)
                patterns_found += len(patterns)
            
            stocks_processed += 1
        except Exception as e:
            print(f"Error processing {symbol}: {str(e)}")
            continue
    
    return {
        "stocks_processed": stocks_processed,
        "patterns_found": patterns_found,
    }


async def calculate_all_metrics_4h() -> Dict[str, Any]:
    """
    Calculate TA metrics for all stocks on 4‑hour timeframe.

    This updates the `timeseries_4h` table but does not calculate/store patterns.
    """
    stocks_processed = 0

    for symbol in STOCKS:
        try:
            df = fetch_timeseries_data_4h(symbol)
            if df.empty:
                continue

            df_with_metrics = calculate_metrics(df)
            update_timeseries_metrics_4h(symbol, df_with_metrics)
            stocks_processed += 1
        except Exception as e:
            print(f"Error processing 4h metrics for {symbol}: {str(e)}")
            continue

    return {"stocks_processed": stocks_processed}

