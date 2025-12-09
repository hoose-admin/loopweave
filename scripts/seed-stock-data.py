#!/usr/bin/env python3
"""
Seed BigQuery with historical stock data from Financial Modeling Prep API.

This script fetches historical 30-minute interval data for a single stock
and inserts it into BigQuery timeseries table. Designed to be run both
locally and as a cron job endpoint.

Usage:
    python scripts/seed-stock-data.py AAPL
    python scripts/seed-stock-data.py AAPL --api-key YOUR_KEY
    python scripts/seed-stock-data.py AAPL --dry-run  # Test without inserting
    python scripts/seed-stock-data.py AAPL --batch-size 1000  # Process in batches
"""

import argparse
import os
import sys
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
import httpx
from google.cloud import bigquery
from google.cloud.exceptions import GoogleCloudError

# Load environment variables from root .env file
root_dir = Path(__file__).parent.parent
env_file = root_dir / ".env"
if env_file.exists():
    load_dotenv(env_file)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)

# FMP API Configuration
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"
FMP_API_KEY = os.getenv("FMP_API_KEY", "")

# BigQuery Configuration
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "")
BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET", "loopweave")
BIGQUERY_TABLE = "timeseries"

# Default configuration
DEFAULT_BATCH_SIZE = 1000
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 5  # seconds


def get_bigquery_client():
    """Get BigQuery client"""
    if not GCP_PROJECT_ID:
        raise ValueError("GCP_PROJECT_ID environment variable is not set")
    return bigquery.Client(project=GCP_PROJECT_ID)


def fetch_historical_data(
    symbol: str, 
    api_key: str, 
    max_retries: int = DEFAULT_MAX_RETRIES,
    retry_delay: int = DEFAULT_RETRY_DELAY
) -> List[Dict[str, Any]]:
    """
    Fetch historical 30-minute data from FMP API with retry logic.
    
    This uses the historical-chart endpoint which should return
    as much historical data as available in a single query.
    """
    url = f"{FMP_BASE_URL}/historical-chart/30min/{symbol}"
    params = {
        "apikey": api_key,
    }
    
    logger.info(f"Fetching historical data for {symbol}...")
    logger.debug(f"URL: {url}")
    
    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if not data:
                    logger.warning(f"No data returned for {symbol}")
                    return []
                
                logger.info(f"Received {len(data)} data points")
                
                # Transform FMP API response to our format
                transformed_data = []
                parse_errors = 0
                
                for item in data:
                    try:
                        # Parse timestamp - FMP returns ISO format
                        timestamp_str = item.get("date", "")
                        if not timestamp_str:
                            continue
                        
                        # Handle different timestamp formats
                        if timestamp_str.endswith("Z"):
                            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                        else:
                            timestamp = datetime.fromisoformat(timestamp_str)
                        
                        # Validate data
                        open_price = float(item.get("open", 0))
                        high_price = float(item.get("high", 0))
                        low_price = float(item.get("low", 0))
                        close_price = float(item.get("close", 0))
                        volume = float(item.get("volume", 0))
                        
                        # Basic data validation
                        if high_price < low_price or close_price < 0 or open_price < 0:
                            parse_errors += 1
                            continue
                        
                        transformed_data.append({
                            "stock_symbol": symbol.upper(),
                            "timestamp": timestamp.isoformat(),
                            "open": open_price,
                            "high": high_price,
                            "low": low_price,
                            "close": close_price,
                            "volume": volume,
                        })
                    except (ValueError, KeyError) as e:
                        parse_errors += 1
                        logger.debug(f"Error parsing data point: {e}")
                        continue
                
                if parse_errors > 0:
                    logger.warning(f"Skipped {parse_errors} invalid data points")
                
                # Sort by timestamp (oldest first)
                transformed_data.sort(key=lambda x: x["timestamp"])
                
                if transformed_data:
                    first_timestamp = transformed_data[0]["timestamp"]
                    last_timestamp = transformed_data[-1]["timestamp"]
                    logger.info(f"Date range: {first_timestamp} to {last_timestamp}")
                    logger.info(f"Total valid records: {len(transformed_data)}")
                
                return transformed_data
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:  # Rate limit
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (attempt + 1)
                    logger.warning(f"Rate limited. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
            logger.error(f"HTTP Error {e.response.status_code}: {e.response.text}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
            else:
                return []
        except httpx.TimeoutException:
            logger.error(f"Request timeout for {symbol}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
            else:
                return []
        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}", exc_info=True)
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
            else:
                return []
    
    return []


def get_latest_timestamp(symbol: str) -> Optional[datetime]:
    """Get the latest timestamp for a stock from BigQuery"""
    bq_client = get_bigquery_client()
    
    query = f"""
    SELECT MAX(timestamp) as latest_timestamp
    FROM `{GCP_PROJECT_ID}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}`
    WHERE stock_symbol = '{symbol.upper()}'
    """
    
    try:
        query_job = bq_client.query(query)
        results = query_job.result()
        for row in results:
            if row.latest_timestamp:
                return row.latest_timestamp
        return None
    except Exception as e:
        logger.error(f"Error getting latest timestamp: {str(e)}")
        return None


def filter_new_data(data: List[Dict[str, Any]], symbol: str) -> List[Dict[str, Any]]:
    """Filter out data that already exists in BigQuery"""
    latest_timestamp = get_latest_timestamp(symbol)
    
    if latest_timestamp is None:
        logger.info("No existing data found, inserting all records")
        return data
    
    # Convert latest_timestamp to string for comparison
    latest_str = latest_timestamp.isoformat()
    
    # Filter to only include data after the latest timestamp
    new_data = [row for row in data if row["timestamp"] > latest_str]
    
    if len(new_data) < len(data):
        logger.info(f"Filtered {len(data) - len(new_data)} existing records, {len(new_data)} new records to insert")
    
    return new_data


def insert_to_bigquery(
    rows: List[Dict[str, Any]], 
    symbol: str,
    batch_size: int = DEFAULT_BATCH_SIZE,
    dry_run: bool = False
) -> bool:
    """
    Insert rows into BigQuery timeseries table in batches.
    
    Returns True if all inserts succeeded, False otherwise.
    """
    if not rows:
        logger.info("No data to insert")
        return True
    
    if dry_run:
        logger.info(f"[DRY RUN] Would insert {len(rows)} rows into BigQuery")
        return True
    
    bq_client = get_bigquery_client()
    table_ref = bq_client.dataset(BIGQUERY_DATASET).table(BIGQUERY_TABLE)
    
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
    
    logger.info(f"Inserting {len(bq_rows)} rows into BigQuery in batches of {batch_size}...")
    logger.info(f"Table: {GCP_PROJECT_ID}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}")
    
    total_inserted = 0
    total_errors = 0
    
    # Process in batches
    for i in range(0, len(bq_rows), batch_size):
        batch = bq_rows[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(bq_rows) + batch_size - 1) // batch_size
        
        logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} rows)...")
        
        try:
            errors = bq_client.insert_rows_json(table_ref, batch)
            if errors:
                logger.error(f"Errors in batch {batch_num}: {errors}")
                total_errors += len(errors)
            else:
                total_inserted += len(batch)
                logger.debug(f"Batch {batch_num} inserted successfully")
        except GoogleCloudError as e:
            logger.error(f"Google Cloud error inserting batch {batch_num}: {str(e)}")
            total_errors += len(batch)
        except Exception as e:
            logger.error(f"Error inserting batch {batch_num}: {str(e)}", exc_info=True)
            total_errors += len(batch)
    
    if total_errors == 0:
        logger.info(f"✓ Successfully inserted {total_inserted} rows")
        return True
    else:
        logger.warning(f"Inserted {total_inserted} rows with {total_errors} errors")
        return False


def check_existing_data(symbol: str) -> int:
    """Check how many records already exist for this symbol"""
    bq_client = get_bigquery_client()
    
    query = f"""
    SELECT COUNT(*) as count
    FROM `{GCP_PROJECT_ID}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}`
    WHERE stock_symbol = '{symbol.upper()}'
    """
    
    try:
        query_job = bq_client.query(query)
        results = query_job.result()
        for row in results:
            return row.count
    except Exception as e:
        logger.error(f"Error checking existing data: {str(e)}")
        return 0


def main():
    parser = argparse.ArgumentParser(
        description="Seed BigQuery with historical stock data from FMP API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python seed-stock-data.py AAPL
  
  # Dry run (test without inserting)
  python seed-stock-data.py AAPL --dry-run
  
  # Process in smaller batches
  python seed-stock-data.py AAPL --batch-size 500
  
  # Check existing data only
  python seed-stock-data.py AAPL --check-only
  
  # Verbose logging
  python seed-stock-data.py AAPL --verbose
        """
    )
    parser.add_argument(
        "symbol",
        help="Stock symbol (e.g., AAPL)",
        default="AAPL",
        nargs="?",
    )
    parser.add_argument(
        "--api-key",
        help="FMP API key (defaults to FMP_API_KEY from .env file)",
        default=FMP_API_KEY,
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check existing data, don't fetch new data",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Test run without inserting data into BigQuery",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=f"Number of rows to insert per batch (default: {DEFAULT_BATCH_SIZE})",
    )
    parser.add_argument(
        "--skip-duplicates",
        action="store_true",
        help="Skip records that already exist in BigQuery",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=DEFAULT_MAX_RETRIES,
        help=f"Maximum number of retries for API calls (default: {DEFAULT_MAX_RETRIES})",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    symbol = args.symbol.upper()
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Stock Data Seeding Script")
    logger.info(f"{'='*60}")
    logger.info(f"Symbol: {symbol}")
    if args.api_key:
        logger.info(f"API Key: {args.api_key[:10]}...")
    else:
        logger.warning(f"API Key: Not set (check .env file)")
    logger.info(f"BigQuery Project: {GCP_PROJECT_ID or 'Not set'}")
    logger.info(f"BigQuery Dataset: {BIGQUERY_DATASET}")
    logger.info(f"BigQuery Table: {BIGQUERY_TABLE}")
    if args.dry_run:
        logger.info(f"Mode: DRY RUN (no data will be inserted)")
    logger.info(f"{'='*60}\n")
    
    if not args.api_key:
        logger.error("FMP_API_KEY not found. Please set it in the root .env file.")
        sys.exit(1)
    
    if not GCP_PROJECT_ID:
        logger.error("GCP_PROJECT_ID not found. Please set it in the root .env file.")
        sys.exit(1)
    
    try:
        # Check existing data
        existing_count = check_existing_data(symbol)
        logger.info(f"Existing records for {symbol}: {existing_count}")
        
        if args.check_only:
            return
        
        # Fetch historical data
        start_time = time.time()
        data = fetch_historical_data(symbol, args.api_key, max_retries=args.max_retries)
        fetch_duration = time.time() - start_time
        
        if not data:
            logger.error("No data fetched. Exiting.")
            sys.exit(1)
        
        logger.info(f"Fetched {len(data)} records in {fetch_duration:.2f} seconds")
        
        # Filter duplicates if requested
        if args.skip_duplicates:
            data = filter_new_data(data, symbol)
            if not data:
                logger.info("No new data to insert (all records already exist)")
                return
        
        # Insert into BigQuery
        insert_start = time.time()
        success = insert_to_bigquery(data, symbol, batch_size=args.batch_size, dry_run=args.dry_run)
        insert_duration = time.time() - insert_start
        
        if success:
            if not args.dry_run:
                # Check final count
                final_count = check_existing_data(symbol)
                new_records = final_count - existing_count
                logger.info(f"\n{'='*60}")
                logger.info(f"Summary:")
                logger.info(f"  Final record count: {final_count}")
                logger.info(f"  New records added: {new_records}")
                logger.info(f"  Fetch duration: {fetch_duration:.2f}s")
                logger.info(f"  Insert duration: {insert_duration:.2f}s")
                logger.info(f"{'='*60}")
            else:
                logger.info(f"\n[DRY RUN] Would have inserted {len(data)} records")
        else:
            logger.error("Failed to insert data into BigQuery")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

