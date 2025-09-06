import pytest
import asyncio
from decimal import Decimal
from datetime import datetime

from core.engine.trading_engine import TradingEngine, RiskCheckResult
from core.models.orders import Order, OrderType, OrderSide, OrderStatus
from core.models.portfolio import Portfolio, Position

class MockConnector:
    def __init__(self):
        self.orders = {}
        self.order_counter = 1
    
    async def place_order(self, symbol, exchange, side, quantity, order_type="MARKET", price=None):
        order_id = f"MOCK_{self.order_counter}"
        self.order_counter += 1
        self.orders[order_id] = {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "status": "SUBMITTED"
        }
        return order_id
    
    async def cancel_order(self, order_id):
        if order_id in self.orders:
            self.orders[order_id]["status"] = "CANCELLED"
            return True
        return False
    
    async def modify_order(self, order_id, **kwargs):
        if order_id in self.orders:
            self.orders[order_id].update(kwargs)
            return True
        return False

@pytest.fixture
async def trading_engine():
    engine = TradingEngine()
    await engine.initialize()
    
    # Register mock connector
    mock_connector = MockConnector()
    engine.register_connector("mock_broker", mock_connector)
    
    return engine

@pytest.fixture
def sample_portfolio():
    portfolio = Portfolio(user_id="test_user")
    portfolio.cash_balance = Decimal('100000')  # 1 lakh
    
    # Add a sample position
    position = Position(
        symbol="RELIANCE",
        exchange="NSE",
        quantity=100,
        average_price=Decimal('2500'),
        current_price=Decimal('2550')
    )
    portfolio.add_or_update_position(position)
    
    return portfolio

@pytest.mark.asyncio
class TestTradingEngine:
    
    async def test_place_order_success(self, trading_engine):
        """Test successful order placement."""
        order_request = {
            "symbol": "RELIANCE",
            "exchange": "NSE",
            "side": "BUY",
            "quantity": 100,
            "order_type": "MARKET"
        }
        
        # Mock portfolio for user
        trading_engine.user_portfolios["test_user"] = Portfolio(
            user_id="test_user",
            cash_balance=Decimal('100000')
        )
        
        result = await trading_engine.place_order("test_user", "mock_broker", order_request)
        
        assert result["success"] is True
        assert "order_id" in result
        assert "broker_order_id" in result
    
    async def test_place_order_insufficient_funds(self, trading_engine):
        """Test order placement with insufficient funds."""
        order_request = {
            "symbol": "RELIANCE",
            "exchange": "NSE",
            "side": "BUY",
            "quantity": 1000,  # Large quantity
            "order_type": "LIMIT",
            "price": 2500
        }
        
        # Mock portfolio with low balance
        trading_engine.user_portfolios["test_user"] = Portfolio(
            user_id="test_user",
            cash_balance=Decimal('1000')  # Only 1000 rupees
        )
        
        result = await trading_engine.place_order("test_user", "mock_broker", order_request)
        
        assert result["success"] is False
        assert "insufficient funds" in result["error"].lower()
    
    async def test_cancel_order_success(self, trading_engine):
        """Test successful order cancellation."""
        # First place an order
        order_request = {
            "symbol": "RELIANCE",
            "exchange": "NSE",
            "side": "BUY",
            "quantity": 100,
            "order_type": "MARKET"
        }
        
        trading_engine.user_portfolios["test_user"] = Portfolio(
            user_id="test_user",
            cash_balance=Decimal('100000')
        )
        
        place_result = await trading_engine.place_order("test_user", "mock_broker", order_request)
        order_id = place_result["order_id"]
        
        # Now cancel it
        cancel_result = await trading_engine.cancel_order("test_user", order_id)
        
        assert cancel_result["success"] is True
        assert cancel_result["order_id"] == order_id
    
    async def test_cancel_nonexistent_order(self, trading_engine):
        """Test cancelling non-existent order."""
        result = await trading_engine.cancel_order("test_user", "non_existent_id")
        
        assert result["success"] is False
        assert result["error_code"] == "ORDER_NOT_FOUND"
    
    async def test_risk_check_order_value_limits(self, trading_engine):
        """Test risk checks for order value limits."""
        # Create order that exceeds maximum value
        large_order = Order(
            user_id="test_user",
            symbol="RELIANCE",
            exchange="NSE",
            side=OrderSide.BUY,
            quantity=100000,  # Very large quantity
            order_type=OrderType.LIMIT,
            price=Decimal('5000')  # High price
        )
        
        trading_engine.user_portfolios["test_user"] = Portfolio(
            user_id="test_user",
            cash_balance=Decimal('1000000000')  # Sufficient cash
        )
        
        risk_result = await trading_engine._perform_risk_checks("test_user", large_order)
        
        assert risk_result.result == RiskCheckResult.FAILED
        assert "exceeds maximum" in risk_result.message
    
    async def test_modify_order_success(self, trading_engine):
        """Test successful order modification."""
        # First place an order
        order_request = {
            "symbol": "RELIANCE",
            "exchange": "NSE",
            "side": "BUY",
            "quantity": 100,
            "order_type": "LIMIT",
            "price": 2500
        }
        
        trading_engine.user_portfolios["test_user"] = Portfolio(
            user_id="test_user",
            cash_balance=Decimal('100000')
        )
        
        place_result = await trading_engine.place_order("test_user", "mock_broker", order_request)
        order_id = place_result["order_id"]
        
        # Now modify it
        modifications = {"quantity": 150, "price": 2450}
        modify_result = await trading_engine.modify_order("test_user", order_id, modifications)
        
        assert modify_result["success"] is True
        assert modify_result["order_id"] == order_id
    
    def test_engine_stats(self, trading_engine):
        """Test getting engine statistics."""
        stats = trading_engine.get_engine_stats()
        
        assert "active_orders" in stats
        assert "connected_brokers" in stats
        assert "user_portfolios" in stats
        assert "is_market_open" in stats
        
        assert isinstance(stats["active_orders"], int)
        assert isinstance(stats["connected_brokers"], int)
