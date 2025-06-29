import os
import logging
import sys

# --- CONFIGURAÇÕES DE API ---
API_KEY = os.getenv('BINANCE_API_KEY_TESTNET')
API_SECRET = os.getenv('BINANCE_API_SECRET_TESTNET')
IS_TESTNET = True

# Validação para garantir que as variáveis de ambiente foram configuradas
if not API_KEY or not API_SECRET:
    raise ValueError("As variáveis de ambiente BINANCE_API_KEY_TESTNET e BINANCE_API_SECRET_TESTNET não foram configuradas.")

# --- CONFIGURAÇÕES GERAIS DO ROBÔ ---
SYMBOL = 'BTCUSDT'
INTERVAL = '5m' # Intervalos maiores tendem a ser mais confiáveis
TRADE_QUANTITY = 0.001

# --- GERENCIAMENTO DE ESTRATÉGIAS ---
# Adicione os NOMES DAS CLASSES das estratégias que você quer ativar.
ACTIVE_STRATEGIES = [
    'RSIStrategy',
    'MACrossoverStrategy',
    'BollingerBandsStrategy'
]

# --- PARÂMETROS DAS ESTRATÉGIAS ---
MA_CROSSOVER_CONFIG = {
    'short_window': 12,
    'long_window': 26
}
RSI_CONFIG = {
    'rsi_period': 14,
    'rsi_low': 30,
    'rsi_high': 70
}
BOLLINGER_CONFIG = {
    'length': 20,
    'std_dev': 2
}

# --- CONFIGURAÇÕES DE LOGS E ESTADO ---
LOG_FOLDER = 'logs'
LOG_FILE = os.path.join(LOG_FOLDER, 'trade_bot.log')
STATE_FILE = 'state.json'

# --- FUNÇÃO DE CONFIGURAÇÃO DE LOGGING ---
# Esta é a função que estava faltando!
def setup_logging():
    """Configura o sistema de logging para salvar em arquivo e mostrar no console."""
    # Cria a pasta de logs se ela não existir
    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout) # Garante que os logs apareçam no terminal
        ]
    )
    logging.info("Sistema de Logging configurado.")