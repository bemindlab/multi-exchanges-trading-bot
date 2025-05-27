"""
Trading Bots
===========

Collection of trading bots for Gate.io
"""

from .macd_bot import MACDBot, load_config
from .market_analyzer import run_market_analysis

__all__ = ["MACDBot", "load_config", "run_market_analysis"] 