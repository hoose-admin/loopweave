from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException

from utils.sync import sync_all_stocks, sync_timeseries_daily, sync_timeseries_4h
from utils.ta_metrics import (
    calculate_all_metrics,
    calculate_all_metrics_4h,
    fetch_timeseries_data,
    fetch_timeseries_data_4h,
    calculate_patterns,
    insert_patterns,
)
from utils.company_enrichment import (
    enrich_companies,
    insert_stocks_to_bigquery,
)

from strategies import STRATEGIES

app = FastAPI(title="LoopWeave Analytics")


@app.get("/")
async def root():
    return {"message": "LoopWeave Analytics Service"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


# @app.post("/sync")
# async def sync_data():
#     """Legacy sync of daily timeseries data."""
#     try:
#         result = await sync_all_stocks()
#         return {
#             "success": True,
#             "message": f"Synced data for {result['stocks_synced']} stocks",
#             "records_inserted": result["records_inserted"],
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@app.post("/sync-companies")
async def sync_companies():
    """
    Sync company metadata and ratios into Cloud SQL `stocks` table.

    - Reads symbols from local stocks.json
    - Enriches via FMP profile + ratios endpoints
    - Bulk uploads to Cloud SQL using upsert (ON CONFLICT)
    """
    try:
        import json

        stocks_path = Path(__file__).resolve().parent / "stocks.json"
        symbols = json.loads(stocks_path.read_text())
        companies = [{"symbol": s} for s in symbols]

        enriched = await enrich_companies(companies)
        result = await insert_stocks_to_bigquery(enriched)

        return {"success": True, **result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sync-timeseries-daily")
async def sync_timeseries_daily_endpoint():
    """
    Sync dividend‑adjusted daily timeseries data for all symbols in stocks.json.

    Data is consolidated per symbol and bulk inserted into Cloud SQL `timeseries`.
    """
    try:
        import json

        stocks_path = Path(__file__).resolve().parent / "stocks.json"
        symbols = json.loads(stocks_path.read_text())
        result = await sync_timeseries_daily(symbols)
        return {
            "success": True,
            "message": f"Synced daily timeseries for {result['stocks_synced']} stocks",
            "records_inserted": result["records_inserted"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sync-timeseries-4hr")
async def sync_timeseries_4h_endpoint():
    """
    Sync 4‑hour timeseries data for all symbols in stocks.json into Cloud SQL `timeseries_4h`.
    """
    try:
        import json

        stocks_path = Path(__file__).resolve().parent / "stocks.json"
        symbols = json.loads(stocks_path.read_text())
        result = await sync_timeseries_4h(symbols)
        return {
            "success": True,
            "message": f"Synced 4h timeseries for {result['stocks_synced']} stocks",
            "records_inserted": result["records_inserted"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sync-metrics-daily")
async def sync_metrics():
    """
    Backfill and update technical metrics for the daily timeseries table in Cloud SQL.
    """
    try:
        result = await calculate_all_metrics()
        return {
            "success": True,
            "message": f"Calculated metrics for {result['stocks_processed']} stocks",
            "patterns_found": result.get("patterns_found", 0),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sync-metrics-4hr")
async def sync_metrics_4h():
    """
    Backfill and update technical metrics for the 4‑hour timeseries table in Cloud SQL.
    """
    try:
        result = await calculate_all_metrics_4h()
        return {
            "success": True,
            "message": f"Calculated 4h metrics for {result['stocks_processed']} stocks",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/patterns/{symbol}")
async def calculate_and_store_patterns(symbol: str):
    """
    Calculate all chart patterns for a stock and upload them to Cloud SQL.
    """
    try:
        df = fetch_timeseries_data(symbol.upper())
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
        
        patterns = calculate_patterns(df, symbol.upper())
        
        if not patterns:
            return {
                "success": True,
                "message": f"No patterns detected for {symbol}",
                "symbol": symbol.upper(),
                "patterns_found": 0,
            }
        
        insert_patterns(patterns)
        
        return {
            "success": True,
            "message": f"Patterns calculated and stored for {symbol}",
            "symbol": symbol.upper(),
            "patterns_found": len(patterns),
            "patterns": [
                {
                    "pattern_type": p["pattern_type"],
                    "start_time": p["start_time"],
                    "end_time": p["end_time"],
                }
                for p in patterns
            ],
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating patterns: {str(e)}")


@app.get("/strategy-daily/{symbol}/{strategy}")
async def run_strategy(symbol: str, strategy: str):
    """
    Run a strategy for a given symbol using daily timeseries data from Cloud SQL.

    Supported strategies (extendable via strategies package):
    - 20sma
    - golden_cross
    - death_cross
    - rsi_overbought
    - rsi_oversold
    """
    symbol_u = symbol.upper()
    strategy_key = strategy.lower()

    if strategy_key not in STRATEGIES:
        raise HTTPException(status_code=404, detail=f"Unknown strategy '{strategy}'")

    # Use daily data for strategies
    df = fetch_timeseries_data(symbol_u)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol_u}")

    try:
        result = STRATEGIES[strategy_key](df, symbol_u)
        return {"success": True, "symbol": symbol_u, "strategy": strategy_key, "timeframe": "daily", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running strategy: {str(e)}")


@app.get("/strategy-4hr/{symbol}/{strategy}")
async def run_strategy_4hr(symbol: str, strategy: str):
    """
    Run a strategy for a given symbol using 4-hour timeseries data from Cloud SQL.

    Supported strategies (extendable via strategies package):
    - 20sma
    - golden_cross
    - death_cross
    - rsi_overbought
    - rsi_oversold
    """
    symbol_u = symbol.upper()
    strategy_key = strategy.lower()

    if strategy_key not in STRATEGIES:
        raise HTTPException(status_code=404, detail=f"Unknown strategy '{strategy}'")

    # Use 4-hour data for strategies
    df = fetch_timeseries_data_4h(symbol_u)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No 4h data found for symbol {symbol_u}")

    try:
        result = STRATEGIES[strategy_key](df, symbol_u)
        return {"success": True, "symbol": symbol_u, "strategy": strategy_key, "timeframe": "4hr", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running 4hr strategy: {str(e)}")


if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

