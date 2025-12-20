from typing import List, Optional
from .bigquery import get_bigquery_client
import importlib.util
import sys
from pathlib import Path

# Import types from parent directory
types_path = Path(__file__).parent.parent / "types.py"
spec = importlib.util.spec_from_file_location("api_types", types_path)
if "api_types" not in sys.modules:
    api_types = importlib.util.module_from_spec(spec)
    sys.modules["api_types"] = api_types
    spec.loader.exec_module(api_types)
else:
    api_types = sys.modules["api_types"]
Stock = api_types.Stock

def get_all_stocks() -> List[Stock]:
    """Get all stocks from BigQuery"""
    bq_client = get_bigquery_client()
    
    query = """
    SELECT 
        symbol,
        name,
        exchange,
        sector,
        industry,
        market_cap,
        pe_ratio,
        forward_pe,
        ebitda,
        description,
        website,
        logo
    FROM `{project}.{dataset}.stocks`
    ORDER BY name
    """.format(
        project=bq_client.project_id,
        dataset=bq_client.dataset_id,
    )
    
    results = bq_client.query(query)
    return results

def get_stock_by_symbol(symbol: str) -> Optional[Stock]:
    """Get a specific stock by symbol"""
    bq_client = get_bigquery_client()
    
    query = """
    SELECT 
        symbol,
        name,
        exchange,
        sector,
        industry,
        market_cap,
        pe_ratio,
        forward_pe,
        ebitda,
        description,
        website,
        logo
    FROM `{project}.{dataset}.stocks`
    WHERE symbol = '{symbol}'
    LIMIT 1
    """.format(
        project=bq_client.project_id,
        dataset=bq_client.dataset_id,
        symbol=symbol.upper(),
    )
    
    results = bq_client.query(query)
    if not results:
        return None
    return results[0]

