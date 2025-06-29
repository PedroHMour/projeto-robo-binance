import time
import logging
import asyncio
import json
import pandas_ta as ta

# Importa nossos módulos personalizados
import config
from binance_client import BinanceHandler
from state_manager import load_state, save_state
from strategies.ma_crossover import MACrossoverStrategy
from strategies.rsi_strategy import RSIStrategy
from strategies.bollinger_bands import BollingerBandsStrategy

class TradingBot:
    def __init__(self, connection_manager):
        self.client = BinanceHandler(config.API_KEY, config.API_SECRET, testnet=config.IS_TESTNET)
        self.state = load_state(config.STATE_FILE)
        self.manager = connection_manager
        # Mapeamento explícito das classes de estratégia para segurança e clareza
        self.strategy_classes = {
            'MACrossoverStrategy': MACrossoverStrategy,
            'RSIStrategy': RSIStrategy,
            'BollingerBandsStrategy': BollingerBandsStrategy
        }
        self.active_strategies = self._load_strategies()
        logging.info(f"Estado inicial carregado: {self.state}")
        logging.info(f"Estratégias carregadas com sucesso: {[s.__class__.__name__ for s in self.active_strategies]}")

    def _load_strategies(self):
        """
        Carrega as instâncias das estratégias ativas com seus respectivos parâmetros do config.py.
        """
        strategies = []
        for strategy_name in config.ACTIVE_STRATEGIES:
            if strategy_name in self.strategy_classes:
                strategy_class = self.strategy_classes[strategy_name]
                
                # --- A CORREÇÃO ESTÁ AQUI ---
                # Corrigimos a lógica para construir o nome da variável de configuração corretamente.
                # Ex: 'MACrossoverStrategy' -> 'MA_CROSSOVER_CONFIG'
                # Ex: 'RSIStrategy' -> 'RSI_CONFIG'
                config_key = strategy_name.replace('Strategy', '').upper()
                if strategy_name == 'MACrossoverStrategy':
                    config_key = 'MA_CROSSOVER' # Tratamento especial para o nome abreviado
                
                config_name = f"{config_key}_CONFIG"
                strategy_params = getattr(config, config_name, {})
                # --- FIM DA CORREÇÃO ---

                if not strategy_params:
                    logging.warning(f"Configuração para a estratégia '{strategy_name}' não encontrada. Usando defaults.")
                
                try:
                    # Cria a instância da estratégia, passando os parâmetros
                    strategies.append(strategy_class(df=None, **strategy_params))
                    logging.info(f"Estratégia '{strategy_name}' carregada com sucesso.")
                except TypeError as e:
                    logging.error(f"Erro ao instanciar '{strategy_name}': {e}. Verifique se os parâmetros em config.py estão corretos.")

        return strategies

    def run(self):
        """
        O loop principal e inteligente que executa a lógica de negociação.
        """
        logging.info("Iniciando o loop principal do robô inteligente...")
        while True:
            try:
                market_data = self.client.get_historical_data(config.SYMBOL, config.INTERVAL, limit=300)
                if market_data.empty:
                    logging.warning("Não foi possível obter dados de mercado. Pulando ciclo.")
                    time.sleep(60)
                    continue

                # Calcula o ADX para determinar a condição do mercado
                market_data.ta.adx(length=config.RSI_CONFIG['rsi_period'], append=True)
                adx_col = f'ADX_{config.RSI_CONFIG["rsi_period"]}'
                if adx_col not in market_data.columns:
                    logging.warning("Coluna ADX não pôde ser calculada. Aguardando mais dados.")
                    time.sleep(60)
                    continue
                
                adx_value = market_data[adx_col].iloc[-1]
                logging.info(f"Diagnóstico de Mercado - ADX Atual: {adx_value:.2f}")

                signals, active_now = [], []
                if adx_value > 25:
                    logging.info("CONDIÇÃO: Mercado em Tendência Forte -> Ativando MACrossover.")
                    active_now = [s for s in self.active_strategies if isinstance(s, MACrossoverStrategy)]
                elif adx_value < 20:
                    logging.info("CONDIÇÃO: Mercado Lateral -> Ativando RSI e Bollinger.")
                    active_now = [s for s in self.active_strategies if isinstance(s, (RSIStrategy, BollingerBandsStrategy))]
                else:
                    logging.info("CONDIÇÃO: Mercado Indefinido. Aguardando.")
                
                for strat in active_now:
                    strat.df = market_data
                    signal = strat.generate_signal()
                    signals.append(signal)
                    logging.info(f"Sinal de '{strat.__class__.__name__}': {signal}")
                
                final_decision = 'HOLD'
                if not self.state.get('in_position', False) and 'BUY' in signals:
                    final_decision = 'BUY'
                elif self.state.get('in_position', False) and 'SELL' in signals:
                    final_decision = 'SELL'
                
                logging.info(f"Decisão final: {final_decision}")
                if final_decision != 'HOLD':
                    self.execute_trade(final_decision)
                
                logging.info("Ciclo completo. Aguardando 60 segundos...")
                time.sleep(60)

            except Exception as e:
                logging.error(f"Erro crítico no loop principal: {e}", exc_info=True)
                time.sleep(60)

    def execute_trade(self, side):
        """
        Executa a ordem de compra ou venda e notifica o frontend.
        """
        logging.info(f"Executando ordem {side}...")
        order = self.client.place_order(config.SYMBOL, side, config.TRADE_QUANTITY)
        if order:
            self.state['in_position'] = (side == 'BUY')
            save_state(self.state, config.STATE_FILE)
            logging.info(f"Ordem {side} processada. Novo estado: {self.state}")
            msg = json.dumps({"type": "new_trade", "data": {"side": side}})
            try:
                loop = asyncio.get_running_loop()
                loop.call_soon_threadsafe(asyncio.create_task, self.manager.broadcast(msg))
            except RuntimeError:
                asyncio.run(self.manager.broadcast(msg))