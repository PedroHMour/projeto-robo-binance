import os
from binance.client import Client
from binance.exceptions import BinanceAPIException
import pandas as pd

# Carrega as mesmas configurações do nosso robô
API_KEY = os.getenv('BINANCE_API_KEY_TESTNET')
API_SECRET = os.getenv('BINANCE_API_SECRET_TESTNET')
SYMBOL = 'BTCUSDT'

# Validação das chaves
if not API_KEY or not API_SECRET:
    raise ValueError("As variáveis de ambiente da Testnet não foram configuradas. Execute 'source ~/.bashrc'")

print("Conectando à Binance Testnet para verificar ordens...")

try:
    # Conecta ao cliente da Testnet
    client = Client(API_KEY, API_SECRET, testnet=True)

    # Busca todas as ordens (abertas e fechadas) para o símbolo
    orders = client.get_all_orders(symbol=SYMBOL, limit=10) # Pega as últimas 10 ordens

    if not orders:
        print(f"\nNenhuma ordem encontrada para o par {SYMBOL}.")
    else:
        print(f"\n--- Últimas Ordens para {SYMBOL} ---")
        # Transforma a lista de ordens em um DataFrame do Pandas para visualização fácil
        df = pd.DataFrame(orders)
        # Seleciona e renomeia as colunas mais importantes para mostrar
        df_filtered = df[['time', 'symbol', 'side', 'type', 'price', 'executedQty', 'status']]
        df_filtered = df_filtered.rename(columns={
            'time': 'Data/Hora (UTC)',
            'symbol': 'Símbolo',
            'side': 'Lado',
            'type': 'Tipo',
            'price': 'Preço',
            'executedQty': 'Qtd. Executada',
            'status': 'Status'
        })
        # Converte o timestamp para um formato legível
        df_filtered['Data/Hora (UTC)'] = pd.to_datetime(df_filtered['Data/Hora (UTC)'], unit='ms')
        
        print(df_filtered.to_string(index=False))

except BinanceAPIException as e:
    print(f"Erro da API da Binance: {e}")
except Exception as e:
    print(f"Ocorreu um erro: {e}")