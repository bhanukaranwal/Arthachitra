import pytest
import asyncio
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import json

from main import app
from core.models.market_data import OHLCV

client = TestClient(app)

class TestMarketDataAPI:
    
    def test_get_symbols(self):
        """Test getting list of available symbols."""
        response = client.get("/api/v1/market/symbols")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check symbol structure
        symbol = data[0]
        required_fields = ["symbol", "name", "exchange", "asset_type", "lot_size", "tick_size"]
        for field in required_fields:
            assert field in symbol
    
    def test_get_symbols_with_filter(self):
        """Test getting symbols with exchange filter."""
        response = client.get("/api/v1/market/symbols?exchange=NSE")
        assert response.status_code == 200
        
        data = response.json()
        for symbol in data:
            assert symbol["exchange"] == "NSE"
    
    def test_get_ohlc_data(self):
        """Test getting OHLC data for a symbol."""
        response = client.get("/api/v1/market/ohlc/NIFTY?timeframe=1d&limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert "symbol" in data
        assert "timeframe" in data
        assert "data" in data
        assert "count" in data
        
        assert data["symbol"] == "NIFTY"
        assert data["timeframe"] == "1d"
        assert len(data["data"]) <= 10
        
        # Check OHLC structure
        if data["data"]:
            candle = data["data"][0]
            required_fields = ["timestamp", "open", "high", "low", "close", "volume"]
            for field in required_fields:
                assert field in candle
    
    def test_get_ohlc_data_with_dates(self):
        """Test getting OHLC data with date range."""
        from_date = (datetime.now() - timedelta(days=7)).isoformat()
        to_date = datetime.now().isoformat()
        
        response = client.get(
            f"/api/v1/market/ohlc/NIFTY?timeframe=1d&from_date={from_date}&to_date={to_date}"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["data"]) <= 7  # Should not exceed date range
    
    def test_get_ohlc_invalid_symbol(self):
        """Test getting OHLC data for invalid symbol."""
        response = client.get("/api/v1/market/ohlc/INVALID_SYMBOL")
        assert response.status_code == 200  # Should still return data (simulated)
        
        data = response.json()
        assert data["symbol"] == "INVALID_SYMBOL"
    
    def test_get_quote(self):
        """Test getting current quote for a symbol."""
        response = client.get("/api/v1/market/quote/NIFTY")
        assert response.status_code == 200
        
        data = response.json()
        required_fields = ["symbol", "price", "bid", "ask", "volume", "change", "change_percent", "timestamp"]
        for field in required_fields:
            assert field in data
        
        assert data["symbol"] == "NIFTY"
        assert isinstance(data["price"], (int, float))
        assert isinstance(data["volume"], int)
    
    def test_get_quote_invalid_symbol(self):
        """Test getting quote for invalid symbol."""
        response = client.get("/api/v1/market/quote/INVALID")
        assert response.status_code == 200  # Should still return simulated data
        
        data = response.json()
        assert data["symbol"] == "INVALID"
    
    def test_ohlc_data_validation(self):
        """Test OHLC data validation."""
        response = client.get("/api/v1/market/ohlc/NIFTY?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        for candle in data["data"]:
            # Validate OHLC relationships
            assert candle["high"] >= candle["open"]
            assert candle["high"] >= candle["close"]
            assert candle["low"] <= candle["open"]
            assert candle["low"] <= candle["close"]
            assert candle["volume"] >= 0
    
    def test_timeframe_validation(self):
        """Test different timeframe formats."""
        timeframes = ["1m", "5m", "15m", "1h", "1d"]
        
        for tf in timeframes:
            response = client.get(f"/api/v1/market/ohlc/NIFTY?timeframe={tf}&limit=5")
            assert response.status_code == 200
            
            data = response.json()
            assert data["timeframe"] == tf
    
    def test_limit_validation(self):
        """Test limit parameter validation."""
        # Valid limits
        for limit in [1, 100, 1000]:
            response = client.get(f"/api/v1/market/ohlc/NIFTY?limit={limit}")
            assert response.status_code == 200
            
            data = response.json()
            assert len(data["data"]) <= limit
        
        # Invalid limits should be handled gracefully
        response = client.get("/api/v1/market/ohlc/NIFTY?limit=0")
        assert response.status_code == 422  # Validation error
        
        response = client.get("/api/v1/market/ohlc/NIFTY?limit=10000")
        assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
class TestWebSocketConnections:
    
    async def test_market_data_websocket(self):
        """Test WebSocket connection for market data."""
        import websockets
        
        uri = "ws://localhost:8000/ws/market/NIFTY/1m"
        
        try:
            async with websockets.connect(uri) as websocket:
                # Should receive historical data first
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                
                assert data["type"] == "historical"
                assert data["symbol"] == "NIFTY"
                assert data["timeframe"] == "1m"
                assert "candles" in data
                assert "volume" in data
                
        except asyncio.TimeoutError:
            pytest.fail("WebSocket did not send data within timeout")
        except Exception as e:
            pytest.fail(f"WebSocket connection failed: {e}")
    
    async def test_orderbook_websocket(self):
        """Test WebSocket connection for order book data."""
        import websockets
        
        uri = "ws://localhost:8000/ws/orderbook/NIFTY"
        
        try:
            async with websockets.connect(uri) as websocket:
                # Should receive order book updates
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                
                assert data["type"] == "orderbook"
                assert data["symbol"] == "NIFTY"
                assert "bids" in data
                assert "asks" in data
                
        except asyncio.TimeoutError:
            pytest.fail("WebSocket did not send order book data within timeout")
        except Exception as e:
            pytest.fail(f"WebSocket connection failed: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
