"""
Trading strategies for the multi-exchange trading bot.

This module contains various trading strategies:
- MACDBot: MACD-based trading strategy
- MultiExchangeTradingBot: Cross-exchange arbitrage strategy
"""

from .macd_bot import MACDBot
from .multi_exchange_bot import MultiExchangeTradingBot

__all__ = [
    'MACDBot',
    'MultiExchangeTradingBot',
] 