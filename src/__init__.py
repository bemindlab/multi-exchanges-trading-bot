"""
Trading Bots
===========

Collection of trading bots for multiple exchanges including Hummingbot integration
"""

# Core components
from .core.exchange_manager import ExchangeManager
from .core.market_analyzer import MarketAnalyzer, run_market_analysis
from .core.risk_manager import RiskManager

# Strategies
from .strategies.macd_bot import MACDBot, load_config
from .strategies.multi_exchange_bot import MultiExchangeTradingBot, run_multi_exchange_bot

# Managers
from .managers.hummingbot_manager import HummingbotMQTTManager, run_hummingbot_manager

# Utils
from .utils.crypto_scanner import CryptoScanner
from .utils.monitor import Monitor

# Examples
from .examples.mqtt_client_example import HummingbotMQTTClient

__all__ = [
    # Core
    "ExchangeManager",
    "MarketAnalyzer", 
    "run_market_analysis",
    "RiskManager",
    
    # Strategies
    "MACDBot", 
    "load_config", 
    "MultiExchangeTradingBot",
    "run_multi_exchange_bot",
    
    # Managers
    "HummingbotMQTTManager",
    "run_hummingbot_manager",
    
    # Utils
    "CryptoScanner",
    "Monitor",
    
    # Examples
    "HummingbotMQTTClient"
] 