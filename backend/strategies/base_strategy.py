from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    def __init__(self, df: pd.DataFrame):
        self.df = df

    @abstractmethod
    def generate_signal(self) -> str:
        pass