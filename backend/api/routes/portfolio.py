from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from decimal import Decimal

from ...core.auth.jwt_handler import security, jwt_handler
from ...database.connection import get_db
from ...database.models import Position, User
from ...core.models.portfolio import Portfolio as PortfolioModel

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

@router.get("/")
async def get_portfolio(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Get user's complete portfolio."""
    try:
        user_id = jwt_handler.get_current_user_id(credentials)
        
        # Get positions from database
        result = await db.execute(
            select(Position).where(Position.user_id == user_id)
        )
        positions = result.scalars().all()
        
        # Calculate portfolio metrics
        total_equity_value = sum(pos.quantity * pos.current_price for pos in positions if pos.current_price)
        total_pnl = sum(pos.unrealized_pnl + pos.realized_pnl for pos in positions)
        day_pnl = sum(pos.unrealized_pnl for pos in positions)
        
        # Get cash balance (would be from a separate cash_balance table)
        cash_balance = Decimal('100000.00')  # Placeholder
        
        portfolio_data = {
            "total_value": float(total_equity_value + cash_balance),
            "cash_balance": float(cash_balance),
            "equity_value": float(total_equity_value),
            "day_pnl": float(day_pnl),
            "total_pnl": float(total_pnl),
            "positions": [
                {
                    "symbol": pos.symbol,
                    "exchange": pos.exchange,
                    "quantity": pos.quantity,
                    "average_price": float(pos.average_price),
                    "current_price": float(pos.current_price) if pos.current_price else 0,
                    "unrealized_pnl": float(pos.unrealized_pnl),
                    "realized_pnl": float(pos.realized_pnl),
                }
                for pos in positions
            ]
        }
        
        return portfolio_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/positions")
async def get_positions(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Get user's current positions."""
    try:
        user_id = jwt_handler.get_current_user_id(credentials)
        
        result = await db.execute(
            select(Position).where(Position.user_id == user_id)
        )
        positions = result.scalars().all()
        
        return [
            {
                "id": str(pos.id),
                "symbol": pos.symbol,
                "exchange": pos.exchange,
                "quantity": pos.quantity,
                "average_price": float(pos.average_price),
                "current_price": float(pos.current_price) if pos.current_price else 0,
                "market_value": float(pos.quantity * pos.current_price) if pos.current_price else 0,
                "unrealized_pnl": float(pos.unrealized_pnl),
                "realized_pnl": float(pos.realized_pnl),
                "pnl_percent": float((pos.unrealized_pnl / (pos.average_price * pos.quantity)) * 100) if pos.average_price else 0,
                "created_at": pos.created_at.isoformat(),
                "updated_at": pos.updated_at.isoformat()
            }
            for pos in positions
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_portfolio_history(
    days: int = 30,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Get portfolio historical performance."""
    try:
        user_id = jwt_handler.get_current_user_id(credentials)
        
        # This would fetch from a portfolio_snapshots table
        # For now, return sample data
        from datetime import datetime, timedelta
        import random
        
        history = []
        start_date = datetime.now() - timedelta(days=days)
        base_value = 1000000.0  # 10 lakh starting value
        
        for i in range(days):
            date = start_date + timedelta(days=i)
            daily_change = random.uniform(-0.02, 0.02)  # ±2% daily
            base_value *= (1 + daily_change)
            
            history.append({
                "date": date.date().isoformat(),
                "total_value": round(base_value, 2),
                "day_pnl": round(base_value * daily_change, 2),
                "day_pnl_percent": round(daily_change * 100, 3)
            })
        
        return {
            "history": history,
            "period": f"{days} days",
            "total_return": round(((base_value / 1000000.0) - 1) * 100, 2),
            "volatility": round(random.uniform(15, 25), 2)  # Placeholder volatility
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
