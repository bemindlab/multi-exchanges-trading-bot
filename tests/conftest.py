"""
Pytest configuration and shared fixtures for the trading bot test suite.
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add src to Python path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Test configuration
pytest_plugins = []


@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration."""
    return {
        "api_key": "test_api_key",
        "api_secret": "test_api_secret",
        "trading_pairs": ["BTC_USDT", "ETH_USDT"],
        "amount": 10.0,
        "check_interval": 60,
        "max_daily_loss": 100.0,
        "max_position_size": 1000.0,
    }


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_exchange_api():
    """Mock exchange API for testing."""
    mock_api = Mock()
    mock_api.fetch_ticker.return_value = {
        'symbol': 'BTC/USDT',
        'last': 50000.0,
        'bid': 49999.0,
        'ask': 50001.0,
        'high': 51000.0,
        'low': 49000.0,
        'volume': 1000.0
    }
    mock_api.fetch_ohlcv.return_value = [
        [1640995200000, 49000, 51000, 48000, 50000, 1000],  # Sample OHLCV data
        [1640998800000, 50000, 52000, 49500, 51000, 1100],
        [1641002400000, 51000, 51500, 50000, 50500, 950],
    ]
    mock_api.create_market_buy_order.return_value = {
        'id': 'test_order_123',
        'symbol': 'BTC/USDT',
        'side': 'buy',
        'amount': 0.001,
        'price': 50000,
        'status': 'closed'
    }
    return mock_api


@pytest.fixture
def mock_risk_manager():
    """Mock risk manager for testing."""
    mock_rm = Mock()
    mock_rm.can_open_position.return_value = True
    mock_rm.get_risk_metrics.return_value = {
        'daily_pnl': 0.0,
        'total_positions': 0,
        'risk_score': 0.1
    }
    return mock_rm


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    return Mock()


@pytest.fixture
def sample_market_data():
    """Provide sample market data for testing."""
    return {
        'prices': [49000, 49500, 50000, 50500, 51000, 50800, 50200, 49800],
        'volumes': [100, 120, 150, 130, 110, 140, 160, 125],
        'timestamps': [
            1640995200, 1640998800, 1641002400, 1641006000,
            1641009600, 1641013200, 1641016800, 1641020400
        ]
    }


@pytest.fixture
def mock_mqtt_client():
    """Mock MQTT client for testing."""
    mock_client = Mock()
    mock_client.connect.return_value = 0
    mock_client.publish.return_value = MagicMock()
    mock_client.subscribe.return_value = (0, 1)
    return mock_client


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Setup test environment variables."""
    test_env_vars = {
        'GATE_API_KEY': 'test_api_key',
        'GATE_API_SECRET': 'test_api_secret',
        'TELEGRAM_BOT_TOKEN': 'test_telegram_token',
        'TELEGRAM_CHAT_ID': 'test_chat_id',
        'DISCORD_WEBHOOK_URL': 'https://discord.com/api/webhooks/test',
        'DEBUG': '1',
    }
    
    for key, value in test_env_vars.items():
        monkeypatch.setenv(key, value)


@pytest.fixture
def mock_config_file(temp_dir):
    """Create a mock configuration file."""
    config_content = {
        "trading_pairs": ["BTC_USDT", "ETH_USDT"],
        "amount": 10.0,
        "check_interval": 60,
        "macd_fast": 12,
        "macd_slow": 26,
        "macd_signal": 9,
        "risk_management": {
            "max_daily_loss": 100.0,
            "max_position_size": 1000.0,
            "stop_loss_percentage": 0.05
        }
    }
    
    import json
    config_path = temp_dir / "test_config.json"
    with open(config_path, 'w') as f:
        json.dump(config_content, f, indent=2)
    
    return config_path


# Pytest markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "security: marks tests as security tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )


# Test collection customization
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add unit marker to unit tests
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add integration marker to integration tests
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Add performance marker to performance tests
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)
        
        # Add security marker to security tests
        elif "security" in str(item.fspath):
            item.add_marker(pytest.mark.security) 