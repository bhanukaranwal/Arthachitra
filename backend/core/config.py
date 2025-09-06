import os
from typing import List, Optional, Dict, Any
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Arthachitra"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/arthachitra"
    DATABASE_TEST_URL: str = "postgresql://postgres:password@localhost:5432/arthachitra_test"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: Optional[str] = None
    
    # Authentication
    JWT_SECRET_KEY: str = "your-jwt-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Rate Limiting
    RATE_LIMIT_DEFAULT: str = "1000/minute"
    RATE_LIMIT_AUTHENTICATED: str = "5000/minute"
    RATE_LIMIT_PREMIUM: str = "10000/minute"
    
    # External Services
    SENTRY_DSN: Optional[str] = None
    
    # Email Configuration
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Broker API Keys
    ZERODHA_API_KEY: Optional[str] = None
    ZERODHA_API_SECRET: Optional[str] = None
    FYERS_APP_ID: Optional[str] = None
    FYERS_SECRET_KEY: Optional[str] = None
    ANGEL_ONE_API_KEY: Optional[str] = None
    ANGEL_ONE_SECRET: Optional[str] = None
    
    # Global Brokers
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_API_SECRET: Optional[str] = None
    IBKR_USERNAME: Optional[str] = None
    IBKR_PASSWORD: Optional[str] = None
    ALPACA_API_KEY: Optional[str] = None
    ALPACA_SECRET_KEY: Optional[str] = None
    
    # ML Configuration
    ML_SERVICE_URL: str = "http://localhost:8001"
    HUGGINGFACE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # Monitoring
    PROMETHEUS_PORT: int = 9090
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Trading Configuration
    TRADING_ENABLED: bool = True
    PAPER_TRADING_ENABLED: bool = True
    MAX_ORDER_VALUE: float = 10000000.0  # 1 crore
    MAX_POSITION_SIZE: float = 50000000.0  # 5 crore
    
    # Data Sources
    DATA_PROVIDER: str = "yahoo"  # yahoo, alpha_vantage, quandl
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

# Global settings instance
settings = get_settings()
