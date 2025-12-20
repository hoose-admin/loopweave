-- Cloud SQL PostgreSQL Indexes
-- Run this file after 001_create_tables.sql
-- Usage: psql "host=/cloudsql/PROJECT:REGION:INSTANCE dbname=loopweave user=loopweave_app" -f 002_create_indexes.sql

-- Note: Primary keys automatically create indexes, so we only need additional indexes for lookup columns

-- Patterns: Index on stock_symbol for filtering patterns by symbol
CREATE INDEX IF NOT EXISTS idx_patterns_stock_symbol ON patterns(stock_symbol);

-- Patterns: Index on pattern_type for filtering by pattern type
CREATE INDEX IF NOT EXISTS idx_patterns_pattern_type ON patterns(pattern_type);

-- Trades: Index on stock_symbol for filtering trades by symbol
CREATE INDEX IF NOT EXISTS idx_trades_stock_symbol ON trades(stock_symbol);

-- Optional: Date index for timeseries tables ONLY if cross-symbol date queries are needed
-- Uncomment if you need to query by date across all symbols
-- CREATE INDEX IF NOT EXISTS idx_timeseries_date ON timeseries(date);
-- CREATE INDEX IF NOT EXISTS idx_timeseries_4h_date ON timeseries_4h(date);
