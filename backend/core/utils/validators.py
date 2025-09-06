import re
from typing import Any, Dict, List, Optional
from decimal import Decimal
from pydantic import BaseModel, validator

def validate_symbol(symbol: str) -> bool:
    """Validate trading symbol format."""
    if not symbol:
        return False
    
    # Allow alphanumeric characters and hyphens
    pattern = r'^[A-Z0-9\-]{1,20}$'
    return bool(re.match(pattern, symbol.upper()))

def validate_exchange(exchange: str) -> bool:
    """Validate exchange code."""
    valid_exchanges = {'NSE', 'BSE', 'MCX', 'NCDEX', 'NASDAQ', 'NYSE', 'BINANCE'}
    return exchange.upper() in valid_exchanges

def validate_order_quantity(quantity: int) -> bool:
    """Validate order quantity."""
    return isinstance(quantity, int) and quantity > 0 and quantity <= 1000000

def validate_price(price: float) -> bool:
    """Validate price value."""
    if not isinstance(price, (int, float, Decimal)):
        return False
    
    price_decimal = Decimal(str(price))
    return price_decimal > 0 and price_decimal <= Decimal('1000000')

def validate_order_side(side: str) -> bool:
    """Validate order side."""
    return side.upper() in {'BUY', 'SELL'}

def validate_order_type(order_type: str) -> bool:
    """Validate order type."""
    valid_types = {'MARKET', 'LIMIT', 'STOP', 'STOP_LIMIT', 'ICEBERG'}
    return order_type.upper() in valid_types

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate phone number (Indian format)."""
    # Remove any spaces, hyphens, or plus signs
    clean_phone = re.sub(r'[\s\-\+]', '', phone)
    
    # Indian mobile number patterns
    patterns = [
        r'^91[6-9]\d{9}$',  # +91 format
        r'^[6-9]\d{9}$',    # 10-digit format
    ]
    
    return any(re.match(pattern, clean_phone) for pattern in patterns)

class OrderValidationError(ValueError):
    """Custom exception for order validation errors."""
    pass

class OrderValidator:
    """Comprehensive order validation."""
    
    @staticmethod
    def validate_order_data(order_data: Dict[str, Any]) -> Dict[str, str]:
        """Validate complete order data and return errors."""
        errors = {}
        
        # Required fields
        required_fields = ['symbol', 'exchange', 'side', 'quantity', 'order_type']
        for field in required_fields:
            if field not in order_data or order_data[field] is None:
                errors[field] = f"{field} is required"
        
        # Symbol validation
        if 'symbol' in order_data:
            if not validate_symbol(order_data['symbol']):
                errors['symbol'] = "Invalid symbol format"
        
        # Exchange validation
        if 'exchange' in order_data:
            if not validate_exchange(order_data['exchange']):
                errors['exchange'] = "Invalid exchange"
        
        # Quantity validation
        if 'quantity' in order_data:
            try:
                quantity = int(order_data['quantity'])
                if not validate_order_quantity(quantity):
                    errors['quantity'] = "Invalid quantity (must be 1-1000000)"
            except (ValueError, TypeError):
                errors['quantity'] = "Quantity must be a valid integer"
        
        # Side validation
        if 'side' in order_data:
            if not validate_order_side(order_data['side']):
                errors['side'] = "Side must be 'BUY' or 'SELL'"
        
        # Order type validation
        if 'order_type' in order_data:
            if not validate_order_type(order_data['order_type']):
                errors['order_type'] = "Invalid order type"
        
        # Price validation for limit orders
        if order_data.get('order_type') in ['LIMIT', 'STOP_LIMIT']:
            if 'price' not in order_data or order_data['price'] is None:
                errors['price'] = "Price is required for limit orders"
            else:
                try:
                    price = float(order_data['price'])
                    if not validate_price(price):
                        errors['price'] = "Invalid price"
                except (ValueError, TypeError):
                    errors['price'] = "Price must be a valid number"
        
        return errors
    
    @classmethod
    def validate_and_raise(cls, order_data: Dict[str, Any]):
        """Validate order data and raise exception if invalid."""
        errors = cls.validate_order_data(order_data)
        if errors:
            error_msg = "; ".join([f"{k}: {v}" for k, v in errors.items()])
            raise OrderValidationError(f"Order validation failed: {error_msg}")
