import logging
import logging.config
import os
import sys
from typing import Dict, Any
import json
from datetime import datetime

# Logging configuration
LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s:%(lineno)d - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
            "stream": sys.stdout
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": "logs/arthachitra.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "json",
            "filename": "logs/errors.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 10
        }
    },
    "loggers": {
        "arthachitra": {
            "level": "DEBUG",
            "handlers": ["console", "file", "error_file"],
            "propagate": False
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console", "file"]
        },
        "sqlalchemy": {
            "level": "WARNING",
            "handlers": ["file"]
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"]
    }
}

class CustomAdapter(logging.LoggerAdapter):
    """Custom logger adapter to add context information."""
    
    def process(self, msg, kwargs):
        # Add user context if available
        if 'user_id' in self.extra:
            msg = f"[User: {self.extra['user_id']}] {msg}"
        
        # Add request context if available
        if 'request_id' in self.extra:
            msg = f"[Req: {self.extra['request_id']}] {msg}"
            
        return msg, kwargs

def setup_logging():
    """Setup logging configuration."""
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Configure logging
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # Set log level from environment
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.getLogger().setLevel(getattr(logging, log_level))

def get_logger(name: str, **context) -> CustomAdapter:
    """Get a logger with optional context."""
    logger = logging.getLogger(name)
    if context:
        return CustomAdapter(logger, context)
    return CustomAdapter(logger, {})

def log_trade_execution(order_id: str, symbol: str, quantity: int, price: float, user_id: str):
    """Log trade execution with structured data."""
    logger = get_logger("arthachitra.trading")
    logger.info(
        "Trade executed",
        extra={
            "event_type": "trade_execution",
            "order_id": order_id,
            "symbol": symbol,
            "quantity": quantity,
            "price": price,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
    )

def log_api_request(method: str, endpoint: str, user_id: str = None, response_time: float = None):
    """Log API request with timing information."""
    logger = get_logger("arthachitra.api")
    extra_data = {
        "event_type": "api_request",
        "method": method,
        "endpoint": endpoint,
        "timestamp": datetime.now().isoformat()
    }
    
    if user_id:
        extra_data["user_id"] = user_id
    if response_time:
        extra_data["response_time_ms"] = response_time
        
    logger.info(f"{method} {endpoint}", extra=extra_data)

def log_error_with_context(error: Exception, context: Dict[str, Any] = None):
    """Log error with additional context."""
    logger = get_logger("arthachitra.errors")
    
    error_data = {
        "event_type": "error",
        "error_type": type(error).__name__,
        "error_message": str(error),
        "timestamp": datetime.now().isoformat()
    }
    
    if context:
        error_data.update(context)
    
    logger.error("Application error occurred", extra=error_data, exc_info=True)

# Initialize logging when module is imported
setup_logging()
