from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import os

from .types import Stock, TimeSeriesData, Pattern
from .utils.timeseries import get_timeseries
from .utils.stocks import get_all_stocks, get_stock_by_symbol
from .utils.patterns import get_patterns

app = FastAPI(title="LoopWeave API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "LoopWeave API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/timeseries", response_model=List[TimeSeriesData])
async def get_timeseries_endpoint(
    symbol: Optional[str] = Query(None, description="Stock symbol"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
):
    """Get timeseries data from BigQuery"""
    try:
        return get_timeseries(symbol=symbol, start_date=start_date, end_date=end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/patterns/{pattern_type}", response_model=List[Pattern])
async def get_patterns_endpoint(
    pattern_type: str,
    symbol: Optional[str] = Query(None, description="Stock symbol"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
):
    """Get pattern data from BigQuery"""
    try:
        return get_patterns(pattern_type=pattern_type, symbol=symbol, start_date=start_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stocks", response_model=List[Stock])
async def get_stocks_endpoint():
    """Get all stocks from BigQuery"""
    try:
        return get_all_stocks()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stocks/{symbol}", response_model=Stock)
async def get_stock_endpoint(symbol: str):
    """Get a specific stock by symbol"""
    try:
        stock = get_stock_by_symbol(symbol)
        if not stock:
            raise HTTPException(status_code=404, detail="Stock not found")
        return stock
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

