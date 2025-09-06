from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
import redis
from typing import Dict, List
import uvicorn

from api.routes import market_data, orderbook, execution, portfolio
from core.engine.tick_engine import TickEngine
from core.models.market_data import MarketDataManager
from market_connectors.indian.zerodha import ZerodhaConnector

# Global instances
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
tick_engine = TickEngine()
market_data_manager = MarketDataManager()
active_connections: Dict[str, List[WebSocket]] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await tick_engine.start()
    await market_data_manager.start()
    print("Arthachitra Trading Platform Started")
    yield
    # Shutdown
    await tick_engine.stop()
    await market_data_manager.stop()
    print("Arthachitra Trading Platform Stopped")

app = FastAPI(
    title="Arthachitra Trading Platform",
    description="Next-generation trading and market visualization platform",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(market_data.router, prefix="/api/v1")
app.include_router(orderbook.router, prefix="/api/v1")
app.include_router(execution.router, prefix="/api/v1")
app.include_router(portfolio.router, prefix="/api/v1")

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str):
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)

    def disconnect(self, websocket: WebSocket, channel: str):
        if channel in self.active_connections:
            self.active_connections[channel].remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast_to_channel(self, message: str, channel: str):
        if channel in self.active_connections:
            for connection in self.active_connections[channel]:
                try:
                    await connection.send_text(message)
                except:
                    # Remove dead connections
                    self.active_connections[channel].remove(connection)

manager = ConnectionManager()

@app.websocket("/ws/market/{symbol}/{timeframe}")
async def websocket_market_data(websocket: WebSocket, symbol: str, timeframe: str):
    channel = f"market:{symbol}:{timeframe}"
    await manager.connect(websocket, channel)
    
    try:
        # Send historical data first
        historical_data = await market_data_manager.get_historical_data(symbol, timeframe, 100)
        await manager.send_personal_message(json.dumps({
            "type": "historical",
            "symbol": symbol,
            "timeframe": timeframe,
            "candles": historical_data["candles"],
            "volume": historical_data["volume"]
        }), websocket)
        
        # Listen for real-time updates
        while True:
            # This would be replaced with actual market data subscription
            await asyncio.sleep(1)
            
            # Simulate real-time tick data
            tick_data = await market_data_manager.get_latest_tick(symbol)
            if tick_data:
                await manager.send_personal_message(json.dumps({
                    "type": "tick",
                    "symbol": symbol,
                    "candle": tick_data["candle"],
                    "volume": tick_data["volume"]
                }), websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)

@app.websocket("/ws/orderbook/{symbol}")
async def websocket_orderbook(websocket: WebSocket, symbol: str):
    channel = f"orderbook:{symbol}"
    await manager.connect(websocket, channel)
    
    try:
        while True:
            # Get order book data from Redis or direct feed
            orderbook_data = redis_client.get(f"orderbook:{symbol}")
            if orderbook_data:
                await manager.send_personal_message(orderbook_data, websocket)
            await asyncio.sleep(0.1)  # 10 updates per second
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Arthachitra (अर्थचित्र) Trading Platform",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "connections": sum(len(conns) for conns in manager.active_connections.values()),
        "redis": redis_client.ping(),
        "tick_engine": tick_engine.is_running()
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
