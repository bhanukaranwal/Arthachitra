import asyncio
import json
import hashlib
import hmac
import time
from typing import Dict, List, Optional, Any
import aiohttp
import websockets
from datetime import datetime, timedelta

from ..base.connector import BaseConnector, Order, Position, Trade
from ...core.models.market_data import OHLCV, Quote

class ZerodhaConnector(BaseConnector):
    """
    Zerodha Kite API connector for Indian markets.
    Supports NSE, BSE equity and derivatives trading.
    """
    
    def __init__(self, api_key: str, api_secret: str, access_token: str = None):
        super().__init__()
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.base_url = "https://api.kite.trade"
        self.ws_url = "wss://ws.kite.trade"
        self.session = None
        self.ws_connection = None
        self.subscribed_tokens = set()
        
    async def connect(self) -> bool:
        """Establish connection to Zerodha Kite API."""
        try:
            self.session = aiohttp.ClientSession()
            
            if not self.access_token:
                raise ValueError("Access token required for Zerodha connection")
            
            # Verify connection
            profile = await self._make_request("GET", "/user/profile")
            if profile:
                self.connected = True
                print(f"Connected to Zerodha as {profile.get('user_name', 'Unknown')}")
                return True
                
        except Exception as e:
            print(f"Failed to connect to Zerodha: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from Zerodha API."""
        if self.ws_connection:
            await self.ws_connection.close()
        
        if self.session:
            await self.session.close()
        
        self.connected = False
        self.subscribed_tokens.clear()
    
    async def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Optional[Dict]:
        """Make authenticated HTTP request to Kite API."""
        if not self.session:
            return None
        
        headers = {
            "Authorization": f"token {self.api_key}:{self.access_token}",
            "X-Kite-Version": "3"
        }
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                async with self.session.get(url, headers=headers, params=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("data")
            elif method == "POST":
                async with self.session.post(url, headers=headers, data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("data")
            elif method == "PUT":
                async with self.session.put(url, headers=headers, data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("data")
            elif method == "DELETE":
                async with self.session.delete(url, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("data")
                        
        except Exception as e:
            print(f"API request failed: {e}")
            return None
    
    async def get_instruments(self, exchange: str = None) -> List[Dict]:
        """Get list of tradeable instruments."""
        endpoint = "/instruments"
        if exchange:
            endpoint += f"/{exchange}"
        
        # Kite provides CSV data for instruments
        headers = {
            "Authorization": f"token {self.api_key}:{self.access_token}",
        }
        
        try:
            async with self.session.get(f"{self.base_url}{endpoint}", headers=headers) as response:
                if response.status == 200:
                    csv_data = await response.text()
                    # Parse CSV and convert to dict format
                    lines = csv_data.strip().split('\n')
                    headers = lines[0].split(',')
                    instruments = []
                    
                    for line in lines[1:]:
                        values = line.split(',')
                        instrument = dict(zip(headers, values))
                        instruments.append(instrument)
                    
                    return instruments
        except Exception as e:
            print(f"Failed to fetch instruments: {e}")
            return []
    
    async def get_quote(self, symbol: str, exchange: str = "NSE") -> Optional[Quote]:
        """Get current quote for a symbol."""
        instrument_key = f"{exchange}:{symbol}"
        data = await self._make_request("GET", f"/quote", {"i": instrument_key})
        
        if data and instrument_key in data:
            quote_data = data[instrument_key]
            return Quote(
                symbol=symbol,
                exchange=exchange,
                price=quote_data.get("last_price", 0),
                bid=quote_data.get("depth", {}).get("buy", [{}])[0].get("price", 0),
                ask=quote_data.get("depth", {}).get("sell", [{}])[0].get("price", 0),
                volume=quote_data.get("volume", 0),
                change=quote_data.get("net_change", 0),
                change_percent=quote_data.get("net_change", 0) / quote_data.get("last_price", 1) * 100,
                timestamp=datetime.now()
            )
        return None
    
    async def get_historical_data(self, symbol: str, exchange: str, timeframe: str, 
                                from_date: datetime, to_date: datetime) -> List[OHLCV]:
        """Get historical OHLCV data."""
        instrument_key = f"{exchange}:{symbol}"
        
        # Convert timeframe to Kite format
        interval_map = {
            "1m": "minute",
            "5m": "5minute",
            "15m": "15minute",
            "1h": "60minute",
            "1d": "day"
        }
        
        interval = interval_map.get(timeframe, "day")
        
        params = {
            "instrument_token": instrument_key,  # This needs to be the actual token
            "interval": interval,
            "from": from_date.strftime("%Y-%m-%d"),
            "to": to_date.strftime("%Y-%m-%d")
        }
        
        data = await self._make_request("GET", "/instruments/historical", params)
        
        if data and "candles" in data:
            ohlcv_data = []
            for candle in data["candles"]:
                ohlcv_data.append(OHLCV(
                    timestamp=datetime.fromisoformat(candle[0]),
                    open=candle[1],
                    high=candle[2],
                    low=candle[3],
                    close=candle[4],
                    volume=candle[5]
                ))
            return ohlcv_data
        
        return []
    
    async def place_order(self, symbol: str, exchange: str, side: str, quantity: int,
                         order_type: str = "MARKET", price: float = None, 
                         product: str = "MIS", validity: str = "DAY") -> Optional[str]:
        """Place a new order."""
        order_data = {
            "tradingsymbol": symbol,
            "exchange": exchange,
            "transaction_type": side.upper(),
            "quantity": quantity,
            "order_type": order_type,
            "product": product,
            "validity": validity
        }
        
        if price and order_type in ["LIMIT", "SL", "SL-M"]:
            order_data["price"] = price
        
        result = await self._make_request("POST", "/orders/regular", order_data)
        
        if result and "order_id" in result:
            return result["order_id"]
        
        return None
    
    async def modify_order(self, order_id: str, quantity: int = None, 
                          price: float = None, order_type: str = None) -> bool:
        """Modify an existing order."""
        modify_data = {}
        
        if quantity:
            modify_data["quantity"] = quantity
        if price:
            modify_data["price"] = price
        if order_type:
            modify_data["order_type"] = order_type
        
        result = await self._make_request("PUT", f"/orders/regular/{order_id}", modify_data)
        return result is not None
    
    async def cancel_order(self, order_id: str, variety: str = "regular") -> bool:
        """Cancel an order."""
        result = await self._make_request("DELETE", f"/orders/{variety}/{order_id}")
        return result is not None
    
    async def get_orders(self) -> List[Order]:
        """Get all orders for the day."""
        data = await self._make_request("GET", "/orders")
        
        orders = []
        if data:
            for order_data in data:
                orders.append(Order(
                    order_id=order_data.get("order_id"),
                    symbol=order_data.get("tradingsymbol"),
                    exchange=order_data.get("exchange"),
                    side=order_data.get("transaction_type"),
                    quantity=order_data.get("quantity", 0),
                    filled_quantity=order_data.get("filled_quantity", 0),
                    price=order_data.get("price", 0),
                    order_type=order_data.get("order_type"),
                    status=order_data.get("status"),
                    timestamp=datetime.fromisoformat(order_data.get("order_timestamp", ""))
                ))
        
        return orders
    
    async def get_positions(self) -> List[Position]:
        """Get current positions."""
        data = await self._make_request("GET", "/portfolio/positions")
        
        positions = []
        if data and "net" in data:
            for pos_data in data["net"]:
                if pos_data.get("quantity", 0) != 0:
                    positions.append(Position(
                        symbol=pos_data.get("tradingsymbol"),
                        exchange=pos_data.get("exchange"),
                        quantity=pos_data.get("quantity", 0),
                        average_price=pos_data.get("average_price", 0),
                        pnl=pos_data.get("pnl", 0),
                        product=pos_data.get("product")
                    ))
        
        return positions
    
    async def start_websocket(self, on_tick_callback):
        """Start WebSocket connection for real-time data."""
        if not self.access_token:
            raise ValueError("Access token required for WebSocket connection")
        
        try:
            # WebSocket connection requires special authentication for Kite
            ws_url = f"{self.ws_url}?api_key={self.api_key}&access_token={self.access_token}"
            
            self.ws_connection = await websockets.connect(ws_url)
            
            async for message in self.ws_connection:
                try:
                    # Kite sends binary data that needs to be parsed
                    if isinstance(message, bytes):
                        # Parse binary tick data (Kite-specific format)
                        tick_data = self._parse_binary_tick(message)
                        if tick_data and on_tick_callback:
                            await on_tick_callback(tick_data)
                except Exception as e:
                    print(f"Error processing WebSocket message: {e}")
                    
        except Exception as e:
            print(f"WebSocket connection failed: {e}")
    
    def _parse_binary_tick(self, binary_data: bytes) -> Optional[Dict]:
        """Parse Kite's binary tick data format."""
        # This is a simplified parser - actual Kite binary format is more complex
        try:
            # Kite binary format parsing would go here
            # For now, return a placeholder
            return {
                "instrument_token": 0,
                "last_price": 0,
                "volume": 0,
                "timestamp": datetime.now()
            }
        except Exception:
            return None
    
    async def subscribe_symbols(self, symbols: List[str], mode: str = "quote"):
        """Subscribe to real-time data for symbols."""
        if not self.ws_connection:
            await self.start_websocket(None)
        
        # Convert symbols to instrument tokens (would need instrument mapping)
        subscribe_data = {
            "a": "subscribe",
            "v": symbols  # In actual implementation, these would be instrument tokens
        }
        
        await self.ws_connection.send(json.dumps(subscribe_data))
        self.subscribed_tokens.update(symbols)
    
    async def unsubscribe_symbols(self, symbols: List[str]):
        """Unsubscribe from real-time data."""
        if not self.ws_connection:
            return
        
        unsubscribe_data = {
            "a": "unsubscribe",
            "v": symbols
        }
        
        await self.ws_connection.send(json.dumps(unsubscribe_data))
        self.subscribed_tokens.difference_update(symbols)

# Usage example
async def main():
    # Initialize connector
    connector = ZerodhaConnector(
        api_key="your_api_key",
        api_secret="your_api_secret",
        access_token="your_access_token"
    )
    
    # Connect
    if await connector.connect():
        # Get quote
        quote = await connector.get_quote("RELIANCE", "NSE")
        print(f"RELIANCE Quote: {quote}")
        
        # Get historical data
        from_date = datetime.now() - timedelta(days=30)
        to_date = datetime.now()
        historical = await connector.get_historical_data("RELIANCE", "NSE", "1d", from_date, to_date)
        print(f"Historical data points: {len(historical)}")
        
        # Get positions
        positions = await connector.get_positions()
        print(f"Current positions: {len(positions)}")
        
        await connector.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
