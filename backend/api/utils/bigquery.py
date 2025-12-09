from google.cloud import bigquery
from typing import List, Dict, Any
import os

class BigQueryClient:
    def __init__(self):
        self.client = bigquery.Client(project=os.getenv("GCP_PROJECT_ID"))
        self.project_id = os.getenv("GCP_PROJECT_ID", "")
        self.dataset_id = os.getenv("BIGQUERY_DATASET", "loopweave")
    
    def query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a BigQuery query and return results as list of dicts"""
        query_job = self.client.query(query)
        results = query_job.result()
        
        rows = []
        for row in results:
            rows.append(dict(row))
        
        return rows
    
    def insert_rows(self, table_id: str, rows: List[Dict[str, Any]]):
        """Insert rows into a BigQuery table"""
        table_ref = self.client.dataset(self.dataset_id).table(table_id)
        errors = self.client.insert_rows_json(table_ref, rows)
        
        if errors:
            raise Exception(f"Error inserting rows: {errors}")
        
        return True

# Singleton instance
_bq_client = None

def get_bigquery_client() -> BigQueryClient:
    """Get or create BigQuery client instance"""
    global _bq_client
    if _bq_client is None:
        _bq_client = BigQueryClient()
    return _bq_client

