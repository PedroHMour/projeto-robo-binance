import pandas as pd
import pandas_ta as ta
from .base_strategy import BaseStrategy

class BollingerBandsStrategy(BaseStrategy):
    def __init__(self, df: pd.DataFrame, length: int, std_dev: float):
        super().__init__(df)
        self.length = length
        self.std_dev = std_dev

    def generate_signal(self) -> str:
        df = self.df.copy()
        df.ta.bbands(length=self.length, std=self.std_dev, append=True)
        lower_col = f'BBL_{self.length}_{self.std_dev}'
        upper_col = f'BBU_{self.length}_{self.std_dev}'
        if lower_col not in df.columns or len(df) < self.length + 2: return 'HOLD'
        last_row = df.iloc[-2]
        price = last_row['close']
        lower_band = last_row[lower_col]
        upper_band = last_row[upper_col]
        if price < lower_band: return 'BUY'
        elif price > upper_band: return 'SELL'
        return 'HOLD'