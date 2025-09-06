import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.ensemble import RandomForestClassifier
from scipy.signal import find_peaks
import talib
from typing import Tuple, List, Optional

class TrianglePatternDetector(BaseEstimator, ClassifierMixin):
    """
    Machine Learning model for detecting triangle patterns in financial time series.
    Detects ascending, descending, and symmetrical triangles.
    """
    
    def __init__(self, lookback_period: int = 50, min_touches: int = 4, 
                 tolerance: float = 0.02, n_estimators: int = 100):
        self.lookback_period = lookback_period
        self.min_touches = min_touches
        self.tolerance = tolerance
        self.n_estimators = n_estimators
        self.model = RandomForestClassifier(n_estimators=n_estimators, random_state=42)
        self.is_fitted = False
        
    def extract_features(self, ohlc_data: pd.DataFrame) -> np.ndarray:
        """Extract features from OHLC data for pattern recognition."""
        features = []
        
        high = ohlc_data['high'].values
        low = ohlc_data['low'].values
        close = ohlc_data['close'].values
        volume = ohlc_data['volume'].values
        
        # Price features
        features.extend([
            np.mean(high[-20:]) / np.mean(high[-50:]) - 1,  # Recent high momentum
            np.mean(low[-20:]) / np.mean(low[-50:]) - 1,     # Recent low momentum
            (high[-1] - low[-1]) / close[-1],                 # Current range
            np.std(close[-20:]) / np.mean(close[-20:]),       # Recent volatility
        ])
        
        # Trend features
        sma_20 = talib.SMA(close, timeperiod=20)
        sma_50 = talib.SMA(close, timeperiod=50)
        features.extend([
            (sma_20[-1] - sma_50[-1]) / close[-1],           # Trend strength
            (close[-1] - sma_20[-1]) / close[-1],            # Position relative to MA
        ])
        
        # Support/Resistance features
        highs_peaks, _ = find_peaks(high, distance=5)
        lows_peaks, _ = find_peaks(-low, distance=5)
        
        if len(highs_peaks) >= 2:
            recent_highs = high[highs_peaks[-2:]]
            features.append((recent_highs[-1] - recent_highs[0]) / close[-1])  # High trend
        else:
            features.append(0)
            
        if len(lows_peaks) >= 2:
            recent_lows = low[lows_peaks[-2:]]
            features.append((recent_lows[-1] - recent_lows[0]) / close[-1])   # Low trend
        else:
            features.append(0)
        
        # Technical indicators
        rsi = talib.RSI(close, timeperiod=14)
        macd, macd_signal, _ = talib.MACD(close)
        bb_upper, bb_middle, bb_lower = talib.BBANDS(close, timeperiod=20)
        
        features.extend([
            rsi[-1] / 100,                                    # RSI normalized
            (macd[-1] - macd_signal[-1]) / close[-1],        # MACD divergence
            (close[-1] - bb_middle[-1]) / (bb_upper[-1] - bb_lower[-1]),  # BB position
        ])
        
        # Volume features
        volume_sma = talib.SMA(volume.astype(float), timeperiod=20)
        features.extend([
            volume[-1] / volume_sma[-1] if volume_sma[-1] > 0 else 1,  # Volume ratio
            np.corrcoef(close[-20:], volume[-20:])[0, 1] if len(close) >= 20 else 0,  # Price-volume correlation
        ])
        
        return np.array(features)
    
    def detect_triangle_manual(self, ohlc_data: pd.DataFrame) -> Tuple[str, float, dict]:
        """Manual triangle detection using geometric analysis."""
        high = ohlc_data['high'].values
        low = ohlc_data['low'].values
        
        # Find significant peaks and troughs
        highs_peaks, _ = find_peaks(high, distance=5, prominence=np.std(high) * 0.5)
        lows_peaks, _ = find_peaks(-low, distance=5, prominence=np.std(low) * 0.5)
        
        if len(highs_peaks) < 2 or len(lows_peaks) < 2:
            return "none", 0.0, {}
        
        # Get recent peaks
        recent_highs = highs_peaks[-4:] if len(highs_peaks) >= 4 else highs_peaks
        recent_lows = lows_peaks[-4:] if len(lows_peaks) >= 4 else lows_peaks
        
        # Calculate trend lines
        if len(recent_highs) >= 2:
            high_slope = np.polyfit(recent_highs, high[recent_highs], 1)[0]
        else:
            high_slope = 0
            
        if len(recent_lows) >= 2:
            low_slope = np.polyfit(recent_lows, low[recent_lows], 1)[0]
        else:
            low_slope = 0
        
        # Classify triangle type
        high_trend = "flat" if abs(high_slope) < self.tolerance else ("down" if high_slope < 0 else "up")
        low_trend = "flat" if abs(low_slope) < self.tolerance else ("up" if low_slope > 0 else "down")
        
        confidence = min(len(recent_highs), len(recent_lows)) / 4.0
        
        if high_trend == "down" and low_trend == "up":
            return "symmetrical", confidence, {"high_slope": high_slope, "low_slope": low_slope}
        elif high_trend == "flat" and low_trend == "up":
            return "ascending", confidence, {"high_slope": high_slope, "low_slope": low_slope}
        elif high_trend == "down" and low_trend == "flat":
            return "descending", confidence, {"high_slope": high_slope, "low_slope": low_slope}
        else:
            return "none", 0.0, {}
    
    def fit(self, X: List[pd.DataFrame], y: List[str]):
        """Train the model on labeled triangle patterns."""
        features_list = []
        labels = []
        
        label_mapping = {"none": 0, "ascending": 1, "descending": 2, "symmetrical": 3}
        
        for ohlc_data, label in zip(X, y):
            if len(ohlc_data) >= self.lookback_period:
                features = self.extract_features(ohlc_data)
                features_list.append(features)
                labels.append(label_mapping.get(label, 0))
        
        if features_list:
            X_train = np.array(features_list)
            y_train = np.array(labels)
            self.model.fit(X_train, y_train)
            self.is_fitted = True
        
        return self
    
    def predict_pattern(self, ohlc_data: pd.DataFrame) -> Tuple[str, float, dict]:
        """Predict triangle pattern using both ML and manual methods."""
        if len(ohlc_data) < self.lookback_period:
            return "none", 0.0, {}
        
        # Manual detection
        manual_pattern, manual_confidence, manual_details = self.detect_triangle_manual(ohlc_data)
        
        # ML prediction if model is trained
        if self.is_fitted:
            features = self.extract_features(ohlc_data).reshape(1, -1)
            ml_prediction = self.model.predict(features)[0]
            ml_confidence = np.max(self.model.predict_proba(features))
            
            label_reverse_mapping = {0: "none", 1: "ascending", 2: "descending", 3: "symmetrical"}
            ml_pattern = label_reverse_mapping[ml_prediction]
            
            # Combine predictions
            if manual_pattern == ml_pattern and manual_pattern != "none":
                combined_confidence = (manual_confidence + ml_confidence) / 2
                return manual_pattern, combined_confidence, manual_details
            elif ml_confidence > 0.8:
                return ml_pattern, ml_confidence, {"source": "ml_prediction"}
            else:
                return manual_pattern, manual_confidence, manual_details
        
        return manual_pattern, manual_confidence, manual_details
    
    def get_breakout_targets(self, ohlc_data: pd.DataFrame, pattern_type: str) -> dict:
        """Calculate potential breakout targets for detected patterns."""
        if pattern_type == "none":
            return {}
        
        high = ohlc_data['high'].values
        low = ohlc_data['low'].values
        current_price = ohlc_data['close'].iloc[-1]
        
        # Calculate pattern height
        pattern_high = np.max(high[-self.lookback_period:])
        pattern_low = np.min(low[-self.lookback_period:])
        pattern_height = pattern_high - pattern_low
        
        if pattern_type in ["ascending", "symmetrical"]:
            # Bullish breakout target
            upside_target = pattern_high + pattern_height
            return {
                "direction": "bullish",
                "entry": pattern_high,
                "target": upside_target,
                "stop_loss": pattern_low,
                "risk_reward": (upside_target - pattern_high) / (pattern_high - pattern_low)
            }
        elif pattern_type == "descending":
            # Bearish breakout target
            downside_target = pattern_low - pattern_height
            return {
                "direction": "bearish",
                "entry": pattern_low,
                "target": downside_target,
                "stop_loss": pattern_high,
                "risk_reward": (pattern_low - downside_target) / (pattern_high - pattern_low)
            }
        
        return {}

# Usage example and testing
if __name__ == "__main__":
    # Generate sample data for testing
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    
    # Create a sample ascending triangle pattern
    base_price = 100
    trend = np.linspace(0, 5, 100)  # Upward trend
    noise = np.random.normal(0, 1, 100)
    
    # Ascending triangle: rising lows, flat highs
    resistance_level = 105
    support_trend = base_price + trend + noise
    
    high = np.minimum(support_trend + np.random.uniform(1, 3, 100), resistance_level + np.random.uniform(-0.5, 0.5, 100))
    low = support_trend + np.random.uniform(-2, 0, 100)
    close = (high + low) / 2 + np.random.uniform(-0.5, 0.5, 100)
    open_price = close + np.random.uniform(-1, 1, 100)
    volume = np.random.randint(1000, 10000, 100)
    
    sample_data = pd.DataFrame({
        'date': dates,
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    })
    
    # Test the detector
    detector = TrianglePatternDetector()
    pattern, confidence, details = detector.predict_pattern(sample_data)
    targets = detector.get_breakout_targets(sample_data, pattern)
    
    print(f"Detected Pattern: {pattern}")
    print(f"Confidence: {confidence:.2f}")
    print(f"Details: {details}")
    print(f"Breakout Targets: {targets}")
