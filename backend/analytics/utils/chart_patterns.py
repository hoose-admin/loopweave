"""
Chart Pattern Detection Library

This module provides chart pattern detection functions using scipy and numpy.
Chart patterns are multi-candle patterns that require analyzing price action,
support/resistance levels, and trend lines over multiple periods.

All functions are stateless and accept DataFrames as input, returning
DataFrames with pattern detection columns added.
"""

import pandas as pd
import numpy as np
from scipy import signal
from typing import Tuple


def find_local_extrema(df: pd.DataFrame, window: int = 5) -> Tuple[pd.Series, pd.Series]:
    """
    Find local maxima (peaks) and minima (troughs) in price data using scipy.
    
    Args:
        df: DataFrame with 'high' and 'low' columns
        window: Minimum distance between peaks/troughs
    
    Returns:
        Tuple of (peaks, troughs) boolean Series
    """
    highs = df['high'].values
    lows = df['low'].values
    
    # Use scipy's find_peaks for more robust peak detection
    peak_indices, _ = signal.find_peaks(highs, distance=window, prominence=np.std(highs) * 0.5)
    trough_indices, _ = signal.find_peaks(-lows, distance=window, prominence=np.std(lows) * 0.5)
    
    # Create boolean series
    peaks = pd.Series(False, index=df.index)
    troughs = pd.Series(False, index=df.index)
    
    peaks.iloc[peak_indices] = True
    troughs.iloc[trough_indices] = True
    
    return peaks, troughs


def detect_head_and_shoulders(df: pd.DataFrame, lookback: int = 60) -> pd.Series:
    """
    Detect head and shoulders pattern (bearish reversal).
    
    Args:
        df: DataFrame with OHLC data
        lookback: Number of candles to look back
    
    Returns:
        Series with 1 where pattern is detected, 0 otherwise
    """
    if len(df) < lookback:
        return pd.Series(0, index=df.index)
    
    detected = pd.Series(0, index=df.index)
    peaks, _ = find_local_extrema(df, window=5)
    
    for i in range(lookback, len(df)):
        window_df = df.iloc[i-lookback:i]
        window_peaks = peaks.iloc[i-lookback:i]
        
        peak_indices = window_df[window_peaks].index
        if len(peak_indices) >= 3:
            peak_prices = window_df.loc[peak_indices, 'high'].values
            # Head and shoulders: left shoulder, head (highest), right shoulder
            if len(peak_prices) >= 3:
                sorted_peaks = sorted(enumerate(peak_prices), key=lambda x: x[1], reverse=True)
                head_idx, head_price = sorted_peaks[0]
                # Check if head is significantly higher than shoulders
                if head_idx > 0 and head_idx < len(peak_prices) - 1:
                    left_shoulder = peak_prices[head_idx - 1]
                    right_shoulder = peak_prices[head_idx + 1]
                    if (head_price > left_shoulder * 1.02 and head_price > right_shoulder * 1.02 and
                        abs(left_shoulder - right_shoulder) / left_shoulder < 0.05):  # Shoulders similar height
                        detected.iloc[i] = 1
    
    return detected


def detect_rectangle(df: pd.DataFrame, lookback: int = 40, tolerance: float = 0.02) -> Tuple[pd.Series, pd.Series]:
    """
    Detect rectangle patterns (consolidation).
    
    Args:
        df: DataFrame with OHLC data
        lookback: Number of candles to look back
        tolerance: Price tolerance for support/resistance levels
    
    Returns:
        Tuple of (bullish_rectangle, bearish_rectangle) Series
    """
    if len(df) < lookback:
        return pd.Series(0, index=df.index), pd.Series(0, index=df.index)
    
    bullish = pd.Series(0, index=df.index)
    bearish = pd.Series(0, index=df.index)
    
    for i in range(lookback, len(df)):
        window_df = df.iloc[i-lookback:i]
        highs = window_df['high']
        lows = window_df['low']
        
        resistance = highs.max()
        support = lows.min()
        range_size = resistance - support
        
        # Check if price oscillates between support and resistance
        touches_resistance = (highs >= resistance * (1 - tolerance)).sum()
        touches_support = (lows <= support * (1 + tolerance)).sum()
        
        if touches_resistance >= 2 and touches_support >= 2:
            # Determine direction based on recent price action
            recent_close = window_df['close'].iloc[-1]
            if recent_close > (support + resistance) / 2:
                bullish.iloc[i] = 1
            else:
                bearish.iloc[i] = 1
    
    return bullish, bearish


def detect_triple_top_bottom(df: pd.DataFrame, lookback: int = 60) -> Tuple[pd.Series, pd.Series]:
    """
    Detect triple top (bearish) and triple bottom (bullish) patterns.
    
    Args:
        df: DataFrame with OHLC data
        lookback: Number of candles to look back
    
    Returns:
        Tuple of (triple_top, triple_bottom) Series
    """
    if len(df) < lookback:
        return pd.Series(0, index=df.index), pd.Series(0, index=df.index)
    
    triple_top = pd.Series(0, index=df.index)
    triple_bottom = pd.Series(0, index=df.index)
    peaks, troughs = find_local_extrema(df, window=5)
    
    for i in range(lookback, len(df)):
        window_df = df.iloc[i-lookback:i]
        window_peaks = peaks.iloc[i-lookback:i]
        window_troughs = troughs.iloc[i-lookback:i]
        
        # Triple top
        peak_indices = window_df[window_peaks].index
        if len(peak_indices) >= 3:
            peak_prices = window_df.loc[peak_indices, 'high'].values[-3:]
            if len(peak_prices) == 3:
                # Check if three peaks are at similar levels
                if (max(peak_prices) - min(peak_prices)) / max(peak_prices) < 0.03:
                    triple_top.iloc[i] = 1
        
        # Triple bottom
        trough_indices = window_df[window_troughs].index
        if len(trough_indices) >= 3:
            trough_prices = window_df.loc[trough_indices, 'low'].values[-3:]
            if len(trough_prices) == 3:
                # Check if three troughs are at similar levels
                if (max(trough_prices) - min(trough_prices)) / max(trough_prices) < 0.03:
                    triple_bottom.iloc[i] = 1
    
    return triple_top, triple_bottom


def detect_double_top_bottom(df: pd.DataFrame, lookback: int = 50) -> Tuple[pd.Series, pd.Series]:
    """
    Detect double top (bearish) and double bottom (bullish) patterns.
    
    Args:
        df: DataFrame with OHLC data
        lookback: Number of candles to look back
    
    Returns:
        Tuple of (double_top, double_bottom) Series
    """
    if len(df) < lookback:
        return pd.Series(0, index=df.index), pd.Series(0, index=df.index)
    
    double_top = pd.Series(0, index=df.index)
    double_bottom = pd.Series(0, index=df.index)
    peaks, troughs = find_local_extrema(df, window=5)
    
    for i in range(lookback, len(df)):
        window_df = df.iloc[i-lookback:i]
        window_peaks = peaks.iloc[i-lookback:i]
        window_troughs = troughs.iloc[i-lookback:i]
        
        # Double top
        peak_indices = window_df[window_peaks].index
        if len(peak_indices) >= 2:
            peak_prices = window_df.loc[peak_indices, 'high'].values[-2:]
            if len(peak_prices) == 2:
                if abs(peak_prices[0] - peak_prices[1]) / max(peak_prices) < 0.02:
                    double_top.iloc[i] = 1
        
        # Double bottom
        trough_indices = window_df[window_troughs].index
        if len(trough_indices) >= 2:
            trough_prices = window_df.loc[trough_indices, 'low'].values[-2:]
            if len(trough_prices) == 2:
                if abs(trough_prices[0] - trough_prices[1]) / max(trough_prices) < 0.02:
                    double_bottom.iloc[i] = 1
    
    return double_top, double_bottom


def detect_channels(df: pd.DataFrame, lookback: int = 40) -> Tuple[pd.Series, pd.Series]:
    """
    Detect ascending (bullish) and descending (bearish) channels.
    
    Args:
        df: DataFrame with OHLC data
        lookback: Number of candles to look back
    
    Returns:
        Tuple of (ascending_channel, descending_channel) Series
    """
    if len(df) < lookback:
        return pd.Series(0, index=df.index), pd.Series(0, index=df.index)
    
    ascending = pd.Series(0, index=df.index)
    descending = pd.Series(0, index=df.index)
    
    for i in range(lookback, len(df)):
        window_df = df.iloc[i-lookback:i]
        highs = window_df['high']
        lows = window_df['low']
        
        # Fit trend lines
        x = np.arange(len(window_df))
        high_slope = np.polyfit(x, highs.values, 1)[0]
        low_slope = np.polyfit(x, lows.values, 1)[0]
        
        # Ascending channel: both trend lines slope up
        if high_slope > 0 and low_slope > 0 and abs(high_slope - low_slope) / abs(high_slope) < 0.3:
            ascending.iloc[i] = 1
        
        # Descending channel: both trend lines slope down
        if high_slope < 0 and low_slope < 0 and abs(high_slope - low_slope) / abs(high_slope) < 0.3:
            descending.iloc[i] = 1
    
    return ascending, descending


def detect_triangles(df: pd.DataFrame, lookback: int = 40) -> Tuple[pd.Series, pd.Series]:
    """
    Detect ascending (bullish) and descending (bearish) triangles.
    
    Args:
        df: DataFrame with OHLC data
        lookback: Number of candles to look back
    
    Returns:
        Tuple of (ascending_triangle, descending_triangle) Series
    """
    if len(df) < lookback:
        return pd.Series(0, index=df.index), pd.Series(0, index=df.index)
    
    ascending_triangle = pd.Series(0, index=df.index)
    descending_triangle = pd.Series(0, index=df.index)
    
    for i in range(lookback, len(df)):
        window_df = df.iloc[i-lookback:i]
        highs = window_df['high']
        lows = window_df['low']
        
        x = np.arange(len(window_df))
        high_slope = np.polyfit(x, highs.values, 1)[0]
        low_slope = np.polyfit(x, lows.values, 1)[0]
        
        # Ascending triangle: flat resistance, rising support
        if abs(high_slope) < 0.01 and low_slope > 0.01:
            ascending_triangle.iloc[i] = 1
        
        # Descending triangle: falling resistance, flat support
        if high_slope < -0.01 and abs(low_slope) < 0.01:
            descending_triangle.iloc[i] = 1
    
    return ascending_triangle, descending_triangle


def detect_flags(df: pd.DataFrame, lookback: int = 30) -> Tuple[pd.Series, pd.Series]:
    """
    Detect bull flag and bear flag patterns (continuation patterns).
    
    Args:
        df: DataFrame with OHLC data
        lookback: Number of candles to look back
    
    Returns:
        Tuple of (bull_flag, bear_flag) Series
    """
    if len(df) < lookback:
        return pd.Series(0, index=df.index), pd.Series(0, index=df.index)
    
    bull_flag = pd.Series(0, index=df.index)
    bear_flag = pd.Series(0, index=df.index)
    
    for i in range(lookback, len(df)):
        window_df = df.iloc[i-lookback:i]
        
        # Split into two halves: pole and flag
        pole_df = window_df.iloc[:lookback//2]
        flag_df = window_df.iloc[lookback//2:]
        
        # Bull flag: strong upward move (pole) followed by slight downward consolidation (flag)
        pole_trend = (pole_df['close'].iloc[-1] - pole_df['close'].iloc[0]) / pole_df['close'].iloc[0]
        flag_trend = (flag_df['close'].iloc[-1] - flag_df['close'].iloc[0]) / flag_df['close'].iloc[0]
        
        if pole_trend > 0.05 and -0.05 < flag_trend < 0.02:  # Strong up, slight down/consolidation
            bull_flag.iloc[i] = 1
        
        # Bear flag: strong downward move (pole) followed by slight upward consolidation (flag)
        if pole_trend < -0.05 and -0.02 < flag_trend < 0.05:  # Strong down, slight up/consolidation
            bear_flag.iloc[i] = 1
    
    return bull_flag, bear_flag


def calculate_all_chart_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate all chart patterns using robust scipy/numpy implementations.
    
    Chart patterns are multi-candle patterns that require analyzing price action,
    support/resistance levels, and trend lines over multiple periods.
    
    Patterns detected:
    - Head and shoulders, rectangles, triple/double tops/bottoms
    - Channels, triangles, flags
    
    Args:
        df: DataFrame with OHLC data (must have 'open', 'high', 'low', 'close' columns)
    
    Returns:
        DataFrame with pattern detection columns added:
        - head_and_shoulders_detected
        - bullish_rectangle_detected, bearish_rectangle_detected
        - triple_top_detected, triple_bottom_detected
        - double_top_detected, double_bottom_detected
        - ascending_channel_detected, descending_channel_detected
        - ascending_triangle_detected, descending_triangle_detected
        - bull_flag_detected, bear_flag_detected
    """
    if df.empty or len(df) < 40:
        # Return DataFrame with all pattern columns initialized to 0
        pattern_columns = [
            'head_and_shoulders_detected',
            'bullish_rectangle_detected', 'bearish_rectangle_detected',
            'triple_top_detected', 'triple_bottom_detected',
            'double_top_detected', 'double_bottom_detected',
            'ascending_channel_detected', 'descending_channel_detected',
            'ascending_triangle_detected', 'descending_triangle_detected',
            'bull_flag_detected', 'bear_flag_detected',
        ]
        for col in pattern_columns:
            df[col] = 0
        return df
    
    # Detect patterns using robust scipy/numpy implementations
    try:
        # Head and shoulders
        df['head_and_shoulders_detected'] = detect_head_and_shoulders(df)
        
        # Rectangles
        bullish_rect, bearish_rect = detect_rectangle(df)
        df['bullish_rectangle_detected'] = bullish_rect
        df['bearish_rectangle_detected'] = bearish_rect
        
        # Triple top/bottom
        triple_top, triple_bottom = detect_triple_top_bottom(df)
        df['triple_top_detected'] = triple_top
        df['triple_bottom_detected'] = triple_bottom
        
        # Double top/bottom
        double_top, double_bottom = detect_double_top_bottom(df)
        df['double_top_detected'] = double_top
        df['double_bottom_detected'] = double_bottom
        
        # Channels
        ascending_chan, descending_chan = detect_channels(df)
        df['ascending_channel_detected'] = ascending_chan
        df['descending_channel_detected'] = descending_chan
        
        # Triangles
        ascending_tri, descending_tri = detect_triangles(df)
        df['ascending_triangle_detected'] = ascending_tri
        df['descending_triangle_detected'] = descending_tri
        
        # Flags
        bull_flag, bear_flag = detect_flags(df)
        df['bull_flag_detected'] = bull_flag
        df['bear_flag_detected'] = bear_flag
        
    except Exception as e:
        # Initialize all pattern columns to 0 on error
        pattern_columns = [
            'head_and_shoulders_detected',
            'bullish_rectangle_detected', 'bearish_rectangle_detected',
            'triple_top_detected', 'triple_bottom_detected',
            'double_top_detected', 'double_bottom_detected',
            'ascending_channel_detected', 'descending_channel_detected',
            'ascending_triangle_detected', 'descending_triangle_detected',
            'bull_flag_detected', 'bear_flag_detected',
        ]
        for col in pattern_columns:
            df[col] = 0
    
    return df

