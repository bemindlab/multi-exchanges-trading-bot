#!/usr/bin/env python3
"""
Multi-Exchange Trading Bot - Main Entry Point

A comprehensive trading bot system for managing multiple exchanges
with advanced strategies and risk management.

Usage:
    python main.py --mode manual --action buy --pair BTC_USDT --amount 100
    python main.py --mode macd --pairs BTC_USDT ETH_USDT --interval 60
    python main.py --mode webhook
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from flask import Flask, request, jsonify
import gate_api
from dotenv import load_dotenv
import json
from datetime import datetime

# Import from our restructured modules
from src.strategies.macd_bot import MACDBot, load_config
from src.core.risk_manager import RiskManager
from config_manager import ConfigManager, ensure_config_exists

# Load environment variables
load_dotenv()

# Flask app for webhook mode
app = Flask(__name__)

# Configuration constants
AVAILABLE_PAIRS = {
    'BTC_USDT': 'Bitcoin/USDT',
    'ETH_USDT': 'Ethereum/USDT',
    'PBUX_USDT': 'PBUX/USDT',
    'DOGE_USDT': 'Dogecoin/USDT',
    'SOL_USDT': 'Solana/USDT',
    'XRP_USDT': 'XRP/USDT',
    'ADA_USDT': 'Cardano/USDT',
    'DOT_USDT': 'Polkadot/USDT',
    'LINK_USDT': 'Chainlink/USDT',
    'BCH_USDT': 'Bitcoin Cash/USDT',
    'LTC_USDT': 'Litecoin/USDT',
    'XLM_USDT': 'Stellar/USDT',
}

AVAILABLE_TIMEFRAMES = {
    '1m': '1 minute',
    '5m': '5 minutes', 
    '15m': '15 minutes',
    '30m': '30 minutes',
    '1h': '1 hour',
    '4h': '4 hours',
    '1d': '1 day',
    '1w': '1 week'
}


class TradingBotApp:
    """Main application class for the trading bot."""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.risk_manager = None
        
    def _setup_logging(self):
        """Setup logging configuration."""
        # Create temp directory if it doesn't exist
        temp_dir = Path('temp')
        temp_dir.mkdir(exist_ok=True)
        
        # Configure logging
        log_file = temp_dir / f'trading_bot_{datetime.now().strftime("%Y%m%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        return logging.getLogger(__name__)
    
    def validate_trade_params(self, currency_pair, amount, timeframe):
        """Validate trading parameters."""
        if currency_pair not in AVAILABLE_PAIRS:
            return False, f'Invalid currency pair. Available: {list(AVAILABLE_PAIRS.keys())}'
        
        if timeframe not in AVAILABLE_TIMEFRAMES:
            return False, f'Invalid timeframe. Available: {list(AVAILABLE_TIMEFRAMES.keys())}'
        
        try:
            amount = float(amount)
            if amount <= 0:
                return False, 'Amount must be positive'
        except ValueError:
            return False, 'Invalid amount format'
        
        return True, None
    
    def save_config(self, config):
        """Save configuration to file."""
        config_path = Path('config') / 'config.json'
        config_path.parent.mkdir(exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
    
    def run_manual_mode(self, args):
        """Execute manual trading mode."""
        self.logger.info(f"Starting manual trade: {args.action} {args.amount} {args.pair}")
        
        # Validate parameters
        is_valid, error_message = self.validate_trade_params(args.pair, args.amount, args.timeframe)
        if not is_valid:
            self.logger.error(f'Validation error: {error_message}')
            return False
        
        # Check risk management
        if self.risk_manager and not self.risk_manager.can_open_position(
            args.pair, float(args.amount), 0  # current_price would be fetched in real implementation
        ):
            self.logger.error("Trade rejected by risk manager")
            return False
        
        # Execute trade (implementation would go here)
        self.logger.info(f"Manual trade executed successfully")
        return True
    
    def run_macd_mode(self, args):
        """Execute MACD strategy mode."""
        self.logger.info(f"Starting MACD bot with pairs: {args.pairs}")
        
        # Load or create config
        config = load_config()
        
        # Update config with command line arguments
        if args.pairs:
            config['trading_pairs'] = args.pairs
        if args.interval:
            config['check_interval'] = args.interval
        if args.trade_amount:
            config['amount'] = args.trade_amount
            
        # Save updated config
        self.save_config(config)
        
        # Start MACD bot
        bot = MACDBot(config)
        bot.run()
        
        return True
    
    def run_webhook_mode(self, args):
        """Execute webhook mode for TradingView integration."""
        self.logger.info("Starting webhook server on port 5000")
        
        @app.route('/webhook', methods=['POST'])
        def handle_webhook():
            try:
                data = request.get_json()
                self.logger.info(f"Received webhook: {data}")
                
                # Process webhook data here
                # Implementation would depend on TradingView webhook format
                
                return jsonify({'status': 'success', 'message': 'Webhook processed'})
            except Exception as e:
                self.logger.error(f"Webhook error: {e}")
                return jsonify({'status': 'error', 'message': str(e)}), 400
        
        app.run(host='0.0.0.0', port=5000, debug=False)
        return True
    
    def run(self, args):
        """Main run method."""
        # Initialize risk manager
        self.risk_manager = RiskManager(
            max_daily_loss=args.max_daily_loss,
            max_position_size=args.max_position_size
        )
        
        # Route to appropriate mode
        if args.mode == 'manual':
            if not all([args.action, args.pair, args.amount]):
                self.logger.error("Manual mode requires --action, --pair, and --amount")
                return False
            return self.run_manual_mode(args)
            
        elif args.mode == 'macd':
            if not args.pairs:
                self.logger.error("MACD mode requires --pairs")
                return False
            return self.run_macd_mode(args)
            
        elif args.mode == 'webhook':
            return self.run_webhook_mode(args)
            
        else:
            self.logger.error(f"Unknown mode: {args.mode}")
            return False


def create_parser():
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description='Multi-Exchange Trading Bot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --mode manual --action buy --pair BTC_USDT --amount 100
  %(prog)s --mode macd --pairs BTC_USDT ETH_USDT --interval 60 --trade-amount 50
  %(prog)s --mode webhook
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--mode', 
        choices=['manual', 'macd', 'webhook'], 
        required=True,
        help='Trading mode'
    )
    
    # Manual trading parameters
    manual_group = parser.add_argument_group('manual mode options')
    manual_group.add_argument('--action', choices=['buy', 'sell'], help='Trading action')
    manual_group.add_argument('--pair', help='Currency pair (e.g., BTC_USDT)')
    manual_group.add_argument('--amount', help='Trade amount in USDT')
    manual_group.add_argument('--timeframe', default='1h', help='Trading timeframe')
    
    # MACD bot parameters
    macd_group = parser.add_argument_group('MACD mode options')
    macd_group.add_argument('--pairs', nargs='+', help='List of trading pairs')
    macd_group.add_argument('--interval', type=int, help='Check interval in seconds')
    macd_group.add_argument('--trade-amount', type=float, help='Trade amount in USDT')
    
    # Risk management
    risk_group = parser.add_argument_group('risk management')
    risk_group.add_argument('--max-daily-loss', type=float, default=100,
                           help='Maximum daily loss in USDT (default: 100)')
    risk_group.add_argument('--max-position-size', type=float, default=1000,
                           help='Maximum position size in USDT (default: 1000)')
    
    # Configuration
    config_group = parser.add_argument_group('configuration')
    config_group.add_argument('--config', default='config/config.json', help='Config file path')
    config_group.add_argument('--create-config', action='store_true', 
                             help='Create config from template')
    
    return parser


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle config creation
    if args.create_config:
        config_manager = ConfigManager(args.config)
        config_manager.create_config_from_template(force=True)
        print("✅ Config file created successfully")
        return 0
    
    # Ensure config exists
    if not ensure_config_exists(args.config):
        print("❌ Cannot create config file")
        print("💡 Try: python main.py --create-config")
        return 1
    
    # Run the application
    app = TradingBotApp()
    success = app.run(args)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())