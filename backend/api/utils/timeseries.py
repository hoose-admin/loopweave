from typing import Optional, List, Dict, Any
from .bigquery import get_bigquery_client
from ..types import TimeSeriesData

def get_timeseries(
    symbol: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[TimeSeriesData]:
    """Get timeseries data from BigQuery"""
    bq_client = get_bigquery_client()
    
    query = """
    SELECT 
        symbol,
        date,
        open,
        high,
        low,
        close,
        volume,
        change,
        change_percent,
        vwap,
        sma_50,
        sma_200,
        macd_histogram,
        rsi
    FROM `{project}.{dataset}.timeseries`
    WHERE 1=1
    """.format(
        project=bq_client.project_id,
        dataset=bq_client.dataset_id,
    )
    
    conditions = []
    if symbol:
        conditions.append(f"symbol = '{symbol.upper()}'")
    if start_date:
        conditions.append(f"date >= '{start_date}'")
    if end_date:
        conditions.append(f"date <= '{end_date}'")
    
    if conditions:
        query += " AND " + " AND ".join(conditions)
    
    query += " ORDER BY date DESC LIMIT 1000"
    
    results = bq_client.query(query)
    return results

