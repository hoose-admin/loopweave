from fastapi import FastAPI, HTTPException

from .utils.sync import sync_all_stocks
from .utils.ta_metrics import calculate_all_metrics

app = FastAPI(title="LoopWeave Analytics")

@app.get("/")
async def root():
    return {"message": "LoopWeave Analytics Service"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/sync")
async def sync_data():
    """Sync financial data from FMP API to BigQuery"""
    try:
        result = await sync_all_stocks()
        return {
            "success": True,
            "message": f"Synced data for {result['stocks_synced']} stocks",
            "records_inserted": result["records_inserted"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ta-metrics")
async def calculate_ta_metrics():
    """Calculate technical analysis metrics and patterns"""
    try:
        result = await calculate_all_metrics()
        return {
            "success": True,
            "message": "TA metrics calculated successfully",
            "stocks_processed": result["stocks_processed"],
            "patterns_found": result["patterns_found"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

