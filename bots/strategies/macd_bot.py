import gate_api
import os
import time
import json
from datetime import datetime
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MACDBot:
    def __init__(self, config):
        self.config = config
        self.setup_api()
        
    def setup_api(self):
        """Setup Gate.io API"""
        configuration = gate_api.Configuration(
            key=os.getenv('GATE_API_KEY'),
            secret=os.getenv('GATE_API_SECRET')
        )
        self.spot_api = gate_api.SpotApi(gate_api.ApiClient(configuration))

    def get_klines(self, pair, timeframe, limit=100):
        """Get klines (candlestick) data from Gate.io"""
        try:
            klines = self.spot_api.list_candlesticks(
                currency_pair=pair,
                interval=timeframe,
                limit=limit
            )
            return pd.DataFrame(klines, columns=['timestamp', 'volume', 'close', 'high', 'low', 'open'])
        except Exception as e:
            print(f"Error getting klines: {str(e)}")
            return None

    def calculate_macd(self, df):
        """Calculate MACD indicator"""
        # Calculate EMA
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        
        # Calculate MACD line
        macd = exp1 - exp2
        
        # Calculate Signal line
        signal = macd.ewm(span=9, adjust=False).mean()
        
        # Calculate MACD histogram
        hist = macd - signal
        
        return macd, signal, hist

    def check_macd_signal(self, pair, timeframe):
        """Check MACD trading signals"""
        # Get klines data
        df = self.get_klines(pair, timeframe)
        if df is None:
            return None

        # Calculate MACD
        macd, signal, hist = self.calculate_macd(df)

        # Get latest values
        current_macd = macd.iloc[-1]
        current_signal = signal.iloc[-1]
        current_hist = hist.iloc[-1]
        prev_hist = hist.iloc[-2]

        # Check for buy signal (MACD crosses above signal line)
        if prev_hist < 0 and current_hist > 0:
            return 'buy'
        
        # Check for sell signal (MACD crosses below signal line)
        elif prev_hist > 0 and current_hist < 0:
            return 'sell'
        
        return None

    def execute_trade(self, action, pair, amount):
        """Execute trade on Gate.io"""
        try:
            # Market order ไม่ต้องการ time_in_force
            order = gate_api.Order(
                currency_pair=pair,
                side=action,
                amount=str(amount),
                type="market",
                account="spot"
            )
            result = self.spot_api.create_order(order)
            
            trade_result = {
                'status': 'success',
                'action': action,
                'pair': pair,
                'amount': amount,
                'timestamp': datetime.now().isoformat(),
                'order_id': result.id
            }
            
            # Save trade log
            self.save_trade_log(trade_result)
            return trade_result
            
        except Exception as e:
            print(f"Error executing trade: {str(e)}")
            return None

    def save_trade_log(self, trade_result):
        """Save trade result to log file"""
        # สร้างโฟลเดอร์ temp ถ้ายังไม่มี
        os.makedirs('temp', exist_ok=True)
        log_file = 'temp/macd_trades.log'
        with open(log_file, 'a') as f:
            f.write(json.dumps(trade_result) + '\n')

    def run(self):
        """Run MACD trading bot"""
        print("Starting MACD trading bot...")
        print(f"Trading pairs: {self.config['trading_pairs']}")
        print(f"Timeframe: {self.config['timeframe']}")
        print(f"Amount: {self.config['amount']} USDT")
        print(f"Check interval: {self.config['check_interval']} seconds")

        while True:
            try:
                for pair in self.config['trading_pairs']:
                    # Check MACD signals
                    signal = self.check_macd_signal(pair, self.config['timeframe'])
                    
                    if signal:
                        print(f"MACD signal detected for {pair}: {signal}")
                        # Execute trade
                        result = self.execute_trade(
                            action=signal,
                            pair=pair,
                            amount=self.config['amount']
                        )
                        if result:
                            print(f"Trade executed: {result}")

                # Wait for next check
                time.sleep(self.config['check_interval'])

            except Exception as e:
                print(f"Error in trading loop: {str(e)}")
                time.sleep(10)  # Wait before retrying

def load_config():
    """Load trading configuration from config.json"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'trading_pairs': ['BTC_USDT'],
            'timeframe': '1h',
            'amount': 50,
            'check_interval': 60  # seconds
        } 