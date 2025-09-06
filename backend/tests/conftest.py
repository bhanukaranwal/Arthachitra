import pytest
import asyncio
from typing import Generator, AsyncGenerator
from httpx import AsyncClient
from fastapi.testclient import TestClient

from main import app
from core.config import settings
from database.models import Base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Test database URL
TEST_DATABASE_URL = settings.DATABASE_TEST_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def setup_database():
    """Create test database tables."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session(setup_database) -> AsyncGenerator[AsyncSession, None]:
    """Get database session for tests."""
    async with TestSessionLocal() as session:
        yield session

@pytest.fixture
def client() -> Generator:
    """Get test client."""
    with TestClient(app) as c:
        yield c

@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Get async test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }

@pytest.fixture
def sample_order_data():
    """Sample order data for testing."""
    return {
        "symbol": "RELIANCE",
        "exchange": "NSE",
        "side": "BUY",
        "quantity": 100,
        "order_type": "MARKET"
    }

@pytest.fixture
def sample_market_data():
    """Sample market data for testing."""
    return {
        "symbol": "NIFTY",
        "data": [
            {
                "timestamp": "2024-01-01T09:15:00Z",
                "open": 18000.0,
                "high": 18100.0,
                "low": 17900.0,
                "close": 18050.0,
                "volume": 1000000
            },
            {
                "timestamp": "2024-01-01T09:16:00Z",
                "open": 18050.0,
                "high": 18150.0,
                "low": 18000.0,
                "close": 18100.0,
                "volume": 1200000
            }
        ]
    }
