import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel
import numpy as np
import re
from typing import Dict, List, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor

class NewsSentimentAnalyzer:
    """
    News sentiment analyzer using pre-trained transformer models.
    Analyzes financial news and social media content for market sentiment.
    """
    
    def __init__(self, model_name: str = "nlptown/bert-base-multilingual-uncased-sentiment"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.financial_keywords = self._load_financial_keywords()
        
    def _load_financial_keywords(self) -> Dict[str, List[str]]:
        """Load financial keywords for context weighting."""
        return {
            "bullish": [
                "growth", "profit", "gain", "rise", "increase", "positive", "strong",
                "bull", "rally", "surge", "boom", "expansion", "dividend", "earnings beat"
            ],
            "bearish": [
                "loss", "decline", "fall", "decrease", "negative", "weak", "bear",
                "crash", "drop", "recession", "downturn", "bankruptcy", "layoffs", "miss"
            ],
            "neutral": [
                "stable", "flat", "unchanged", "steady", "maintain", "hold", "sideways"
            ]
        }
    
    async def initialize(self):
        """Initialize the sentiment analyzer."""
        try:
            loop = asyncio.get_event_loop()
            
            # Load tokenizer and model in executor to avoid blocking
            self.tokenizer, self.model = await loop.run_in_executor(
                self.executor, self._load_model
            )
            
            print("✅ News sentiment analyzer initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize sentiment analyzer: {e}")
            return False
    
    def _load_model(self):
        """Load the pre-trained model and tokenizer."""
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            model.to(self.device)
            model.eval()
            
            return tokenizer, model
            
        except Exception as e:
            print(f"Error loading model: {e}")
            # Fallback to rule-based sentiment
            return None, None
    
    def analyze_text(self, text: str, symbol: str = None) -> Dict[str, Any]:
        """
        Analyze sentiment of a single text.
        
        Args:
            text: Text to analyze
            symbol: Stock symbol for context (optional)
            
        Returns:
            Dict with sentiment_score, sentiment_label, and confidence
        """
        try:
            # Clean and preprocess text
            cleaned_text = self._preprocess_text(text)
            
            if self.model and self.tokenizer:
                # Use transformer model
                return self._analyze_with_model(cleaned_text, symbol)
            else:
                # Use rule-based approach
                return self._analyze_rule_based(cleaned_text, symbol)
                
        except Exception as e:
            print(f"Error analyzing text: {e}")
            return {
                "sentiment_score": 0.0,
                "sentiment_label": "neutral",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for analysis."""
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?;:]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Truncate if too long
        if len(text) > 512:
            text = text[:512]
            
        return text.strip()
    
    def _analyze_with_model(self, text: str, symbol: str = None) -> Dict[str, Any]:
        """Analyze sentiment using transformer model."""
        try:
            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                
            # Extract sentiment
            predictions = predictions.cpu().numpy()[0]
            
            # Map to sentiment (assuming 5-class model: very negative to very positive)
            if len(predictions) == 5:
                sentiment_score = (np.argmax(predictions) - 2) / 2  # Scale to [-1, 1]
                confidence = float(np.max(predictions))
            else:
                # Binary classification
                sentiment_score = float(predictions[1] - predictions[0])  # positive - negative
                confidence = float(np.max(predictions))
            
            # Apply financial context weighting
            if symbol:
                sentiment_score = self._apply_financial_context(text, sentiment_score, symbol)
            
            # Determine label
            if sentiment_score > 0.1:
                label = "positive"
            elif sentiment_score < -0.1:
                label = "negative"
            else:
                label = "neutral"
                
            return {
                "sentiment_score": float(sentiment_score),
                "sentiment_label": label,
                "confidence": confidence,
                "method": "transformer"
            }
            
        except Exception as e:
            print(f"Error in model analysis: {e}")
            return self._analyze_rule_based(text, symbol)
    
    def _analyze_rule_based(self, text: str, symbol: str = None) -> Dict[str, Any]:
        """Fallback rule-based sentiment analysis."""
        try:
            text_lower = text.lower()
            
            # Count keyword occurrences
            bullish_count = sum(1 for word in self.financial_keywords["bullish"] if word in text_lower)
            bearish_count = sum(1 for word in self.financial_keywords["bearish"] if word in text_lower)
            neutral_count = sum(1 for word in self.financial_keywords["neutral"] if word in text_lower)
            
            # Calculate sentiment score
            total_keywords = bullish_count + bearish_count + neutral_count
            if total_keywords == 0:
                sentiment_score = 0.0
                confidence = 0.1
            else:
                sentiment_score = (bullish_count - bearish_count) / total_keywords
                confidence = min(total_keywords / 10.0, 1.0)  # More keywords = higher confidence
            
            # Apply financial context
            if symbol:
                sentiment_score = self._apply_financial_context(text, sentiment_score, symbol)
            
            # Determine label
            if sentiment_score > 0.1:
                label = "positive"
            elif sentiment_score < -0.1:
                label = "negative"
            else:
                label = "neutral"
                
            return {
                "sentiment_score": float(sentiment_score),
                "sentiment_label": label,
                "confidence": float(confidence),
                "method": "rule_based",
                "keyword_counts": {
                    "bullish": bullish_count,
                    "bearish": bearish_count,
                    "neutral": neutral_count
                }
            }
            
        except Exception as e:
            return {
                "sentiment_score": 0.0,
                "sentiment_label": "neutral",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _apply_financial_context(self, text: str, sentiment_score: float, symbol: str) -> float:
        """Apply financial context to adjust sentiment score."""
        try:
            text_lower = text.lower()
            symbol_lower = symbol.lower()
            
            # Boost sentiment if symbol is mentioned
            if symbol_lower in text_lower:
                sentiment_score *= 1.2
            
            # Check for financial report indicators
            if any(term in text_lower for term in ["earnings", "quarterly", "annual", "results"]):
                sentiment_score *= 1.1
            
            # Check for analyst ratings
            if any(term in text_lower for term in ["upgrade", "buy rating", "outperform"]):
                sentiment_score = max(sentiment_score, 0.3)
            elif any(term in text_lower for term in ["downgrade", "sell rating", "underperform"]):
                sentiment_score = min(sentiment_score, -0.3)
            
            # Clamp to [-1, 1]
            sentiment_score = max(-1.0, min(1.0, sentiment_score))
            
            return sentiment_score
            
        except Exception:
            return sentiment_score
    
    async def analyze_batch(self, texts: List[str], symbol: str = None) -> List[Dict[str, Any]]:
        """Analyze multiple texts in batch."""
        tasks = []
        for text in texts:
            task = asyncio.get_event_loop().run_in_executor(
                self.executor, self.analyze_text, text, symbol
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append({
                    "sentiment_score": 0.0,
                    "sentiment_label": "neutral",
                    "confidence": 0.0,
                    "error": str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    def aggregate_sentiment(self, sentiments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate multiple sentiment analyses."""
        if not sentiments:
            return {
                "aggregate_score": 0.0,
                "aggregate_label": "neutral",
                "confidence": 0.0,
                "count": 0
            }
        
        # Calculate weighted average
        total_weight = 0
        weighted_sum = 0
        
        for sentiment in sentiments:
            confidence = sentiment.get("confidence", 0.5)
            score = sentiment.get("sentiment_score", 0.0)
            
            weighted_sum += score * confidence
            total_weight += confidence
        
        if total_weight == 0:
            aggregate_score = 0.0
            aggregate_confidence = 0.0
        else:
            aggregate_score = weighted_sum / total_weight
            aggregate_confidence = total_weight / len(sentiments)
        
        # Determine aggregate label
        if aggregate_score > 0.1:
            label = "positive"
        elif aggregate_score < -0.1:
            label = "negative"
        else:
            label = "neutral"
        
        # Calculate distribution
        positive_count = sum(1 for s in sentiments if s.get("sentiment_label") == "positive")
        negative_count = sum(1 for s in sentiments if s.get("sentiment_label") == "negative")
        neutral_count = len(sentiments) - positive_count - negative_count
        
        return {
            "aggregate_score": float(aggregate_score),
            "aggregate_label": label,
            "confidence": float(aggregate_confidence),
            "count": len(sentiments),
            "distribution": {
                "positive": positive_count,
                "negative": negative_count,
                "neutral": neutral_count
            }
        }

# Usage example
if __name__ == "__main__":
    async def test_sentiment():
        analyzer = NewsSentimentAnalyzer()
        await analyzer.initialize()
        
        # Test texts
        texts = [
            "Reliance Industries reports strong quarterly earnings with 15% growth",
            "Market crash expected as inflation rises to decade high",
            "TCS maintains steady performance in competitive market"
        ]
        
        for text in texts:
            result = analyzer.analyze_text(text, "RELIANCE")
            print(f"Text: {text[:50]}...")
            print(f"Sentiment: {result['sentiment_label']} ({result['sentiment_score']:.3f})")
            print(f"Confidence: {result['confidence']:.3f}")
            print()
    
    # Run test
    asyncio.run(test_sentiment())
