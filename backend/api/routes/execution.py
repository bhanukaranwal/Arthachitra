from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal

from ...core.auth.jwt_handler import security, jwt_handler
from ...database.connection import get_db
from ...core.engine.trading_engine import trading_engine
from ...core.websocket_manager import websocket_manager

router = APIRouter(prefix="/execution", tags=["order_execution"])

class OrderRequest(BaseModel):
    symbol: str
    exchange: str = "NSE"
    side: str  # BUY or SELL
    quantity: int
    order_type: str = "MARKET"  # MARKET, LIMIT, STOP, STOP_LIMIT
    price: Optional[float] = None
    stop_price: Optional[float] = None
    product: str = "MIS"  # MIS, CNC, NRML
    validity: str = "DAY"  # DAY, IOC, GTD
    disclosed_quantity: Optional[int] = None
    strategy_name: Optional[str] = None

class OrderModifyRequest(BaseModel):
    quantity: Optional[int] = None
    price: Optional[float] = None
    order_type: Optional[str] = None
    validity: Optional[str] = None

@router.post("/orders")
async def place_order(
    order_request: OrderRequest,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Place a new order."""
    try:
        user_id = jwt_handler.get_current_user_id(credentials)
        
        # Convert to dict for trading engine
        order_data = order_request.dict()
        
        # Place order through trading engine
        result = await trading_engine.place_order(user_id, "zerodha", order_data)
        
        if result["success"]:
            # Send WebSocket notification
            background_tasks.add_task(
                websocket_manager.send_to_user,
                user_id,
                {
                    "type": "order_placed",
                    "order_id": result["order_id"],
                    "symbol": order_request.symbol,
                    "side": order_request.side,
                    "quantity": order_request.quantity
                }
            )
            
            return {
                "success": True,
                "order_id": result["order_id"],
                "message": "Order placed successfully"
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=result["error"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders")
async def get_orders(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Get all orders for the user."""
    try:
        user_id = jwt_handler.get_current_user_id(credentials)
        
        # Get orders from database
        from ...database.models import Order
        from sqlalchemy import select
        
        result = await db.execute(
            select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
        )
        orders = result.scalars().all()
        
        return [
            {
                "id": str(order.id),
                "symbol": order.symbol,
                "exchange": order.exchange,
                "side": order.side,
                "quantity": order.quantity,
                "filled_quantity": order.filled_quantity,
                "price": float(order.price) if order.price else None,
                "average_price": float(order.average_price) if order.average_price else None,
                "order_type": order.order_type,
                "status": order.status,
                "created_at": order.created_at.isoformat(),
                "executed_at": order.executed_at.isoformat() if order.executed_at else None
            }
            for order in orders
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/orders/{order_id}")
async def modify_order(
    order_id: str,
    modify_request: OrderModifyRequest,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Modify an existing order."""
    try:
        user_id = jwt_handler.get_current_user_id(credentials)
        
        # Modify order through trading engine
        modifications = modify_request.dict(exclude_unset=True)
        result = await trading_engine.modify_order(user_id, order_id, modifications)
        
        if result["success"]:
            # Send WebSocket notification
            background_tasks.add_task(
                websocket_manager.send_to_user,
                user_id,
                {
                    "type": "order_modified",
                    "order_id": order_id,
                    "modifications": modifications
                }
            )
            
            return {
                "success": True,
                "message": "Order modified successfully"
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=result["error"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/orders/{order_id}")
async def cancel_order(
    order_id: str,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Cancel an existing order."""
    try:
        user_id = jwt_handler.get_current_user_id(credentials)
        
        # Cancel order through trading engine
        result = await trading_engine.cancel_order(user_id, order_id)
        
        if result["success"]:
            # Send WebSocket notification
            background_tasks.add_task(
                websocket_manager.send_to_user,
                user_id,
                {
                    "type": "order_cancelled",
                    "order_id": order_id
                }
            )
            
            return {
                "success": True,
                "message": "Order cancelled successfully"
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=result["error"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders/{order_id}")
async def get_order_details(
    order_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Get details of a specific order."""
    try:
        user_id = jwt_handler.get_current_user_id(credentials)
        
        from ...database.models import Order
        from sqlalchemy import select
        
        result = await db.execute(
            select(Order).where(
                Order.id == order_id,
                Order.user_id == user_id
            )
        )
        order = result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return {
            "id": str(order.id),
            "symbol": order.symbol,
            "exchange": order.exchange,
            "side": order.side,
            "quantity": order.quantity,
            "filled_quantity": order.filled_quantity,
            "remaining_quantity": order.quantity - order.filled_quantity,
            "price": float(order.price) if order.price else None,
            "average_price": float(order.average_price) if order.average_price else None,
            "order_type": order.order_type,
            "status": order.status,
            "broker_order_id": order.order_id_broker,
            "strategy_name": order.strategy_name,
            "created_at": order.created_at.isoformat(),
            "submitted_at": order.submitted_at.isoformat() if order.submitted_at else None,
            "executed_at": order.executed_at.isoformat() if order.executed_at else None,
            "fill_percentage": (order.filled_quantity / order.quantity * 100) if order.quantity > 0 else 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trades")
async def get_trades(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Get all trades for the user."""
    try:
        user_id = jwt_handler.get_current_user_id(credentials)
        
        from ...database.models import Trade
        from sqlalchemy import select
        
        result = await db.execute(
            select(Trade).where(Trade.user_id == user_id).order_by(Trade.executed_at.desc())
        )
        trades = result.scalars().all()
        
        return [
            {
                "id": str(trade.id),
                "order_id": str(trade.order_id),
                "symbol": trade.symbol,
                "exchange": trade.exchange,
                "side": trade.side,
                "quantity": trade.quantity,
                "price": float(trade.price),
                "commission": float(trade.commission),
                "executed_at": trade.executed_at.isoformat()
            }
            for trade in trades
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
