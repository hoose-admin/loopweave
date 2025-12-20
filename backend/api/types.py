from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Stock(BaseModel):
    symbol: str
    name: str
    exchange: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    description: Optional[str] = None
    website: Optional[str] = None
    logo: Optional[str] = None
    # Ratio fields (all from /stable/ratios endpoint)
    ratio_date: Optional[str] = None
    fiscal_year: Optional[str] = None
    period: Optional[str] = None
    reported_currency: Optional[str] = None
    gross_profit_margin: Optional[float] = None
    ebit_margin: Optional[float] = None
    ebitda_margin: Optional[float] = None
    operating_profit_margin: Optional[float] = None
    pretax_profit_margin: Optional[float] = None
    continuous_operations_profit_margin: Optional[float] = None
    net_profit_margin: Optional[float] = None
    bottom_line_profit_margin: Optional[float] = None
    receivables_turnover: Optional[float] = None
    payables_turnover: Optional[float] = None
    inventory_turnover: Optional[float] = None
    fixed_asset_turnover: Optional[float] = None
    asset_turnover: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    solvency_ratio: Optional[float] = None
    cash_ratio: Optional[float] = None
    pe_ratio: Optional[float] = None
    price_to_earnings_growth_ratio: Optional[float] = None
    forward_price_to_earnings_growth_ratio: Optional[float] = None
    price_to_book_ratio: Optional[float] = None
    price_to_sales_ratio: Optional[float] = None
    price_to_free_cash_flow_ratio: Optional[float] = None
    price_to_operating_cash_flow_ratio: Optional[float] = None
    debt_to_assets_ratio: Optional[float] = None
    debt_to_equity_ratio: Optional[float] = None
    debt_to_capital_ratio: Optional[float] = None
    long_term_debt_to_capital_ratio: Optional[float] = None
    financial_leverage_ratio: Optional[float] = None
    working_capital_turnover_ratio: Optional[float] = None
    operating_cash_flow_ratio: Optional[float] = None
    operating_cash_flow_sales_ratio: Optional[float] = None
    free_cash_flow_operating_cash_flow_ratio: Optional[float] = None
    debt_service_coverage_ratio: Optional[float] = None
    interest_coverage_ratio: Optional[float] = None
    short_term_operating_cash_flow_coverage_ratio: Optional[float] = None
    operating_cash_flow_coverage_ratio: Optional[float] = None
    capital_expenditure_coverage_ratio: Optional[float] = None
    dividend_paid_and_capex_coverage_ratio: Optional[float] = None
    dividend_payout_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    dividend_yield_percentage: Optional[float] = None
    revenue_per_share: Optional[float] = None
    net_income_per_share: Optional[float] = None
    interest_debt_per_share: Optional[float] = None
    cash_per_share: Optional[float] = None
    book_value_per_share: Optional[float] = None
    tangible_book_value_per_share: Optional[float] = None
    shareholders_equity_per_share: Optional[float] = None
    operating_cash_flow_per_share: Optional[float] = None
    capex_per_share: Optional[float] = None
    free_cash_flow_per_share: Optional[float] = None
    net_income_per_ebt: Optional[float] = None
    ebt_per_ebit: Optional[float] = None
    price_to_fair_value: Optional[float] = None
    debt_to_market_cap: Optional[float] = None
    effective_tax_rate: Optional[float] = None
    enterprise_value_multiple: Optional[float] = None
    dividend_per_share: Optional[float] = None

class TimeSeriesData(BaseModel):
    symbol: str
    date: str
    # FMP API fields from historical-price-eod/full endpoint (daily EOD data)
    open: float
    high: float
    low: float
    close: float
    volume: float
    unadjusted_close: Optional[float] = None
    unadjusted_volume: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    vwap: Optional[float] = None
    label: Optional[str] = None
    change_over_time: Optional[float] = None
    # Technical analysis metrics (calculated fields)
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    rsi: Optional[float] = None

class Pattern(BaseModel):
    pattern_id: str
    stock_symbol: str
    pattern_type: str
    start_time: str
    end_time: str
    confidence: Optional[float] = None

class Trade(BaseModel):
    trade_uuid: str
    pattern_uuid: Optional[str] = None
    pattern_name: Optional[str] = None
    prediction: Optional[str] = None
    result: Optional[str] = None  # "correct" or "incorrect"
    percent: Optional[float] = None
    stock_symbol: str
    position_type: Optional[str] = None  # "long" or "short"
    dt_open: str
    dt_close: Optional[str] = None
    stock_value_open: float
    stock_value_close: Optional[float] = None
