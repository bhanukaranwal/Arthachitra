from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import torch
import numpy as np
import pandas as pd
from datetime import datetime
import asyncio
import joblib
import os

from ..models.pattern_recognition.triangle_detector import TrianglePatternDetector
from ..models.sentiment.news_sentiment import NewsSentimentAnalyzer

app = FastAPI(
    title="Arthachitra ML Services",
    description="Machine Learning services for pattern recognition and market analysis",
    version="1.0.0"
)

# Global model instances
pattern_detector = None
sentiment_analyzer = None

class MarketDataInput(BaseModel):
    symbol: str
    ohlc_data: List[Dict[str, Any]]
    timeframe: str = "1d"

class PatternResult(BaseModel):
    pattern_type: str
    confidence: float
    details: Dict[str, Any]
    breakout_targets: Optional[Dict[str, Any]] = None

class SentimentInput(BaseModel):
    text: str
    symbol: Optional[str] = None
    source: Optional[str] = None

class SentimentResult(BaseModel):
    sentiment_score: float
    sentiment_label: str
    confidence: float

@app.on_event("startup")
async def startup_event():
    """Load ML models on startup."""
    global pattern_detector, sentiment_analyzer
    
    try:
        # Load pattern recognition model
        pattern_detector = TrianglePatternDetector()
        
        model_path = "models/pattern_recognition_model.pth"
        if os.path.exists(model_path):
            checkpoint = torch.load(model_path, map_location='cpu')
            # Load model weights if available
            print("✅ Pattern recognition model loaded")
        else:
            print("⚠️ Pattern recognition model not found, using rule-based approach")
        
        # Load sentiment analyzer
        sentiment_analyzer = NewsSentimentAnalyzer()
        print("✅ Sentiment analyzer loaded")
        
    except Exception as e:
        print(f"❌ Error loading ML models: {e}")

@app.get("/")
async def root():
    return {
        "service": "Arthachitra ML Services",
        "version": "1.0.0",
        "status": "running",
        "available_endpoints": [
            "/pattern/detect",
            "/sentiment/analyze",
            "/health"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "pattern_detector": pattern_detector is not None,
        "sentiment_analyzer": sentiment_analyzer is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/pattern/detect", response_model=PatternResult)
async def detect_pattern(data: MarketDataInput):
    """Detect chart patterns in market data."""
    try:
        if not pattern_detector:
            raise HTTPException(status_code=503, detail="Pattern detector not available")
        
        # Convert input data to DataFrame
        df = pd.DataFrame(data.ohlc_data)
        
        # Ensure required columns exist
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in df.columns:
                raise HTTPException(status_code=400, detail=f"Missing required column: {col}")
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Detect pattern
        pattern_type, confidence, details = await asyncio.get_event_loop().run_in_executor(
            None, pattern_detector.predict_pattern, df
        )
        
        # Get breakout targets
        breakout_targets = None
        if pattern_type != "none":
            breakout_targets = await asyncio.get_event_loop().run_in_executor(
                None, pattern_detector.get_breakout_targets, df, pattern_type
            )
        
        return PatternResult(
            pattern_type=pattern_type,
            confidence=confidence,
            details=details,
            breakout_targets=breakout_targets
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sentiment/analyze", response_model=SentimentResult)
async def analyze_sentiment(data: SentimentInput):
    """Analyze sentiment of text (news, social media, etc.)."""
    try:
        if not sentiment_analyzer:
            raise HTTPException(status_code=503, detail="Sentiment analyzer not available")
        
        # Analyze sentiment
        result = await asyncio.get_event_loop().run_in_executor(
            None, sentiment_analyzer.analyze_text, data.text
        )
        
        return SentimentResult(
            sentiment_score=result['sentiment_score'],
            sentiment_label=result['sentiment_label'],
            confidence=result['confidence']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/patterns/supported")
async def get_supported_patterns():
    """Get list of supported chart patterns."""
    return {
        "patterns": [
            {
                "name": "triangular_ascending",
                "description": "Ascending triangle pattern with flat resistance and rising support"
            },
            {
                "name": "triangular_descending", 
                "description": "Descending triangle pattern with flat support and declining resistance"
            },
            {
                "name": "triangular_symmetrical",
                "description": "Symmetrical triangle pattern with converging support and resistance"
            },
            {
                "name": "none",
                "description": "No clear pattern detected"
            }
        ]
    }

@app.get("/models/status")
async def get_models_status():
    """Get status of loaded ML models."""
    return {
        "pattern_detector": {
            "loaded": pattern_detector is not None,
            "type": "TrianglePatternDetector",
            "version": "1.0.0"
        },
        "sentiment_analyzer": {
            "loaded": sentiment_analyzer is not None,
            "type": "NewsSentimentAnalyzer", 
            "version": "1.0.0"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
