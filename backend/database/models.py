from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Numeric, ForeignKey, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    subscription_tier = Column(String(20), default='free')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    broker_accounts = relationship("BrokerAccount", back_populates="user")
    orders = relationship("Order", back_populates="user")
    positions = relationship("Position", back_populates="user")

class BrokerAccount(Base):
    __tablename__ = "broker_accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    broker_name = Column(String(50), nullable=False)
    account_id = Column(String(100), nullable=False)
    api_key_encrypted = Column(Text)
    api_secret_encrypted = Column(Text)
    access_token_encrypted = Column(Text)
    is_active = Column(Boolean, default=True)
    is_paper_trading = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="broker_accounts")

class MarketData(Base):
    __tablename__ = "market_data"
    
    time = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    symbol = Column(String(50), nullable=False, primary_key=True)
    exchange = Column(String(20), nullable=False)
    open = Column(Numeric(15, 4), nullable=False)
    high = Column(Numeric(15, 4), nullable=False)
    low = Column(Numeric(15, 4), nullable=False)
    close = Column(Numeric(15, 4), nullable=False)
    volume = Column(Integer, nullable=False)
    vwap = Column(Numeric(15, 4))
    timeframe = Column(String(10), nullable=False)

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    broker_account_id = Column(UUID(as_uuid=True), ForeignKey("broker_accounts.id"))
    symbol = Column(String(50), nullable=False)
    exchange = Column(String(20), nullable=False)
    order_type = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(15, 4))
    filled_quantity = Column(Integer, default=0)
    average_price = Column(Numeric(15, 4))
    status = Column(String(20), nullable=False)
    order_id_broker = Column(String(100))
    strategy_name = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    executed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="orders")

class Position(Base):
    __tablename__ = "positions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    broker_account_id = Column(UUID(as_uuid=True), ForeignKey("broker_accounts.id"))
    symbol = Column(String(50), nullable=False)
    exchange = Column(String(20), nullable=False)
    quantity = Column(Integer, nullable=False)
    average_price = Column(Numeric(15, 4), nullable=False)
    current_price = Column(Numeric(15, 4))
    unrealized_pnl = Column(Numeric(15, 4))
    realized_pnl = Column(Numeric(15, 4), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="positions")
