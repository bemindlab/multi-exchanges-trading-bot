from flask import Flask, request, jsonify
import gate_api
from dotenv import load_dotenv
import os
import argparse
import json
from macd_bot import MACDBot, load_config
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from bots.risk_manager import RiskManager
from config_manager import ConfigManager, ensure_config_exists

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Available trading pairs
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

# Available timeframes
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

def validate_trade_params(currency_pair, amount, timeframe):
    """Validate trading parameters"""
    if currency_pair not in AVAILABLE_PAIRS:
        return False, f'Invalid currency pair. Available pairs: {list(AVAILABLE_PAIRS.keys())}'
    
    if timeframe not in AVAILABLE_TIMEFRAMES:
        return False, f'Invalid timeframe. Available timeframes: {list(AVAILABLE_TIMEFRAMES.keys())}'
    
    try:
        amount = float(amount)
    except ValueError:
        return False, 'Invalid amount format. Please provide a valid number.'
    
    return True, None

def save_config(config):
    """Save configuration to config.json"""
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

def setup_logging():
    # สร้างโฟลเดอร์ temp ถ้ายังไม่มี
    if not os.path.exists('temp'):
        os.makedirs('temp')
    
    # ตั้งค่า logging
    log_file = f'temp/gate_bot_{datetime.now().strftime("%Y%m%d")}.log'
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # ตั้งค่า file handler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # ตั้งค่า console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # ตั้งค่า root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def main():
    parser = argparse.ArgumentParser(description='Gate.io Trading Bot')
    parser.add_argument('--mode', choices=['manual', 'macd', 'webhook'], required=True,
                      help='Trading mode: manual (single trade), macd (MACD strategy), webhook (TradingView webhook)')
    
    # Manual trading parameters
    parser.add_argument('--action', choices=['buy', 'sell'], help='Trading action (buy/sell) for manual mode')
    parser.add_argument('--pair', help='Currency pair (e.g., BTC_USDT)')
    parser.add_argument('--amount', help='Trade amount in USDT')
    parser.add_argument('--timeframe', default='1h', help='Trading timeframe')
    
    # MACD bot parameters
    parser.add_argument('--pairs', nargs='+', help='List of trading pairs for MACD bot')
    parser.add_argument('--interval', type=int, help='Check interval in seconds for MACD bot')
    parser.add_argument('--trade-amount', type=float, help='Trade amount in USDT for MACD bot')
    
    # เพิ่ม argument สำหรับ risk management
    parser.add_argument('--max-daily-loss', type=float, default=100,
                      help='Maximum daily loss in USDT')
    parser.add_argument('--max-position-size', type=float, default=1000,
                      help='Maximum position size in USDT')
    
    # Config management
    parser.add_argument('--config', default='config.json', help='Config file path')
    parser.add_argument('--create-config', action='store_true', help='Create config from template')
    
    args = parser.parse_args()
    
    # ตรวจสอบและสร้าง config ถ้าจำเป็น
    if args.create_config:
        config_manager = ConfigManager(args.config)
        config_manager.create_config_from_template(force=True)
        return
    
    # ตรวจสอบว่ามี config file หรือไม่
    if not ensure_config_exists(args.config):
        print("❌ ไม่สามารถสร้างไฟล์ config ได้")
        print("💡 ลองใช้: python main.py --create-config")
        return

    # สร้าง Risk Manager
    risk_manager = RiskManager(
        max_daily_loss=args.max_daily_loss,
        max_position_size=args.max_position_size
    )

    if args.mode == 'webhook':
        app.run(port=5000)
    elif args.mode == 'macd':
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
        save_config(config)
        
        # Start MACD bot
        bot = MACDBot(config)
        bot.run()
        
        for pair in args.pairs:
            # ตรวจสอบความเสี่ยงก่อนเทรด
            if not risk_manager.can_open_position(pair, float(args.trade_amount), current_price):
                logger.warning(f"Trade rejected for {pair} by risk manager")
                continue
            
            # ทำการเทรด
            # ... existing code ...
            
            # บันทึกการเทรด
            risk_manager.add_trade(pair, float(args.trade_amount), current_price, action)
        
        # แสดงเมตริกความเสี่ยง
        risk_metrics = risk_manager.get_risk_metrics()
        logger.info(f"Risk metrics: {risk_metrics}")
        
        # ล้างประวัติการเทรดเก่า
        risk_manager.cleanup_old_trades()
    else:  # manual mode
        if not all([args.action, args.pair, args.amount]):
            print("Error: --action, --pair, and --amount are required for manual trading")
            return

        # Validate parameters
        is_valid, error_message = validate_trade_params(args.pair, args.amount, args.timeframe)
        if not is_valid:
            print(f'Error: {error_message}')
            return

        # ตรวจสอบความเสี่ยงก่อนเทรด
        if not risk_manager.can_open_position(args.pair, float(args.amount), current_price):
            logger.error("Trade rejected by risk manager")
            return

        # Execute trade
        configuration = gate_api.Configuration(
            key=os.getenv('GATE_API_KEY'),
            secret=os.getenv('GATE_API_SECRET')
        )
        spot_api = gate_api.SpotApi(gate_api.ApiClient(configuration))
        
        order = gate_api.Order(
            currency_pair=args.pair,
            side=args.action,
            amount=str(args.amount),
            type="market",
            account="spot"
        )
        result = spot_api.create_order(order)
        print(f"Trade executed: {result}")
        
        # บันทึกการเทรด
        risk_manager.add_trade(args.pair, float(args.amount), current_price, args.action)

if __name__ == "__main__":
    logger = setup_logging()
    logger.info("Starting Gate.io Trading Bot")
    
    try:
        main()
        logger.info("Trading completed successfully")
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}", exc_info=True)
        raise