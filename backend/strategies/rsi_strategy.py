import pandas as pd
import pandas_ta as ta
from .base_strategy import BaseStrategy

class RSIStrategy(BaseStrategy):
    def __init__(self, df: pd.DataFrame, rsi_period: int, rsi_low: int, rsi_high: int):
        super().__init__(df)
        self.rsi_period = rsi_period
        self.rsi_low = rsi_low
        self.rsi_high = rsi_high

    def generate_signal(self) -> str:
        df = self.df.copy()
        df.ta.rsi(length=self.rsi_period, append=True)
        rsi_col = f'RSI_{self.rsi_period}'
        if rsi_col not in df.columns or len(df) < self.rsi_period + 2: return 'HOLD'
        last_rsi = df[rsi_col].iloc[-2]
        if last_rsi < self.rsi_low: return 'BUY'
        elif last_rsi > self.rsi_high: return 'SELL'
        return 'HOLD'