from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIAL_FILLED = "partial_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

@dataclass
class Order:
    order_id: str
    symbol: str
    exchange: str
    side: str
    quantity: int
    filled_quantity: int
    price: float
    order_type: str
    status: OrderStatus
    timestamp: datetime

@dataclass
class Position:
    symbol: str
    exchange: str
    quantity: int
    average_price: float
    current_price: Optional[float] = None
    pnl: float = 0.0
    product: str = "MIS"

@dataclass
class Trade:
    trade_id: str
    order_id: str
    symbol: str
    exchange: str
    side: str
    quantity: int
    price: float
    timestamp: datetime

class BaseConnector(ABC):
    """
    Abstract base class for all broker connectors.
    Defines the interface that all broker integrations must implement.
    """
    
    def __init__(self):
        self.connected = False
        self.name = ""
        
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to the broker."""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from the broker."""
        pass
    
    @abstractmethod
    async def get_quote(self, symbol: str, exchange: str = "NSE") -> Optional[Dict]:
        """Get current market quote for a symbol."""
        pass
    
    @abstractmethod
    async def get_historical_data(self, symbol: str, exchange: str, timeframe: str, 
                                from_date: datetime, to_date: datetime) -> List[Dict]:
        """Get historical OHLC data."""
        pass
    
    @abstractmethod
    async def place_order(self, symbol: str, exchange: str, side: str, quantity: int,
                         order_type: str = "MARKET", price: float = None, 
                         product: str = "MIS", validity: str = "DAY") -> Optional[str]:
        """Place a new order."""
        pass
    
    @abstractmethod
    async def modify_order(self, order_id: str, quantity: int = None, 
                          price: float = None, order_type: str = None) -> bool:
        """Modify an existing order."""
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str, variety: str = "regular") -> bool:
        """Cancel an order."""
        pass
    
    @abstractmethod
    async def get_orders(self) -> List[Order]:
        """Get all orders for the day."""
        pass
    
    @abstractmethod
    async def get_positions(self) -> List[Position]:
        """Get current positions."""
        pass
    
    @abstractmethod
    async def start_websocket(self, on_tick_callback):
        """Start WebSocket connection for real-time data."""
        pass
    
    @abstractmethod
    async def subscribe_symbols(self, symbols: List[str], mode: str = "quote"):
        """Subscribe to real-time data for symbols."""
        pass
    
    @abstractmethod
    async def unsubscribe_symbols(self, symbols: List[str]):
        """Unsubscribe from real-time data."""
        pass
    
    def is_connected(self) -> bool:
        """Check if connector is connected."""
        return self.connected
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the connector."""
        return {
            "broker": self.name,
            "connected": self.connected,
            "timestamp": datetime.now().isoformat()
        }
