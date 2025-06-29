import asyncio, threading, uvicorn, logging, json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from binance import AsyncClient, BinanceSocketManager
import config
from bot_core import TradingBot

config.setup_logging()
app = FastAPI(title="API Robô Trader", version="2.5.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self): self.active_connections: List[WebSocket] = []
    async def connect(self, ws: WebSocket): await ws.accept(); self.active_connections.append(ws)
    def disconnect(self, ws: WebSocket): self.active_connections.remove(ws)
    async def broadcast(self, msg: str): 
        for conn in self.active_connections: await conn.send_text(msg)

manager = ConnectionManager()
bot = TradingBot(connection_manager=manager)

async def price_streamer(manager: ConnectionManager):
    client = await AsyncClient.create()
    bsm = BinanceSocketManager(client)
    socket = bsm.trade_socket(config.SYMBOL)
    async with socket as ts:
        while True:
            res = await ts.recv()
            msg = json.dumps({"type": "price_update", "data": {"time": res['T']/1000, "price": float(res['p'])}})
            await manager.broadcast(msg)

@app.on_event("startup")
async def startup_event():
    threading.Thread(target=bot.run, daemon=True).start()
    threading.Thread(target=lambda: asyncio.run(price_streamer(manager)), daemon=True).start()

@app.get("/")
def root(): return {"message": "API Online"}
@app.get("/api/status")
def status(): return {"state": bot.state}
@app.get("/api/trades")
async def trades(): return await bot.client.client.get_my_trades(symbol=config.SYMBOL, limit=1000)
@app.get("/api/klines")
async def klines(): return await bot.client.client.get_historical_klines(symbol=config.SYMBOL, interval=config.INTERVAL, limit=200)

@app.websocket("/ws/updates")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True: await ws.receive_text()
    except WebSocketDisconnect: manager.disconnect(ws)