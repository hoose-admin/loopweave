# BigQuery Dataset
resource "google_bigquery_dataset" "loopweave" {
  dataset_id  = var.bigquery_dataset_id
  location    = var.bigquery_location
  description = "LoopWeave financial data warehouse"
}

# Timeseries Table (Daily)
resource "google_bigquery_table" "timeseries" {
  dataset_id          = google_bigquery_dataset.loopweave.dataset_id
  table_id            = "timeseries"
  description         = "Stock price timeseries data with technical analysis metrics (daily EOD, dividend-adjusted)"
  deletion_protection = false

  # No time partitioning - we always query by symbol first, never by date across all symbols
  # Clustering by symbol then date ensures efficient queries: WHERE symbol = 'X' AND date >= 'Y'
  clustering = ["symbol", "date"]

  schema = jsonencode([
    { name = "symbol", type = "STRING", mode = "REQUIRED" },
    { name = "date", type = "TIMESTAMP", mode = "REQUIRED" },
    # OHLCV Data (adjusted prices from dividend-adjusted endpoint)
    { name = "open", type = "FLOAT", mode = "REQUIRED" },
    { name = "high", type = "FLOAT", mode = "REQUIRED" },
    { name = "low", type = "FLOAT", mode = "REQUIRED" },
    { name = "close", type = "FLOAT", mode = "REQUIRED" },
    { name = "volume", type = "FLOAT", mode = "REQUIRED" },
    # Optional FMP fields
    { name = "change", type = "FLOAT", mode = "NULLABLE" },
    { name = "change_percent", type = "FLOAT", mode = "NULLABLE" },
    { name = "vwap", type = "FLOAT", mode = "NULLABLE" },
    # Simple Moving Averages
    { name = "sma_20", type = "FLOAT", mode = "NULLABLE" },
    { name = "sma_50", type = "FLOAT", mode = "NULLABLE" },
    { name = "sma_200", type = "FLOAT", mode = "NULLABLE" },
    # Exponential Moving Averages
    { name = "ema_12", type = "FLOAT", mode = "NULLABLE" },
    { name = "ema_20", type = "FLOAT", mode = "NULLABLE" },
    { name = "ema_26", type = "FLOAT", mode = "NULLABLE" },
    # MACD
    { name = "macd_line", type = "FLOAT", mode = "NULLABLE" },
    { name = "macd_signal_line", type = "FLOAT", mode = "NULLABLE" },
    { name = "macd_histogram", type = "FLOAT", mode = "NULLABLE" },
    # Momentum Indicators
    { name = "rsi", type = "FLOAT", mode = "NULLABLE" },
    # Volatility Indicators
    { name = "atr", type = "FLOAT", mode = "NULLABLE" },
    # Bollinger Bands
    { name = "bb_upper", type = "FLOAT", mode = "NULLABLE" },
    { name = "bb_lower", type = "FLOAT", mode = "NULLABLE" },
  ])
}

# Timeseries 4-Hour Table
resource "google_bigquery_table" "timeseries_4h" {
  dataset_id          = google_bigquery_dataset.loopweave.dataset_id
  table_id            = "timeseries_4h"
  description         = "Stock price timeseries data with technical analysis metrics (4-hour intervals)"
  deletion_protection = false

  clustering = ["symbol", "date"]

  schema = jsonencode([
    { name = "symbol", type = "STRING", mode = "REQUIRED" },
    { name = "date", type = "TIMESTAMP", mode = "REQUIRED" },
    # OHLCV Data (from 4-hour endpoint)
    { name = "open", type = "FLOAT", mode = "REQUIRED" },
    { name = "high", type = "FLOAT", mode = "REQUIRED" },
    { name = "low", type = "FLOAT", mode = "REQUIRED" },
    { name = "close", type = "FLOAT", mode = "REQUIRED" },
    { name = "volume", type = "FLOAT", mode = "REQUIRED" },
    # Simple Moving Averages
    { name = "sma_20", type = "FLOAT", mode = "NULLABLE" },
    { name = "sma_50", type = "FLOAT", mode = "NULLABLE" },
    { name = "sma_200", type = "FLOAT", mode = "NULLABLE" },
    # Exponential Moving Averages
    { name = "ema_12", type = "FLOAT", mode = "NULLABLE" },
    { name = "ema_20", type = "FLOAT", mode = "NULLABLE" },
    { name = "ema_26", type = "FLOAT", mode = "NULLABLE" },
    # MACD
    { name = "macd_line", type = "FLOAT", mode = "NULLABLE" },
    { name = "macd_signal_line", type = "FLOAT", mode = "NULLABLE" },
    { name = "macd_histogram", type = "FLOAT", mode = "NULLABLE" },
    # Momentum Indicators
    { name = "rsi", type = "FLOAT", mode = "NULLABLE" },
    # Volatility Indicators
    { name = "atr", type = "FLOAT", mode = "NULLABLE" },
    # Bollinger Bands
    { name = "bb_upper", type = "FLOAT", mode = "NULLABLE" },
    { name = "bb_lower", type = "FLOAT", mode = "NULLABLE" },
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
    { name = "name", type = "STRING", mode = "REQUIRED" },
    { name = "exchange", type = "STRING", mode = "NULLABLE" },
    { name = "sector", type = "STRING", mode = "NULLABLE" },
    { name = "industry", type = "STRING", mode = "NULLABLE" },
    { name = "market_cap", type = "FLOAT", mode = "NULLABLE" },
    { name = "description", type = "STRING", mode = "NULLABLE" },
    { name = "website", type = "STRING", mode = "NULLABLE" },
    { name = "logo", type = "STRING", mode = "NULLABLE" },
    # Ratio fields from /stable/ratios endpoint
    { name = "ratio_date", type = "STRING", mode = "NULLABLE" },
    { name = "fiscal_year", type = "STRING", mode = "NULLABLE" },
    { name = "period", type = "STRING", mode = "NULLABLE" },
    { name = "reported_currency", type = "STRING", mode = "NULLABLE" },
    { name = "gross_profit_margin", type = "FLOAT", mode = "NULLABLE" },
    { name = "ebit_margin", type = "FLOAT", mode = "NULLABLE" },
    { name = "ebitda_margin", type = "FLOAT", mode = "NULLABLE" },
    { name = "operating_profit_margin", type = "FLOAT", mode = "NULLABLE" },
    { name = "pretax_profit_margin", type = "FLOAT", mode = "NULLABLE" },
    { name = "continuous_operations_profit_margin", type = "FLOAT", mode = "NULLABLE" },
    { name = "net_profit_margin", type = "FLOAT", mode = "NULLABLE" },
    { name = "bottom_line_profit_margin", type = "FLOAT", mode = "NULLABLE" },
    { name = "receivables_turnover", type = "FLOAT", mode = "NULLABLE" },
    { name = "payables_turnover", type = "FLOAT", mode = "NULLABLE" },
    { name = "inventory_turnover", type = "FLOAT", mode = "NULLABLE" },
    { name = "fixed_asset_turnover", type = "FLOAT", mode = "NULLABLE" },
    { name = "asset_turnover", type = "FLOAT", mode = "NULLABLE" },
    { name = "current_ratio", type = "FLOAT", mode = "NULLABLE" },
    { name = "quick_ratio", type = "FLOAT", mode = "NULLABLE" },
    { name = "solvency_ratio", type = "FLOAT", mode = "NULLABLE" },
    { name = "cash_ratio", type = "FLOAT", mode = "NULLABLE" },
    { name = "pe_ratio", type = "FLOAT", mode = "NULLABLE" },
    { name = "price_to_earnings_growth_ratio", type = "FLOAT", mode = "NULLABLE" },
    { name = "forward_price_to_earnings_growth_ratio", type = "FLOAT", mode = "NULLABLE" },
    { name = "price_to_book_ratio", type = "FLOAT", mode = "NULLABLE" },
    { name = "price_to_sales_ratio", type = "FLOAT", mode = "NULLABLE" },
    { name = "price_to_free_cash_flow_ratio", type = "FLOAT", mode = "NULLABLE" },
    { name = "price_to_operating_cash_flow_ratio", type = "FLOAT", mode = "NULLABLE" },
    { name = "debt_to_assets_ratio", type = "FLOAT", mode = "NULLABLE" },
    { name = "debt_to_equity_ratio", type = "FLOAT", mode = "NULLABLE" },
    { name = "debt_to_capital_ratio", type = "FLOAT", mode = "NULLABLE" },
    { name = "long_term_debt_to_capital_ratio", type = "FLOAT", mode = "NULLABLE" },
    { name = "financial_leverage_ratio", type = "FLOAT", mode = "NULLABLE" },
    { name = "working_capital_turnover_ratio", type = "FLOAT", mode = "NULLABLE" },
    { name = "operating_cash_flow_ratio", type = "FLOAT", mode = "NULLABLE" },
    { name = "operating_cash_flow_sales_ratio", type = "FLOAT", mode = "NULLABLE" },
    { name = "free_cash_flow_operating_cash_flow_ratio", type = "FLOAT", mode = "NULLABLE" },
    { name = "debt_service_coverage_ratio", type = "FLOAT", mode = "NULLABLE" },
    { name = "interest_coverage_ratio", type = "FLOAT", mode = "NULLABLE" },
    { name = "short_term_operating_cash_flow_coverage_ratio", type = "FLOAT", mode = "NULLABLE" },
    { name = "operating_cash_flow_coverage_ratio", type = "FLOAT", mode = "NULLABLE" },
    { name = "capital_expenditure_coverage_ratio", type = "FLOAT", mode = "NULLABLE" },
    { name = "dividend_paid_and_capex_coverage_ratio", type = "FLOAT", mode = "NULLABLE" },
    { name = "dividend_payout_ratio", type = "FLOAT", mode = "NULLABLE" },
    { name = "dividend_yield", type = "FLOAT", mode = "NULLABLE" },
    { name = "dividend_yield_percentage", type = "FLOAT", mode = "NULLABLE" },
    { name = "revenue_per_share", type = "FLOAT", mode = "NULLABLE" },
    { name = "net_income_per_share", type = "FLOAT", mode = "NULLABLE" },
    { name = "interest_debt_per_share", type = "FLOAT", mode = "NULLABLE" },
    { name = "cash_per_share", type = "FLOAT", mode = "NULLABLE" },
    { name = "book_value_per_share", type = "FLOAT", mode = "NULLABLE" },
    { name = "tangible_book_value_per_share", type = "FLOAT", mode = "NULLABLE" },
    { name = "shareholders_equity_per_share", type = "FLOAT", mode = "NULLABLE" },
    { name = "operating_cash_flow_per_share", type = "FLOAT", mode = "NULLABLE" },
    { name = "capex_per_share", type = "FLOAT", mode = "NULLABLE" },
    { name = "free_cash_flow_per_share", type = "FLOAT", mode = "NULLABLE" },
    { name = "net_income_per_ebt", type = "FLOAT", mode = "NULLABLE" },
    { name = "ebt_per_ebit", type = "FLOAT", mode = "NULLABLE" },
    { name = "price_to_fair_value", type = "FLOAT", mode = "NULLABLE" },
    { name = "debt_to_market_cap", type = "FLOAT", mode = "NULLABLE" },
    { name = "effective_tax_rate", type = "FLOAT", mode = "NULLABLE" },
    { name = "enterprise_value_multiple", type = "FLOAT", mode = "NULLABLE" },
    { name = "dividend_per_share", type = "FLOAT", mode = "NULLABLE" },
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

