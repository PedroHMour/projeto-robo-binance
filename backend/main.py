import time
import logging
import os

# Importa nossas configurações e módulos personalizados
import config
from binance_client import BinanceHandler
from strategy import MovingAverageCrossover
from state_manager import load_state, save_state

def setup_logging():
    """Configura o sistema de logging para salvar em arquivo e mostrar no console."""
    # Cria a pasta de logs se ela não existir
    if not os.path.exists(config.LOG_FOLDER):
        os.makedirs(config.LOG_FOLDER)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler() # Envia logs também para o console
        ]
    )

def run_bot():
    """Função principal que executa o loop do robô."""
    setup_logging()
    logging.info("=============================================")
    logging.info("====== INICIANDO O ROBÔ DE TRADE BINANCE =====")
    logging.info("=============================================")

    # Inicializa os componentes
    try:
        client = BinanceHandler(config.API_KEY, config.API_SECRET, testnet=config.IS_TESTNET)
        strategy = MovingAverageCrossover(config.SHORT_MA_PERIOD, config.LONG_MA_PERIOD)
        state = load_state(config.STATE_FILE)
    except Exception as e:
        logging.critical(f"Falha crítica na inicialização. O robô não pode continuar. Erro: {e}")
        return # Encerra a execução se a inicialização falhar

    logging.info(f"Robô operando com o par: {config.SYMBOL} no intervalo de {config.INTERVAL}")
    logging.info(f"Estado inicial carregado: {state}")
    
    while True:
        try:
            logging.info("-------------------------------------------")
            
            # 1. Obter dados de mercado
            market_data = client.get_historical_data(config.SYMBOL, config.INTERVAL)
            
            if market_data.empty:
                logging.warning("Não foi possível obter dados de mercado. Tentando novamente em 60 segundos.")
                time.sleep(60)
                continue

            # 2. Obter sinal da estratégia
            signal = strategy.generate_signals(market_data)
            logging.info(f"Sinal da estratégia: {signal}. Estado atual: {'Em posição' if state['in_position'] else 'Fora de posição'}")
            
            # 3. Tomar decisão com base no estado atual e no sinal
            if signal == 'BUY' and not state['in_position']:
                logging.info(f"Sinal de COMPRA recebido. Enviando ordem para {config.TRADE_QUANTITY} {config.SYMBOL}.")
                order = client.place_order(config.SYMBOL, 'BUY', config.TRADE_QUANTITY)
                if order:
                    logging.info("Ordem de COMPRA processada pela API.")
                    state['in_position'] = True
                    save_state(state, config.STATE_FILE)
                else:
                    logging.error("Falha ao processar a ordem de COMPRA.")

            elif signal == 'SELL' and state['in_position']:
                logging.info(f"Sinal de VENDA recebido. Enviando ordem para {config.TRADE_QUANTITY} {config.SYMBOL}.")
                order = client.place_order(config.SYMBOL, 'SELL', config.TRADE_QUANTITY)
                if order:
                    logging.info("Ordem de VENDA processada pela API.")
                    state['in_position'] = False
                    save_state(state, config.STATE_FILE)
                else:
                    logging.error("Falha ao processar a ordem de VENDA.")
            else:
                logging.info("Nenhuma ação necessária. Aguardando a próxima vela.")

            # Espera para a próxima verificação
            logging.info("Aguardando 60 segundos para o próximo ciclo...")
            time.sleep(60)

        except KeyboardInterrupt:
            logging.info("Robô interrompido pelo usuário (Ctrl+C). Encerrando...")
            break
        except Exception as e:
            logging.critical(f"Ocorreu um erro inesperado no loop principal: {e}", exc_info=True)
            logging.info("Aguardando 60 segundos antes de tentar novamente...")
            time.sleep(60)

if __name__ == "__main__":
    run_bot()