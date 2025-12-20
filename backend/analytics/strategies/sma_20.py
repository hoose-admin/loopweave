from typing import Dict, Any

import pandas as pd
import pandas_ta as ta


def run(df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
    """
    20‑period simple moving average strategy.

    Returns the latest close, SMA20 value, and whether price is above/below SMA20.
    """
    if df.empty:
        return {"message": "No data available"}

    close = df["close"]
    sma20 = ta.sma(close, length=20)

    df_out = df.copy()
    df_out["sma_20"] = sma20

    last_idx = df_out.index[-1]
    last_close = float(df_out.loc[last_idx, "close"])
    last_sma20 = float(df_out.loc[last_idx, "sma_20"]) if pd.notna(df_out.loc[last_idx, "sma_20"]) else None

    signal = None
    if last_sma20 is not None:
        if last_close > last_sma20:
            signal = "above_sma_20"
        elif last_close < last_sma20:
            signal = "below_sma_20"

    return {
        "symbol": symbol,
        "last_date": last_idx.isoformat(),
        "last_close": last_close,
        "last_sma_20": last_sma20,
        "signal": signal,
    }

