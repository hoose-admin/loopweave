-- Cloud SQL PostgreSQL Schema Migration
-- Run this file after Terraform creates the Cloud SQL instance
-- Usage: psql "host=/cloudsql/PROJECT:REGION:INSTANCE dbname=loopweave user=loopweave_app" -f 001_create_tables.sql

-- Timeseries Table (Daily)
CREATE TABLE IF NOT EXISTS timeseries (
    symbol VARCHAR(10) NOT NULL,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    -- OHLCV Data (adjusted prices from dividend-adjusted endpoint)
    open DOUBLE PRECISION NOT NULL,
    high DOUBLE PRECISION NOT NULL,
    low DOUBLE PRECISION NOT NULL,
    close DOUBLE PRECISION NOT NULL,
    volume DOUBLE PRECISION NOT NULL,
    -- Optional FMP fields
    change DOUBLE PRECISION,
    change_percent DOUBLE PRECISION,
    vwap DOUBLE PRECISION,
    -- Simple Moving Averages
    sma_20 DOUBLE PRECISION,
    sma_50 DOUBLE PRECISION,
    sma_200 DOUBLE PRECISION,
    -- Exponential Moving Averages
    ema_12 DOUBLE PRECISION,
    ema_20 DOUBLE PRECISION,
    ema_26 DOUBLE PRECISION,
    -- MACD
    macd_line DOUBLE PRECISION,
    macd_signal_line DOUBLE PRECISION,
    macd_histogram DOUBLE PRECISION,
    -- Momentum Indicators
    rsi DOUBLE PRECISION,
    -- Volatility Indicators
    atr DOUBLE PRECISION,
    -- Bollinger Bands
    bb_upper DOUBLE PRECISION,
    bb_lower DOUBLE PRECISION,
    PRIMARY KEY (symbol, date)
);

-- Timeseries 4-Hour Table
CREATE TABLE IF NOT EXISTS timeseries_4h (
    symbol VARCHAR(10) NOT NULL,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    -- OHLCV Data (from 4-hour endpoint)
    open DOUBLE PRECISION NOT NULL,
    high DOUBLE PRECISION NOT NULL,
    low DOUBLE PRECISION NOT NULL,
    close DOUBLE PRECISION NOT NULL,
    volume DOUBLE PRECISION NOT NULL,
    -- Simple Moving Averages
    sma_20 DOUBLE PRECISION,
    sma_50 DOUBLE PRECISION,
    sma_200 DOUBLE PRECISION,
    -- Exponential Moving Averages
    ema_12 DOUBLE PRECISION,
    ema_20 DOUBLE PRECISION,
    ema_26 DOUBLE PRECISION,
    -- MACD
    macd_line DOUBLE PRECISION,
    macd_signal_line DOUBLE PRECISION,
    macd_histogram DOUBLE PRECISION,
    -- Momentum Indicators
    rsi DOUBLE PRECISION,
    -- Volatility Indicators
    atr DOUBLE PRECISION,
    -- Bollinger Bands
    bb_upper DOUBLE PRECISION,
    bb_lower DOUBLE PRECISION,
    PRIMARY KEY (symbol, date)
);

-- Stocks Table
CREATE TABLE IF NOT EXISTS stocks (
    symbol VARCHAR(10) NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    exchange VARCHAR(20),
    sector TEXT,
    industry TEXT,
    market_cap DOUBLE PRECISION,
    description TEXT,
    website TEXT,
    logo TEXT,
    -- Ratio fields from /stable/ratios endpoint
    ratio_date VARCHAR(20),
    fiscal_year VARCHAR(10),
    period VARCHAR(10),
    reported_currency VARCHAR(10),
    gross_profit_margin DOUBLE PRECISION,
    ebit_margin DOUBLE PRECISION,
    ebitda_margin DOUBLE PRECISION,
    operating_profit_margin DOUBLE PRECISION,
    pretax_profit_margin DOUBLE PRECISION,
    continuous_operations_profit_margin DOUBLE PRECISION,
    net_profit_margin DOUBLE PRECISION,
    bottom_line_profit_margin DOUBLE PRECISION,
    receivables_turnover DOUBLE PRECISION,
    payables_turnover DOUBLE PRECISION,
    inventory_turnover DOUBLE PRECISION,
    fixed_asset_turnover DOUBLE PRECISION,
    asset_turnover DOUBLE PRECISION,
    current_ratio DOUBLE PRECISION,
    quick_ratio DOUBLE PRECISION,
    solvency_ratio DOUBLE PRECISION,
    cash_ratio DOUBLE PRECISION,
    pe_ratio DOUBLE PRECISION,
    price_to_earnings_growth_ratio DOUBLE PRECISION,
    forward_price_to_earnings_growth_ratio DOUBLE PRECISION,
    price_to_book_ratio DOUBLE PRECISION,
    price_to_sales_ratio DOUBLE PRECISION,
    price_to_free_cash_flow_ratio DOUBLE PRECISION,
    price_to_operating_cash_flow_ratio DOUBLE PRECISION,
    debt_to_assets_ratio DOUBLE PRECISION,
    debt_to_equity_ratio DOUBLE PRECISION,
    debt_to_capital_ratio DOUBLE PRECISION,
    long_term_debt_to_capital_ratio DOUBLE PRECISION,
    financial_leverage_ratio DOUBLE PRECISION,
    working_capital_turnover_ratio DOUBLE PRECISION,
    operating_cash_flow_ratio DOUBLE PRECISION,
    operating_cash_flow_sales_ratio DOUBLE PRECISION,
    free_cash_flow_operating_cash_flow_ratio DOUBLE PRECISION,
    debt_service_coverage_ratio DOUBLE PRECISION,
    interest_coverage_ratio DOUBLE PRECISION,
    short_term_operating_cash_flow_coverage_ratio DOUBLE PRECISION,
    operating_cash_flow_coverage_ratio DOUBLE PRECISION,
    capital_expenditure_coverage_ratio DOUBLE PRECISION,
    dividend_paid_and_capex_coverage_ratio DOUBLE PRECISION,
    dividend_payout_ratio DOUBLE PRECISION,
    dividend_yield DOUBLE PRECISION,
    dividend_yield_percentage DOUBLE PRECISION,
    revenue_per_share DOUBLE PRECISION,
    net_income_per_share DOUBLE PRECISION,
    interest_debt_per_share DOUBLE PRECISION,
    cash_per_share DOUBLE PRECISION,
    book_value_per_share DOUBLE PRECISION,
    tangible_book_value_per_share DOUBLE PRECISION,
    shareholders_equity_per_share DOUBLE PRECISION,
    operating_cash_flow_per_share DOUBLE PRECISION,
    capex_per_share DOUBLE PRECISION,
    free_cash_flow_per_share DOUBLE PRECISION,
    net_income_per_ebt DOUBLE PRECISION,
    ebt_per_ebit DOUBLE PRECISION,
    price_to_fair_value DOUBLE PRECISION,
    debt_to_market_cap DOUBLE PRECISION,
    effective_tax_rate DOUBLE PRECISION,
    enterprise_value_multiple DOUBLE PRECISION,
    dividend_per_share DOUBLE PRECISION
);

-- Patterns Table
CREATE TABLE IF NOT EXISTS patterns (
    pattern_id VARCHAR(255) NOT NULL PRIMARY KEY,
    stock_symbol VARCHAR(10) NOT NULL,
    pattern_type VARCHAR(100) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    confidence DOUBLE PRECISION
);

-- Trades Table
CREATE TABLE IF NOT EXISTS trades (
    trade_uuid VARCHAR(255) NOT NULL PRIMARY KEY,
    pattern_uuid VARCHAR(255),
    pattern_name VARCHAR(100),
    prediction VARCHAR(50),
    result VARCHAR(50),
    percent DOUBLE PRECISION,
    stock_symbol VARCHAR(10) NOT NULL,
    position_type VARCHAR(10),
    dt_open TIMESTAMP WITH TIME ZONE NOT NULL,
    dt_close TIMESTAMP WITH TIME ZONE,
    stock_value_open DOUBLE PRECISION NOT NULL,
    stock_value_close DOUBLE PRECISION
);
