# Broker Integration Guide

This guide explains how to integrate new brokers with the Arthachitra trading platform.

## Architecture Overview

The broker integration system uses a plugin architecture where each broker implements the `BaseConnector` interface. This ensures consistency across all broker integrations while allowing for broker-specific implementations.

## Creating a New Broker Connector

### 1. Implement BaseConnector

Create a new file in the appropriate directory:
- Indian brokers: `backend/market_connectors/indian/`
- Global brokers: `backend/market_connectors/global/`

from ..base.connector import BaseConnector, Order, Position, Trade

class YourBrokerConnector(BaseConnector):
def init(self, api_key: str, api_secret: str, access_token: str = None):
super().init()
self.api_key = api_key
self.api_secret = api_secret
self.access_token = access_token
self.name = "YourBroker"
# ... other initialization

text
async def connect(self) -> bool:
    # Implement connection logic
    pass

# ... implement other required methods
text

### 2. Required Methods

Every broker connector must implement these methods:

#### Connection Management
- `connect()`: Establish connection to broker API
- `disconnect()`: Clean up connections
- `health_check()`: Verify connection status

#### Market Data
- `get_quote(symbol, exchange)`: Get current market quote
- `get_historical_data()`: Fetch historical OHLC data
- `start_websocket()`: Start real-time data feed
- `subscribe_symbols()`: Subscribe to symbol updates
- `unsubscribe_symbols()`: Unsubscribe from symbols

#### Order Management
- `place_order()`: Place new order
- `modify_order()`: Modify existing order
- `cancel_order()`: Cancel order
- `get_orders()`: Fetch all orders
- `get_positions()`: Get current positions

### 3. Error Handling

Implement proper error handling for all API calls:

async def place_order(self, symbol: str, exchange: str, side: str, quantity: int, **kwargs) -> Optional[str]:
try:
# API call logic
response = await self._make_request("POST", "/orders", order_data)
return response.get("order_id")

text
except BrokerAPIError as e:
    logger.error(f"Order placement failed: {e}")
    return None
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return None
text

### 4. Rate Limiting

Implement rate limiting to comply with broker API limits:

import asyncio
from datetime import datetime, timedelta

class RateLimiter:
def init(self, max_requests: int, time_window: int):
self.max_requests = max_requests
self.time_window = time_window
self.requests = []

text
async def acquire(self):
    now = datetime.now()
    # Remove old requests
    self.requests = [req_time for req_time in self.requests 
                    if now - req_time < timedelta(seconds=self.time_window)]
    
    if len(self.requests) >= self.max_requests:
        sleep_time = self.time_window - (now - self.requests).seconds
        await asyncio.sleep(sleep_time)
    
    self.requests.append(now)
text

### 5. Testing

Create comprehensive tests for your connector:

tests/test_connectors/test_your_broker.py
import pytest
from market_connectors.your_broker.connector import YourBrokerConnector

@pytest.fixture
async def connector():
conn = YourBrokerConnector(
api_key="test_key",
api_secret="test_secret"
)
await conn.connect()
yield conn
await conn.disconnect()

@pytest.mark.asyncio
async def test_get_quote(connector):
quote = await connector.get_quote("RELIANCE", "NSE")
assert quote is not None
assert "price" in quote
assert quote["price"] > 0

text

## Supported Brokers

### Indian Brokers

#### Zerodha Kite
- **Status**: ✅ Production Ready
- **Features**: Full order management, real-time data, positions
- **Rate Limits**: 1000 requests/minute
- **Documentation**: [Kite Connect API](https://kite.trade/docs/connect/v3/)

#### Fyers
- **Status**: ✅ Production Ready
- **Features**: Full order management, real-time data, positions
- **Rate Limits**: 500 requests/minute
- **Documentation**: [Fyers API](https://myapi.fyers.in/docsv2)

#### Angel One
- **Status**: 🚧 In Development
- **Features**: Basic order management
- **Rate Limits**: 200 requests/minute
- **Documentation**: [Angel One API](https://smartapi.angelbroking.com/)

### Global Brokers

#### Interactive Brokers (IBKR)
- **Status**: ✅ Production Ready
- **Features**: Global markets, complex orders, real-time data
- **Rate Limits**: Variable by account type
- **Documentation**: [TWS API](https://interactivebrokers.github.io/tws-api/)

#### Alpaca
- **Status**: ✅ Production Ready
- **Features**: US equities, commission-free trading
- **Rate Limits**: 200 requests/minute
- **Documentation**: [Alpaca API](https://alpaca.markets/docs/)

#### Binance
- **Status**: ✅ Production Ready
- **Features**: Cryptocurrency trading, spot and futures
- **Rate Limits**: 1200 requests/minute
- **Documentation**: [Binance API](https://binance-docs.github.io/apidocs/)

## Configuration

### 1. Environment Variables

Add broker configuration to your environment:

.env file
YOUR_BROKER_API_KEY=your_api_key
YOUR_BROKER_API_SECRET=your_api_secret
YOUR_BROKER_ACCESS_TOKEN=your_access_token
YOUR_BROKER_SANDBOX=false

text

### 2. Register Connector

Register your connector in the trading engine:

backend/main.py
from market_connectors.your_broker.connector import YourBrokerConnector

@app.on_event("startup")
async def startup_event():
# Initialize broker connector
broker = YourBrokerConnector(
api_key=settings.YOUR_BROKER_API_KEY,
api_secret=settings.YOUR_BROKER_API_SECRET,
access_token=settings.YOUR_BROKER_ACCESS_TOKEN
)

text
if await broker.connect():
    trading_engine.register_connector("your_broker", broker)
    logger.info("YourBroker connector registered successfully")
text

### 3. Frontend Integration

Add broker to frontend broker selection:

// frontend/src/components/BrokerSelector.tsx
const SUPPORTED_BROKERS = [
{ id: 'zerodha', name: 'Zerodha', flag: '🇮🇳' },
{ id: 'fyers', name: 'Fyers', flag: '🇮🇳' },
{ id: 'your_broker', name: 'Your Broker', flag: '🌐' },
// ... other brokers
];

text

## Best Practices

### 1. Security
- Never store API credentials in plain text
- Use environment variables or secure vaults
- Implement proper token refresh mechanisms
- Validate all API responses

### 2. Performance
- Implement connection pooling
- Use async/await for all I/O operations
- Cache frequently accessed data
- Implement exponential backoff for retries

### 3. Reliability
- Handle network failures gracefully
- Implement circuit breakers for API calls
- Log all important events
- Monitor API usage and limits

### 4. Testing
- Write unit tests for all methods
- Test with live sandbox environments
- Implement integration tests
- Test error scenarios and edge cases

## Troubleshooting

### Common Issues

#### Authentication Failures
Debug authentication
logger.debug(f"API Key: {self.api_key[:10]}...")
logger.debug(f"Access Token: {self.access_token[:10]}...")

Check token expiry
if hasattr(self, 'token_expiry'):
if datetime.now() > self.token_expiry:
await self.refresh_token()

text

#### Rate Limiting
Implement exponential backoff
async def _make_request_with_retry(self, method, url, data=None, max_retries=3):
for attempt in range(max_retries):
try:
return await self._make_request(method, url, data)
except RateLimitError:
wait_time = 2 ** attempt
logger.warning(f"Rate limited, waiting {wait_time}s")
await asyncio.sleep(wait_time)

text
raise Exception("Max retries exceeded")
text

#### WebSocket Connection Issues
Implement reconnection logic
async def _websocket_reconnect(self):
max_retries = 5
retry_delay = 5

text
for attempt in range(max_retries):
    try:
        await self.start_websocket(self.on_tick_callback)
        logger.info("WebSocket reconnected successfully")
        return
    except Exception as e:
        logger.warning(f"WebSocket reconnection attempt {attempt + 1} failed: {e}")
        await asyncio.sleep(retry_delay * (attempt + 1))

logger.error("WebSocket reconnection failed after max retries")
text

## Contributing

To contribute a new broker integration:

1. Fork the repository
2. Create your broker connector following this guide
3. Write comprehensive tests
4. Update documentation
5. Submit a pull request

For questions or support, join our [Discord community](https://discord.gg/arthachitra) or create an issue on GitHub.
