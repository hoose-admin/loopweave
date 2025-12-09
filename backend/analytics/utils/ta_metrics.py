import os
import pandas as pd
import pandas_ta as ta
from google.cloud import bigquery
from typing import Dict, Any, List

# List of stocks to process
STOCKS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META",
    "TSLA", "NVDA", "JPM", "V", "JNJ",
    "WMT", "PG", "MA", "UNH", "HD",
    "DIS", "BAC", "ADBE", "NFLX", "CRM"
]

def get_bigquery_client():
    """Get BigQuery client"""
    return bigquery.Client(project=os.getenv("GCP_PROJECT_ID"))

def get_dataset_id():
    """Get BigQuery dataset ID"""
    return os.getenv("BIGQUERY_DATASET", "loopweave")

def fetch_timeseries_data(symbol: str) -> pd.DataFrame:
    """Fetch timeseries data from BigQuery"""
    bq_client = get_bigquery_client()
    dataset_id = get_dataset_id()
    
    query = f"""
    SELECT 
        timestamp,
        open,
        high,
        low,
        close,
        volume
    FROM `{os.getenv("GCP_PROJECT_ID")}.{dataset_id}.timeseries`
    WHERE stock_symbol = '{symbol}'
    ORDER BY timestamp ASC
    """
    
    query_job = bq_client.query(query)
    df = query_job.to_dataframe()
    
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
    
    return df

def calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical analysis metrics using pandas-ta"""
    # EMA
    df['ema_12'] = ta.ema(df['close'], length=12)
    df['ema_26'] = ta.ema(df['close'], length=26)
    
    # SMA
    df['sma_50'] = ta.sma(df['close'], length=50)
    df['sma_200'] = ta.sma(df['close'], length=200)
    
    # MACD
    macd = ta.macd(df['close'])
    if macd is not None and not macd.empty:
        df['macd'] = macd['MACD_12_26_9']
        df['macd_signal'] = macd['MACDs_12_26_9']
        df['macd_histogram'] = macd['MACDh_12_26_9']
    
    # RSI
    df['rsi'] = ta.rsi(df['close'], length=14)
    
    return df

def update_timeseries_metrics(symbol: str, df: pd.DataFrame):
    """Update timeseries table with calculated metrics"""
    bq_client = get_bigquery_client()
    dataset_id = get_dataset_id()
    
    updates = []
    
    for idx, row in df.iterrows():
        updates.append({
            "stock_symbol": symbol,
            "timestamp": idx.isoformat(),
            "ema_12": float(row.get('ema_12', 0)) if pd.notna(row.get('ema_12')) else None,
            "ema_26": float(row.get('ema_26', 0)) if pd.notna(row.get('ema_26')) else None,
            "sma_50": float(row.get('sma_50', 0)) if pd.notna(row.get('sma_50')) else None,
            "sma_200": float(row.get('sma_200', 0)) if pd.notna(row.get('sma_200')) else None,
            "macd": float(row.get('macd', 0)) if pd.notna(row.get('macd')) else None,
            "macd_signal": float(row.get('macd_signal', 0)) if pd.notna(row.get('macd_signal')) else None,
            "macd_histogram": float(row.get('macd_histogram', 0)) if pd.notna(row.get('macd_histogram')) else None,
            "rsi": float(row.get('rsi', 0)) if pd.notna(row.get('rsi')) else None,
        })
    
    # Use MERGE or UPDATE query to update existing rows
    # For now, we'll use a simplified approach with UPDATE statements
    for update in updates[:100]:  # Limit batch size
        query = f"""
        UPDATE `{os.getenv("GCP_PROJECT_ID")}.{dataset_id}.timeseries`
        SET 
            ema_12 = {update['ema_12'] or 'NULL'},
            ema_26 = {update['ema_26'] or 'NULL'},
            sma_50 = {update['sma_50'] or 'NULL'},
            sma_200 = {update['sma_200'] or 'NULL'},
            macd = {update['macd'] or 'NULL'},
            macd_signal = {update['macd_signal'] or 'NULL'},
            macd_histogram = {update['macd_histogram'] or 'NULL'},
            rsi = {update['rsi'] or 'NULL'}
        WHERE stock_symbol = '{symbol}' AND timestamp = '{update['timestamp']}'
        """
        try:
            bq_client.query(query).result()
        except Exception as e:
            print(f"Error updating metrics: {str(e)}")

def calculate_patterns(df: pd.DataFrame, symbol: str) -> List[Dict[str, Any]]:
    """Calculate candlestick patterns using pandas-ta"""
    patterns = []
    
    if len(df) < 3:
        return patterns
    
    # Calculate candlestick patterns
    try:
        # Bullish patterns
        inverted_hammer = ta.cdl_pattern(df['open'], df['high'], df['low'], df['close'], name="invertedhammer")
        bullish_engulfing = ta.cdl_pattern(df['open'], df['high'], df['low'], df['close'], name="engulfing")
        morning_star = ta.cdl_pattern(df['open'], df['high'], df['low'], df['close'], name="morningstar")
        three_white_soldiers = ta.cdl_pattern(df['open'], df['high'], df['low'], df['close'], name="3whitesoldiers")
        
        # Bearish patterns
        three_black_crows = ta.cdl_pattern(df['open'], df['high'], df['low'], df['close'], name="3blackcrows")
        bearish_engulfing = ta.cdl_pattern(df['open'], df['high'], df['low'], df['close'], name="engulfing")
        shooting_star = ta.cdl_pattern(df['open'], df['high'], df['low'], df['close'], name="shootingstar")
        evening_star = ta.cdl_pattern(df['open'], df['high'], df['low'], df['close'], name="eveningstar")
        
        # Process patterns and add to list
        pattern_columns = {
            'inverted_hammer': inverted_hammer,
            'bullish_engulfing': bullish_engulfing,
            'morning_star': morning_star,
            'three_white_soldiers': three_white_soldiers,
            'three_black_crows': three_black_crows,
            'bearish_engulfing': bearish_engulfing,
            'shooting_star': shooting_star,
            'evening_star': evening_star,
        }
        
        for pattern_name, pattern_series in pattern_columns.items():
            if pattern_series is not None and not pattern_series.empty:
                # Find where pattern occurs (non-zero values)
                pattern_occurrences = df[pattern_series != 0]
                
                for idx, row in pattern_occurrences.iterrows():
                    patterns.append({
                        "pattern_id": f"{symbol}_{pattern_name}_{idx.isoformat()}",
                        "stock_symbol": symbol,
                        "pattern_type": pattern_name,
                        "start_time": idx.isoformat(),
                        "end_time": idx.isoformat(),
                        "confidence": 1.0,  # Can be calculated based on pattern strength
                    })
    except Exception as e:
        print(f"Error calculating patterns for {symbol}: {str(e)}")
    
    return patterns

def insert_patterns(patterns: List[Dict[str, Any]]):
    """Insert patterns into BigQuery patterns table"""
    if not patterns:
        return
    
    bq_client = get_bigquery_client()
    dataset_id = get_dataset_id()
    table_ref = bq_client.dataset(dataset_id).table("patterns")
    
    errors = bq_client.insert_rows_json(table_ref, patterns)
    if errors:
        raise Exception(f"Error inserting patterns: {errors}")

async def calculate_all_metrics() -> Dict[str, Any]:
    """Calculate TA metrics and patterns for all stocks"""
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

