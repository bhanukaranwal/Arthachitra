from fastapi import HTTPException, status
from typing import Any, Dict, Optional

class ArthachitiraException(Exception):
    """Base exception for Arthachitra application."""
    
    def __init__(self, message: str, code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(ArthachitiraException):
    """Raised when input validation fails."""
    pass

class AuthenticationError(ArthachitiraException):
    """Raised when authentication fails."""
    pass

class AuthorizationError(ArthachitiraException):
    """Raised when authorization fails."""
    pass

class BrokerError(ArthachitiraException):
    """Raised when broker operations fail."""
    pass

class OrderError(ArthachitiraException):
    """Raised when order operations fail."""
    pass

class MarketDataError(ArthachitiraException):
    """Raised when market data operations fail."""
    pass

class DatabaseError(ArthachittraException):
    """Raised when database operations fail."""
    pass

class ExternalServiceError(ArthachittraException):
    """Raised when external service calls fail."""
    pass

# HTTP Exception mappings
def arthachitra_to_http_exception(exc: ArthachittraException) -> HTTPException:
    """Convert Arthachitra exception to HTTP exception."""
    
    status_map = {
        ValidationError: status.HTTP_400_BAD_REQUEST,
        AuthenticationError: status.HTTP_401_UNAUTHORIZED,
        AuthorizationError: status.HTTP_403_FORBIDDEN,
        BrokerError: status.HTTP_502_BAD_GATEWAY,
        OrderError: status.HTTP_400_BAD_REQUEST,
        MarketDataError: status.HTTP_503_SERVICE_UNAVAILABLE,
        DatabaseError: status.HTTP_503_SERVICE_UNAVAILABLE,
        ExternalServiceError: status.HTTP_502_BAD_GATEWAY,
    }
    
    status_code = status_map.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return HTTPException(
        status_code=status_code,
        detail={
            "message": exc.message,
            "code": exc.code,
            "details": exc.details
        }
    )
