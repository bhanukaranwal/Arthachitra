import asyncio
import logging
from typing import Dict, List, Optional, Any
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from ..models.orders import Order, OrderStatus, OrderType, OrderSide
from ..models.portfolio import Position, Portfolio
from ...market_connectors.base.connector import BaseConnector
from ...database.models import User, BrokerAccount

logger = logging.getLogger(__name__)

class RiskCheckResult(Enum):
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"

@dataclass
class RiskCheck:
    result: RiskCheckResult
    message: str
    details: Dict[str, Any] = None

@dataclass
class TradingLimits:
    max_order_value: Decimal = Decimal('10000000')  # 1 crore
    max_position_size: Decimal = Decimal('50000000')  # 5 crore
    max_daily_loss: Decimal = Decimal('1000000')  # 10 lakh
    max_orders_per_minute: int = 100
    min_order_value: Decimal = Decimal('1000')  # 1000 rupees

class TradingEngine:
    """
    Core trading engine that handles order management, risk checks,
    position tracking, and broker interaction.
    """
    
    def __init__(self):
        self.connectors: Dict[str, BaseConnector] = {}
        self.user_portfolios: Dict[str, Portfolio] = {}
        self.active_orders: Dict[str, Order] = {}
        self.trading_limits = TradingLimits()
        self.order_history: Dict[str, List[Order]] = {}
        self.is_market_open = True  # Would be set based on market hours
        
    async def initialize(self):
        """Initialize the trading engine."""
        logger.info("Trading engine initializing...")
        
        # Initialize any required components
        await self._load_user_portfolios()
        await self._load_active_orders()
        
        logger.info("Trading engine initialized successfully")
    
    def register_connector(self, name: str, connector: BaseConnector):
        """Register a broker connector."""
        self.connectors[name] = connector
        logger.info(f"Registered connector: {name}")
    
    async def place_order(self, user_id: str, broker_name: str, order_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Place a new order through the trading engine.
        
        Args:
            user_id: ID of the user placing the order
            broker_name: Name of the broker to route the order
            order_request: Order details
            
        Returns:
            Dict containing order result and details
        """
        try:
            # Validate broker connector
            if broker_name not in self.connectors:
                return {
                    "success": False,
                    "error": f"Broker connector '{broker_name}' not found",
                    "error_code": "BROKER_NOT_FOUND"
                }
            
            connector = self.connectors[broker_name]
            
            # Create order object
            order = Order(
                user_id=user_id,
                symbol=order_request["symbol"],
                exchange=order_request.get("exchange", "NSE"),
                side=OrderSide(order_request["side"].upper()),
                quantity=int(order_request["quantity"]),
                order_type=OrderType(order_request.get("order_type", "MARKET").upper()),
                price=Decimal(str(order_request.get("price", 0))) if order_request.get("price") else None,
                status=OrderStatus.PENDING
            )
            
            # Pre-flight risk checks
            risk_result = await self._perform_risk_checks(user_id, order)
            if risk_result.result == RiskCheckResult.FAILED:
                return {
                    "success": False,
                    "error": risk_result.message,
                    "error_code": "RISK_CHECK_FAILED",
                    "details": risk_result.details
                }
            
            # Check market hours
            if not self._is_market_open(order.exchange):
                return {
                    "success": False,
                    "error": f"Market is closed for {order.exchange}",
                    "error_code": "MARKET_CLOSED"
                }
            
            # Place order through connector
            broker_order_id = await connector.place_order(
                symbol=order.symbol,
                exchange=order.exchange,
                side=order.side.value,
                quantity=order.quantity,
                order_type=order.order_type.value,
                price=float(order.price) if order.price else None
            )
            
            if broker_order_id:
                order.broker_order_id = broker_order_id
                order.status = OrderStatus.SUBMITTED
                order.submitted_at = datetime.now()
                
                # Store active order
                self.active_orders[order.id] = order
                
                # Add to user's order history
                if user_id not in self.order_history:
                    self.order_history[user_id] = []
                self.order_history[user_id].append(order)
                
                # Send order update notification
                await self._notify_order_update(order)
                
                return {
                    "success": True,
                    "order_id": order.id,
                    "broker_order_id": broker_order_id,
                    "status": order.status.value,
                    "message": "Order placed successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to place order with broker",
                    "error_code": "BROKER_ORDER_FAILED"
                }
                
        except Exception as e:
            logger.error(f"Error placing order for user {user_id}: {e}")
            return {
                "success": False,
                "error": f"Internal error: {str(e)}",
                "error_code": "INTERNAL_ERROR"
            }
    
    async def cancel_order(self, user_id: str, order_id: str) -> Dict[str, Any]:
        """Cancel an existing order."""
        try:
            if order_id not in self.active_orders:
                return {
                    "success": False,
                    "error": "Order not found",
                    "error_code": "ORDER_NOT_FOUND"
                }
            
            order = self.active_orders[order_id]
            
            # Verify ownership
            if order.user_id != user_id:
                return {
                    "success": False,
                    "error": "Unauthorized access to order",
                    "error_code": "UNAUTHORIZED"
                }
            
            # Check if order can be cancelled
            if order.status not in [OrderStatus.PENDING, OrderStatus.SUBMITTED, OrderStatus.PARTIAL_FILLED]:
                return {
                    "success": False,
                    "error": f"Cannot cancel order in {order.status.value} status",
                    "error_code": "INVALID_STATUS"
                }
            
            # Get connector and cancel order
            connector = self._get_connector_for_order(order)
            if not connector:
                return {
                    "success": False,
                    "error": "Broker connector not available",
                    "error_code": "CONNECTOR_NOT_FOUND"
                }
            
            success = await connector.cancel_order(order.broker_order_id)
            
            if success:
                order.status = OrderStatus.CANCELLED
                order.cancelled_at = datetime.now()
                
                # Remove from active orders
                del self.active_orders[order_id]
                
                # Send update notification
                await self._notify_order_update(order)
                
                return {
                    "success": True,
                    "message": "Order cancelled successfully",
                    "order_id": order_id
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to cancel order with broker",
                    "error_code": "BROKER_CANCEL_FAILED"
                }
                
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            return {
                "success": False,
                "error": f"Internal error: {str(e)}",
                "error_code": "INTERNAL_ERROR"
            }
    
    async def modify_order(self, user_id: str, order_id: str, modifications: Dict[str, Any]) -> Dict[str, Any]:
        """Modify an existing order."""
        try:
            if order_id not in self.active_orders:
                return {
                    "success": False,
                    "error": "Order not found",
                    "error_code": "ORDER_NOT_FOUND"
                }
            
            order = self.active_orders[order_id]
            
            # Verify ownership
            if order.user_id != user_id:
                return {
                    "success": False,
                    "error": "Unauthorized access to order",
                    "error_code": "UNAUTHORIZED"
                }
            
            # Check if order can be modified
            if order.status not in [OrderStatus.PENDING, OrderStatus.SUBMITTED]:
                return {
                    "success": False,
                    "error": f"Cannot modify order in {order.status.value} status",
                    "error_code": "INVALID_STATUS"
                }
            
            # Get connector and modify order
            connector = self._get_connector_for_order(order)
            if not connector:
                return {
                    "success": False,
                    "error": "Broker connector not available",
                    "error_code": "CONNECTOR_NOT_FOUND"
                }
            
            # Prepare modification parameters
            modify_params = {}
            if "quantity" in modifications:
                modify_params["quantity"] = int(modifications["quantity"])
            if "price" in modifications:
                modify_params["price"] = float(modifications["price"])
            if "order_type" in modifications:
                modify_params["order_type"] = modifications["order_type"]
            
            success = await connector.modify_order(order.broker_order_id, **modify_params)
            
            if success:
                # Update order details
                if "quantity" in modifications:
                    order.quantity = int(modifications["quantity"])
                if "price" in modifications:
                    order.price = Decimal(str(modifications["price"]))
                if "order_type" in modifications:
                    order.order_type = OrderType(modifications["order_type"].upper())
                
                order.modified_at = datetime.now()
                
                # Send update notification
                await self._notify_order_update(order)
                
                return {
                    "success": True,
                    "message": "Order modified successfully",
                    "order_id": order_id
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to modify order with broker",
                    "error_code": "BROKER_MODIFY_FAILED"
                }
                
        except Exception as e:
            logger.error(f"Error modifying order {order_id}: {e}")
            return {
                "success": False,
                "error": f"Internal error: {str(e)}",
                "error_code": "INTERNAL_ERROR"
            }
    
    async def _perform_risk_checks(self, user_id: str, order: Order) -> RiskCheck:
        """Perform comprehensive risk checks before placing an order."""
        
        # Get user portfolio
        portfolio = self.user_portfolios.get(user_id)
        if not portfolio:
            return RiskCheck(
                result=RiskCheckResult.FAILED,
                message="User portfolio not found"
            )
        
        # Calculate order value
        if order.price:
            order_value = order.price * Decimal(str(order.quantity))
        else:
            # For market orders, estimate using last price
            last_price = await self._get_last_price(order.symbol, order.exchange)
            if not last_price:
                return RiskCheck(
                    result=RiskCheckResult.FAILED,
                    message="Cannot determine order value - price unavailable"
                )
            order_value = last_price * Decimal(str(order.quantity))
        
        # Check minimum order value
        if order_value < self.trading_limits.min_order_value:
            return RiskCheck(
                result=RiskCheckResult.FAILED,
                message=f"Order value {order_value} is below minimum {self.trading_limits.min_order_value}",
                details={"order_value": float(order_value), "min_required": float(self.trading_limits.min_order_value)}
            )
        
        # Check maximum order value
        if order_value > self.trading_limits.max_order_value:
            return RiskCheck(
                result=RiskCheckResult.FAILED,
                message=f"Order value {order_value} exceeds maximum {self.trading_limits.max_order_value}",
                details={"order_value": float(order_value), "max_allowed": float(self.trading_limits.max_order_value)}
            )
        
        # Check available buying power
        if order.side == OrderSide.BUY:
            if portfolio.cash_balance < order_value:
                return RiskCheck(
                    result=RiskCheckResult.FAILED,
                    message="Insufficient funds for purchase",
                    details={
                        "required": float(order_value),
                        "available": float(portfolio.cash_balance)
                    }
                )
        
        # Check position limits
        current_position = portfolio.get_position(order.symbol, order.exchange)
        if current_position:
            new_quantity = current_position.quantity
            if order.side == OrderSide.BUY:
                new_quantity += order.quantity
            else:
                new_quantity -= order.quantity
            
            new_position_value = abs(new_quantity) * (current_position.average_price or order.price or last_price)
            
            if new_position_value > self.trading_limits.max_position_size:
                return RiskCheck(
                    result=RiskCheckResult.FAILED,
                    message=f"Position size would exceed limit",
                    details={
                        "new_position_value": float(new_position_value),
                        "max_allowed": float(self.trading_limits.max_position_size)
                    }
                )
        
        # Check daily loss limits
        today_pnl = await self._get_today_pnl(user_id)
        if today_pnl < -self.trading_limits.max_daily_loss:
            return RiskCheck(
                result=RiskCheckResult.FAILED,
                message="Daily loss limit exceeded",
                details={
                    "daily_pnl": float(today_pnl),
                    "max_loss": float(-self.trading_limits.max_daily_loss)
                }
            )
        
        # Check order frequency
        recent_orders = await self._get_recent_orders(user_id, minutes=1)
        if len(recent_orders) >= self.trading_limits.max_orders_per_minute:
            return RiskCheck(
                result=RiskCheckResult.FAILED,
                message="Order frequency limit exceeded",
                details={
                    "recent_orders": len(recent_orders),
                    "max_per_minute": self.trading_limits.max_orders_per_minute
                }
            )
        
        return RiskCheck(result=RiskCheckResult.PASSED, message="All risk checks passed")
    
    async def _get_last_price(self, symbol: str, exchange: str) -> Optional[Decimal]:
        """Get the last traded price for a symbol."""
        # This would typically fetch from market data service
        # For now, return a placeholder
        return Decimal('100.00')
    
    async def _get_today_pnl(self, user_id: str) -> Decimal:
        """Get today's P&L for a user."""
        # This would calculate from positions and trades
        return Decimal('0.00')
    
    async def _get_recent_orders(self, user_id: str, minutes: int) -> List[Order]:
        """Get recent orders for a user within specified minutes."""
        if user_id not in self.order_history:
            return []
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_orders = [
            order for order in self.order_history[user_id]
            if order.created_at >= cutoff_time
        ]
        
        return recent_orders
    
    def _get_connector_for_order(self, order: Order) -> Optional[BaseConnector]:
        """Get the appropriate connector for an order."""
        # Logic to determine which connector to use based on order details
        # For now, return the first available connector
        return next(iter(self.connectors.values())) if self.connectors else None
    
    def _is_market_open(self, exchange: str) -> bool:
        """Check if the market is open for trading."""
        # This would implement actual market hours checking
        return self.is_market_open
    
    async def _notify_order_update(self, order: Order):
        """Send order update notification via WebSocket."""
        from ..websocket_manager import websocket_manager
        
        message = {
            "type": "order_update",
            "order_id": order.id,
            "symbol": order.symbol,
            "status": order.status.value,
            "filled_quantity": order.filled_quantity,
            "remaining_quantity": order.quantity - order.filled_quantity
        }
        
        await websocket_manager.send_to_user(order.user_id, message)
    
    async def _load_user_portfolios(self):
        """Load user portfolios from database."""
        # Implementation would load from database
        pass
    
    async def _load_active_orders(self):
        """Load active orders from database."""
        # Implementation would load from database
        pass
    
    def get_engine_stats(self) -> Dict[str, Any]:
        """Get trading engine statistics."""
        return {
            "active_orders": len(self.active_orders),
            "connected_brokers": len(self.connectors),
            "user_portfolios": len(self.user_portfolios),
            "is_market_open": self.is_market_open
        }

# Global trading engine instance
trading_engine = TradingEngine()
