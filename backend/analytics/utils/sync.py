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
    """Get the latest date for a stock from BigQuery"""
    bq_client = get_bigquery_client()
    dataset_id = get_dataset_id()
    
    query = f"""
    SELECT MAX(date) as latest_date
    FROM `{os.getenv("GCP_PROJECT_ID")}.{dataset_id}.timeseries`
    WHERE symbol = '{symbol}'
    """
    
    query_job = bq_client.query(query)
    results = query_job.result()
    
    for row in results:
        if row.latest_date:
            return row.latest_date
    
    # If no data exists, return date 5 years ago
    return datetime.now() - timedelta(days=5*365)

async def fetch_historical_data(
    symbol: str, from_date: datetime, fmp_api_key: str
) -> List[Dict[str, Any]]:
    """Fetch historical daily (EOD) data from FMP API"""
    fmp_base_url = "https://financialmodelingprep.com/stable"
    
    async with httpx.AsyncClient() as client:
        url = f"{fmp_base_url}/historical-price-eod/full"
        params = {
            "symbol": symbol,
            "apikey": fmp_api_key,
        }
        
        try:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            
            # Transform FMP API response to our format
            transformed_data = []
            for item in data:
                # Parse date - EOD endpoint returns "YYYY-MM-DD" format
                date_str = item.get("date", "")
                if not date_str:
                    continue
                
                try:
                    # Parse date string (YYYY-MM-DD) and convert to datetime
                    # Set time to end of day (23:59:59) since this is EOD data
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    timestamp = date_obj.replace(hour=23, minute=59, second=59)
                except ValueError:
                    # Try ISO format as fallback
                    if date_str.endswith("Z"):
                        timestamp = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    else:
                        timestamp = datetime.fromisoformat(date_str)
                
                # Only include data after from_date
                if timestamp > from_date:
                    # Build row with all FMP API fields
                    row = {
                        "symbol": symbol,
                        "date": timestamp.isoformat(),
                        "open": float(item["open"]),
                        "high": float(item["high"]),
                        "low": float(item["low"]),
                        "close": float(item["close"]),
                        "volume": float(item["volume"]),
                    }
                    
                    # Add optional FMP EOD fields if present
                    if "change" in item:
                        row["change"] = float(item["change"])
                    if "changePercent" in item:
                        row["change_percent"] = float(item["changePercent"])
                    if "vwap" in item:
                        row["vwap"] = float(item["vwap"])
                    # EOD endpoint doesn't have unadjustedClose/Volume or changeOverTime
                    # but we'll keep the checks for compatibility
                    if "unadjustedClose" in item:
                        row["unadjusted_close"] = float(item["unadjustedClose"])
                    if "unadjustedVolume" in item:
                        row["unadjusted_volume"] = float(item["unadjustedVolume"])
                    if "changeOverTime" in item:
                        row["change_over_time"] = float(item["changeOverTime"])
                    
                    transformed_data.append(row)
            
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
    
    # Convert to BigQuery format (include all fields from FMP API)
    bq_rows = []
    for row in rows:
        bq_row = {
            "symbol": row["symbol"],
            "date": row["date"],
            "open": row["open"],
            "high": row["high"],
            "low": row["low"],
            "close": row["close"],
            "volume": row["volume"],
        }
        # Add optional FMP fields if present
        if "unadjusted_close" in row:
            bq_row["unadjusted_close"] = row["unadjusted_close"]
        if "unadjusted_volume" in row:
            bq_row["unadjusted_volume"] = row["unadjusted_volume"]
        if "change" in row:
            bq_row["change"] = row["change"]
        if "change_percent" in row:
            bq_row["change_percent"] = row["change_percent"]
        if "vwap" in row:
            bq_row["vwap"] = row["vwap"]
        if "label" in row:
            bq_row["label"] = row["label"]
        if "change_over_time" in row:
            bq_row["change_over_time"] = row["change_over_time"]
        bq_rows.append(bq_row)
    
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

