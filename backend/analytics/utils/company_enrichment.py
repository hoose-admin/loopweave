"""
Utilities for enriching company data from FMP API.

Fetches missing fields (description, website, logo, and all ratio fields)
using batch requests to minimize API calls.
"""

import os
import asyncio
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import httpx

logger = logging.getLogger(__name__)

FMP_BASE_URL = "https://financialmodelingprep.com/stable"
BATCH_SIZE = 50  # Safe limit for batch requests
RATE_LIMIT_DELAY = 0.3  # seconds between API calls


def get_fmp_api_key() -> str:
    """Get FMP API key from environment"""
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        raise ValueError("FMP_API_KEY environment variable is not set")
    return api_key


async def fetch_profiles_batch(
    symbols: List[str], api_key: str
) -> Dict[str, Dict[str, Any]]:
    """
    Fetch company profiles for a batch of symbols.
    
    Args:
        symbols: List of stock symbols (max 50 recommended)
        api_key: FMP API key
        
    Returns:
        Dictionary mapping symbol to profile data with keys:
        - description
        - website
        - logo (from 'image' field)
    """
    if not symbols:
        return {}
    
    symbols_str = ",".join(symbols)
    url = f"{FMP_BASE_URL}/profile/{symbols_str}"
    params = {"apikey": api_key}
    
    profiles = {}
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Handle both single dict and list of dicts
            if isinstance(data, dict):
                data = [data]
            elif not isinstance(data, list):
                logger.warning(f"Unexpected response format for profiles: {type(data)}")
                return {}
            
            for profile in data:
                symbol = profile.get("symbol", "").upper()
                if not symbol:
                    continue
                
                # FMP returns e.g. {"companyName": "...", "symbol": "...", ...}
                name = profile.get("companyName") or profile.get("company_name") or profile.get("name")
                
                profiles[symbol] = {
                    "name": name,
                    "description": profile.get("description"),
                    "website": profile.get("website"),
                    "logo": profile.get("image"),  # FMP uses "image" not "logo"
                }
            
            logger.info(f"Fetched profiles for {len(profiles)}/{len(symbols)} symbols")
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP Error fetching profiles: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        logger.error(f"Error fetching profiles batch: {str(e)}", exc_info=True)
    
    return profiles


async def fetch_ratios_batch(
    symbols: List[str], api_key: str
) -> Dict[str, Dict[str, Any]]:
    """
    Fetch financial ratios for a batch of symbols.
    
    Args:
        symbols: List of stock symbols (max 50 recommended)
        api_key: FMP API key
        
    Returns:
        Dictionary mapping symbol to all ratio fields from the API response.
        Converts camelCase to snake_case for consistency.
    """
    if not symbols:
        return {}
    
    symbols_str = ",".join(symbols)
    url = f"{FMP_BASE_URL}/ratios/{symbols_str}"
    params = {"apikey": api_key}
    
    ratios = {}
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Handle both single dict and list of dicts
            if isinstance(data, dict):
                data = [data]
            elif not isinstance(data, list):
                logger.warning(f"Unexpected response format for ratios: {type(data)}")
                return {}
            
            # Group by symbol (in case of multiple entries per symbol)
            # Store the first (most recent) entry for each symbol
            symbol_ratios = {}
            for ratio_data in data:
                symbol = ratio_data.get("symbol", "").upper()
                if not symbol:
                    continue
                
                if symbol not in symbol_ratios:
                    symbol_ratios[symbol] = ratio_data
            
            # Convert all fields from camelCase to snake_case
            for symbol, ratio_data in symbol_ratios.items():
                converted = {}
                for key, value in ratio_data.items():
                    # Convert camelCase to snake_case
                    snake_key = _camel_to_snake(key)
                    # Special mapping: 'date' -> 'ratio_date' to avoid conflicts
                    if snake_key == "date":
                        snake_key = "ratio_date"
                    converted[snake_key] = value
                ratios[symbol] = converted
            
            logger.info(f"Fetched ratios for {len(ratios)}/{len(symbols)} symbols")
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP Error fetching ratios: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        logger.error(f"Error fetching ratios batch: {str(e)}", exc_info=True)
    
    return ratios


def _camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case"""
    import re
    # Insert underscore before uppercase letters (except the first one)
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    # Insert underscore before uppercase letters that follow lowercase
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of specified size"""
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


async def enrich_companies(
    companies: List[Dict[str, Any]], api_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Enrich company data by fetching missing fields from FMP API.
    
    Args:
        companies: List of company dictionaries with at least 'symbol' field
        api_key: Optional FMP API key (defaults to FMP_API_KEY env var)
        
    Returns:
        List of enriched company dictionaries with additional fields:
        - description, website, logo (from profile endpoint)
        - All ratio fields from ratios endpoint (converted to snake_case)
    """
    if not api_key:
        api_key = get_fmp_api_key()
    
    if not companies:
        return []
    
    # Extract all symbols
    symbols = [c.get("symbol", "").upper() for c in companies if c.get("symbol")]
    if not symbols:
        logger.warning("No valid symbols found in companies list")
        return companies
    
    logger.info(f"Enriching {len(symbols)} companies...")
    
    # Split symbols into batches
    symbol_batches = chunk_list(symbols, BATCH_SIZE)
    logger.info(f"Split into {len(symbol_batches)} batches of up to {BATCH_SIZE} symbols each")
    
    # Fetch all data in batches (with rate limiting)
    all_profiles = {}
    all_ratios = {}
    
    # Process each endpoint type sequentially (to avoid overwhelming API)
    logger.info("Fetching profiles...")
    for i, batch in enumerate(symbol_batches):
        profiles = await fetch_profiles_batch(batch, api_key)
        all_profiles.update(profiles)
        if i < len(symbol_batches) - 1:
            await asyncio.sleep(RATE_LIMIT_DELAY)
    
    logger.info("Fetching ratios...")
    for i, batch in enumerate(symbol_batches):
        ratios = await fetch_ratios_batch(batch, api_key)
        all_ratios.update(ratios)
        if i < len(symbol_batches) - 1:
            await asyncio.sleep(RATE_LIMIT_DELAY)
    
    # Merge enriched data back into companies
    enriched_companies = []
    for company in companies:
        symbol = company.get("symbol", "").upper()
        if not symbol:
            enriched_companies.append(company)
            continue
        
        enriched = company.copy()
        
        # Add profile data
        if symbol in all_profiles:
            enriched.update(all_profiles[symbol])
        
        # Add ratios data
        if symbol in all_ratios:
            enriched.update(all_ratios[symbol])
        
        enriched_companies.append(enriched)
    
    logger.info(f"Enriched {len(enriched_companies)} companies")
    
    return enriched_companies


def load_companies_from_json(file_path: str) -> List[Dict[str, Any]]:
    """Load companies from JSON file"""
    import json
    
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Companies file not found: {file_path}")
    
    with open(path, "r") as f:
        return json.load(f)


def save_companies_to_json(companies: List[Dict[str, Any]], file_path: str):
    """Save companies to JSON file"""
    import json
    
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w") as f:
        json.dump(companies, f, indent=2)
    
    logger.info(f"Saved {len(companies)} companies to {file_path}")


async def insert_stocks_to_bigquery(
    companies: List[Dict[str, Any]], dry_run: bool = False
) -> Dict[str, Any]:
    """
    Insert enriched company data into Cloud SQL stocks table.
    
    Args:
        companies: List of enriched company dictionaries
        dry_run: If True, don't actually insert, just return what would be inserted
        
    Returns:
        Dictionary with insertion results
    """
    from utils.db import execute_insert
    
    if not companies:
        return {"inserted": 0, "errors": 0, "message": "No companies to insert"}
    
    
    # Convert companies to Cloud SQL format
    bq_rows = []
    for company in companies:
        symbol = company.get("symbol", "").upper()
        name = company.get("name", "")
        
        if not symbol or not name:
            logger.warning(f"Skipping company with missing symbol or name: {company}")
            continue
        
        bq_row = {
            "symbol": symbol,
            "name": name,
            "exchange": company.get("exchange"),
            "sector": company.get("sector"),
            "industry": company.get("industry"),
            "market_cap": company.get("marketCap") or company.get("market_cap"),
            "description": company.get("description"),
            "website": company.get("website"),
            "logo": company.get("logo"),
            # Ratio fields (all from ratios endpoint, already in snake_case)
            "ratio_date": company.get("date"),
            "fiscal_year": company.get("fiscal_year"),
            "period": company.get("period"),
            "reported_currency": company.get("reported_currency"),
            "gross_profit_margin": company.get("gross_profit_margin"),
            "ebit_margin": company.get("ebit_margin"),
            "ebitda_margin": company.get("ebitda_margin"),
            "operating_profit_margin": company.get("operating_profit_margin"),
            "pretax_profit_margin": company.get("pretax_profit_margin"),
            "continuous_operations_profit_margin": company.get("continuous_operations_profit_margin"),
            "net_profit_margin": company.get("net_profit_margin"),
            "bottom_line_profit_margin": company.get("bottom_line_profit_margin"),
            "receivables_turnover": company.get("receivables_turnover"),
            "payables_turnover": company.get("payables_turnover"),
            "inventory_turnover": company.get("inventory_turnover"),
            "fixed_asset_turnover": company.get("fixed_asset_turnover"),
            "asset_turnover": company.get("asset_turnover"),
            "current_ratio": company.get("current_ratio"),
            "quick_ratio": company.get("quick_ratio"),
            "solvency_ratio": company.get("solvency_ratio"),
            "cash_ratio": company.get("cash_ratio"),
            "pe_ratio": company.get("price_to_earnings_ratio") or company.get("pe_ratio"),  # Map from priceToEarningsRatio
            "price_to_earnings_growth_ratio": company.get("price_to_earnings_growth_ratio"),
            "forward_price_to_earnings_growth_ratio": company.get("forward_price_to_earnings_growth_ratio"),
            "price_to_book_ratio": company.get("price_to_book_ratio"),
            "price_to_sales_ratio": company.get("price_to_sales_ratio"),
            "price_to_free_cash_flow_ratio": company.get("price_to_free_cash_flow_ratio"),
            "price_to_operating_cash_flow_ratio": company.get("price_to_operating_cash_flow_ratio"),
            "debt_to_assets_ratio": company.get("debt_to_assets_ratio"),
            "debt_to_equity_ratio": company.get("debt_to_equity_ratio"),
            "debt_to_capital_ratio": company.get("debt_to_capital_ratio"),
            "long_term_debt_to_capital_ratio": company.get("long_term_debt_to_capital_ratio"),
            "financial_leverage_ratio": company.get("financial_leverage_ratio"),
            "working_capital_turnover_ratio": company.get("working_capital_turnover_ratio"),
            "operating_cash_flow_ratio": company.get("operating_cash_flow_ratio"),
            "operating_cash_flow_sales_ratio": company.get("operating_cash_flow_sales_ratio"),
            "free_cash_flow_operating_cash_flow_ratio": company.get("free_cash_flow_operating_cash_flow_ratio"),
            "debt_service_coverage_ratio": company.get("debt_service_coverage_ratio"),
            "interest_coverage_ratio": company.get("interest_coverage_ratio"),
            "short_term_operating_cash_flow_coverage_ratio": company.get("short_term_operating_cash_flow_coverage_ratio"),
            "operating_cash_flow_coverage_ratio": company.get("operating_cash_flow_coverage_ratio"),
            "capital_expenditure_coverage_ratio": company.get("capital_expenditure_coverage_ratio"),
            "dividend_paid_and_capex_coverage_ratio": company.get("dividend_paid_and_capex_coverage_ratio"),
            "dividend_payout_ratio": company.get("dividend_payout_ratio"),
            "dividend_yield": company.get("dividend_yield"),
            "dividend_yield_percentage": company.get("dividend_yield_percentage"),
            "revenue_per_share": company.get("revenue_per_share"),
            "net_income_per_share": company.get("net_income_per_share"),
            "interest_debt_per_share": company.get("interest_debt_per_share"),
            "cash_per_share": company.get("cash_per_share"),
            "book_value_per_share": company.get("book_value_per_share"),
            "tangible_book_value_per_share": company.get("tangible_book_value_per_share"),
            "shareholders_equity_per_share": company.get("shareholders_equity_per_share"),
            "operating_cash_flow_per_share": company.get("operating_cash_flow_per_share"),
            "capex_per_share": company.get("capex_per_share"),
            "free_cash_flow_per_share": company.get("free_cash_flow_per_share"),
            "net_income_per_ebt": company.get("net_income_per_ebt"),
            "ebt_per_ebit": company.get("ebt_per_ebit"),
            "price_to_fair_value": company.get("price_to_fair_value"),
            "debt_to_market_cap": company.get("debt_to_market_cap"),
            "effective_tax_rate": company.get("effective_tax_rate"),
            "enterprise_value_multiple": company.get("enterprise_value_multiple"),
            "dividend_per_share": company.get("dividend_per_share"),
        }
        bq_rows.append(bq_row)
    
    if not bq_rows:
        return {"inserted": 0, "errors": 0, "message": "No valid companies to insert"}
    
    if dry_run:
        logger.info(f"[DRY RUN] Would insert {len(bq_rows)} rows into Cloud SQL")
        return {"inserted": len(bq_rows), "errors": 0, "message": "Dry run completed"}
    
    try:
        # Use ON CONFLICT to upsert (update existing, insert new)
        on_conflict = """
            ON CONFLICT (symbol) DO UPDATE SET
                name = EXCLUDED.name,
                exchange = EXCLUDED.exchange,
                sector = EXCLUDED.sector,
                industry = EXCLUDED.industry,
                market_cap = EXCLUDED.market_cap,
                description = EXCLUDED.description,
                website = EXCLUDED.website,
                logo = EXCLUDED.logo,
                ratio_date = EXCLUDED.ratio_date,
                fiscal_year = EXCLUDED.fiscal_year,
                period = EXCLUDED.period,
                reported_currency = EXCLUDED.reported_currency,
                gross_profit_margin = EXCLUDED.gross_profit_margin,
                ebit_margin = EXCLUDED.ebit_margin,
                ebitda_margin = EXCLUDED.ebitda_margin,
                operating_profit_margin = EXCLUDED.operating_profit_margin,
                pretax_profit_margin = EXCLUDED.pretax_profit_margin,
                continuous_operations_profit_margin = EXCLUDED.continuous_operations_profit_margin,
                net_profit_margin = EXCLUDED.net_profit_margin,
                bottom_line_profit_margin = EXCLUDED.bottom_line_profit_margin,
                receivables_turnover = EXCLUDED.receivables_turnover,
                payables_turnover = EXCLUDED.payables_turnover,
                inventory_turnover = EXCLUDED.inventory_turnover,
                fixed_asset_turnover = EXCLUDED.fixed_asset_turnover,
                asset_turnover = EXCLUDED.asset_turnover,
                current_ratio = EXCLUDED.current_ratio,
                quick_ratio = EXCLUDED.quick_ratio,
                solvency_ratio = EXCLUDED.solvency_ratio,
                cash_ratio = EXCLUDED.cash_ratio,
                pe_ratio = EXCLUDED.pe_ratio,
                price_to_earnings_growth_ratio = EXCLUDED.price_to_earnings_growth_ratio,
                forward_price_to_earnings_growth_ratio = EXCLUDED.forward_price_to_earnings_growth_ratio,
                price_to_book_ratio = EXCLUDED.price_to_book_ratio,
                price_to_sales_ratio = EXCLUDED.price_to_sales_ratio,
                price_to_free_cash_flow_ratio = EXCLUDED.price_to_free_cash_flow_ratio,
                price_to_operating_cash_flow_ratio = EXCLUDED.price_to_operating_cash_flow_ratio,
                debt_to_assets_ratio = EXCLUDED.debt_to_assets_ratio,
                debt_to_equity_ratio = EXCLUDED.debt_to_equity_ratio,
                debt_to_capital_ratio = EXCLUDED.debt_to_capital_ratio,
                long_term_debt_to_capital_ratio = EXCLUDED.long_term_debt_to_capital_ratio,
                financial_leverage_ratio = EXCLUDED.financial_leverage_ratio,
                working_capital_turnover_ratio = EXCLUDED.working_capital_turnover_ratio,
                operating_cash_flow_ratio = EXCLUDED.operating_cash_flow_ratio,
                operating_cash_flow_sales_ratio = EXCLUDED.operating_cash_flow_sales_ratio,
                free_cash_flow_operating_cash_flow_ratio = EXCLUDED.free_cash_flow_operating_cash_flow_ratio,
                debt_service_coverage_ratio = EXCLUDED.debt_service_coverage_ratio,
                interest_coverage_ratio = EXCLUDED.interest_coverage_ratio,
                short_term_operating_cash_flow_coverage_ratio = EXCLUDED.short_term_operating_cash_flow_coverage_ratio,
                operating_cash_flow_coverage_ratio = EXCLUDED.operating_cash_flow_coverage_ratio,
                capital_expenditure_coverage_ratio = EXCLUDED.capital_expenditure_coverage_ratio,
                dividend_paid_and_capex_coverage_ratio = EXCLUDED.dividend_paid_and_capex_coverage_ratio,
                dividend_payout_ratio = EXCLUDED.dividend_payout_ratio,
                dividend_yield = EXCLUDED.dividend_yield,
                dividend_yield_percentage = EXCLUDED.dividend_yield_percentage,
                revenue_per_share = EXCLUDED.revenue_per_share,
                net_income_per_share = EXCLUDED.net_income_per_share,
                interest_debt_per_share = EXCLUDED.interest_debt_per_share,
                cash_per_share = EXCLUDED.cash_per_share,
                book_value_per_share = EXCLUDED.book_value_per_share,
                tangible_book_value_per_share = EXCLUDED.tangible_book_value_per_share,
                shareholders_equity_per_share = EXCLUDED.shareholders_equity_per_share,
                operating_cash_flow_per_share = EXCLUDED.operating_cash_flow_per_share,
                capex_per_share = EXCLUDED.capex_per_share,
                free_cash_flow_per_share = EXCLUDED.free_cash_flow_per_share,
                net_income_per_ebt = EXCLUDED.net_income_per_ebt,
                ebt_per_ebit = EXCLUDED.ebt_per_ebit,
                price_to_fair_value = EXCLUDED.price_to_fair_value,
                debt_to_market_cap = EXCLUDED.debt_to_market_cap,
                effective_tax_rate = EXCLUDED.effective_tax_rate,
                enterprise_value_multiple = EXCLUDED.enterprise_value_multiple,
                dividend_per_share = EXCLUDED.dividend_per_share
        """
        
        execute_insert("stocks", bq_rows, on_conflict=on_conflict)
        
        logger.info(f"Successfully inserted {len(bq_rows)} stocks into Cloud SQL")
        return {
            "inserted": len(bq_rows),
            "errors": 0,
            "message": f"Successfully inserted {len(bq_rows)} stocks",
        }
        
    except Exception as e:
        logger.error(f"Error inserting to Cloud SQL: {str(e)}", exc_info=True)
        return {
            "inserted": 0,
            "errors": len(bq_rows),
            "message": f"Error: {str(e)}",
        }
