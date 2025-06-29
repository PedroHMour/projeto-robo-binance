import pandas as pd
from .base_strategy import BaseStrategy

class MACrossoverStrategy(BaseStrategy):
    def __init__(self, df: pd.DataFrame, short_window: int, long_window: int):
        super().__init__(df)
        self.short_window = short_window
        self.long_window = long_window

    def generate_signal(self) -> str:
        df = self.df.copy()
        df['short_ma'] = df['close'].rolling(window=self.short_window).mean()
        df['long_ma'] = df['close'].rolling(window=self.long_window).mean()
        if len(df) < self.long_window + 3: return 'HOLD'
        last_row, prev_row = df.iloc[-2], df.iloc[-3]
        if prev_row['short_ma'] <= prev_row['long_ma'] and last_row['short_ma'] > last_row['long_ma']: return 'BUY'
        elif prev_row['short_ma'] >= prev_row['long_ma'] and last_row['short_ma'] < last_row['long_ma']: return 'SELL'
        return 'HOLD'