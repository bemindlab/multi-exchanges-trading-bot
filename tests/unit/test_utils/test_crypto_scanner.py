"""
Tests for bots/crypto_scanner.py
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import asyncio
import json
import os

from bots.crypto_scanner import (
    CryptoPairsScanner, MACDSignal, ScannerConfig,
    run_single_scan, run_continuous_scan
)


class TestMACDSignal:
    """Test cases for MACDSignal dataclass"""
    
    def test_macd_signal_creation(self):
        """Test MACDSignal creation"""
        signal = MACDSignal(
            symbol='BTC/USDT',
            exchange='binance',
            timeframe='1h',
            signal_type='long',
            macd_value=0.0015,
            macd_signal=0.0010,
            macd_histogram=0.0005,
            price=50000.0,
            volume=1000000.0,
            timestamp=datetime.now(),
            strength=75.5
        )
        
        assert signal.symbol == 'BTC/USDT'
        assert signal.exchange == 'binance'
        assert signal.timeframe == '1h'
        assert signal.signal_type == 'long'
        assert signal.macd_value == 0.0015
        assert signal.strength == 75.5


class TestScannerConfig:
    """Test cases for ScannerConfig dataclass"""
    
    def test_scanner_config_defaults(self):
        """Test ScannerConfig with default values"""
        config = ScannerConfig()
        
        assert config.timeframes == ['1h', '4h', '1d']
        assert config.exchanges == ['binance', 'gateio']
        assert len(config.trading_pairs) == 20  # Default pairs
        assert config.min_volume_24h == 100000
        assert config.min_signal_strength == 60
        assert config.macd_fast == 12
        assert config.macd_slow == 26
        assert config.macd_signal_period == 9
    
    def test_scanner_config_custom(self):
        """Test ScannerConfig with custom values"""
        config = ScannerConfig(
            timeframes=['15m', '1h'],
            exchanges=['binance'],
            trading_pairs=['BTC/USDT', 'ETH/USDT'],
            min_volume_24h=50000,
            min_signal_strength=70
        )
        
        assert config.timeframes == ['15m', '1h']
        assert config.exchanges == ['binance']
        assert config.trading_pairs == ['BTC/USDT', 'ETH/USDT']
        assert config.min_volume_24h == 50000
        assert config.min_signal_strength == 70


class TestCryptoPairsScanner:
    """Test cases for CryptoPairsScanner class"""
    
    def test_init(self, temp_config_file):
        """Test scanner initialization"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        assert scanner.exchange_manager is not None
        assert isinstance(scanner.config, ScannerConfig)
        assert scanner.scan_results == {}
        assert scanner.is_scanning is False
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, temp_config_file):
        """Test successful scanner initialization"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        with patch.object(scanner.exchange_manager, 'initialize_exchanges', return_value=True):
            result = await scanner.initialize()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_initialize_failure(self, temp_config_file):
        """Test scanner initialization failure"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        with patch.object(scanner.exchange_manager, 'initialize_exchanges', return_value=False):
            result = await scanner.initialize()
            assert result is False
    
    def test_update_config(self, temp_config_file):
        """Test config update"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        scanner.update_config(
            min_signal_strength=80,
            timeframes=['1h', '4h']
        )
        
        assert scanner.config.min_signal_strength == 80
        assert scanner.config.timeframes == ['1h', '4h']
    
    def test_update_config_invalid_attribute(self, temp_config_file):
        """Test config update with invalid attribute"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        # Should not raise error, just ignore invalid attributes
        scanner.update_config(invalid_attribute='value')
        
        # Config should remain unchanged
        assert not hasattr(scanner.config, 'invalid_attribute')
    
    @pytest.mark.asyncio
    async def test_fetch_ohlcv_data_success(self, temp_config_file, sample_ohlcv_data):
        """Test successful OHLCV data fetching"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        # Mock exchange
        mock_exchange = Mock()
        ohlcv_data = []
        for _, row in sample_ohlcv_data.iterrows():
            ohlcv_data.append([
                int(row['timestamp'].timestamp() * 1000),
                row['open'], row['high'], row['low'], row['close'], row['volume']
            ])
        mock_exchange.fetch_ohlcv.return_value = ohlcv_data
        
        scanner.exchange_manager.exchanges = {'binance': {'instance': mock_exchange}}
        scanner.exchange_manager.get_exchange = Mock(return_value=mock_exchange)
        
        result = await scanner.fetch_ohlcv_data('binance', 'BTC/USDT', '1h', 100)
        
        assert result is not None
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_ohlcv_data)
        assert 'open' in result.columns
        assert 'close' in result.columns
    
    @pytest.mark.asyncio
    async def test_fetch_ohlcv_data_exchange_not_found(self, temp_config_file):
        """Test OHLCV data fetching with non-existent exchange"""
        scanner = CryptoPairsScanner(temp_config_file)
        scanner.exchange_manager.get_exchange = Mock(return_value=None)
        
        result = await scanner.fetch_ohlcv_data('nonexistent', 'BTC/USDT', '1h')
        assert result is None
    
    @pytest.mark.asyncio
    async def test_fetch_ohlcv_data_dex_not_supported(self, temp_config_file):
        """Test OHLCV data fetching from DEX (not supported)"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        mock_dex = {'w3': Mock(), 'account': Mock()}
        scanner.exchange_manager.exchanges = {}  # No CEX
        scanner.exchange_manager.dex_connections = {'uniswap_v3': mock_dex}
        scanner.exchange_manager.get_exchange = Mock(return_value=mock_dex)
        
        result = await scanner.fetch_ohlcv_data('uniswap_v3', 'WETH/USDC', '1h')
        assert result is None
    
    @pytest.mark.asyncio
    async def test_fetch_ohlcv_data_exception(self, temp_config_file):
        """Test OHLCV data fetching with exception"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        mock_exchange = Mock()
        mock_exchange.fetch_ohlcv.side_effect = Exception("API Error")
        scanner.exchange_manager.exchanges = {'binance': {'instance': mock_exchange}}
        scanner.exchange_manager.get_exchange = Mock(return_value=mock_exchange)
        
        result = await scanner.fetch_ohlcv_data('binance', 'BTC/USDT', '1h')
        assert result is None
    
    def test_calculate_macd(self, temp_config_file, sample_ohlcv_data):
        """Test MACD calculation"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        df = sample_ohlcv_data.copy().set_index('timestamp')
        result = scanner.calculate_macd(df)
        
        # Check that MACD indicators were added
        expected_columns = [
            'macd', 'macd_signal', 'macd_histogram',
            'macd_cross_up', 'macd_cross_down', 'signal_strength'
        ]
        
        for col in expected_columns:
            assert col in result.columns
        
        # Check that values are calculated (not all NaN)
        assert not result['macd'].isna().all()
        assert not result['macd_signal'].isna().all()
        assert not result['signal_strength'].isna().all()
    
    def test_calculate_macd_exception(self, temp_config_file):
        """Test MACD calculation with exception"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        # Invalid DataFrame
        df = pd.DataFrame({'invalid': [1, 2, 3]})
        
        result = scanner.calculate_macd(df)
        
        # Should return original DataFrame on error
        assert 'invalid' in result.columns
        assert len(result) == 3
    
    def test_calculate_signal_strength(self, temp_config_file, sample_ohlcv_data):
        """Test signal strength calculation"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        df = sample_ohlcv_data.copy().set_index('timestamp')
        df = scanner.calculate_macd(df)
        
        strength = scanner._calculate_signal_strength(df)
        
        assert isinstance(strength, pd.Series)
        assert len(strength) == len(df)
        assert strength.min() >= 0
        assert strength.max() <= 100
    
    def test_calculate_signal_strength_exception(self, temp_config_file):
        """Test signal strength calculation with exception"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        # Invalid DataFrame
        df = pd.DataFrame({'invalid': [1, 2, 3]})
        
        strength = scanner._calculate_signal_strength(df)
        
        assert isinstance(strength, pd.Series)
        assert len(strength) == 3
        assert all(strength == 0)
    
    def test_detect_macd_signals_long(self, temp_config_file):
        """Test MACD long signal detection"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        # Create data with long signal
        dates = pd.date_range(start='2024-01-01', periods=50, freq='1H')
        df = pd.DataFrame({
            'close': np.random.uniform(49000, 51000, 50),
            'volume': np.random.uniform(500, 1500, 50),
            'macd': [0.001] * 50,
            'macd_signal': [0.0005] * 50,
            'macd_histogram': [0.0005] * 50,
            'macd_cross_up': [False] * 49 + [True],  # Signal on last candle
            'macd_cross_down': [False] * 50,
            'signal_strength': [70.0] * 50  # Above minimum threshold
        }, index=dates)
        
        signals = scanner.detect_macd_signals(df, 'BTC/USDT', 'binance', '1h')
        
        assert len(signals) == 1
        assert signals[0].signal_type == 'long'
        assert signals[0].symbol == 'BTC/USDT'
        assert signals[0].exchange == 'binance'
        assert signals[0].timeframe == '1h'
        assert signals[0].strength == 70.0
    
    def test_detect_macd_signals_short(self, temp_config_file):
        """Test MACD short signal detection"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        # Create data with short signal
        dates = pd.date_range(start='2024-01-01', periods=50, freq='1H')
        df = pd.DataFrame({
            'close': np.random.uniform(49000, 51000, 50),
            'volume': np.random.uniform(500, 1500, 50),
            'macd': [-0.001] * 50,
            'macd_signal': [-0.0005] * 50,
            'macd_histogram': [-0.0005] * 50,
            'macd_cross_up': [False] * 50,
            'macd_cross_down': [False] * 49 + [True],  # Signal on last candle
            'signal_strength': [75.0] * 50  # Above minimum threshold
        }, index=dates)
        
        signals = scanner.detect_macd_signals(df, 'BTC/USDT', 'binance', '1h')
        
        assert len(signals) == 1
        assert signals[0].signal_type == 'short'
        assert signals[0].strength == 75.0
    
    def test_detect_macd_signals_low_volume(self, temp_config_file):
        """Test MACD signal detection with low volume"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        # Create data with low volume
        dates = pd.date_range(start='2024-01-01', periods=50, freq='1H')
        df = pd.DataFrame({
            'close': np.random.uniform(49000, 51000, 50),
            'volume': [10] * 50,  # Very low volume
            'macd': [0.001] * 50,
            'macd_signal': [0.0005] * 50,
            'macd_histogram': [0.0005] * 50,
            'macd_cross_up': [False] * 49 + [True],
            'macd_cross_down': [False] * 50,
            'signal_strength': [70.0] * 50
        }, index=dates)
        
        signals = scanner.detect_macd_signals(df, 'BTC/USDT', 'binance', '1h')
        
        # Should be empty due to low volume
        assert len(signals) == 0
    
    def test_detect_macd_signals_low_strength(self, temp_config_file):
        """Test MACD signal detection with low signal strength"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        # Create data with low signal strength
        dates = pd.date_range(start='2024-01-01', periods=50, freq='1H')
        df = pd.DataFrame({
            'close': np.random.uniform(49000, 51000, 50),
            'volume': np.random.uniform(500, 1500, 50),
            'macd': [0.001] * 50,
            'macd_signal': [0.0005] * 50,
            'macd_histogram': [0.0005] * 50,
            'macd_cross_up': [False] * 49 + [True],
            'macd_cross_down': [False] * 50,
            'signal_strength': [30.0] * 50  # Below minimum threshold
        }, index=dates)
        
        signals = scanner.detect_macd_signals(df, 'BTC/USDT', 'binance', '1h')
        
        # Should be empty due to low signal strength
        assert len(signals) == 0
    
    def test_detect_macd_signals_empty_data(self, temp_config_file):
        """Test MACD signal detection with empty data"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        signals = scanner.detect_macd_signals(None, 'BTC/USDT', 'binance', '1h')
        assert len(signals) == 0
        
        empty_df = pd.DataFrame()
        signals = scanner.detect_macd_signals(empty_df, 'BTC/USDT', 'binance', '1h')
        assert len(signals) == 0
    
    @pytest.mark.asyncio
    async def test_scan_single_pair_success(self, temp_config_file, sample_ohlcv_data):
        """Test successful single pair scanning"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        # Mock fetch_ohlcv_data
        df = sample_ohlcv_data.copy().set_index('timestamp')
        df = scanner.calculate_macd(df)
        
        with patch.object(scanner, 'fetch_ohlcv_data', return_value=df):
            with patch.object(scanner, 'detect_macd_signals', return_value=[Mock()]) as mock_detect:
                signals = await scanner.scan_single_pair('binance', 'BTC/USDT', '1h')
                
                assert len(signals) == 1
                mock_detect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_scan_single_pair_no_data(self, temp_config_file):
        """Test single pair scanning with no data"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        with patch.object(scanner, 'fetch_ohlcv_data', return_value=None):
            signals = await scanner.scan_single_pair('binance', 'BTC/USDT', '1h')
            assert len(signals) == 0
    
    @pytest.mark.asyncio
    async def test_scan_single_pair_exception(self, temp_config_file):
        """Test single pair scanning with exception"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        with patch.object(scanner, 'fetch_ohlcv_data', side_effect=Exception("API Error")):
            signals = await scanner.scan_single_pair('binance', 'BTC/USDT', '1h')
            assert len(signals) == 0
    
    @pytest.mark.asyncio
    async def test_scan_all_pairs_success(self, temp_config_file):
        """Test successful all pairs scanning"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        # Mock dependencies
        scanner.exchange_manager.get_enabled_exchanges = Mock(return_value=['binance'])
        scanner.config.exchanges = ['binance']
        scanner.config.trading_pairs = ['BTC/USDT', 'ETH/USDT']
        
        # Mock scan_single_pair to return signals
        mock_signal = MACDSignal(
            symbol='BTC/USDT', exchange='binance', timeframe='1h',
            signal_type='long', macd_value=0.001, macd_signal=0.0005,
            macd_histogram=0.0005, price=50000.0, volume=1000000.0,
            timestamp=datetime.now(), strength=70.0
        )
        
        with patch.object(scanner, 'scan_single_pair', return_value=[mock_signal]):
            results = await scanner.scan_all_pairs(['1h'])
            
            assert len(results) > 0
            assert 'binance_1h' in results
            assert len(results['binance_1h']) > 0
    
    @pytest.mark.asyncio
    async def test_scan_all_pairs_no_enabled_exchanges(self, temp_config_file):
        """Test all pairs scanning with no enabled exchanges"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        scanner.exchange_manager.get_enabled_exchanges = Mock(return_value=[])
        
        results = await scanner.scan_all_pairs(['1h'])
        assert len(results) == 0
    
    def test_get_top_signals(self, temp_config_file):
        """Test getting top signals"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        # Create mock signals with different strengths
        signals = [
            MACDSignal('BTC/USDT', 'binance', '1h', 'long', 0.001, 0.0005, 0.0005, 50000, 1000000, datetime.now(), 80.0),
            MACDSignal('ETH/USDT', 'binance', '1h', 'long', 0.001, 0.0005, 0.0005, 3000, 500000, datetime.now(), 70.0),
            MACDSignal('BNB/USDT', 'binance', '1h', 'short', -0.001, -0.0005, -0.0005, 300, 200000, datetime.now(), 90.0),
        ]
        
        scanner.scan_results = {'binance_1h': signals}
        
        # Test getting all top signals
        top_all = scanner.get_top_signals(limit=3)
        assert len(top_all) == 3
        assert top_all[0].strength == 90.0  # Highest strength first
        assert top_all[1].strength == 80.0
        assert top_all[2].strength == 70.0
        
        # Test getting only long signals
        top_long = scanner.get_top_signals('long', limit=2)
        assert len(top_long) == 2
        assert all(s.signal_type == 'long' for s in top_long)
        assert top_long[0].strength == 80.0  # Highest long signal
        
        # Test getting only short signals
        top_short = scanner.get_top_signals('short', limit=1)
        assert len(top_short) == 1
        assert top_short[0].signal_type == 'short'
        assert top_short[0].strength == 90.0
    
    def test_get_top_signals_empty_results(self, temp_config_file):
        """Test getting top signals with empty results"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        top_signals = scanner.get_top_signals()
        assert len(top_signals) == 0
    
    def test_print_scan_results_no_results(self, temp_config_file, capsys):
        """Test printing scan results with no results"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        scanner.print_scan_results()
        
        captured = capsys.readouterr()
        assert "ยังไม่มีผลการสแกน" in captured.out
    
    def test_print_scan_results_with_signals(self, temp_config_file, capsys):
        """Test printing scan results with signals"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        # Create mock signals
        signals = [
            MACDSignal('BTC/USDT', 'binance', '1h', 'long', 0.001, 0.0005, 0.0005, 50000, 1000000, datetime.now(), 80.0),
            MACDSignal('ETH/USDT', 'binance', '1h', 'short', -0.001, -0.0005, -0.0005, 3000, 500000, datetime.now(), 70.0),
        ]
        
        scanner.scan_results = {'binance_1h': signals}
        
        scanner.print_scan_results()
        
        captured = capsys.readouterr()
        assert "ผลการสแกน MACD Signals" in captured.out
        assert "TOP 5 LONG SIGNALS" in captured.out
        assert "TOP 5 SHORT SIGNALS" in captured.out
        assert "BTC/USDT" in captured.out
        assert "ETH/USDT" in captured.out
    
    def test_export_signals_to_json(self, temp_config_file, temp_directory):
        """Test exporting signals to JSON"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        # Create mock signals
        signal = MACDSignal(
            'BTC/USDT', 'binance', '1h', 'long', 0.001, 0.0005, 0.0005,
            50000, 1000000, datetime.now(), 80.0
        )
        scanner.scan_results = {'binance_1h': [signal]}
        
        # Export to temp directory
        filename = os.path.join(temp_directory, 'test_signals.json')
        result_filename = scanner.export_signals_to_json(filename)
        
        assert result_filename == filename
        assert os.path.exists(filename)
        
        # Verify JSON content
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert 'scan_time' in data
        assert 'config' in data
        assert 'signals' in data
        assert 'binance_1h' in data['signals']
        assert len(data['signals']['binance_1h']) == 1
        assert data['signals']['binance_1h'][0]['symbol'] == 'BTC/USDT'
    
    def test_export_signals_to_json_default_filename(self, temp_config_file):
        """Test exporting signals with default filename"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        signal = MACDSignal(
            'BTC/USDT', 'binance', '1h', 'long', 0.001, 0.0005, 0.0005,
            50000, 1000000, datetime.now(), 80.0
        )
        scanner.scan_results = {'binance_1h': [signal]}
        
        filename = scanner.export_signals_to_json()
        
        assert filename.startswith('temp/macd_signals_')
        assert filename.endswith('.json')
        assert os.path.exists(filename)
        
        # Cleanup
        os.unlink(filename)
    
    @pytest.mark.asyncio
    async def test_start_continuous_scan(self, temp_config_file):
        """Test starting continuous scan (short run)"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        # Mock methods
        scanner.scan_all_pairs = AsyncMock(return_value={'binance_1h': []})
        scanner.print_scan_results = Mock()
        scanner.get_top_signals = Mock(return_value=[])
        
        # Run for a very short time
        async def short_run():
            await asyncio.sleep(0.1)
            scanner.stop_scanning()
        
        # Start both tasks
        scan_task = asyncio.create_task(scanner.start_continuous_scan(1))  # 1 minute interval
        stop_task = asyncio.create_task(short_run())
        
        await asyncio.gather(scan_task, stop_task)
        
        # Verify methods were called
        scanner.scan_all_pairs.assert_called()
        scanner.print_scan_results.assert_called()
    
    def test_stop_scanning(self, temp_config_file):
        """Test stopping scan"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        scanner.is_scanning = True
        scanner.stop_scanning()
        
        assert scanner.is_scanning is False


class TestRunSingleScan:
    """Test cases for run_single_scan function"""
    
    @pytest.mark.asyncio
    async def test_run_single_scan_success(self, temp_config_file):
        """Test successful single scan run"""
        with patch('bots.crypto_scanner.CryptoPairsScanner') as mock_scanner_class:
            mock_scanner = Mock()
            mock_scanner.initialize = AsyncMock(return_value=True)
            mock_scanner.scan_all_pairs = AsyncMock(return_value={'binance_1h': []})
            mock_scanner.print_scan_results = Mock()
            mock_scanner.export_signals_to_json = Mock()
            mock_scanner.update_config = Mock()
            mock_scanner_class.return_value = mock_scanner
            
            result = await run_single_scan(['1h'], ['binance'])
            
            assert result is not None
            mock_scanner.initialize.assert_called_once()
            mock_scanner.update_config.assert_called()
            mock_scanner.scan_all_pairs.assert_called_once()
            mock_scanner.print_scan_results.assert_called_once()
            mock_scanner.export_signals_to_json.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_single_scan_initialization_failure(self):
        """Test single scan run with initialization failure"""
        with patch('bots.crypto_scanner.CryptoPairsScanner') as mock_scanner_class:
            mock_scanner = Mock()
            mock_scanner.initialize = AsyncMock(return_value=False)
            mock_scanner_class.return_value = mock_scanner
            
            result = await run_single_scan()
            
            assert result is None
            mock_scanner.initialize.assert_called_once()
            mock_scanner.scan_all_pairs.assert_not_called()


class TestRunContinuousScan:
    """Test cases for run_continuous_scan function"""
    
    @pytest.mark.asyncio
    async def test_run_continuous_scan_success(self):
        """Test successful continuous scan run"""
        with patch('bots.crypto_scanner.CryptoPairsScanner') as mock_scanner_class:
            mock_scanner = Mock()
            mock_scanner.initialize = AsyncMock(return_value=True)
            mock_scanner.start_continuous_scan = AsyncMock()
            mock_scanner_class.return_value = mock_scanner
            
            # Mock KeyboardInterrupt to stop the scan
            mock_scanner.start_continuous_scan.side_effect = KeyboardInterrupt()
            
            await run_continuous_scan(1)
            
            mock_scanner.initialize.assert_called_once()
            mock_scanner.start_continuous_scan.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_run_continuous_scan_initialization_failure(self):
        """Test continuous scan run with initialization failure"""
        with patch('bots.crypto_scanner.CryptoPairsScanner') as mock_scanner_class:
            mock_scanner = Mock()
            mock_scanner.initialize = AsyncMock(return_value=False)
            mock_scanner_class.return_value = mock_scanner
            
            await run_continuous_scan()
            
            mock_scanner.initialize.assert_called_once()
            mock_scanner.start_continuous_scan.assert_not_called()


class TestCryptoScannerIntegration:
    """Integration tests for CryptoPairsScanner"""
    
    @pytest.mark.asyncio
    async def test_full_scanning_workflow(self, temp_config_file, sample_ohlcv_data):
        """Test complete scanning workflow"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        # Mock exchange manager
        mock_exchange = Mock()
        ohlcv_data = []
        for _, row in sample_ohlcv_data.iterrows():
            ohlcv_data.append([
                int(row['timestamp'].timestamp() * 1000),
                row['open'], row['high'], row['low'], row['close'], row['volume']
            ])
        mock_exchange.fetch_ohlcv.return_value = ohlcv_data
        
        scanner.exchange_manager.exchanges = {'binance': {'instance': mock_exchange}}
        scanner.exchange_manager.get_exchange = Mock(return_value=mock_exchange)
        scanner.exchange_manager.get_enabled_exchanges = Mock(return_value=['binance'])
        
        # Update config for testing
        scanner.update_config(
            exchanges=['binance'],
            trading_pairs=['BTC/USDT'],
            timeframes=['1h'],
            min_signal_strength=0  # Lower threshold for testing
        )
        
        # Test complete workflow
        # 1. Fetch OHLCV data
        df = await scanner.fetch_ohlcv_data('binance', 'BTC/USDT', '1h')
        assert df is not None
        
        # 2. Calculate MACD
        df_with_macd = scanner.calculate_macd(df)
        assert 'macd' in df_with_macd.columns
        assert 'signal_strength' in df_with_macd.columns
        
        # 3. Detect signals
        signals = scanner.detect_macd_signals(df_with_macd, 'BTC/USDT', 'binance', '1h')
        # May or may not have signals depending on data
        
        # 4. Scan single pair
        single_signals = await scanner.scan_single_pair('binance', 'BTC/USDT', '1h')
        assert isinstance(single_signals, list)
        
        # 5. Scan all pairs
        all_results = await scanner.scan_all_pairs(['1h'])
        assert isinstance(all_results, dict)
        
        # 6. Get top signals
        top_signals = scanner.get_top_signals(limit=5)
        assert isinstance(top_signals, list)
    
    def test_error_handling_workflow(self, temp_config_file):
        """Test error handling in various scenarios"""
        scanner = CryptoPairsScanner(temp_config_file)
        
        # Test with invalid data
        invalid_df = pd.DataFrame({'invalid': [1, 2, 3]})
        
        # Should handle errors gracefully
        macd_df = scanner.calculate_macd(invalid_df)
        assert 'invalid' in macd_df.columns
        
        signals = scanner.detect_macd_signals(invalid_df, 'BTC/USDT', 'binance', '1h')
        assert len(signals) == 0
        
        # Test signal strength calculation with invalid data
        strength = scanner._calculate_signal_strength(invalid_df)
        assert len(strength) == 3
        assert all(strength == 0) 