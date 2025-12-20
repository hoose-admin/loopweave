from typing import Optional, List
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
Pattern = api_types.Pattern

def get_patterns(
    pattern_type: str,
    symbol: Optional[str] = None,
    start_date: Optional[str] = None,
) -> List[Pattern]:
    """Get pattern data from BigQuery"""
    bq_client = get_bigquery_client()
    
    query = """
    SELECT 
        pattern_id,
        stock_symbol,
        pattern_type,
        start_time,
        end_time,
        confidence
    FROM `{project}.{dataset}.patterns`
    WHERE pattern_type = '{pattern_type}'
    """.format(
        project=bq_client.project_id,
        dataset=bq_client.dataset_id,
        pattern_type=pattern_type,
    )
    
    conditions = []
    if symbol:
        conditions.append(f"stock_symbol = '{symbol.upper()}'")
    if start_date:
        conditions.append(f"start_time >= '{start_date}'")
    
    if conditions:
        query += " AND " + " AND ".join(conditions)
    
    query += " ORDER BY start_time DESC LIMIT 100"
    
    results = bq_client.query(query)
    return results

