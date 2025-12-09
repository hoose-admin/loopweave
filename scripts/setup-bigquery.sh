#!/bin/bash

# Setup BigQuery dataset and tables
# Usage: ./scripts/setup-bigquery.sh

set -e

# Try to get project from gcloud config if not set
if [ -z "$GCP_PROJECT_ID" ]; then
    GCP_PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
    if [ -z "$GCP_PROJECT_ID" ]; then
        echo "Error: GCP_PROJECT_ID environment variable is not set"
        echo "Please set it in your root .env file or run:"
        echo "  gcloud config set project YOUR_PROJECT_ID"
        echo "  export GCP_PROJECT_ID=YOUR_PROJECT_ID"
        exit 1
    fi
    echo "Using GCP project from gcloud config: $GCP_PROJECT_ID"
fi

PROJECT_ID=${GCP_PROJECT_ID}
DATASET_ID="loopweave"

echo "Creating BigQuery dataset..."
bq mk --dataset --location=US ${PROJECT_ID}:${DATASET_ID}

echo "Creating timeseries table..."
bq mk --table \
  --time_partitioning_field timestamp \
  --clustering_fields stock_symbol \
  ${PROJECT_ID}:${DATASET_ID}.timeseries \
  stock_symbol:STRING,timestamp:TIMESTAMP,open:FLOAT,high:FLOAT,low:FLOAT,close:FLOAT,volume:FLOAT,ema_12:FLOAT,ema_26:FLOAT,sma_50:FLOAT,sma_200:FLOAT,macd:FLOAT,macd_signal:FLOAT,macd_histogram:FLOAT,rsi:FLOAT

echo "Creating stocks table..."
bq mk --table \
  ${PROJECT_ID}:${DATASET_ID}.stocks \
  symbol:STRING,company_name:STRING,sector:STRING,industry:STRING,market_cap:FLOAT,pe_ratio:FLOAT,forward_pe:FLOAT,ebitda:FLOAT,description:STRING,website:STRING,logo:STRING

echo "Creating patterns table..."
bq mk --table \
  --clustering_fields stock_symbol,pattern_type \
  ${PROJECT_ID}:${DATASET_ID}.patterns \
  pattern_id:STRING,stock_symbol:STRING,pattern_type:STRING,start_time:TIMESTAMP,end_time:TIMESTAMP,confidence:FLOAT

echo "Creating trades table..."
bq mk --table \
  --clustering_fields stock_symbol \
  ${PROJECT_ID}:${DATASET_ID}.trades \
  trade_uuid:STRING,pattern_uuid:STRING,pattern_name:STRING,prediction:STRING,result:STRING,percent:FLOAT,stock_symbol:STRING,position_type:STRING,dt_open:TIMESTAMP,dt_close:TIMESTAMP,stock_value_open:FLOAT,stock_value_close:FLOAT

echo "BigQuery setup complete!"

