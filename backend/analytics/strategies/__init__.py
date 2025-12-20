from typing import Callable, Dict, Any

import pandas as pd

from .sma_20 import run as sma_20_run
from .golden_cross import run as golden_cross_run
from .death_cross import run as death_cross_run
from .rsi_overbought import run as rsi_overbought_run
from .rsi_oversold import run as rsi_oversold_run


StrategyFunc = Callable[[pd.DataFrame, str], Dict[str, Any]]


STRATEGIES: Dict[str, StrategyFunc] = {
    "20sma": sma_20_run,
    "sma_20": sma_20_run,
    "golden_cross": golden_cross_run,
    "death_cross": death_cross_run,
    "rsi_overbought": rsi_overbought_run,
    "rsi_oversold": rsi_oversold_run,
}

