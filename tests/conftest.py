"""
Pytest configuration and shared fixtures
"""

import pytest
import json
import os
import tempfile
from unittest.mock import Mock, patch
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Test data fixtures
@pytest.fixture
def sample_config():
    """Sample configuration for testing"""
    return {
        "exchanges": {
            "binance": {
                "enabled": True,
                "type": "cex",
                "api_key": "test_api_key",
                "secret": "test_secret",
                "sandbox": True,
                "trading_pairs": ["BTC/USDT", "ETH/USDT"],
                "min_order_amount": 10.0,
                "max_order_amount": 1000.0,
                "fee_rate": 0.001
            },
            "gateio": {
                "enabled": False,
                "type": "cex",
                "api_key": "",
                "secret": "",
                "sandbox": True,
                "trading_pairs": ["BTC/USDT"],
                "min_order_amount": 10.0,
                "max_order_amount": 1000.0,
                "fee_rate": 0.002
            }
        },
        "trading_strategy": {
            "strategy_type": "market_making",
            "timeframe": "1m",
            "indicators": ["sma", "ema", "rsi", "macd"],
            "risk_management": {
                "max_position_size": 0.1,
                "stop_loss": 0.02,
                "take_profit": 0.03,
                "max_daily_loss": 0.05
            }
        },
        "bot_settings": {
            "check_interval": 30,
            "log_level": "INFO",
            "log_file": "temp/trading_bot.log",
            "telegram_notifications": {
                "enabled": False,
                "bot_token": "",
                "chat_id": ""
            },
            "database": {
                "enabled": True,
                "type": "sqlite",
                "path": "temp/trading_data.db"
            }
        }
    }

@pytest.fixture
def temp_config_file(sample_config):
    """Create a temporary config file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_config, f, indent=2)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)

@pytest.fixture
def temp_env_file():
    """Create a temporary .env file"""
    env_content = """
BINANCE_API_KEY=test_binance_key
BINANCE_SECRET=test_binance_secret
GATEIO_API_KEY=test_gateio_key
GATEIO_SECRET=test_gateio_secret
TELEGRAM_BOT_TOKEN=test_bot_token
TELEGRAM_CHAT_ID=test_chat_id
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write(env_content)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)

@pytest.fixture
def sample_ohlcv_data():
    """Sample OHLCV data for testing"""
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1H')
    np.random.seed(42)  # For reproducible tests
    
    # Generate realistic price data
    base_price = 50000
    price_changes = np.random.normal(0, 0.02, 100)
    prices = [base_price]
    
    for change in price_changes[1:]:
        new_price = prices[-1] * (1 + change)
        prices.append(max(new_price, 1000))  # Minimum price
    
    data = []
    for i, date in enumerate(dates):
        open_price = prices[i]
        close_price = prices[i] * (1 + np.random.normal(0, 0.01))
        high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, 0.005)))
        low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, 0.005)))
        volume = np.random.uniform(100, 1000)
        
        data.append({
            'timestamp': date,
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': volume
        })
    
    return pd.DataFrame(data)

@pytest.fixture
def sample_balance_data():
    """Sample balance data for testing"""
    return {
        'total': {
            'USDT': 1000.0,
            'BTC': 0.05,
            'ETH': 1.5
        },
        'free': {
            'USDT': 800.0,
            'BTC': 0.03,
            'ETH': 1.0
        },
        'used': {
            'USDT': 200.0,
            'BTC': 0.02,
            'ETH': 0.5
        }
    }

@pytest.fixture
def sample_ticker_data():
    """Sample ticker data for testing"""
    return {
        'symbol': 'BTC/USDT',
        'last': 50000.0,
        'bid': 49950.0,
        'ask': 50050.0,
        'high': 51000.0,
        'low': 49000.0,
        'volume': 1000.0,
        'quoteVolume': 50000000.0,
        'percentage': 2.5,
        'change': 1250.0,
        'timestamp': datetime.now().timestamp() * 1000
    }

@pytest.fixture
def sample_orderbook_data():
    """Sample orderbook data for testing"""
    return {
        'bids': [
            [49950.0, 0.1],
            [49940.0, 0.2],
            [49930.0, 0.15],
            [49920.0, 0.3],
            [49910.0, 0.25]
        ],
        'asks': [
            [50050.0, 0.1],
            [50060.0, 0.2],
            [50070.0, 0.15],
            [50080.0, 0.3],
            [50090.0, 0.25]
        ],
        'timestamp': datetime.now().timestamp() * 1000
    }

@pytest.fixture
def mock_exchange():
    """Mock exchange object for testing"""
    exchange = Mock()
    exchange.id = 'binance'
    exchange.name = 'Binance'
    exchange.has = {
        'fetchTicker': True,
        'fetchOHLCV': True,
        'fetchBalance': True,
        'fetchOrderBook': True,
        'createOrder': True,
        'cancelOrder': True,
        'fetchOrder': True,
        'fetchOrders': True,
        'fetchOpenOrders': True
    }
    return exchange

@pytest.fixture
def mock_ccxt_exchange(mock_exchange, sample_ticker_data, sample_ohlcv_data, 
                      sample_balance_data, sample_orderbook_data):
    """Mock CCXT exchange with realistic responses"""
    
    # Convert DataFrame to CCXT OHLCV format
    ohlcv_data = []
    for _, row in sample_ohlcv_data.iterrows():
        ohlcv_data.append([
            int(row['timestamp'].timestamp() * 1000),
            row['open'],
            row['high'],
            row['low'],
            row['close'],
            row['volume']
        ])
    
    mock_exchange.fetch_ticker.return_value = sample_ticker_data
    mock_exchange.fetch_ohlcv.return_value = ohlcv_data
    mock_exchange.fetch_balance.return_value = sample_balance_data
    mock_exchange.fetch_order_book.return_value = sample_orderbook_data
    mock_exchange.create_order.return_value = {
        'id': 'test_order_123',
        'symbol': 'BTC/USDT',
        'type': 'limit',
        'side': 'buy',
        'amount': 0.01,
        'price': 50000.0,
        'status': 'open',
        'timestamp': datetime.now().timestamp() * 1000
    }
    
    return mock_exchange

@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def sample_macd_signal():
    """Sample MACD signal data for testing"""
    return {
        'exchange': 'binance',
        'symbol': 'BTC/USDT',
        'timeframe': '1h',
        'signal_type': 'long',
        'price': 50000.0,
        'macd_value': 0.0015,
        'macd_signal': 0.0010,
        'macd_histogram': 0.0005,
        'strength': 75.5,
        'timestamp': datetime.now(),
        'volume_24h': 1000000.0
    }

@pytest.fixture
def sample_market_analysis():
    """Sample market analysis data for testing"""
    return {
        'exchange': 'binance',
        'symbol': 'BTC/USDT',
        'current_price': 50000.0,
        'price_change_24h': 2.5,
        'volatility': 3.2,
        'trend': 'bullish',
        'momentum': 'neutral',
        'rsi': 65.2,
        'market_condition': 'bullish_momentum',
        'recommended_config': {
            'bid_spread': 0.002,
            'ask_spread': 0.0025,
            'stop_loss': 0.015,
            'expected_profit': 0.0025
        },
        'timestamp': datetime.now()
    }

# Mock patches for external dependencies
@pytest.fixture
def mock_ccxt():
    """Mock CCXT library"""
    with patch('ccxt.binance') as mock_binance, \
         patch('ccxt.gateio') as mock_gateio:
        yield {
            'binance': mock_binance,
            'gateio': mock_gateio
        }

@pytest.fixture
def mock_web3():
    """Mock Web3 library for DEX testing"""
    with patch('web3.Web3') as mock_web3:
        mock_web3.isConnected.return_value = True
        mock_web3.eth.account.from_key.return_value.address = '0x1234567890123456789012345678901234567890'
        yield mock_web3

@pytest.fixture
def mock_telegram():
    """Mock Telegram bot"""
    with patch('telegram.Bot') as mock_bot:
        mock_bot.send_message.return_value = True
        yield mock_bot

# Environment setup
@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Setup test environment variables"""
    test_env = {
        'BINANCE_API_KEY': 'test_binance_key',
        'BINANCE_SECRET': 'test_binance_secret',
        'GATEIO_API_KEY': 'test_gateio_key',
        'GATEIO_SECRET': 'test_gateio_secret',
        'TELEGRAM_BOT_TOKEN': 'test_bot_token',
        'TELEGRAM_CHAT_ID': 'test_chat_id'
    }
    
    for key, value in test_env.items():
        monkeypatch.setenv(key, value)

# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Cleanup temporary files after tests"""
    yield
    
    # Clean up any temp files that might have been created
    temp_patterns = ['temp_*.json', 'test_*.db', 'test_*.log']
    for pattern in temp_patterns:
        import glob
        for file in glob.glob(pattern):
            try:
                os.unlink(file)
            except:
                pass 