import asyncio
import aiohttp
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import hashlib
import hmac

from ..base.connector import BaseConnector, Order, Position, Trade

class FyersConnector(BaseConnector):
    """Fyers API connector for Indian markets."""
    
    def __init__(self, app_id: str, secret_key: str, access_token: str = None):
        super().__init__()
        self.app_id = app_id
        self.secret_key = secret_key
        self.access_token = access_token
        self.base_url = "https://api.fyers.in/api/v2"
        self.name = "Fyers"
        self.session = None
        
    async def connect(self) -> bool:
        """Connect to Fyers API."""
        try:
            self.session = aiohttp.ClientSession()
            
            # Verify connection with profile API
            headers = {"Authorization": f"{self.app_id}:{self.access_token}"}
            async with self.session.get(f"{self.base_url}/profile", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("s") == "ok":
                        self.connected = True
                        print(f"Connected to Fyers for user: {data.get('data', {}).get('name', 'Unknown')}")
                        return True
                        
        except Exception as e:
            print(f"Failed to connect to Fyers: {e}")
            
        self.connected = False
        return False
    
    async def disconnect(self):
        """Disconnect from Fyers API."""
        if self.session:
            await self.session.close()
        self.connected = False
    
    async def get_quote(self, symbol: str, exchange: str = "NSE") -> Optional[Dict]:
        """Get current quote for a symbol."""
        try:
            fyers_symbol = f"{exchange}:{symbol}-EQ"
            headers = {"Authorization": f"{self.app_id}:{self.access_token}"}
            
            async with self.session.get(
                f"{self.base_url}/quotes",
                headers=headers,
                params={"symbols": fyers_symbol}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    if data.get("s") == "ok" and fyers_symbol in data.get("d", {}):
                        quote_data = data["d"][fyers_symbol]
                        return {
                            "symbol": symbol,
                            "price": quote_data.get("v", {}).get("lp", 0),
                            "bid": quote_data.get("v", {}).get("bp1", 0),
                            "ask": quote_data.get("v", {}).get("ap1", 0),
                            "volume": quote_data.get("v", {}).get("volume", 0),
                            "change": quote_data.get("v", {}).get("ch", 0),
                            "change_percent": quote_data.get("v", {}).get("chp", 0),
                            "timestamp": datetime.now()
                        }
                        
        except Exception as e:
            print(f"Error getting quote from Fyers: {e}")
        
        return None
    
    async def place_order(self, symbol: str, exchange: str, side: str, quantity: int,
                         order_type: str = "MARKET", price: float = None, 
                         product: str = "CNC", validity: str = "DAY") -> Optional[str]:
        """Place order with Fyers."""
        try:
            fyers_symbol = f"{exchange}:{symbol}-EQ"
            
            order_data = {
                "symbol": fyers_symbol,
                "qty": quantity,
                "type": 2 if order_type == "LIMIT" else 1,  # 1=Market, 2=Limit
                "side": 1 if side.upper() == "BUY" else -1,
                "productType": product,
                "validity": validity,
                "disclosedQty": 0,
                "offlineOrder": "False",
                "stopPrice": 0,
                "limitPrice": price if price else 0
            }
            
            headers = {
                "Authorization": f"{self.app_id}:{self.access_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(
                f"{self.base_url}/orders",
                headers=headers,
                json=order_data
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    if data.get("s") == "ok":
                        return data.get("d", {}).get("id")
                        
        except Exception as e:
            print(f"Error placing order with Fyers: {e}")
        
        return None
    
    async def get_orders(self) -> List[Order]:
        """Get all orders."""
        try:
            headers = {"Authorization": f"{self.app_id}:{self.access_token}"}
            
            async with self.session.get(f"{self.base_url}/orders", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("s") == "ok":
                        orders = []
                        for order_data in data.get("d", {}).get("orderBook", []):
                            orders.append(Order(
                                order_id=order_data.get("id"),
                                symbol=order_data.get("symbol", "").split(":")[-1].replace("-EQ", ""),
                                exchange=order_data.get("symbol", "").split(":")[0],
                                side="BUY" if order_data.get("side") == 1 else "SELL",
                                quantity=order_data.get("qty", 0),
                                filled_quantity=order_data.get("filledQty", 0),
                                price=order_data.get("limitPrice", 0),
                                order_type="LIMIT" if order_data.get("type") == 2 else "MARKET",
                                status=self._map_order_status(order_data.get("status", 0)),
                                timestamp=datetime.now()
                            ))
                        return orders
                        
        except Exception as e:
            print(f"Error getting orders from Fyers: {e}")
        
        return []
    
    def _map_order_status(self, status_code: int) -> str:
        """Map Fyers status codes to standard status."""
        status_map = {
            1: "PENDING",
            2: "FILLED",
            3: "CANCELLED",
            4: "REJECTED",
            5: "PARTIAL_FILLED"
        }
        return status_map.get(status_code, "UNKNOWN")
    
    # Additional methods would be implemented similarly...
