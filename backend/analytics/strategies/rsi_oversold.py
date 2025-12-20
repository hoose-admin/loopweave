from typing import Dict, Any

import pandas as pd
import pandas_ta as ta


def run(df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
    """
    RSI oversold strategy.

    Flags when RSI(14) is below 30 on the latest bar and returns recent oversold dates.
    """
    if df.empty:
        return {"message": "No data available"}

    rsi = ta.rsi(df["close"], length=14)
    df_out = df.copy()
    df_out["rsi_14"] = rsi

    oversold = df_out[df_out["rsi_14"] < 30].tail(20)

    last_idx = df_out.index[-1]
    last_rsi = float(df_out.loc[last_idx, "rsi_14"]) if pd.notna(df_out.loc[last_idx, "rsi_14"]) else None
    is_oversold = last_rsi is not None and last_rsi < 30

    events = [
        {
            "date": idx.isoformat(),
            "rsi": float(row["rsi_14"]),
        }
        for idx, row in oversold.iterrows()
        if pd.notna(row["rsi_14"])
    ]

    return {
        "symbol": symbol,
        "last_date": last_idx.isoformat(),
        "last_rsi": last_rsi,
        "is_oversold": is_oversold,
        "recent_oversold_events": events,
    }

