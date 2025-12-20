from typing import Dict, Any

import pandas as pd
import pandas_ta as ta


def run(df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
    """
    RSI overbought strategy.

    Flags when RSI(14) is above 70 on the latest bar and returns recent overbought dates.
    """
    if df.empty:
        return {"message": "No data available"}

    rsi = ta.rsi(df["close"], length=14)
    df_out = df.copy()
    df_out["rsi_14"] = rsi

    overbought = df_out[df_out["rsi_14"] > 70].tail(20)

    last_idx = df_out.index[-1]
    last_rsi = float(df_out.loc[last_idx, "rsi_14"]) if pd.notna(df_out.loc[last_idx, "rsi_14"]) else None
    is_overbought = last_rsi is not None and last_rsi > 70

    events = [
        {
            "date": idx.isoformat(),
            "rsi": float(row["rsi_14"]),
        }
        for idx, row in overbought.iterrows()
        if pd.notna(row["rsi_14"])
    ]

    return {
        "symbol": symbol,
        "last_date": last_idx.isoformat(),
        "last_rsi": last_rsi,
        "is_overbought": is_overbought,
        "recent_overbought_events": events,
    }

