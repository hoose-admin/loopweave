"""
Pattern Visualization Utilities

Functions to create Plotly visualizations for detected chart patterns.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Any, Optional, List, Tuple
from utils.chart_patterns import calculate_all_chart_patterns, find_local_extrema


def find_first_pattern(df: pd.DataFrame) -> Optional[tuple]:
    """
    Find the first (earliest) pattern occurrence across all patterns.
    
    Args:
        df: DataFrame with pattern detection columns
    
    Returns:
        Tuple of (pattern_name, date) or None if no pattern found
    """
    pattern_names = [
        'head_and_shoulders', 'bullish_rectangle', 'bearish_rectangle',
        'triple_top', 'triple_bottom', 'double_top', 'double_bottom',
        'ascending_channel', 'descending_channel',
        'ascending_triangle', 'descending_triangle',
        'bull_flag', 'bear_flag',
    ]
    
    first_pattern_date = None
    first_pattern_name = None
    
    for pattern_name in pattern_names:
        detected_col = f'{pattern_name}_detected'
        if detected_col not in df.columns:
            continue
        
        pattern_occurrences = df[df[detected_col] == 1]
        if not pattern_occurrences.empty:
            earliest = pattern_occurrences.index.min()
            if first_pattern_date is None or earliest < first_pattern_date:
                first_pattern_date = earliest
                first_pattern_name = pattern_name
    
    if first_pattern_date is None:
        return None
    
    return (first_pattern_name, first_pattern_date)


def extract_pattern_geometry(pattern_candles: pd.DataFrame, pattern_name: str) -> Dict[str, Any]:
    """
    Extract geometric features of a pattern for drawing lines.
    
    Args:
        pattern_candles: DataFrame with OHLC data for the pattern period
        pattern_name: Name of the pattern
    
    Returns:
        Dictionary with pattern geometry (lines, points, etc.)
    """
    geometry = {
        'lines': [],  # List of (x_coords, y_coords, label) tuples
        'points': [],  # List of (x, y, label) tuples for key points
    }
    
    if pattern_candles.empty:
        return geometry
    
    peaks, troughs = find_local_extrema(pattern_candles, window=3)
    peak_indices = pattern_candles[peaks].index
    trough_indices = pattern_candles[troughs].index
    
    if pattern_name == 'head_and_shoulders':
        # Find the three peaks: left shoulder, head, right shoulder
        if len(peak_indices) >= 3:
            peak_list = list(peak_indices)
            peak_prices = [pattern_candles.loc[p, 'high'] for p in peak_list]
            
            # Find head (highest peak) by price
            head_price_idx = np.argmax(peak_prices)
            head_pos = head_price_idx
            
            # Find shoulders (peaks before and after head in time order)
            if head_pos > 0 and head_pos < len(peak_list) - 1:
                left_shoulder = peak_list[head_pos - 1]
                right_shoulder = peak_list[head_pos + 1]
                head_idx = peak_list[head_pos]
                
                # Draw line connecting the three peaks
                x_coords = [left_shoulder, head_idx, right_shoulder]
                y_coords = [
                    pattern_candles.loc[left_shoulder, 'high'],
                    pattern_candles.loc[head_idx, 'high'],
                    pattern_candles.loc[right_shoulder, 'high']
                ]
                geometry['lines'].append((x_coords, y_coords, 'Head & Shoulders'))
                
                # Draw neckline (connect troughs between shoulders)
                neckline_troughs = [t for t in trough_indices if left_shoulder < t < right_shoulder]
                if len(neckline_troughs) >= 2:
                    neck_x = [neckline_troughs[0], neckline_troughs[-1]]
                    neck_y = [
                        pattern_candles.loc[neckline_troughs[0], 'low'],
                        pattern_candles.loc[neckline_troughs[-1], 'low']
                    ]
                    geometry['lines'].append((neck_x, neck_y, 'Neckline'))
    
    elif pattern_name in ['double_top', 'triple_top']:
        # Draw line connecting the peaks
        if len(peak_indices) >= 2:
            top_peaks = list(peak_indices)[-3:] if pattern_name == 'triple_top' else list(peak_indices)[-2:]
            x_coords = [p for p in top_peaks]
            y_coords = [pattern_candles.loc[p, 'high'] for p in top_peaks]
            geometry['lines'].append((x_coords, y_coords, f'{pattern_name.replace("_", " ").title()}'))
    
    elif pattern_name in ['double_bottom', 'triple_bottom']:
        # Draw line connecting the troughs
        if len(trough_indices) >= 2:
            bottom_troughs = list(trough_indices)[-3:] if pattern_name == 'triple_bottom' else list(trough_indices)[-2:]
            x_coords = [t for t in bottom_troughs]
            y_coords = [pattern_candles.loc[t, 'low'] for t in bottom_troughs]
            geometry['lines'].append((x_coords, y_coords, f'{pattern_name.replace("_", " ").title()}'))
    
    elif pattern_name in ['bullish_rectangle', 'bearish_rectangle']:
        # Draw horizontal support and resistance lines
        resistance = pattern_candles['high'].max()
        support = pattern_candles['low'].min()
        x_coords = [pattern_candles.index[0], pattern_candles.index[-1]]
        
        # Resistance line
        geometry['lines'].append((x_coords, [resistance, resistance], 'Resistance'))
        # Support line
        geometry['lines'].append((x_coords, [support, support], 'Support'))
    
    elif pattern_name in ['ascending_triangle', 'descending_triangle']:
        # Draw converging trend lines
        x = np.arange(len(pattern_candles))
        highs = pattern_candles['high'].values
        lows = pattern_candles['low'].values
        
        if pattern_name == 'ascending_triangle':
            # Flat resistance, rising support
            resistance = np.mean(highs)
            low_slope, low_intercept = np.polyfit(x, lows, 1)
            x_coords = [pattern_candles.index[0], pattern_candles.index[-1]]
            geometry['lines'].append((x_coords, [resistance, resistance], 'Resistance'))
            geometry['lines'].append((
                x_coords,
                [low_intercept, low_slope * (len(pattern_candles) - 1) + low_intercept],
                'Support'
            ))
        else:  # descending_triangle
            # Falling resistance, flat support
            support = np.mean(lows)
            high_slope, high_intercept = np.polyfit(x, highs, 1)
            x_coords = [pattern_candles.index[0], pattern_candles.index[-1]]
            geometry['lines'].append((
                x_coords,
                [high_intercept, high_slope * (len(pattern_candles) - 1) + high_intercept],
                'Resistance'
            ))
            geometry['lines'].append((x_coords, [support, support], 'Support'))
    
    elif pattern_name in ['ascending_channel', 'descending_channel']:
        # Draw parallel trend lines
        x = np.arange(len(pattern_candles))
        highs = pattern_candles['high'].values
        lows = pattern_candles['low'].values
        
        high_slope, high_intercept = np.polyfit(x, highs, 1)
        low_slope, low_intercept = np.polyfit(x, lows, 1)
        
        x_coords = [pattern_candles.index[0], pattern_candles.index[-1]]
        # Upper trend line
        geometry['lines'].append((
            x_coords,
            [high_intercept, high_slope * (len(pattern_candles) - 1) + high_intercept],
            'Upper Channel'
        ))
        # Lower trend line
        geometry['lines'].append((
            x_coords,
            [low_intercept, low_slope * (len(pattern_candles) - 1) + low_intercept],
            'Lower Channel'
        ))
    
    elif pattern_name in ['bull_flag', 'bear_flag']:
        # Draw pole and flag trend lines
        mid_point = len(pattern_candles) // 2
        pole_df = pattern_candles.iloc[:mid_point]
        flag_df = pattern_candles.iloc[mid_point:]
        
        # Pole line (strong move)
        pole_start_price = pole_df['close'].iloc[0]
        pole_end_price = pole_df['close'].iloc[-1]
        geometry['lines'].append((
            [pole_df.index[0], pole_df.index[-1]],
            [pole_start_price, pole_end_price],
            'Pole'
        ))
        
        # Flag trend line (consolidation)
        if len(flag_df) > 1:
            flag_x = np.arange(len(flag_df))
            flag_highs = flag_df['high'].values
            flag_lows = flag_df['low'].values
            
            if pattern_name == 'bull_flag':
                # Slight downward flag
                flag_slope, flag_intercept = np.polyfit(flag_x, flag_lows, 1)
            else:
                # Slight upward flag
                flag_slope, flag_intercept = np.polyfit(flag_x, flag_highs, 1)
            
            geometry['lines'].append((
                [flag_df.index[0], flag_df.index[-1]],
                [flag_intercept, flag_slope * (len(flag_df) - 1) + flag_intercept],
                'Flag'
            ))
    
    return geometry


def extract_pattern_context(df: pd.DataFrame, pattern_name: str, pattern_date: pd.Timestamp) -> Dict[str, Any]:
    """
    Extract pattern context for visualization.
    
    Args:
        df: DataFrame with OHLC and pattern data
        pattern_name: Name of the pattern
        pattern_date: Date when pattern was detected
    
    Returns:
        Dictionary with pattern context data
    """
    # Pattern length based on pattern type
    pattern_lengths = {
        'head_and_shoulders': 60,
        'triple_top': 60,
        'triple_bottom': 60,
        'double_top': 50,
        'double_bottom': 50,
        'ascending_channel': 40,
        'descending_channel': 40,
        'ascending_triangle': 40,
        'descending_triangle': 40,
        'bullish_rectangle': 40,
        'bearish_rectangle': 40,
        'bull_flag': 30,
        'bear_flag': 30,
    }
    
    pattern_length = pattern_lengths.get(pattern_name, 40)
    
    # Get pattern candles
    pattern_end_idx = df.index.get_loc(pattern_date) + 1
    pattern_start_idx = max(0, pattern_end_idx - pattern_length)
    pattern_candles = df.iloc[pattern_start_idx:pattern_end_idx]
    
    # Calculate context window - 100% of pattern length on both sides
    context_days = pattern_length
    context_start = max(0, pattern_start_idx - context_days)
    context_end = min(len(df), pattern_end_idx + context_days)
    context_df = df.iloc[context_start:context_end]
    
    # Extract pattern geometry for drawing lines
    pattern_geometry = extract_pattern_geometry(pattern_candles, pattern_name)
    
    return {
        'pattern_name': pattern_name,
        'detection_date': pattern_date,
        'pattern_length': pattern_length,
        'pattern_candles': pattern_candles,
        'context_df': context_df,
        'pattern_geometry': pattern_geometry,
    }


def create_pattern_plot_html(symbol: str, df: pd.DataFrame, pattern_type: Optional[str] = None, pattern_date: Optional[pd.Timestamp] = None) -> Optional[str]:
    """
    Create a Plotly HTML visualization for a detected pattern.
    
    Args:
        symbol: Stock symbol
        df: DataFrame with OHLC data
        pattern_type: Optional specific pattern type to plot (if None, finds first pattern)
        pattern_date: Optional specific pattern date to plot (if None, finds first pattern)
    
    Returns:
        HTML string of the plot, or None if no pattern found
    """
    if df.empty or len(df) < 40:
        return None
    
    # Calculate all patterns
    df_with_patterns = calculate_all_chart_patterns(df.copy())
    
    # If specific pattern type and date provided, use those
    if pattern_type and pattern_date:
        pattern_name = pattern_type
        pattern_date = pd.to_datetime(pattern_date)
        # Verify pattern is detected at this date
        detected_col = f'{pattern_name}_detected'
        if detected_col not in df_with_patterns.columns:
            return None
        # Check if pattern_date is in the index
        if pattern_date not in df_with_patterns.index:
            # Try to find the closest date
            closest_idx = df_with_patterns.index.get_indexer([pattern_date], method='nearest')[0]
            pattern_date = df_with_patterns.index[closest_idx]
        if df_with_patterns.loc[pattern_date, detected_col] != 1:
            return None
    else:
        # Find first pattern
        first_pattern = find_first_pattern(df_with_patterns)
        if first_pattern is None:
            return None
        pattern_name, pattern_date = first_pattern
    
    # Extract context
    context = extract_pattern_context(df_with_patterns, pattern_name, pattern_date)
    pattern_candles = context['pattern_candles']
    context_df = context['context_df']
    
    # Determine pattern type for coloring
    pattern_types = {
        'head_and_shoulders': 'bearish',
        'triple_top': 'bearish',
        'double_top': 'bearish',
        'descending_channel': 'bearish',
        'descending_triangle': 'bearish',
        'bearish_rectangle': 'bearish',
        'bear_flag': 'bearish',
    }
    pattern_type = pattern_types.get(pattern_name, 'bullish')
    # Use unique color for pattern lines (orange) - distinct from green/red candlesticks
    pattern_line_color = '#FF8C00'  # Dark orange for pattern lines
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
        subplot_titles=(f'{symbol} - {pattern_name.replace("_", " ").title()} Pattern', 'Volume')
    )
    
    # Main candlestick chart - green for positive days, red for negative days
    fig.add_trace(
        go.Candlestick(
            x=context_df.index,
            open=context_df['open'],
            high=context_df['high'],
            low=context_df['low'],
            close=context_df['close'],
            name='Price',
            increasing_line_color='#26A69A',  # Green for positive days
            decreasing_line_color='#EF5350',  # Red for negative days
            increasing_fillcolor='#26A69A',
            decreasing_fillcolor='#EF5350',
        ),
        row=1, col=1
    )
    
    # Draw pattern lines (trend lines, support/resistance, etc.)
    # Use unique orange color for pattern lines to distinguish from price action
    pattern_geometry = context.get('pattern_geometry', {})
    for x_coords, y_coords, label in pattern_geometry.get('lines', []):
        fig.add_trace(
            go.Scatter(
                x=x_coords,
                y=y_coords,
                mode='lines',
                name=label,
                line=dict(color=pattern_line_color, width=2.5, dash='dash'),
                showlegend=True,
            ),
            row=1, col=1
        )
    
    # Draw pattern key points (peaks, troughs)
    for x, y, label in pattern_geometry.get('points', []):
        fig.add_trace(
            go.Scatter(
                x=[x],
                y=[y],
                mode='markers',
                name=label,
                marker=dict(color=pattern_line_color, size=10, symbol='circle'),
                showlegend=False,
            ),
            row=1, col=1
        )
    
    # Add SMA lines if available - use distinct gray shades
    if 'sma_50' in context_df.columns and context_df['sma_50'].notna().any():
        sma_50_data = context_df[context_df['sma_50'].notna()]
        fig.add_trace(
            go.Scatter(
                x=sma_50_data.index,
                y=sma_50_data['sma_50'],
                mode='lines',
                name='SMA 50',
                line=dict(color='#9E9E9E', width=1.5, dash='dot'),  # Medium gray
            ),
            row=1, col=1
        )
    
    if 'sma_200' in context_df.columns and context_df['sma_200'].notna().any():
        sma_200_data = context_df[context_df['sma_200'].notna()]
        fig.add_trace(
            go.Scatter(
                x=sma_200_data.index,
                y=sma_200_data['sma_200'],
                mode='lines',
                name='SMA 200',
                line=dict(color='#616161', width=1.5, dash='dot'),  # Dark gray
            ),
            row=1, col=1
        )
    
    # Volume bars - green for positive days, red for negative days
    # This matches the candlestick color scheme
    volume_colors = ['#26A69A' if close >= open else '#EF5350' 
                     for close, open in zip(context_df['close'], context_df['open'])]
    
    fig.add_trace(
        go.Bar(
            x=context_df.index,
            y=context_df['volume'],
            name='Volume',
            marker_color=volume_colors,
            opacity=0.7,
        ),
        row=2, col=1
    )
    
    # Update layout
    pattern_display_name = pattern_name.replace('_', ' ').title()
    fig.update_layout(
        title=f"{symbol} - {pattern_display_name} Pattern Detected on {pattern_date.strftime('%Y-%m-%d')}",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        yaxis2_title="Volume",
        height=800,
        showlegend=True,
        xaxis_rangeslider_visible=False,
        template="plotly_white",
    )
    
    # Update x-axis labels
    fig.update_xaxes(title_text="Date", row=2, col=1)
    
    # Return as HTML
    return fig.to_html(include_plotlyjs='cdn', div_id='pattern-plot')

