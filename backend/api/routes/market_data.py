from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta
import pandas as pd

from core.models.market_data import OHLCV, SymbolInfo
from market_connectors.base.connector import BaseConnector

router = APIRouter(prefix="/market", tags=["market_data"])

@router.get("/symbols", response_model=List[SymbolInfo])
async def get_symbols(
    exchange: Optional[str] = Query(None, description="Filter by exchange"),
    asset_type: Optional[str] = Query(None, description="Filter by asset type")
):
    """Get list of available symbols"""
    try:
        # This would fetch from your symbol database
        symbols = [
            SymbolInfo(
                symbol="NIFTY",
                name="Nifty 50",
                exchange="NSE",
                asset_type="INDEX",
                lot_size=25,
                tick_size=0.05
            ),
            SymbolInfo(
                symbol="BANKNIFTY",
                name="Bank Nifty",
                exchange="NSE",
                asset_type="INDEX",
                lot_size=25,
                tick_size=0.05
            ),
            SymbolInfo(
                symbol="RELIANCE",
                name="Reliance Industries Ltd",
                exchange="NSE",
                asset_type="EQUITY",
                lot_size=1,
                tick_size=0.05
            )
        ]
        return symbols
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ohlc/{symbol}")
async def get_ohlc_data(
    symbol: str,
    timeframe: str = Query("1d", description="Timeframe (1m, 5m, 15m, 1h, 1d)"),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=5000)
):
    """Get OHLC data for a symbol"""
    try:
        # Set default dates if not provided
        if not to_date:
            to_date = datetime.now()
        if not from_date:
            from_date = to_date - timedelta(days=30)
        
        # Generate sample OHLC data (replace with actual data fetching)
        import random
        
        base_price = 100.0
        data = []
        current_time = from_date
        
        while current_time <= to_date and len(data) < limit:
            # Simulate price movement
            open_price = base_price + random.uniform(-2, 2)
            high_price = open_price + random.uniform(0, 3)
            low_price = open_price - random.uniform(0, 3)
            close_price = open_price + random.uniform(-2, 2)
            volume = random.randint(1000, 100000)
            
            data.append(OHLCV(
                timestamp=current_time,
                open=round(open_price, 2),
                high=round(high_price, 2),
                low=round(low_price, 2),
                close=round(close_price, 2),
                volume=volume
            ))
            
            base_price = close_price
            
            # Increment time based on timeframe
            if timeframe == "1m":
                current_time += timedelta(minutes=1)
            elif timeframe == "5m":
                current_time += timedelta(minutes=5)
            elif timeframe == "15m":
                current_time += timedelta(minutes=15)
            elif timeframe == "1h":
                current_time += timedelta(hours=1)
            else:  # 1d
                current_time += timedelta(days=1)
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "data": data,
            "count": len(data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quote/{symbol}")
async def get_quote(symbol: str):
    """Get current quote for a symbol"""
    try:
        # This would fetch real-time quote from market data provider
        import random
        
        price = 100 + random.uniform(-10, 10)
        
        return {
            "symbol": symbol,
            "price": round(price, 2),
            "bid": round(price - 0.05, 2),
            "ask": round(price + 0.05, 2),
            "volume": random.randint(1000, 50000),
            "change": round(random.uniform(-5, 5), 2),
            "change_percent": round(random.uniform(-5, 5), 2),
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
