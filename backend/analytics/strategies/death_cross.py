from typing import Dict, Any

import pandas as pd
import pandas_ta as ta


def run(df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
    """
    Death cross strategy: SMA50 crossing below SMA200.

    Returns the most recent death cross signal, if any.
    """
    if df.empty:
        return {"message": "No data available"}

    close = df["close"]
    sma50 = ta.sma(close, length=50)
    sma200 = ta.sma(close, length=200)

    df_out = df.copy()
    df_out["sma_50"] = sma50
    df_out["sma_200"] = sma200

    df_valid = df_out.dropna(subset=["sma_50", "sma_200"])
    if df_valid.empty:
        return {"message": "Not enough data for SMA50/SMA200"}

    # Death cross where SMA50 crosses below SMA200
    prev = df_valid[["sma_50", "sma_200"]].shift(1)
    cross = (df_valid["sma_50"] < df_valid["sma_200"]) & (
        (prev["sma_50"] >= prev["sma_200"])
    )
    events = df_valid[cross]

    if events.empty:
        return {"message": "No death cross detected", "has_signal": False}

    last_idx = events.index[-1]
    row = events.loc[last_idx]

    return {
        "has_signal": True,
        "symbol": symbol,
        "signal_date": last_idx.isoformat(),
        "sma_50": float(row["sma_50"]),
        "sma_200": float(row["sma_200"]),
    }

