"""Performance tests for order processing.

Tests to ensure order processing meets performance requirements.
"""

import time
import pytest
from unittest.mock import Mock, patch
import asyncio
from concurrent.futures import ThreadPoolExecutor

from src.core.exchange_manager import ExchangeManager
from src.strategies.multi_exchange_bot import MultiExchangeBot


class TestOrderProcessingPerformance:
    """Performance tests for order processing operations."""
    
    @pytest.mark.performance
    def test_single_order_processing_time(self, mock_exchange):
        """Test that single order processing completes within acceptable time."""
        # Arrange
        exchange_manager = ExchangeManager()
        exchange_manager.exchange = mock_exchange
        
        order_data = {
            'symbol': 'BTC/USDT',
            'type': 'limit',
            'side': 'buy',
            'amount': 0.1,
            'price': 50000
        }
        
        # Act
        start_time = time.time()
        result = exchange_manager.create_order(**order_data)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Assert
        assert result is not None
        assert processing_time < 0.1, f"Order processing took {processing_time:.3f}s, expected < 0.1s"
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_order_processing(self, mock_exchange):
        """Test concurrent order processing performance."""
        # Arrange
        exchange_manager = ExchangeManager()
        exchange_manager.exchange = mock_exchange
        num_orders = 100
        
        async def create_order(i):
            """Create a single order."""
            return await asyncio.to_thread(
                exchange_manager.create_order,
                symbol='BTC/USDT',
                type='limit',
                side='buy' if i % 2 == 0 else 'sell',
                amount=0.01,
                price=50000 + i
            )
        
        # Act
        start_time = time.time()
        tasks = [create_order(i) for i in range(num_orders)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        processing_time = end_time - start_time
        throughput = num_orders / processing_time
        
        # Assert
        assert len(results) == num_orders
        assert all(r is not None for r in results)
        assert throughput > 50, f"Throughput {throughput:.1f} orders/s, expected > 50"
        
    @pytest.mark.performance
    def test_order_book_update_performance(self, mock_exchange):
        """Test order book update processing performance."""
        # Arrange
        market_analyzer = Mock()
        num_updates = 1000
        
        order_book = {
            'bids': [[50000 - i, 0.1] for i in range(50)],
            'asks': [[50000 + i, 0.1] for i in range(50)]
        }
        
        # Act
        start_time = time.time()
        for _ in range(num_updates):
            market_analyzer.process_order_book(order_book)
        end_time = time.time()
        
        processing_time = end_time - start_time
        updates_per_second = num_updates / processing_time
        
        # Assert
        assert updates_per_second > 1000, f"Processing {updates_per_second:.0f} updates/s, expected > 1000"
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_sustained_load_performance(self, mock_exchange):
        """Test system performance under sustained load."""
        # Arrange
        bot = MultiExchangeBot(config={'exchanges': {'mock': mock_exchange}})
        duration_seconds = 10
        orders_per_second = 10
        
        results = []
        errors = []
        
        # Act
        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            try:
                order = bot.create_order('mock', 'BTC/USDT', 'limit', 'buy', 0.01, 50000)
                results.append(order)
                time.sleep(1 / orders_per_second)
            except Exception as e:
                errors.append(e)
        
        # Assert
        total_orders = len(results)
        error_rate = len(errors) / (len(results) + len(errors)) if results or errors else 0
        
        assert total_orders >= duration_seconds * orders_per_second * 0.9, "Failed to maintain target throughput"
        assert error_rate < 0.01, f"Error rate {error_rate:.2%}, expected < 1%"
    
    @pytest.mark.performance
    def test_memory_usage_under_load(self, mock_exchange):
        """Test memory usage doesn't grow excessively under load."""
        import psutil
        import gc
        
        # Arrange
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        bot = MultiExchangeBot(config={'exchanges': {'mock': mock_exchange}})
        num_iterations = 1000
        
        # Act
        for i in range(num_iterations):
            # Simulate order creation and cleanup
            order = bot.create_order('mock', f'TOKEN{i}/USDT', 'limit', 'buy', 0.01, 100)
            if i % 100 == 0:
                gc.collect()  # Force garbage collection periodically
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory
        
        # Assert
        assert memory_growth < 50, f"Memory grew by {memory_growth:.1f}MB, expected < 50MB"
    
    @pytest.fixture
    def mock_exchange(self):
        """Mock exchange for performance testing."""
        exchange = Mock()
        exchange.create_order = Mock(return_value={'id': 'test_order', 'status': 'open'})
        exchange.fetch_order_book = Mock(return_value={
            'bids': [[50000, 1.0]],
            'asks': [[50001, 1.0]]
        })
        return exchange 