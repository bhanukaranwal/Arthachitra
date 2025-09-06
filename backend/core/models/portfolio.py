from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class Position:
    symbol: str
    exchange: str
    quantity: int
    average_price: Decimal
    current_price: Optional[Decimal] = None
    unrealized_pnl: Decimal = field(default=Decimal('0'))
    realized_pnl: Decimal = field(default=Decimal('0'))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def market_value(self) -> Decimal:
        if self.current_price:
            return self.current_price * abs(self.quantity)
        return self.average_price * abs(self.quantity)
    
    @property
    def total_pnl(self) -> Decimal:
        return self.unrealized_pnl + self.realized_pnl
    
    @property
    def pnl_percentage(self) -> float:
        cost_basis = self.average_price * abs(self.quantity)
        if cost_basis > 0:
            return float((self.total_pnl / cost_basis) * 100)
        return 0.0

@dataclass
class Portfolio:
    user_id: str
    positions: Dict[str, Position] = field(default_factory=dict)
    cash_balance: Decimal = field(default=Decimal('0'))
    initial_capital: Decimal = field(default=Decimal('0'))
    total_invested: Decimal = field(default=Decimal('0'))
    
    def get_position(self, symbol: str, exchange: str) -> Optional[Position]:
        key = f"{symbol}:{exchange}"
        return self.positions.get(key)
    
    def add_or_update_position(self, position: Position):
        key = f"{position.symbol}:{position.exchange}"
        self.positions[key] = position
    
    @property
    def total_equity_value(self) -> Decimal:
        return sum(pos.market_value for pos in self.positions.values())
    
    @property
    def total_portfolio_value(self) -> Decimal:
        return self.cash_balance + self.total_equity_value
    
    @property
    def total_pnl(self) -> Decimal:
        return sum(pos.total_pnl for pos in self.positions.values())
    
    @property
    def day_pnl(self) -> Decimal:
        return sum(pos.unrealized_pnl for pos in self.positions.values())
