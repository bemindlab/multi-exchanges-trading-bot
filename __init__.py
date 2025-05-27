"""
Gate.io Trading Bot
==================

A trading bot for Gate.io with MACD strategy.
"""

from .bots import MACDBot, load_config
from .cli import main

__version__ = "0.1.0"
__all__ = ["MACDBot", "load_config", "main"] 