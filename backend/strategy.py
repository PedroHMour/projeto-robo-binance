import pandas as pd
import logging

class MovingAverageCrossover:
    """
    Estratégia baseada no cruzamento de duas médias móveis simples (MMS).
    """
    def __init__(self, short_window, long_window):
        if short_window >= long_window:
            raise ValueError("A janela da média curta deve ser menor que a da longa.")
        self.short_window = short_window
        self.long_window = long_window
        logging.info(f"Estratégia de Cruzamento de Médias Móveis inicializada com janelas: Curta={short_window}, Longa={long_window}")

    def generate_signals(self, df):
        """
        Analisa o DataFrame de dados de mercado e retorna um sinal de negociação.
        Sinais possíveis: 'BUY', 'SELL', 'HOLD'.
        """
        # Validação para garantir que temos dados suficientes para os cálculos
        if df.empty or len(df) < self.long_window:
            logging.warning("Dados insuficientes para gerar sinal. Necessário: %d, Disponível: %d", self.long_window, len(df))
            return 'HOLD'

        # Calcula as médias móveis
        df['short_ma'] = df['close'].rolling(window=self.short_window, min_periods=1).mean()
        df['long_ma'] = df['close'].rolling(window=self.long_window, min_periods=1).mean()

        # Pega os dois últimos pontos de dados para detectar o momento exato do cruzamento
        # iloc[-1] é a vela mais recente (ainda pode estar em andamento)
        # iloc[-2] é a última vela fechada
        last_row = df.iloc[-2]
        prev_row = df.iloc[-3]

        # Lógica do Sinal de Compra: Média curta cruza PARA CIMA da média longa
        # Verificamos se na vela anterior a curta estava abaixo e na última fechada ela está acima
        buy_signal = prev_row['short_ma'] <= prev_row['long_ma'] and last_row['short_ma'] > last_row['long_ma']
        
        # Lógica do Sinal de Venda: Média curta cruza PARA BAIXO da média longa
        sell_signal = prev_row['short_ma'] >= prev_row['long_ma'] and last_row['short_ma'] < last_row['long_ma']
        
        if buy_signal:
            logging.info(f"Sinal de COMPRA gerado. Preço: {last_row['close']:.2f}, Média Curta: {last_row['short_ma']:.2f}, Média Longa: {last_row['long_ma']:.2f}")
            return 'BUY'
        elif sell_signal:
            logging.info(f"Sinal de VENDA gerado. Preço: {last_row['close']:.2f}, Média Curta: {last_row['short_ma']:.2f}, Média Longa: {last_row['long_ma']:.2f}")
            return 'SELL'
        else:
            return 'HOLD'