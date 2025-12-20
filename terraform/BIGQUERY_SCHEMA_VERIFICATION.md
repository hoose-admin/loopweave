# BigQuery Schema Verification

## Summary

All tables from plan.md are now included in the setup script. Here's the verification:

## Tables in plan.md

1. ✅ **timeseries** - Matches plan.md and Python `TimeSeriesData` type
2. ✅ **stocks** - Matches plan.md and Python `Stock` type
3. ✅ **patterns** - Matches plan.md basic schema and Python `Pattern` type
4. ✅ **trades** - Added to match plan.md schema (lines 278-293)

## Schema Verification

### 1. timeseries Table

**BigQuery Schema:**

- stock_symbol:STRING:REQUIRED
- timestamp:TIMESTAMP:REQUIRED
- open:FLOAT:REQUIRED
- high:FLOAT:REQUIRED
- low:FLOAT:REQUIRED
- close:FLOAT:REQUIRED
- volume:FLOAT:REQUIRED
- ema_12:FLOAT
- ema_26:FLOAT
- sma_50:FLOAT
- sma_200:FLOAT
- macd:FLOAT
- macd_signal:FLOAT
- macd_histogram:FLOAT
- rsi:FLOAT

**Python Type:** `TimeSeriesData` ✅ MATCHES

**Indexing:**

- Partitioned by: `timestamp`
- Clustered by: `stock_symbol`

### 2. stocks Table

**BigQuery Schema:**

- symbol:STRING:REQUIRED
- name:STRING:REQUIRED
- exchange:STRING
- sector:STRING
- industry:STRING
- market_cap:FLOAT
- pe_ratio:FLOAT
- forward_pe:FLOAT
- ebitda:FLOAT
- description:STRING
- website:STRING
- logo:STRING

**Python Type:** `Stock` ✅ MATCHES

### 3. patterns Table

**BigQuery Schema:**

- pattern_id:STRING:REQUIRED
- stock_symbol:STRING:REQUIRED
- pattern_type:STRING:REQUIRED
- start_time:TIMESTAMP:REQUIRED
- end_time:TIMESTAMP:REQUIRED
- confidence:FLOAT

**Python Type:** `Pattern` ✅ MATCHES

**Indexing:**

- Clustered by: `stock_symbol`, `pattern_type`

**Note:** plan.md (lines 262-277) mentions additional fields that could be added later:

- context DT start/end
- volume metrics
- RSI, MACD (could be joined from timeseries)
- stock type, market (could be joined from stocks)
- candle wick info

These are not in the current implementation but can be added as needed.

### 4. trades Table

**BigQuery Schema:**

- trade_uuid:STRING:REQUIRED
- pattern_uuid:STRING
- pattern_name:STRING
- prediction:STRING
- result:STRING (correct/incorrect)
- percent:FLOAT
- stock_symbol:STRING:REQUIRED
- position_type:STRING (long/short)
- dt_open:TIMESTAMP:REQUIRED
- dt_close:TIMESTAMP
- stock_value_open:FLOAT:REQUIRED
- stock_value_close:FLOAT

**Python Type:** `Trade` ✅ ADDED TO types.py

**Indexing:**

- Clustered by: `stock_symbol`

**Note:** This table matches plan.md schema (lines 278-293)

## Verification Complete ✅

All tables from plan.md are now in the setup script and match the Python type definitions.
