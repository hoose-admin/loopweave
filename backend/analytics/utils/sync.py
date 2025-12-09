import os
import httpx
from datetime import datetime, timedelta
from typing import List, Dict, Any
from google.cloud import bigquery
import asyncio

# Initial 20 companies to sync
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

async def get_latest_timestamp(symbol: str) -> datetime:
    """Get the latest timestamp for a stock from BigQuery"""
    bq_client = get_bigquery_client()
    dataset_id = get_dataset_id()
    
    query = f"""
    SELECT MAX(timestamp) as latest_timestamp
    FROM `{os.getenv("GCP_PROJECT_ID")}.{dataset_id}.timeseries`
    WHERE stock_symbol = '{symbol}'
    """
    
    query_job = bq_client.query(query)
    results = query_job.result()
    
    for row in results:
        if row.latest_timestamp:
            return row.latest_timestamp
    
    # If no data exists, return date 5 years ago
    return datetime.now() - timedelta(days=5*365)

async def fetch_historical_data(
    symbol: str, from_date: datetime, fmp_api_key: str
) -> List[Dict[str, Any]]:
    """Fetch historical 30-minute data from FMP API"""
    fmp_base_url = "https://financialmodelingprep.com/api/v3"
    
    async with httpx.AsyncClient() as client:
        url = f"{fmp_base_url}/historical-chart/30min/{symbol}"
        params = {
            "apikey": fmp_api_key,
        }
        
        try:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            
            # Transform FMP API response to our format
            transformed_data = []
            for item in data:
                timestamp = datetime.fromisoformat(item["date"].replace("Z", "+00:00"))
                
                # Only include data after from_date
                if timestamp > from_date:
                    transformed_data.append({
                        "stock_symbol": symbol,
                        "timestamp": timestamp.isoformat(),
                        "open": float(item["open"]),
                        "high": float(item["high"]),
                        "low": float(item["low"]),
                        "close": float(item["close"]),
                        "volume": float(item["volume"]),
                    })
            
            return transformed_data
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            return []

async def insert_to_bigquery(rows: List[Dict[str, Any]]):
    """Insert rows into BigQuery timeseries table"""
    if not rows:
        return
    
    bq_client = get_bigquery_client()
    dataset_id = get_dataset_id()
    table_ref = bq_client.dataset(dataset_id).table("timeseries")
    
    # Convert to BigQuery format
    bq_rows = []
    for row in rows:
        bq_rows.append({
            "stock_symbol": row["stock_symbol"],
            "timestamp": row["timestamp"],
            "open": row["open"],
            "high": row["high"],
            "low": row["low"],
            "close": row["close"],
            "volume": row["volume"],
        })
    
    errors = bq_client.insert_rows_json(table_ref, bq_rows)
    if errors:
        raise Exception(f"Error inserting rows: {errors}")

async def sync_all_stocks() -> Dict[str, Any]:
    """Sync data for all stocks incrementally"""
    fmp_api_key = os.getenv("FMP_API_KEY")
    if not fmp_api_key:
        raise ValueError("FMP_API_KEY environment variable is not set")
    
    records_inserted = 0
    stocks_synced = 0
    
    for symbol in STOCKS:
        try:
            # Get the latest timestamp for this stock from BigQuery
            latest_timestamp = await get_latest_timestamp(symbol)
            
            # Fetch new data from FMP API
            new_data = await fetch_historical_data(symbol, latest_timestamp, fmp_api_key)
            
            if new_data:
                # Insert into BigQuery
                await insert_to_bigquery(new_data)
                records_inserted += len(new_data)
                stocks_synced += 1
            
            # Rate limiting - wait between requests
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Error syncing {symbol}: {str(e)}")
            continue
    
    return {
        "stocks_synced": stocks_synced,
        "records_inserted": records_inserted,
    }

