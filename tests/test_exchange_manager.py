"""
Tests for bots/exchange_manager.py
"""

import pytest
import json
import os
from unittest.mock import Mock, patch, AsyncMock
import asyncio

from bots.exchange_manager import ExchangeManager


class TestExchangeManager:
    """Test cases for ExchangeManager class"""
    
    def test_init_with_valid_config(self, temp_config_file):
        """Test ExchangeManager initialization with valid config"""
        manager = ExchangeManager(temp_config_file)
        assert manager.config is not None
        assert isinstance(manager.config, dict)
        assert manager.exchanges == {}
        assert manager.dex_connections == {}
    
    def test_init_with_invalid_config(self):
        """Test ExchangeManager initialization with invalid config"""
        manager = ExchangeManager("nonexistent_config.json")
        assert manager.config == {}
    
    def test_load_config_success(self, temp_config_file):
        """Test successful config loading"""
        manager = ExchangeManager()
        config = manager._load_config(temp_config_file)
        assert config is not None
        assert isinstance(config, dict)
    
    def test_load_config_file_not_found(self):
        """Test config loading with non-existent file"""
        manager = ExchangeManager()
        config = manager._load_config("nonexistent.json")
        assert config == {}
    
    @patch('ccxt.binance')
    def test_initialize_cex_success(self, mock_binance_class, sample_config, temp_directory):
        """Test successful CEX initialization"""
        # Setup mock
        mock_exchange = Mock()
        mock_exchange.fetch_balance.return_value = {'USDT': {'total': 1000}}
        mock_binance_class.return_value = mock_exchange
        
        # Create config file
        config_path = os.path.join(temp_directory, "config.json")
        with open(config_path, 'w') as f:
            json.dump(sample_config, f)
        
        manager = ExchangeManager(config_path)
        
        # Test CEX initialization
        result = manager._initialize_cex('binance', sample_config['exchanges']['binance'])
        assert result is True
        assert 'binance' in manager.exchanges
        assert manager.exchanges['binance']['type'] == 'cex'
        
        # Verify exchange was created with correct parameters
        mock_binance_class.assert_called_once()
        call_args = mock_binance_class.call_args[0][0]
        assert 'apiKey' in call_args
        assert 'secret' in call_args
        assert call_args['sandbox'] is True
        assert call_args['enableRateLimit'] is True
    
    @patch('ccxt.binance')
    def test_initialize_cex_no_credentials(self, mock_binance_class, sample_config):
        """Test CEX initialization without API credentials"""
        mock_exchange = Mock()
        mock_binance_class.return_value = mock_exchange
        
        # Remove credentials from config
        config = sample_config['exchanges']['binance'].copy()
        config['api_key'] = ''
        config['secret'] = ''
        
        manager = ExchangeManager()
        result = manager._initialize_cex('binance', config)
        assert result is True  # Should still succeed but with warning
    
    @patch('ccxt.binance')
    def test_initialize_cex_failure(self, mock_binance_class):
        """Test CEX initialization failure"""
        mock_binance_class.side_effect = Exception("Connection failed")
        
        manager = ExchangeManager()
        config = {
            'api_key': 'test_key',
            'secret': 'test_secret',
            'sandbox': True
        }
        
        result = manager._initialize_cex('binance', config)
        assert result is False
        assert 'binance' not in manager.exchanges
    
    @patch('web3.Web3')
    def test_initialize_dex_success(self, mock_web3_class, sample_config):
        """Test successful DEX initialization"""
        # Setup mock
        mock_w3 = Mock()
        mock_w3.is_connected.return_value = True
        mock_account = Mock()
        mock_account.address = '0x1234567890123456789012345678901234567890'
        mock_w3.eth.account.from_key.return_value = mock_account
        mock_web3_class.return_value = mock_w3
        
        manager = ExchangeManager()
        
        dex_config = {
            'network': 'ethereum',
            'rpc_url': 'https://mainnet.infura.io/v3/test',
            'private_key': 'test_private_key'
        }
        
        result = manager._initialize_dex('uniswap_v3', dex_config)
        assert result is True
        assert 'uniswap_v3' in manager.dex_connections
        assert manager.dex_connections['uniswap_v3']['type'] == 'dex'
    
    @patch('web3.Web3')
    def test_initialize_dex_no_rpc_url(self, mock_web3_class):
        """Test DEX initialization without RPC URL"""
        manager = ExchangeManager()
        
        dex_config = {
            'network': 'ethereum',
            'rpc_url': '',
            'private_key': 'test_private_key'
        }
        
        result = manager._initialize_dex('uniswap_v3', dex_config)
        assert result is False
        assert 'uniswap_v3' not in manager.dex_connections
    
    @patch('web3.Web3')
    def test_initialize_dex_connection_failed(self, mock_web3_class):
        """Test DEX initialization with connection failure"""
        mock_w3 = Mock()
        mock_w3.is_connected.return_value = False
        mock_web3_class.return_value = mock_w3
        
        manager = ExchangeManager()
        
        dex_config = {
            'network': 'ethereum',
            'rpc_url': 'https://mainnet.infura.io/v3/test',
            'private_key': 'test_private_key'
        }
        
        result = manager._initialize_dex('uniswap_v3', dex_config)
        assert result is False
        assert 'uniswap_v3' not in manager.dex_connections
    
    def test_initialize_exchanges_success(self, sample_config, temp_directory):
        """Test successful exchanges initialization"""
        config_path = os.path.join(temp_directory, "config.json")
        with open(config_path, 'w') as f:
            json.dump(sample_config, f)
        
        manager = ExchangeManager(config_path)
        
        with patch.object(manager, '_initialize_cex', return_value=True) as mock_cex, \
             patch.object(manager, '_initialize_dex', return_value=True) as mock_dex:
            
            result = manager.initialize_exchanges()
            assert result is True
            mock_cex.assert_called_once()  # Only binance is enabled
    
    def test_initialize_exchanges_no_enabled(self, temp_directory):
        """Test exchanges initialization with no enabled exchanges"""
        config = {
            "exchanges": {
                "binance": {"enabled": False},
                "gateio": {"enabled": False}
            }
        }
        
        config_path = os.path.join(temp_directory, "config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f)
        
        manager = ExchangeManager(config_path)
        result = manager.initialize_exchanges()
        assert result is False
    
    def test_get_exchange_cex(self):
        """Test getting CEX exchange instance"""
        manager = ExchangeManager()
        mock_exchange = Mock()
        manager.exchanges['binance'] = {
            'instance': mock_exchange,
            'type': 'cex'
        }
        
        result = manager.get_exchange('binance')
        assert result == mock_exchange
    
    def test_get_exchange_dex(self):
        """Test getting DEX connection"""
        manager = ExchangeManager()
        mock_dex = {'w3': Mock(), 'account': Mock(), 'type': 'dex'}
        manager.dex_connections['uniswap_v3'] = mock_dex
        
        result = manager.get_exchange('uniswap_v3')
        assert result == mock_dex
    
    def test_get_exchange_not_found(self):
        """Test getting non-existent exchange"""
        manager = ExchangeManager()
        result = manager.get_exchange('nonexistent')
        assert result is None
    
    def test_get_enabled_exchanges(self):
        """Test getting list of enabled exchanges"""
        manager = ExchangeManager()
        manager.exchanges['binance'] = {'instance': Mock()}
        manager.dex_connections['uniswap_v3'] = {'w3': Mock()}
        
        enabled = manager.get_enabled_exchanges()
        assert 'binance' in enabled
        assert 'uniswap_v3' in enabled
        assert len(enabled) == 2
    
    def test_get_trading_pairs_cex(self):
        """Test getting trading pairs for CEX"""
        manager = ExchangeManager()
        manager.exchanges['binance'] = {
            'config': {'trading_pairs': ['BTC/USDT', 'ETH/USDT']}
        }
        
        pairs = manager.get_trading_pairs('binance')
        assert pairs == ['BTC/USDT', 'ETH/USDT']
    
    def test_get_trading_pairs_dex(self):
        """Test getting trading pairs for DEX"""
        manager = ExchangeManager()
        manager.dex_connections['uniswap_v3'] = {
            'config': {'trading_pairs': ['WETH/USDC']}
        }
        
        pairs = manager.get_trading_pairs('uniswap_v3')
        assert pairs == ['WETH/USDC']
    
    def test_get_trading_pairs_not_found(self):
        """Test getting trading pairs for non-existent exchange"""
        manager = ExchangeManager()
        pairs = manager.get_trading_pairs('nonexistent')
        assert pairs == []
    
    @pytest.mark.asyncio
    async def test_fetch_ticker_cex_success(self):
        """Test successful ticker fetching from CEX"""
        manager = ExchangeManager()
        mock_exchange = Mock()
        mock_ticker = {
            'symbol': 'BTC/USDT',
            'last': 50000.0,
            'bid': 49950.0,
            'ask': 50050.0
        }
        mock_exchange.fetch_ticker.return_value = mock_ticker
        manager.exchanges['binance'] = {'instance': mock_exchange}
        
        result = await manager.fetch_ticker('binance', 'BTC/USDT')
        assert result == mock_ticker
        mock_exchange.fetch_ticker.assert_called_once_with('BTC/USDT')
    
    @pytest.mark.asyncio
    async def test_fetch_ticker_cex_failure(self):
        """Test ticker fetching failure from CEX"""
        manager = ExchangeManager()
        mock_exchange = Mock()
        mock_exchange.fetch_ticker.side_effect = Exception("API Error")
        manager.exchanges['binance'] = {'instance': mock_exchange}
        
        result = await manager.fetch_ticker('binance', 'BTC/USDT')
        assert result is None
    
    @pytest.mark.asyncio
    async def test_fetch_ticker_dex(self):
        """Test ticker fetching from DEX"""
        manager = ExchangeManager()
        mock_w3 = Mock()
        mock_w3.eth.get_block.return_value = {'timestamp': 1640995200}
        manager.dex_connections['uniswap_v3'] = {
            'w3': mock_w3,
            'config': {}
        }
        
        result = await manager.fetch_ticker('uniswap_v3', 'WETH/USDC')
        assert result is not None
        assert result['symbol'] == 'WETH/USDC'
        assert 'last' in result
    
    @pytest.mark.asyncio
    async def test_place_order_cex_market_buy(self):
        """Test placing market buy order on CEX"""
        manager = ExchangeManager()
        mock_exchange = Mock()
        mock_order = {
            'id': 'order_123',
            'symbol': 'BTC/USDT',
            'side': 'buy',
            'amount': 0.01,
            'type': 'market'
        }
        mock_exchange.create_market_buy_order.return_value = mock_order
        manager.exchanges['binance'] = {'instance': mock_exchange}
        
        result = await manager.place_order('binance', 'BTC/USDT', 'market', 'buy', 0.01)
        assert result == mock_order
        mock_exchange.create_market_buy_order.assert_called_once_with('BTC/USDT', 0.01)
    
    @pytest.mark.asyncio
    async def test_place_order_cex_limit_sell(self):
        """Test placing limit sell order on CEX"""
        manager = ExchangeManager()
        mock_exchange = Mock()
        mock_order = {
            'id': 'order_124',
            'symbol': 'BTC/USDT',
            'side': 'sell',
            'amount': 0.01,
            'type': 'limit',
            'price': 51000.0
        }
        mock_exchange.create_limit_sell_order.return_value = mock_order
        manager.exchanges['binance'] = {'instance': mock_exchange}
        
        result = await manager.place_order('binance', 'BTC/USDT', 'limit', 'sell', 0.01, 51000.0)
        assert result == mock_order
        mock_exchange.create_limit_sell_order.assert_called_once_with('BTC/USDT', 0.01, 51000.0)
    
    @pytest.mark.asyncio
    async def test_place_order_dex(self):
        """Test placing order on DEX"""
        manager = ExchangeManager()
        manager.dex_connections['uniswap_v3'] = {
            'w3': Mock(),
            'account': Mock(),
            'config': {}
        }
        
        with patch.object(asyncio, 'get_event_loop') as mock_loop:
            mock_loop.return_value.time.return_value = 1640995200
            
            result = await manager.place_order('uniswap_v3', 'WETH/USDC', 'market', 'buy', 1.0)
            assert result is not None
            assert result['symbol'] == 'WETH/USDC'
            assert result['side'] == 'buy'
            assert result['amount'] == 1.0
            assert result['status'] == 'pending'
    
    @pytest.mark.asyncio
    async def test_place_order_failure(self):
        """Test order placement failure"""
        manager = ExchangeManager()
        mock_exchange = Mock()
        mock_exchange.create_market_buy_order.side_effect = Exception("Order failed")
        manager.exchanges['binance'] = {'instance': mock_exchange}
        
        result = await manager.place_order('binance', 'BTC/USDT', 'market', 'buy', 0.01)
        assert result is None
    
    def test_get_balance_cex_success(self):
        """Test successful balance fetching from CEX"""
        manager = ExchangeManager()
        mock_exchange = Mock()
        mock_balance = {
            'total': {'USDT': 1000.0, 'BTC': 0.05},
            'free': {'USDT': 800.0, 'BTC': 0.03},
            'used': {'USDT': 200.0, 'BTC': 0.02}
        }
        mock_exchange.fetch_balance.return_value = mock_balance
        manager.exchanges['binance'] = {'instance': mock_exchange}
        
        result = manager.get_balance('binance')
        assert result == mock_balance
        mock_exchange.fetch_balance.assert_called_once()
    
    def test_get_balance_cex_failure(self):
        """Test balance fetching failure from CEX"""
        manager = ExchangeManager()
        mock_exchange = Mock()
        mock_exchange.fetch_balance.side_effect = Exception("API Error")
        manager.exchanges['binance'] = {'instance': mock_exchange}
        
        result = manager.get_balance('binance')
        assert result is None
    
    def test_get_balance_dex_success(self):
        """Test successful balance fetching from DEX"""
        manager = ExchangeManager()
        mock_w3 = Mock()
        mock_w3.eth.get_balance.return_value = 1000000000000000000  # 1 ETH in wei
        mock_w3.from_wei.return_value = 1.0
        mock_account = Mock()
        mock_account.address = '0x1234567890123456789012345678901234567890'
        
        manager.dex_connections['uniswap_v3'] = {
            'w3': mock_w3,
            'account': mock_account,
            'config': {'network': 'ethereum'}
        }
        
        result = manager.get_balance('uniswap_v3')
        assert result is not None
        assert 'ETH' in result['total']
        assert result['total']['ETH'] == 1.0
    
    def test_get_balance_dex_no_account(self):
        """Test balance fetching from DEX without account"""
        manager = ExchangeManager()
        manager.dex_connections['uniswap_v3'] = {
            'w3': Mock(),
            'account': None,
            'config': {'network': 'ethereum'}
        }
        
        result = manager.get_balance('uniswap_v3')
        assert result is None
    
    def test_get_balance_not_found(self):
        """Test balance fetching for non-existent exchange"""
        manager = ExchangeManager()
        result = manager.get_balance('nonexistent')
        assert result is None
    
    def test_close_all_connections(self):
        """Test closing all connections"""
        manager = ExchangeManager()
        
        # Setup mock exchanges
        mock_exchange1 = Mock()
        mock_exchange2 = Mock()
        mock_exchange2.close = Mock()
        
        manager.exchanges = {
            'binance': {'instance': mock_exchange1},
            'gateio': {'instance': mock_exchange2}
        }
        
        manager.close_all_connections()
        
        # Verify close was called where available
        mock_exchange2.close.assert_called_once()


class TestExchangeManagerIntegration:
    """Integration tests for ExchangeManager"""
    
    @patch('ccxt.binance')
    @patch('web3.Web3')
    def test_full_initialization_workflow(self, mock_web3_class, mock_binance_class, 
                                        sample_config, temp_directory):
        """Test complete initialization workflow"""
        # Setup mocks
        mock_exchange = Mock()
        mock_exchange.fetch_balance.return_value = {'USDT': {'total': 1000}}
        mock_binance_class.return_value = mock_exchange
        
        mock_w3 = Mock()
        mock_w3.is_connected.return_value = True
        mock_account = Mock()
        mock_account.address = '0x1234567890123456789012345678901234567890'
        mock_w3.eth.account.from_key.return_value = mock_account
        mock_web3_class.return_value = mock_w3
        
        # Add DEX config
        sample_config['exchanges']['uniswap_v3'] = {
            'enabled': True,
            'type': 'dex',
            'network': 'ethereum',
            'rpc_url': 'https://mainnet.infura.io/v3/test',
            'private_key': 'test_key'
        }
        
        config_path = os.path.join(temp_directory, "config.json")
        with open(config_path, 'w') as f:
            json.dump(sample_config, f)
        
        # Test workflow
        manager = ExchangeManager(config_path)
        
        # 1. Initialize exchanges
        result = manager.initialize_exchanges()
        assert result is True
        
        # 2. Verify exchanges are available
        enabled = manager.get_enabled_exchanges()
        assert 'binance' in enabled
        assert 'uniswap_v3' in enabled
        
        # 3. Test getting exchange instances
        binance_exchange = manager.get_exchange('binance')
        assert binance_exchange is not None
        
        uniswap_connection = manager.get_exchange('uniswap_v3')
        assert uniswap_connection is not None
        
        # 4. Test getting trading pairs
        binance_pairs = manager.get_trading_pairs('binance')
        assert len(binance_pairs) > 0
        
        # 5. Close connections
        manager.close_all_connections()
    
    def test_error_handling_workflow(self, temp_directory):
        """Test error handling in various scenarios"""
        # Create config with invalid exchange
        config = {
            "exchanges": {
                "invalid_exchange": {
                    "enabled": True,
                    "type": "cex",
                    "api_key": "invalid",
                    "secret": "invalid"
                }
            }
        }
        
        config_path = os.path.join(temp_directory, "config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f)
        
        manager = ExchangeManager(config_path)
        
        # Should handle invalid exchange gracefully
        result = manager.initialize_exchanges()
        assert result is False
        
        # Should return empty lists/None for non-existent exchanges
        assert manager.get_enabled_exchanges() == []
        assert manager.get_trading_pairs('invalid_exchange') == []
        assert manager.get_exchange('invalid_exchange') is None
        assert manager.get_balance('invalid_exchange') is None 