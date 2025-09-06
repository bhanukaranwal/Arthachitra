import asyncio
import asyncpg
import os
from datetime import datetime, timedelta
import random
from decimal import Decimal
import uuid

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/arthachitra")

async def create_sample_user(conn):
    """Create sample user for development."""
    user_id = str(uuid.uuid4())
    
    await conn.execute("""
        INSERT INTO users (id, username, email, password_hash, full_name, is_verified)
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (username) DO NOTHING
    """, user_id, "demo_user", "demo@arthachitra.com", 
    "$2b$12$LQv3c1yqBwUAFO.YSHLe.eXTTtNjyb8kU7x8x8x8x8x8x8x8x8x8x", 
    "Demo User", True)
    
    return user_id

async def create_sample_instruments(conn):
    """Create sample instrument data."""
    instruments = [
        ("NIFTY", "Nifty 50", "NSE", "INDEX", 25, 0.05),
        ("BANKNIFTY", "Bank Nifty", "NSE", "INDEX", 25, 0.05),
        ("RELIANCE", "Reliance Industries Ltd", "NSE", "EQUITY", 1, 0.05),
        ("TCS", "Tata Consultancy Services Ltd", "NSE", "EQUITY", 1, 0.05),
        ("HDFC", "HDFC Bank Ltd", "NSE", "EQUITY", 1, 0.05),
        ("INFY", "Infosys Ltd", "NSE", "EQUITY", 1, 0.05),
        ("ITC", "ITC Ltd", "NSE", "EQUITY", 1, 0.05),
        ("HINDUNILVR", "Hindustan Unilever Ltd", "NSE", "EQUITY", 1, 0.05),
        ("HDFCBANK", "HDFC Bank Ltd", "NSE", "EQUITY", 1, 0.05),
        ("ICICIBANK", "ICICI Bank Ltd", "NSE", "EQUITY", 1, 0.05),
    ]
    
    # Note: This would be stored in a separate instruments table in a real implementation
    print("Sample instruments defined:", [inst for inst in instruments])
    return instruments

async def create_sample_market_data(conn):
    """Create sample historical market data."""
    instruments = [
        ("NIFTY", 18000.0),
        ("BANKNIFTY", 42000.0),
        ("RELIANCE", 2500.0),
        ("TCS", 3200.0),
        ("HDFC", 1600.0),
    ]
    
    # Generate 30 days of historical data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    for symbol, base_price in instruments:
        current_price = base_price
        current_date = start_date
        
        while current_date <= end_date:
            # Generate OHLC data with some randomness
            daily_change = random.uniform(-0.03, 0.03)  # ±3% daily change
            
            open_price = current_price
            high_price = open_price * (1 + random.uniform(0, 0.02))
            low_price = open_price * (1 - random.uniform(0, 0.02))
            close_price = open_price * (1 + daily_change)
            volume = random.randint(1000000, 10000000)
            
            # Ensure high >= max(open, close) and low <= min(open, close)
            high_price = max(high_price, open_price, close_price)
            low_price = min(low_price, open_price, close_price)
            
            await conn.execute("""
                INSERT INTO market_data (time, symbol, exchange, open, high, low, close, volume, timeframe)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (time, symbol) DO NOTHING
            """, current_date, symbol, "NSE", 
            Decimal(str(round(open_price, 2))),
            Decimal(str(round(high_price, 2))),
            Decimal(str(round(low_price, 2))),
            Decimal(str(round(close_price, 2))),
            volume, "1d")
            
            current_price = close_price
            current_date += timedelta(days=1)
    
    print("Sample market data created for", [inst for inst in instruments])

async def create_sample_orders(conn, user_id):
    """Create sample orders for the demo user."""
    orders = [
        ("RELIANCE", "NSE", "BUY", 100, "MARKET", "FILLED"),
        ("TCS", "NSE", "BUY", 50, "LIMIT", "FILLED"),
        ("HDFC", "NSE", "SELL", 200, "MARKET", "FILLED"),
        ("INFY", "NSE", "BUY", 75, "LIMIT", "PENDING"),
    ]
    
    for symbol, exchange, side, quantity, order_type, status in orders:
        order_id = str(uuid.uuid4())
        price = Decimal(str(random.uniform(1000, 3000)))
        
        await conn.execute("""
            INSERT INTO orders (id, user_id, symbol, exchange, order_type, side, quantity, price, status)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """, order_id, user_id, symbol, exchange, order_type, side, quantity, price, status)
    
    print("Sample orders created")

async def create_sample_positions(conn, user_id):
    """Create sample positions for the demo user."""
    positions = [
        ("RELIANCE", "NSE", 100, 2500.50),
        ("TCS", "NSE", 50, 3200.25),
        ("INFY", "NSE", 75, 1400.75),
    ]
    
    for symbol, exchange, quantity, avg_price in positions:
        position_id = str(uuid.uuid4())
        current_price = avg_price * random.uniform(0.95, 1.05)  # ±5% from avg price
        unrealized_pnl = (current_price - avg_price) * quantity
        
        await conn.execute("""
            INSERT INTO positions (id, user_id, symbol, exchange, quantity, average_price, current_price, unrealized_pnl)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """, position_id, user_id, symbol, exchange, quantity, 
        Decimal(str(avg_price)), Decimal(str(current_price)), Decimal(str(unrealized_pnl)))
    
    print("Sample positions created")

async def main():
    """Main function to seed the database."""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("Connected to database")
        
        # Create sample data
        user_id = await create_sample_user(conn)
        await create_sample_instruments(conn)
        await create_sample_market_data(conn)
        
        if user_id:
            await create_sample_orders(conn, user_id)
            await create_sample_positions(conn, user_id)
        
        await conn.close()
        print("Database seeding completed successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")

if __name__ == "__main__":
    asyncio.run(main())
