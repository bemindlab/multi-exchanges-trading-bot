"""
Tests for bots/market_analyzer.py
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import asyncio

from bots.market_analyzer import MultiExchangeMarketAnalyzer, run_market_analysis


class TestMultiExchangeMarketAnalyzer:
    """Test cases for MultiExchangeMarketAnalyzer class"""
    
    def test_init(self, temp_config_file):
        """Test analyzer initialization"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        assert analyzer.exchange_manager is not None
        assert analyzer.analysis_results == {}
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, temp_config_file):
        """Test successful analyzer initialization"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        with patch.object(analyzer.exchange_manager, 'initialize_exchanges', return_value=True):
            result = await analyzer.initialize()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_initialize_failure(self, temp_config_file):
        """Test analyzer initialization failure"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        with patch.object(analyzer.exchange_manager, 'initialize_exchanges', return_value=False):
            result = await analyzer.initialize()
            assert result is False
    
    @pytest.mark.asyncio
    async def test_fetch_ohlc_data_cex_success(self, temp_config_file, sample_ohlcv_data):
        """Test successful OHLC data fetching from CEX"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        # Mock exchange
        mock_exchange = Mock()
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
        mock_exchange.fetch_ohlcv.return_value = ohlcv_data
        
        analyzer.exchange_manager.exchanges = {
            'binance': {'instance': mock_exchange}
        }
        analyzer.exchange_manager.get_exchange = Mock(return_value=mock_exchange)
        
        result = await analyzer.fetch_ohlc_data('binance', 'BTC/USDT', '1m', 100)
        
        assert result is not None
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_ohlcv_data)
        assert 'open' in result.columns
        assert 'high' in result.columns
        assert 'low' in result.columns
        assert 'close' in result.columns
        assert 'volume' in result.columns
    
    @pytest.mark.asyncio
    async def test_fetch_ohlc_data_exchange_not_found(self, temp_config_file):
        """Test OHLC data fetching with non-existent exchange"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        analyzer.exchange_manager.get_exchange = Mock(return_value=None)
        
        result = await analyzer.fetch_ohlc_data('nonexistent', 'BTC/USDT')
        assert result is None
    
    @pytest.mark.asyncio
    async def test_fetch_ohlc_data_dex_warning(self, temp_config_file):
        """Test OHLC data fetching from DEX (should show warning)"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        # Mock DEX connection
        mock_dex = {'w3': Mock(), 'account': Mock()}
        analyzer.exchange_manager.exchanges = {}
        analyzer.exchange_manager.dex_connections = {'uniswap_v3': mock_dex}
        analyzer.exchange_manager.get_exchange = Mock(return_value=mock_dex)
        
        result = await analyzer.fetch_ohlc_data('uniswap_v3', 'WETH/USDC')
        assert result is None
    
    @pytest.mark.asyncio
    async def test_fetch_ohlc_data_exception(self, temp_config_file):
        """Test OHLC data fetching with exception"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        mock_exchange = Mock()
        mock_exchange.fetch_ohlcv.side_effect = Exception("API Error")
        analyzer.exchange_manager.exchanges = {'binance': {'instance': mock_exchange}}
        analyzer.exchange_manager.get_exchange = Mock(return_value=mock_exchange)
        
        result = await analyzer.fetch_ohlc_data('binance', 'BTC/USDT')
        assert result is None
    
    def test_calculate_technical_indicators(self, temp_config_file, sample_ohlcv_data):
        """Test technical indicators calculation"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        # Prepare data
        df = sample_ohlcv_data.copy()
        df = df.set_index('timestamp')
        
        result = analyzer.calculate_technical_indicators(df)
        
        # Check that indicators were added
        expected_indicators = [
            'sma_20', 'ema_20', 'sma_50', 'rsi', 'macd', 'macd_signal', 
            'macd_histogram', 'bb_upper', 'bb_middle', 'bb_lower', 
            'volume_sma', 'atr'
        ]
        
        for indicator in expected_indicators:
            assert indicator in result.columns
        
        # Check that values are calculated (not all NaN)
        assert not result['sma_20'].isna().all()
        assert not result['rsi'].isna().all()
        assert not result['macd'].isna().all()
    
    def test_calculate_technical_indicators_exception(self, temp_config_file):
        """Test technical indicators calculation with exception"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        # Create invalid DataFrame
        df = pd.DataFrame({'invalid': [1, 2, 3]})
        
        result = analyzer.calculate_technical_indicators(df)
        
        # Should return original DataFrame on error
        assert 'invalid' in result.columns
        assert len(result) == 3
    
    def test_analyze_market_condition_success(self, temp_config_file, sample_ohlcv_data):
        """Test successful market condition analysis"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        # Prepare data with indicators
        df = sample_ohlcv_data.copy()
        df = df.set_index('timestamp')
        df = analyzer.calculate_technical_indicators(df)
        
        result = analyzer.analyze_market_condition(df, 'BTC/USDT')
        
        assert 'symbol' in result
        assert result['symbol'] == 'BTC/USDT'
        assert 'timestamp' in result
        assert 'price_data' in result
        assert 'technical_analysis' in result
        assert 'market_condition' in result
        
        # Check price data structure
        price_data = result['price_data']
        assert 'current_price' in price_data
        assert 'high_24h' in price_data
        assert 'low_24h' in price_data
        assert 'volume_24h' in price_data
        assert 'price_change_24h' in price_data
        assert 'volatility' in price_data
        
        # Check technical analysis structure
        tech_analysis = result['technical_analysis']
        assert 'trend' in tech_analysis
        assert 'momentum' in tech_analysis
        assert 'support_resistance' in tech_analysis
        assert 'rsi' in tech_analysis
        assert 'macd_signal' in tech_analysis
    
    def test_analyze_market_condition_empty_data(self, temp_config_file):
        """Test market condition analysis with empty data"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        result = analyzer.analyze_market_condition(None, 'BTC/USDT')
        assert 'error' in result
        
        empty_df = pd.DataFrame()
        result = analyzer.analyze_market_condition(empty_df, 'BTC/USDT')
        assert 'error' in result
    
    def test_analyze_trend_bullish(self, temp_config_file):
        """Test bullish trend analysis"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        # Create data with bullish trend
        df = pd.DataFrame({
            'close': [100, 101, 102, 103, 104],
            'sma_20': [99, 100, 101, 102, 103],
            'sma_50': [98, 99, 100, 101, 102]
        })
        
        result = analyzer._analyze_trend(df)
        assert result == "bullish"
    
    def test_analyze_trend_bearish(self, temp_config_file):
        """Test bearish trend analysis"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        # Create data with bearish trend
        df = pd.DataFrame({
            'close': [100, 99, 98, 97, 96],
            'sma_20': [101, 100, 99, 98, 97],
            'sma_50': [102, 101, 100, 99, 98]
        })
        
        result = analyzer._analyze_trend(df)
        assert result == "bearish"
    
    def test_analyze_trend_sideways(self, temp_config_file):
        """Test sideways trend analysis"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        # Create data with sideways trend
        df = pd.DataFrame({
            'close': [100, 100, 100, 100, 100],
            'sma_20': [100, 100, 100, 100, 100],
            'sma_50': [100, 100, 100, 100, 100]
        })
        
        result = analyzer._analyze_trend(df)
        assert result == "sideways"
    
    def test_analyze_trend_missing_data(self, temp_config_file):
        """Test trend analysis with missing data"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        # DataFrame without required columns
        df = pd.DataFrame({'close': [100, 101, 102]})
        
        result = analyzer._analyze_trend(df)
        assert result == "unknown"
    
    def test_analyze_momentum_overbought(self, temp_config_file):
        """Test overbought momentum analysis"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        df = pd.DataFrame({'rsi': [75, 80, 85, 90, 95]})
        
        result = analyzer._analyze_momentum(df)
        assert result == "overbought"
    
    def test_analyze_momentum_oversold(self, temp_config_file):
        """Test oversold momentum analysis"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        df = pd.DataFrame({'rsi': [25, 20, 15, 10, 5]})
        
        result = analyzer._analyze_momentum(df)
        assert result == "oversold"
    
    def test_analyze_momentum_neutral(self, temp_config_file):
        """Test neutral momentum analysis"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        df = pd.DataFrame({'rsi': [45, 50, 55, 60, 65]})
        
        result = analyzer._analyze_momentum(df)
        assert result == "neutral"
    
    def test_analyze_momentum_missing_data(self, temp_config_file):
        """Test momentum analysis with missing data"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        df = pd.DataFrame({'close': [100, 101, 102]})
        
        result = analyzer._analyze_momentum(df)
        assert result == "neutral"
    
    def test_find_support_resistance(self, temp_config_file):
        """Test support and resistance level finding"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        # Create data with clear support and resistance
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', periods=50, freq='1H')
        prices = np.random.uniform(95, 105, 50)
        
        df = pd.DataFrame({
            'high': prices + np.random.uniform(0, 2, 50),
            'low': prices - np.random.uniform(0, 2, 50),
            'close': prices
        }, index=dates)
        
        result = analyzer._find_support_resistance(df)
        
        assert 'resistance' in result
        assert 'support' in result
        assert isinstance(result['resistance'], list)
        assert isinstance(result['support'], list)
        assert len(result['resistance']) <= 3
        assert len(result['support']) <= 3
    
    def test_find_support_resistance_exception(self, temp_config_file):
        """Test support/resistance finding with exception"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        # Invalid DataFrame
        df = pd.DataFrame({'invalid': [1, 2, 3]})
        
        result = analyzer._find_support_resistance(df)
        
        assert result == {"resistance": [], "support": []}
    
    def test_determine_market_condition_high_volatility(self, temp_config_file):
        """Test high volatility market condition"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        result = analyzer._determine_market_condition(0.06, "bullish", "neutral")
        assert result == "high_volatility"
    
    def test_determine_market_condition_low_volatility(self, temp_config_file):
        """Test low volatility market condition"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        result = analyzer._determine_market_condition(0.005, "bullish", "neutral")
        assert result == "low_volatility"
    
    def test_determine_market_condition_bullish_momentum(self, temp_config_file):
        """Test bullish momentum market condition"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        result = analyzer._determine_market_condition(0.02, "bullish", "neutral")
        assert result == "bullish_momentum"
    
    def test_determine_market_condition_bearish_momentum(self, temp_config_file):
        """Test bearish momentum market condition"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        result = analyzer._determine_market_condition(0.02, "bearish", "overbought")
        assert result == "bearish_momentum"
    
    def test_determine_market_condition_sideways(self, temp_config_file):
        """Test sideways market condition"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        result = analyzer._determine_market_condition(0.02, "sideways", "neutral")
        assert result == "sideways"
    
    def test_generate_trading_config_success(self, temp_config_file, sample_market_analysis):
        """Test successful trading config generation"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        # Mock exchange config
        analyzer.exchange_manager.exchanges = {
            'binance': {
                'config': {
                    'min_order_amount': 10.0,
                    'max_order_amount': 1000.0,
                    'fee_rate': 0.001
                }
            }
        }
        
        result = analyzer.generate_trading_config(sample_market_analysis, 'binance')
        
        assert 'exchange' in result
        assert result['exchange'] == 'binance'
        assert 'symbol' in result
        assert 'strategy' in result
        assert 'market_condition' in result
        assert 'spreads' in result
        assert 'risk_management' in result
        assert 'order_settings' in result
        assert 'fees' in result
        
        # Check spreads structure
        spreads = result['spreads']
        assert 'bid_spread' in spreads
        assert 'ask_spread' in spreads
        assert 'minimum_spread' in spreads
        
        # Check risk management structure
        risk_mgmt = result['risk_management']
        assert 'stop_loss' in risk_mgmt
        assert 'take_profit' in risk_mgmt
        assert 'max_position_size' in risk_mgmt
        assert 'min_order_amount' in risk_mgmt
    
    def test_generate_trading_config_error(self, temp_config_file):
        """Test trading config generation with error in analysis"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        analysis_with_error = {"error": "No data available"}
        
        result = analyzer.generate_trading_config(analysis_with_error, 'binance')
        
        assert 'error' in result
        assert result['error'] == "No data available"
    
    def test_generate_trading_config_high_volatility(self, temp_config_file, sample_market_analysis):
        """Test trading config generation for high volatility market"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        # Modify analysis for high volatility
        sample_market_analysis['market_condition'] = 'high_volatility'
        sample_market_analysis['price_data']['volatility'] = 0.06
        
        analyzer.exchange_manager.exchanges = {
            'binance': {'config': {'min_order_amount': 10.0, 'max_order_amount': 1000.0, 'fee_rate': 0.001}}
        }
        
        result = analyzer.generate_trading_config(sample_market_analysis, 'binance')
        
        # High volatility should have wider spreads
        assert result['spreads']['bid_spread'] == 0.003
        assert result['spreads']['ask_spread'] == 0.004
        assert result['risk_management']['stop_loss'] == 0.02
    
    def test_generate_trading_config_low_volatility(self, temp_config_file, sample_market_analysis):
        """Test trading config generation for low volatility market"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        # Modify analysis for low volatility
        sample_market_analysis['market_condition'] = 'low_volatility'
        sample_market_analysis['price_data']['volatility'] = 0.005
        
        analyzer.exchange_manager.exchanges = {
            'binance': {'config': {'min_order_amount': 10.0, 'max_order_amount': 1000.0, 'fee_rate': 0.001}}
        }
        
        result = analyzer.generate_trading_config(sample_market_analysis, 'binance')
        
        # Low volatility should have tighter spreads
        assert result['spreads']['bid_spread'] == 0.001
        assert result['spreads']['ask_spread'] == 0.0015
        assert result['risk_management']['stop_loss'] == 0.01
    
    @pytest.mark.asyncio
    async def test_analyze_all_exchanges_success(self, temp_config_file, sample_ohlcv_data):
        """Test successful analysis of all exchanges"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        # Mock exchange manager
        analyzer.exchange_manager.get_enabled_exchanges = Mock(return_value=['binance'])
        analyzer.exchange_manager.get_trading_pairs = Mock(return_value=['BTC/USDT'])
        analyzer.exchange_manager.exchanges = {
            'binance': {'config': {'min_order_amount': 10.0, 'max_order_amount': 1000.0, 'fee_rate': 0.001}}
        }
        
        # Mock fetch_ohlc_data
        df = sample_ohlcv_data.copy().set_index('timestamp')
        df = analyzer.calculate_technical_indicators(df)
        
        with patch.object(analyzer, 'fetch_ohlc_data', return_value=df):
            result = await analyzer.analyze_all_exchanges('BTC/USDT')
        
        assert 'binance' in result
        assert 'analysis' in result['binance']
        assert 'config' in result['binance']
        assert 'data_points' in result['binance']
    
    @pytest.mark.asyncio
    async def test_analyze_all_exchanges_unsupported_symbol(self, temp_config_file):
        """Test analysis with unsupported symbol"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        analyzer.exchange_manager.get_enabled_exchanges = Mock(return_value=['binance'])
        analyzer.exchange_manager.get_trading_pairs = Mock(return_value=['ETH/USDT'])  # Different symbol
        
        result = await analyzer.analyze_all_exchanges('BTC/USDT')
        
        # Should skip exchange with unsupported symbol
        assert len(result) == 0 or 'binance' not in result
    
    @pytest.mark.asyncio
    async def test_analyze_all_exchanges_no_data(self, temp_config_file):
        """Test analysis when no OHLC data is available"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        analyzer.exchange_manager.get_enabled_exchanges = Mock(return_value=['binance'])
        analyzer.exchange_manager.get_trading_pairs = Mock(return_value=['BTC/USDT'])
        
        with patch.object(analyzer, 'fetch_ohlc_data', return_value=None):
            result = await analyzer.analyze_all_exchanges('BTC/USDT')
        
        # Should skip exchange with no data
        assert len(result) == 0 or 'binance' not in result
    
    @pytest.mark.asyncio
    async def test_analyze_all_exchanges_exception(self, temp_config_file):
        """Test analysis with exception"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        analyzer.exchange_manager.get_enabled_exchanges = Mock(return_value=['binance'])
        analyzer.exchange_manager.get_trading_pairs = Mock(side_effect=Exception("API Error"))
        
        result = await analyzer.analyze_all_exchanges('BTC/USDT')
        
        assert 'binance' in result
        assert 'error' in result['binance']
    
    def test_print_analysis_summary(self, temp_config_file, sample_market_analysis, capsys):
        """Test analysis summary printing"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        # Create mock results
        results = {
            'binance': {
                'analysis': sample_market_analysis,
                'config': {
                    'spreads': {'bid_spread': 0.002, 'ask_spread': 0.0025},
                    'risk_management': {'stop_loss': 0.015},
                    'fees': {'estimated_profit_margin': 0.0035}
                }
            },
            'gateio': {
                'error': 'Connection failed'
            }
        }
        
        analyzer.print_analysis_summary(results)
        
        captured = capsys.readouterr()
        assert 'สรุปผลการวิเคราะห์ตลาดจากหลาย Exchange' in captured.out
        assert 'BINANCE' in captured.out
        assert 'GATEIO' in captured.out
        assert 'Connection failed' in captured.out
    
    @pytest.mark.asyncio
    async def test_run_continuous_analysis(self, temp_config_file):
        """Test continuous analysis (short run)"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        # Mock methods
        analyzer.analyze_all_exchanges = AsyncMock(return_value={'binance': {'analysis': {}, 'config': {}}})
        analyzer.print_analysis_summary = Mock()
        
        # Run for a very short time
        async def short_run():
            await asyncio.sleep(0.1)  # Run for 0.1 seconds
            raise KeyboardInterrupt()
        
        with patch('asyncio.sleep', side_effect=short_run):
            await analyzer.run_continuous_analysis('BTC/USDT', 1)
        
        # Verify methods were called
        analyzer.analyze_all_exchanges.assert_called()
        analyzer.print_analysis_summary.assert_called()


class TestRunMarketAnalysis:
    """Test cases for run_market_analysis function"""
    
    @pytest.mark.asyncio
    async def test_run_market_analysis_success(self, temp_config_file, sample_ohlcv_data):
        """Test successful market analysis run"""
        with patch('bots.market_analyzer.MultiExchangeMarketAnalyzer') as mock_analyzer_class:
            mock_analyzer = Mock()
            mock_analyzer.initialize = AsyncMock(return_value=True)
            mock_analyzer.analyze_all_exchanges = AsyncMock(return_value={'binance': {'analysis': {}, 'config': {}}})
            mock_analyzer.print_analysis_summary = Mock()
            mock_analyzer_class.return_value = mock_analyzer
            
            result = await run_market_analysis()
            
            assert result is not None
            mock_analyzer.initialize.assert_called_once()
            mock_analyzer.analyze_all_exchanges.assert_called_once_with('BTC/USDT')
            mock_analyzer.print_analysis_summary.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_market_analysis_initialization_failure(self):
        """Test market analysis run with initialization failure"""
        with patch('bots.market_analyzer.MultiExchangeMarketAnalyzer') as mock_analyzer_class:
            mock_analyzer = Mock()
            mock_analyzer.initialize = AsyncMock(return_value=False)
            mock_analyzer_class.return_value = mock_analyzer
            
            result = await run_market_analysis()
            
            assert result is None
            mock_analyzer.initialize.assert_called_once()
            mock_analyzer.analyze_all_exchanges.assert_not_called()


class TestMarketAnalyzerIntegration:
    """Integration tests for MarketAnalyzer"""
    
    @pytest.mark.asyncio
    async def test_full_analysis_workflow(self, temp_config_file, sample_ohlcv_data):
        """Test complete analysis workflow"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        # Mock exchange manager
        mock_exchange = Mock()
        ohlcv_data = []
        for _, row in sample_ohlcv_data.iterrows():
            ohlcv_data.append([
                int(row['timestamp'].timestamp() * 1000),
                row['open'], row['high'], row['low'], row['close'], row['volume']
            ])
        mock_exchange.fetch_ohlcv.return_value = ohlcv_data
        
        analyzer.exchange_manager.exchanges = {
            'binance': {
                'instance': mock_exchange,
                'config': {'min_order_amount': 10.0, 'max_order_amount': 1000.0, 'fee_rate': 0.001}
            }
        }
        analyzer.exchange_manager.get_exchange = Mock(return_value=mock_exchange)
        analyzer.exchange_manager.get_enabled_exchanges = Mock(return_value=['binance'])
        analyzer.exchange_manager.get_trading_pairs = Mock(return_value=['BTC/USDT'])
        
        # Test complete workflow
        # 1. Fetch OHLC data
        df = await analyzer.fetch_ohlc_data('binance', 'BTC/USDT')
        assert df is not None
        
        # 2. Calculate technical indicators
        df_with_indicators = analyzer.calculate_technical_indicators(df)
        assert 'sma_20' in df_with_indicators.columns
        assert 'rsi' in df_with_indicators.columns
        
        # 3. Analyze market condition
        analysis = analyzer.analyze_market_condition(df_with_indicators, 'BTC/USDT')
        assert 'market_condition' in analysis
        
        # 4. Generate trading config
        config = analyzer.generate_trading_config(analysis, 'binance')
        assert 'spreads' in config
        assert 'risk_management' in config
        
        # 5. Analyze all exchanges
        results = await analyzer.analyze_all_exchanges('BTC/USDT')
        assert 'binance' in results
        assert 'analysis' in results['binance']
        assert 'config' in results['binance']
    
    def test_error_handling_workflow(self, temp_config_file):
        """Test error handling in various scenarios"""
        analyzer = MultiExchangeMarketAnalyzer(temp_config_file)
        
        # Test with invalid data
        invalid_df = pd.DataFrame({'invalid': [1, 2, 3]})
        
        # Should handle errors gracefully
        analysis = analyzer.analyze_market_condition(invalid_df, 'BTC/USDT')
        assert 'error' in analysis
        
        config = analyzer.generate_trading_config(analysis, 'binance')
        assert 'error' in config
        
        # Test trend analysis with missing columns
        trend = analyzer._analyze_trend(invalid_df)
        assert trend == "unknown"
        
        # Test momentum analysis with missing columns
        momentum = analyzer._analyze_momentum(invalid_df)
        assert momentum == "neutral" 