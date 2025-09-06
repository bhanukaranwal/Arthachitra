from enum import Enum
from datetime import datetime
from typing import Optional
from decimal import Decimal
from dataclasses import dataclass, field
from uuid import uuid4

class OrderStatus(Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIAL_FILLED = "partial_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    ICEBERG = "iceberg"
    BRACKET = "bracket"
    OCO = "oco"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

@dataclass
class Order:
    symbol: str
    exchange: str
    side: OrderSide
    quantity: int
    order_type: OrderType
    user_id: str
    id: str = field(default_factory=lambda: str(uuid4()))
    broker_order_id: Optional[str] = None
    price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    filled_quantity: int = 0
    average_price: Optional[Decimal] = None
    status: OrderStatus = OrderStatus.PENDING
    strategy_name: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    submitted_at: Optional[datetime] = None
    filled_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    
    @property
    def remaining_quantity(self) -> int:
        return self.quantity - self.filled_quantity
    
    @property
    def is_complete(self) -> bool:
        return self.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED, OrderStatus.EXPIRED]
    
    @property
    def fill_percentage(self) -> float:
        return (self.filled_quantity / self.quantity) * 100 if self.quantity > 0 else 0
