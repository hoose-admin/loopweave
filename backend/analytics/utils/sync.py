import os
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional

import httpx
from utils.db import (
    get_latest_timestamp,
    execute_insert,
    execute_copy,
)

# Default stocks list (fallback if stocks.json is not used)
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


async def _get_latest_timestamp_for_table(symbol: str, table: str) -> Optional[datetime]:
    """Get the latest timestamp for a symbol from a specific Cloud SQL table."""
    latest_ts_str = get_latest_timestamp(symbol, table)
    if latest_ts_str:
        return datetime.fromisoformat(latest_ts_str.replace('Z', '+00:00'))
    return None


async def _insert_rows(table: str, rows: List[Dict[str, Any]]) -> None:
    """Insert rows into a Cloud SQL table using COPY (fastest) or batch INSERT."""
    if not rows:
        return
    
    # Use COPY for bulk inserts (fastest)
    # ON CONFLICT clause for upserts
    on_conflict = None
    if table in ("timeseries", "timeseries_4h"):
        on_conflict = "ON CONFLICT (symbol, date) DO UPDATE SET " + \
                     ", ".join([f"{k} = EXCLUDED.{k}" for k in rows[0].keys() if k not in ('symbol', 'date')])
    
    try:
        # Try COPY first (fastest)
        execute_copy(table, rows)
    except Exception:
        # Fallback to batch INSERT if COPY fails
        execute_insert(table, rows, on_conflict=on_conflict)


async def _fetch_dividend_adjusted_daily(
    symbol: str, api_key: str
) -> List[Dict[str, Any]]:
    """
    Fetch full dividend‑adjusted daily EOD history for a symbol.

    Uses FMP /historical-price-eod/dividend-adjusted endpoint.
    """
    base_url = "https://financialmodelingprep.com/stable"
    url = f"{base_url}/historical-price-eod/dividend-adjusted"
    params = {"symbol": symbol, "apikey": api_key}

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

    if not isinstance(data, list):
        return []

    rows: List[Dict[str, Any]] = []
    for item in data:
        date_str = item.get("date")
        if not date_str:
            continue
        # API returns YYYY‑MM‑DD
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        # Store as end-of-day timestamp
        dt = dt.replace(hour=23, minute=59, second=59)

        try:
            row = {
                "symbol": symbol,
                "date": dt.isoformat(),
                # Map adjusted prices into the canonical OHLC fields
                "open": float(item["adjOpen"]),
                "high": float(item["adjHigh"]),
                "low": float(item["adjLow"]),
                "close": float(item["adjClose"]),
                "volume": float(item["volume"]),
            }
        except KeyError:
            # Skip malformed rows
            continue

        rows.append(row)

    # Oldest first to newest last
    rows.sort(key=lambda r: r["date"])
    return rows


async def _fetch_4h_bars(symbol: str, api_key: str) -> List[Dict[str, Any]]:
    """
    Fetch full 4‑hour history for a symbol.

    Uses FMP /historical-chart/4hour endpoint.
    """
    base_url = "https://financialmodelingprep.com/stable"
    url = f"{base_url}/historical-chart/4hour"
    params = {"symbol": symbol, "apikey": api_key}
        
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

    if not isinstance(data, list):
        return []

    rows: List[Dict[str, Any]] = []
    for item in data:
        date_str = item.get("date")
        if not date_str:
            continue
        # Example: "2025-12-12 13:30:00"
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

        try:
            row = {
                "symbol": symbol,
                "date": dt.isoformat(),
                "open": float(item["open"]),
                "high": float(item["high"]),
                "low": float(item["low"]),
                "close": float(item["close"]),
                "volume": float(item["volume"]),
            }
        except KeyError:
            continue

        rows.append(row)

    rows.sort(key=lambda r: r["date"])
    return rows


async def sync_all_stocks() -> Dict[str, Any]:
    """
    Legacy incremental sync using FMP /historical-price-eod/full endpoint.

    Kept for backward compatibility; prefer the newer /sync-timeseries-daily endpoint.
    """
    fmp_api_key = os.getenv("FMP_API_KEY")
    if not fmp_api_key:
        raise ValueError("FMP_API_KEY environment variable is not set")
    
    records_inserted = 0
    stocks_synced = 0
    
    for symbol in STOCKS:
        try:
            latest_timestamp = await _get_latest_timestamp_for_table(symbol, "timeseries")
            from_date = latest_timestamp or datetime(1985, 1, 1)
            
            # Reuse dividend‑adjusted fetcher but map to open/high/low/close
            all_rows = await _fetch_dividend_adjusted_daily(symbol, fmp_api_key)
            new_rows = [r for r in all_rows if datetime.fromisoformat(r["date"]) > from_date]

            if new_rows:
                await _insert_rows("timeseries", new_rows)
                records_inserted += len(new_rows)
                stocks_synced += 1
            
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Error syncing {symbol}: {str(e)}")
            continue
    
    return {"stocks_synced": stocks_synced, "records_inserted": records_inserted}


async def sync_timeseries_daily(symbols: List[str]) -> Dict[str, Any]:
    """
    Sync dividend‑adjusted daily EOD data for the given symbols into Cloud SQL `timeseries`.

    - Uses FMP dividend‑adjusted EOD endpoint.
    - If no data exists for a symbol, pulls all data from 1985‑01‑01 onward.
    - Otherwise, only inserts rows with date greater than the latest Cloud SQL date.
    """
    fmp_api_key = os.getenv("FMP_API_KEY")
    if not fmp_api_key:
        raise ValueError("FMP_API_KEY environment variable is not set")

    records_inserted = 0
    stocks_synced = 0

    for symbol in symbols:
        symbol = symbol.upper()
        try:
            latest_ts = await _get_latest_timestamp_for_table(symbol, "timeseries")
            from_date = latest_ts or datetime(1985, 1, 1)

            all_rows = await _fetch_dividend_adjusted_daily(symbol, fmp_api_key)
            new_rows = [r for r in all_rows if datetime.fromisoformat(r["date"]) > from_date]

            if new_rows:
                await _insert_rows("timeseries", new_rows)
                records_inserted += len(new_rows)
                stocks_synced += 1

            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Error syncing daily timeseries for {symbol}: {str(e)}")
            continue

    return {"stocks_synced": stocks_synced, "records_inserted": records_inserted}


async def sync_timeseries_4h(symbols: List[str]) -> Dict[str, Any]:
    """
    Sync 4‑hour OHLCV data for the given symbols into Cloud SQL `timeseries_4h`.

    - Uses FMP /historical-chart/4hour endpoint.
    - If no data exists for a symbol, loads the full history returned by FMP.
    - Otherwise, only inserts rows newer than the latest Cloud SQL timestamp.
    """
    fmp_api_key = os.getenv("FMP_API_KEY")
    if not fmp_api_key:
        raise ValueError("FMP_API_KEY environment variable is not set")

    records_inserted = 0
    stocks_synced = 0

    for symbol in symbols:
        symbol = symbol.upper()
        try:
            latest_ts = await _get_latest_timestamp_for_table(symbol, "timeseries_4h")

            all_rows = await _fetch_4h_bars(symbol, fmp_api_key)
            if latest_ts:
                new_rows = [
                    r for r in all_rows if datetime.fromisoformat(r["date"]) > latest_ts
                ]
            else:
                new_rows = all_rows

            if new_rows:
                await _insert_rows("timeseries_4h", new_rows)
                records_inserted += len(new_rows)
                stocks_synced += 1

            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Error syncing 4h timeseries for {symbol}: {str(e)}")
            continue

    return {"stocks_synced": stocks_synced, "records_inserted": records_inserted}


