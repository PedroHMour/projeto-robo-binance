import time, logging, asyncio, json
import pandas_ta as ta
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
        self.strategy_classes = {
            'MACrossoverStrategy': MACrossoverStrategy,
            'RSIStrategy': RSIStrategy,
            'BollingerBandsStrategy': BollingerBandsStrategy
        }
        self.active_strategies = self._load_strategies()
        logging.info(f"Estado inicial: {self.state}")
        logging.info(f"Estratégias carregadas: {[s.__class__.__name__ for s in self.active_strategies]}")

    def _load_strategies(self):
        strategies = []
        for name in config.ACTIVE_STRATEGIES:
            if name in self.strategy_classes:
                # --- CORREÇÃO DEFINITIVA DA LÓGICA DE CONFIG ---
                config_key_base = name.replace('Strategy', '').upper()
                if name == 'MACrossoverStrategy':
                    config_key = 'MA_CROSSOVER_CONFIG'
                else:
                    config_key = f"{config_key_base}_CONFIG"
                
                params = getattr(config, config_key, {})
                # --- FIM DA CORREÇÃO ---
                try:
                    strategies.append(self.strategy_classes[name](df=None, **params))
                except TypeError as e:
                    logging.error(f"Erro ao instanciar '{name}': {e}. Verifique os parâmetros em config.py.")
        return strategies

    def run(self):
        logging.info("Iniciando loop do robô...")
        while True:
            try:
                market_data = self.client.get_historical_data(config.SYMBOL, config.INTERVAL, limit=300)
                if market_data.empty: time.sleep(60); continue

                market_data.ta.adx(length=config.RSI_CONFIG['rsi_period'], append=True)
                adx_col = f'ADX_{config.RSI_CONFIG["rsi_period"]}'
                if adx_col not in market_data.columns: time.sleep(60); continue
                
                adx_value = market_data[adx_col].iloc[-1]
                logging.info(f"ADX Atual: {adx_value:.2f}")

                signals, active_now = [], []
                if adx_value > 25:
                    logging.info("Mercado em Tendência -> Ativando MACrossover.")
                    active_now = [s for s in self.active_strategies if isinstance(s, MACrossoverStrategy)]
                elif adx_value < 20:
                    logging.info("Mercado Lateral -> Ativando RSI e Bollinger.")
                    active_now = [s for s in self.active_strategies if isinstance(s, (RSIStrategy, BollingerBandsStrategy))]
                else:
                    logging.info("Mercado Indefinido.")
                
                for strat in active_now:
                    strat.df = market_data
                    signal = strat.generate_signal()
                    signals.append(signal)
                    logging.info(f"Sinal de '{strat.__class__.__name__}': {signal}")
                
                final_decision = 'HOLD'
                if not self.state.get('in_position', False) and 'BUY' in signals: final_decision = 'BUY'
                elif self.state.get('in_position', False) and 'SELL' in signals: final_decision = 'SELL'
                
                logging.info(f"Decisão final: {final_decision}")
                if final_decision != 'HOLD': self.execute_trade(final_decision)
                
                time.sleep(60)
            except Exception as e:
                logging.error(f"Erro no loop: {e}", exc_info=True); time.sleep(60)

    def execute_trade(self, side):
        order = self.client.place_order(config.SYMBOL, side, config.TRADE_QUANTITY)
        if order:
            self.state['in_position'] = (side == 'BUY')
            save_state(self.state, config.STATE_FILE)
            logging.info(f"Ordem {side} processada. Novo estado: {self.state}")
            msg = json.dumps({"type": "new_trade", "data": {"side": side}})
            try:
                loop = asyncio.get_event_loop()
                loop.call_soon_threadsafe(asyncio.create_task, self.manager.broadcast(msg))
            except RuntimeError:
                asyncio.run(self.manager.broadcast(msg))