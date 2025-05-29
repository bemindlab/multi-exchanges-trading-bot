-- Trading Bot Database Initialization Script
-- ============================================

-- Create n8n database for workflow automation
CREATE DATABASE n8n_db;

-- Grant permissions to trading_user for n8n database
GRANT ALL PRIVILEGES ON DATABASE n8n_db TO trading_user;

-- Switch to n8n database and create necessary extensions
\c n8n_db;

-- Create UUID extension for n8n
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Switch back to main trading database
\c trading_db;

-- Create main trading tables
CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    exchange VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL,
    amount DECIMAL(20, 8) NOT NULL,
    price DECIMAL(20, 8) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    order_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS market_data (
    id SERIAL PRIMARY KEY,
    exchange VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    price DECIMAL(20, 8) NOT NULL,
    volume DECIMAL(20, 8),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS strategies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    config JSONB,
    active BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bot_status (
    id SERIAL PRIMARY KEY,
    bot_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    config JSONB
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_trades_exchange_symbol ON trades (exchange, symbol);

CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades (timestamp);

CREATE INDEX IF NOT EXISTS idx_market_data_exchange_symbol ON market_data (exchange, symbol);

CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data (timestamp);

-- Insert default strategy configurations
INSERT INTO
    strategies (name, config, active)
VALUES (
        'MACD Strategy',
        '{"timeframe": "1h", "fast_period": 12, "slow_period": 26, "signal_period": 9}',
        false
    ),
    (
        'RSI Strategy',
        '{"timeframe": "1h", "period": 14, "overbought": 70, "oversold": 30}',
        false
    ),
    (
        'Arbitrage Strategy',
        '{"min_profit_threshold": 0.5, "max_position_size": 1000}',
        false
    ) ON CONFLICT DO NOTHING;

-- Create a view for recent trades
CREATE OR REPLACE VIEW recent_trades AS
SELECT *
FROM trades
WHERE
    timestamp > NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for strategies table
CREATE TRIGGER update_strategies_updated_at 
    BEFORE UPDATE ON strategies 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();