# BigQuery Dataset
resource "google_bigquery_dataset" "loopweave" {
  dataset_id  = var.bigquery_dataset_id
  location    = var.bigquery_location
  description = "LoopWeave financial data warehouse"
}

# Timeseries Table
resource "google_bigquery_table" "timeseries" {
  dataset_id          = google_bigquery_dataset.loopweave.dataset_id
  table_id            = "timeseries"
  description         = "Stock price timeseries data with technical analysis metrics"
  deletion_protection = false

  time_partitioning {
    type  = "DAY"
    field = "date"
  }

  clustering = ["symbol"]

  schema = jsonencode([
    { name = "symbol", type = "STRING", mode = "REQUIRED" },
    { name = "date", type = "TIMESTAMP", mode = "REQUIRED" },
    # FMP API fields from historical-price-eod/full endpoint (daily EOD data)
    { name = "open", type = "FLOAT", mode = "REQUIRED" },
    { name = "high", type = "FLOAT", mode = "REQUIRED" },
    { name = "low", type = "FLOAT", mode = "REQUIRED" },
    { name = "close", type = "FLOAT", mode = "REQUIRED" },
    { name = "volume", type = "FLOAT", mode = "REQUIRED" },
    { name = "change", type = "FLOAT", mode = "NULLABLE" },
    { name = "change_percent", type = "FLOAT", mode = "NULLABLE" },
    { name = "vwap", type = "FLOAT", mode = "NULLABLE" },
    # Technical analysis metrics (calculated fields)
    { name = "sma_50", type = "FLOAT", mode = "NULLABLE" },
    { name = "sma_200", type = "FLOAT", mode = "NULLABLE" },
    { name = "macd_histogram", type = "FLOAT", mode = "NULLABLE" },
    { name = "rsi", type = "FLOAT", mode = "NULLABLE" },
  ])
}

# Stocks Table
resource "google_bigquery_table" "stocks" {
  dataset_id          = google_bigquery_dataset.loopweave.dataset_id
  table_id            = "stocks"
  description         = "Company profile and stock information"
  deletion_protection = false

  schema = jsonencode([
    { name = "symbol", type = "STRING", mode = "REQUIRED" },
    { name = "company_name", type = "STRING", mode = "REQUIRED" },
    { name = "sector", type = "STRING", mode = "NULLABLE" },
    { name = "industry", type = "STRING", mode = "NULLABLE" },
    { name = "market_cap", type = "FLOAT", mode = "NULLABLE" },
    { name = "pe_ratio", type = "FLOAT", mode = "NULLABLE" },
    { name = "forward_pe", type = "FLOAT", mode = "NULLABLE" },
    { name = "ebitda", type = "FLOAT", mode = "NULLABLE" },
    { name = "description", type = "STRING", mode = "NULLABLE" },
    { name = "website", type = "STRING", mode = "NULLABLE" },
    { name = "logo", type = "STRING", mode = "NULLABLE" },
  ])
}

# Patterns Table
resource "google_bigquery_table" "patterns" {
  dataset_id          = google_bigquery_dataset.loopweave.dataset_id
  table_id            = "patterns"
  description         = "Candlestick and technical patterns"
  deletion_protection = false

  clustering = ["stock_symbol", "pattern_type"]

  schema = jsonencode([
    { name = "pattern_id", type = "STRING", mode = "REQUIRED" },
    { name = "stock_symbol", type = "STRING", mode = "REQUIRED" },
    { name = "pattern_type", type = "STRING", mode = "REQUIRED" },
    { name = "start_time", type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "end_time", type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "confidence", type = "FLOAT", mode = "NULLABLE" },
  ])
}

# Trades Table
resource "google_bigquery_table" "trades" {
  dataset_id          = google_bigquery_dataset.loopweave.dataset_id
  table_id            = "trades"
  description         = "Trade execution records"
  deletion_protection = false

  clustering = ["stock_symbol"]

  schema = jsonencode([
    { name = "trade_uuid", type = "STRING", mode = "REQUIRED" },
    { name = "pattern_uuid", type = "STRING", mode = "NULLABLE" },
    { name = "pattern_name", type = "STRING", mode = "NULLABLE" },
    { name = "prediction", type = "STRING", mode = "NULLABLE" },
    { name = "result", type = "STRING", mode = "NULLABLE" },
    { name = "percent", type = "FLOAT", mode = "NULLABLE" },
    { name = "stock_symbol", type = "STRING", mode = "REQUIRED" },
    { name = "position_type", type = "STRING", mode = "NULLABLE" },
    { name = "dt_open", type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "dt_close", type = "TIMESTAMP", mode = "NULLABLE" },
    { name = "stock_value_open", type = "FLOAT", mode = "REQUIRED" },
    { name = "stock_value_close", type = "FLOAT", mode = "NULLABLE" },
  ])
}

