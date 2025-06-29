from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
import pandas as pd
import logging

class BinanceHandler:
    """
    Classe responsável por toda a interação com a API da Binance.
    """
    def __init__(self, api_key, api_secret, testnet=True):
        """Inicializa o cliente da Binance."""
        self.testnet = testnet
        try:
            self.client = Client(api_key, api_secret, testnet=testnet)
            # Testa a conexão com a API
            self.client.ping()
            logging.info("Conexão com a API da Binance estabelecida com sucesso.")
        except (BinanceAPIException, BinanceRequestException) as e:
            logging.critical(f"Erro crítico ao conectar com a Binance: {e}")
            raise  # Re-lança a exceção para parar a execução do robô

    def get_historical_data(self, symbol, interval,limit=100):
        #Busca dados historicos de velas (K-lines) para um simbolo
        try:
            # Traduz o intervalo para o formato da constante da biblioteca (ex: '1m' -> '1MINUTE')
            kline_interval_for_api = interval.replace('m', 'MINUTE')
            api_interval = getattr(Client, f'KLINE_INTERVAL_{kline_interval_for_api.upper()}')
            
            # --- INÍCIO DA NOVA CORREÇÃO ---
            # Traduz o intervalo para a string de busca do histórico (ex: '1m' -> 'minutes')
            # A API da Binance espera um formato como "100 minutes ago UTC"
            history_unit_map = {'m': 'minutes', 'h': 'hours', 'd': 'days', 'w': 'weeks'}
            unit_char = interval[-1] # Pega o último caractere: 'm', 'h', 'd' ou 'w'
            
            history_str = f"{limit} {history_unit_map[unit_char]} ago UTC"
            logging.info(f"Buscando dados históricos com o parâmetro: '{history_str}'")
            
            klines = self.client.get_historical_klines(symbol, api_interval, history_str)
            # --- FIM DA NOVA CORREÇÃO ---

            df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
            
            # Converte as colunas de preço e volume para tipo numérico (float)
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df.dropna(inplace=True)
            
            return df
        except (BinanceAPIException, BinanceRequestException) as e:
            logging.error(f"Erro ao buscar dados históricos da API: {e}")
            return pd.DataFrame() # Retorna um DataFrame vazio em caso de erro
        except Exception as e: # Captura outros erros inesperados
            logging.critical(f"Erro inesperado em get_historical_data: {e}", exc_info=True)
            raise
            
    def place_order(self, symbol, side, quantity):
        """
        Envia uma ordem de compra ou venda a mercado.
        'side' deve ser 'BUY' ou 'SELL'.
        """
        try:
            api_side = getattr(Client, f'SIDE_{side.upper()}')
            
            logging.info(f"Tentando enviar ordem {side} para {quantity} {symbol}...")

            # A função de ordem é diferente para a Testnet e para a produção
            if self.testnet:
                # create_test_order não retorna um resultado, apenas confirma que a sintaxe está correta
                order = self.client.create_test_order(
                    symbol=symbol,
                    side=api_side,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity=quantity
                )
                logging.info("Ordem de TESTE enviada com sucesso (sintaxe verificada).")
                # Retornamos um dicionário simulado para consistência
                return {'symbol': symbol, 'side': side, 'quantity': quantity, 'status': 'TEST_ORDER_PLACED'}
            else:
                # Esta é a chamada para ordens com dinheiro real
                order = self.client.create_order(
                    symbol=symbol,
                    side=api_side,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity=quantity
                )
                logging.info(f"Ordem REAL enviada com sucesso: {order}")
                return order

        except (BinanceAPIException, BinanceRequestException) as e:
            logging.error(f"Erro ao enviar ordem para a API: {e}")
            return None # Retorna None em caso de falha