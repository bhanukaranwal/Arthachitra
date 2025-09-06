import asyncio
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool, NullPool
from contextlib import asynccontextmanager
from core.config import settings

logger = logging.getLogger(__name__)

class DatabasePool:
    """Enhanced database connection pool manager."""
    
    def __init__(self):
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[sessionmaker] = None
        self._is_initialized = False
        
    async def initialize(self):
        """Initialize the database pool."""
        if self._is_initialized:
            return
            
        try:
            # Create async engine with connection pooling
            self.engine = create_async_engine(
                settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
                echo=settings.DEBUG,
                poolclass=QueuePool if settings.ENVIRONMENT != "test" else NullPool,
                pool_size=settings.DATABASE_POOL_SIZE if hasattr(settings, 'DATABASE_POOL_SIZE') else 20,
                max_overflow=settings.DATABASE_MAX_OVERFLOW if hasattr(settings, 'DATABASE_MAX_OVERFLOW') else 30,
                pool_timeout=30,
                pool_recycle=3600,  # Recycle connections every hour
                pool_pre_ping=True,  # Validate connections before use
            )
            
            # Create session factory
            self.session_factory = sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=True,
                autocommit=False
            )
            
            # Test connection
            await self._test_connection()
            
            self._is_initialized = True
            logger.info("✅ Database pool initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize database pool: {e}")
            raise
    
    async def _test_connection(self):
        """Test database connectivity."""
        if not self.engine:
            raise RuntimeError("Database engine not initialized")
            
        async with self.engine.begin() as conn:
            result = await conn.execute("SELECT 1")
            assert result.scalar() == 1
            logger.info("Database connectivity test passed")
    
    @asynccontextmanager
    async def get_session(self):
        """Get database session with automatic cleanup."""
        if not self._is_initialized:
            await self.initialize()
            
        if not self.session_factory:
            raise RuntimeError("Session factory not initialized")
            
        session = self.session_factory()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()
    
    async def execute_query(self, query: str, params: dict = None):
        """Execute raw SQL query."""
        async with self.get_session() as session:
            result = await session.execute(query, params or {})
            return result
    
    async def health_check(self) -> dict:
        """Perform database health check."""
        try:
            start_time = asyncio.get_event_loop().time()
            
            async with self.get_session() as session:
                await session.execute("SELECT 1")
                
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "pool_size": self.engine.pool.size() if self.engine else 0,
                "checked_out_connections": self.engine.pool.checkedout() if self.engine else 0
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def close(self):
        """Close database pool."""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database pool closed")

# Global database pool instance
db_pool = DatabasePool()

# Dependency for FastAPI
async def get_db_session():
    """FastAPI dependency to get database session."""
    async with db_pool.get_session() as session:
        yield session
