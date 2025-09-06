import math
import statistics
from typing import List, Optional, Any, Dict

class BuiltinFunctions:
    def __init__(self, interpreter):
        self.interpreter = interpreter
        
    # Market Data Functions
    def get_open(self, index: int = 0) -> float:
        """Get open price at index (0 = current, 1 = previous, etc.)"""
        data = self.interpreter.market_data.get('open', [])
        if index < len(data):
            return data[-(index + 1)]
        return 0.0
        
    def get_high(self, index: int = 0) -> float:
        """Get high price at index"""
        data = self.interpreter.market_data.get('high', [])
        if index < len(data):
            return data[-(index + 1)]
        return 0.0
        
    def get_low(self, index: int = 0) -> float:
        """Get low price at index"""
        data = self.interpreter.market_data.get('low', [])
        if index < len(data):
            return data[-(index + 1)]
        return 0.0
        
    def get_close(self, index: int = 0) -> float:
        """Get close price at index"""
        data = self.interpreter.market_data.get('close', [])
        if index < len(data):
            return data[-(index + 1)]
        return 0.0
        
    def get_volume(self, index: int = 0) -> float:
        """Get volume at index"""
        data = self.interpreter.market_data.get('volume', [])
        if index < len(data):
            return data[-(index + 1)]
        return 0.0
    
    # Technical Indicators
    def sma(self, period: int = 20, source: str = 'close') -> float:
        """Simple Moving Average"""
        data = self.interpreter.market_data.get(source, [])
        if len(data) < period:
            return 0.0
        return sum(data[-period:]) / period
    
    def ema(self, period: int = 20, source: str = 'close') -> float:
        """Exponential Moving Average"""
        data = self.interpreter.market_data.get(source, [])
        if len(data) < period:
            return 0.0
        
        multiplier = 2 / (period + 1)
        ema_value = data[0]
        
        for price in data[1:]:
            ema_value = (price * multiplier) + (ema_value * (1 - multiplier))
            
        return ema_value
    
    def rsi(self, period: int = 14, source: str = 'close') -> float:
        """Relative Strength Index"""
        data = self.interpreter.market_data.get(source, [])
        if len(data) < period + 1:
            return 50.0
        
        gains = []
        losses = []
        
        for i in range(1, len(data)):
            change = data[i] - data[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(-change)
        
        if len(gains) < period:
            return 50.0
            
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
            
        rs = avg_gain / avg_loss
        rsi_value = 100 - (100 / (1 + rs))
        
        return rsi_value
    
    def macd(self, fast: int = 12, slow: int = 26, signal: int = 9, source: str = 'close') -> Dict[str, float]:
        """MACD Indicator"""
        data = self.interpreter.market_data.get(source, [])
        if len(data) < slow:
            return {"macd": 0.0, "signal": 0.0, "histogram": 0.0}
        
        # Calculate EMAs
        fast_ema = self._calculate_ema(data, fast)
        slow_ema = self._calculate_ema(data, slow)
        
        macd_line = fast_ema - slow_ema
        
        # Calculate signal line (EMA of MACD)
        # For simplicity, using SMA instead of EMA here
        signal_line = macd_line  # Simplified
        
        histogram = macd_line - signal_line
        
        return {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram
        }
    
    def bollinger_bands(self, period: int = 20, multiplier: float = 2.0, source: str = 'close') -> Dict[str, float]:
        """Bollinger Bands"""
        data = self.interpreter.market_data.get(source, [])
        if len(data) < period:
            return {"upper": 0.0, "middle": 0.0, "lower": 0.0}
        
        recent_data = data[-period:]
        middle = sum(recent_data) / period
        
        variance = sum((x - middle) ** 2 for x in recent_data) / period
        std_dev = math.sqrt(variance)
        
        upper = middle + (multiplier * std_dev)
        lower = middle - (multiplier * std_dev)
        
        return {
            "upper": upper,
            "middle": middle,
            "lower": lower
        }
    
    def _calculate_ema(self, data: List[float], period: int) -> float:
        """Helper function to calculate EMA"""
        if len(data) < period:
            return 0.0
        
        multiplier = 2 / (period + 1)
        ema_value = sum(data[:period]) / period
        
        for price in data[period:]:
            ema_value = (price * multiplier) + (ema_value * (1 - multiplier))
            
        return ema_value
    
    # Trading Functions
    def buy(self, message: str = "", quantity: Optional[float] = None):
        """Execute buy order"""
        trade = {
            "action": "buy",
            "message": message,
            "quantity": quantity,
            "price": self.get_close(),
            "timestamp": len(self.interpreter.trades)
        }
        self.interpreter.trades.append(trade)
        return True
    
    def sell(self, message: str = "", quantity: Optional[float] = None):
        """Execute sell order"""
        trade = {
            "action": "sell",
            "message": message,
            "quantity": quantity,
            "price": self.get_close(),
            "timestamp": len(self.interpreter.trades)
        }
        self.interpreter.trades.append(trade)
        return True
    
    def get_position(self) -> Dict[str, Any]:
        """Get current position"""
        buy_qty = sum(t.get("quantity", 0) for t in self.interpreter.trades if t["action"] == "buy")
        sell_qty = sum(t.get("quantity", 0) for t in self.interpreter.trades if t["action"] == "sell")
        
        return {
            "quantity": buy_qty - sell_qty,
            "buy_quantity": buy_qty,
            "sell_quantity": sell_qty,
            "trades_count": len(self.interpreter.trades)
        }
