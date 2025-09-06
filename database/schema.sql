-- Arthachitra Database Schema
-- PostgreSQL with TimescaleDB extension

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "timescaledb";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    subscription_tier VARCHAR(20) DEFAULT 'free',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

-- Broker accounts table
CREATE TABLE broker_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    broker_name VARCHAR(50) NOT NULL,
    account_id VARCHAR(100) NOT NULL,
    api_key_encrypted TEXT,
    api_secret_encrypted TEXT,
    access_token_encrypted TEXT,
    is_active BOOLEAN DEFAULT true,
    is_paper_trading BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Market data table (hypertable for time-series data)
CREATE TABLE market_data (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    open DECIMAL(15,4) NOT NULL,
    high DECIMAL(15,4) NOT NULL,
    low DECIMAL(15,4) NOT NULL,
    close DECIMAL(15,4) NOT NULL,
    volume BIGINT NOT NULL,
    vwap DECIMAL(15,4),
    timeframe VARCHAR(10) NOT NULL,
    PRIMARY KEY (time, symbol, timeframe)
);

-- Convert to hypertable for better time-series performance
SELECT create_hypertable('market_data', 'time');

-- Orders table
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    broker_account_id UUID REFERENCES broker_accounts(id),
    symbol VARCHAR(50) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    order_type VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL,
    quantity INTEGER NOT NULL,
    price DECIMAL(15,4),
    filled_quantity INTEGER DEFAULT 0,
    average_price DECIMAL(15,4),
    status VARCHAR(20) NOT NULL,
    order_id_broker VARCHAR(100),
    strategy_name VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    submitted_at TIMESTAMPTZ,
    executed_at TIMESTAMPTZ
);

-- Positions table
CREATE TABLE positions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    broker_account_id UUID REFERENCES broker_accounts(id),
    symbol VARCHAR(50) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    quantity INTEGER NOT NULL,
    average_price DECIMAL(15,4) NOT NULL,
    current_price DECIMAL(15,4),
    unrealized_pnl DECIMAL(15,4),
    realized_pnl DECIMAL(15,4) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, broker_account_id, symbol, exchange)
);

-- Trades table
CREATE TABLE trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    order_id UUID REFERENCES orders(id),
    symbol VARCHAR(50) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL,
    quantity INTEGER NOT NULL,
    price DECIMAL(15,4) NOT NULL,
    commission DECIMAL(10,4) DEFAULT 0,
    executed_at TIMESTAMPTZ DEFAULT NOW(),
    trade_id_broker VARCHAR(100)
);

-- Portfolio snapshots table for historical tracking
CREATE TABLE portfolio_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    snapshot_time TIMESTAMPTZ NOT NULL,
    total_value DECIMAL(15,4) NOT NULL,
    cash_balance DECIMAL(15,4) NOT NULL,
    equity_value DECIMAL(15,4) NOT NULL,
    day_pnl DECIMAL(15,4) NOT NULL,
    total_pnl DECIMAL(15,4) NOT NULL
);

-- Convert to hypertable
SELECT create_hypertable('portfolio_snapshots', 'snapshot_time');

-- Alerts table
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(50) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    condition_type VARCHAR(20) NOT NULL, -- 'price_above', 'price_below', 'volume_above', etc.
    target_value DECIMAL(15,4) NOT NULL,
    message TEXT,
    is_active BOOLEAN DEFAULT true,
    triggered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User sessions table
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_activity TIMESTAMPTZ DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_broker_accounts_user_id ON broker_accounts(user_id);
CREATE INDEX idx_market_data_symbol_time ON market_data(symbol, time DESC);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_positions_user_id ON positions(user_id);
CREATE INDEX idx_trades_user_id ON trades(user_id);
CREATE INDEX idx_trades_executed_at ON trades(executed_at);
CREATE INDEX idx_portfolio_snapshots_user_time ON portfolio_snapshots(user_id, snapshot_time DESC);
CREATE INDEX idx_alerts_user_active ON alerts(user_id, is_active);
CREATE INDEX idx_user_sessions_token ON user_sessions(session_token);

-- Add updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at columns
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_broker_accounts_updated_at BEFORE UPDATE ON broker_accounts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_positions_updated_at BEFORE UPDATE ON positions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for development
INSERT INTO users (username, email, password_hash, full_name, is_verified) VALUES
('demo_user', 'demo@arthachitra.com', '$2b$12$LQv3c1yqBwUAFO.YSHLe.eXTTtNjyb8kU7x8x8x8x8x8x8x8x8', 'Demo User', true),
('trader1', 'trader1@example.com', '$2b$12$LQv3c1yqBwUAFO.YSHLe.eXTTtNjyb8kU7x8x8x8x8x8x8x8', 'Professional Trader', true);

-- Insert sample market data
INSERT INTO market_data (time, symbol, exchange, open, high, low, close, volume, timeframe) VALUES
(NOW() - INTERVAL '1 day', 'NIFTY', 'NSE', 18000.00, 18100.00, 17900.00, 18050.00, 1000000, '1d'),
(NOW() - INTERVAL '1 day', 'RELIANCE', 'NSE', 2500.00, 2520.00, 2480.00, 2510.00, 500000, '1d'),
(NOW() - INTERVAL '1 day', 'TCS', 'NSE', 3200.00, 3220.00, 3180.00, 3210.00, 300000, '1d');
