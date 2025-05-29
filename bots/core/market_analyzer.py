import asyncio
import pandas as pd
from datetime import datetime
import time
import logging
from typing import Dict, List, Optional
import ta
from .exchange_manager import ExchangeManager

class MultiExchangeMarketAnalyzer:
    """วิเคราะห์ตลาดจากหลาย Exchange พร้อมกับสร้างคำแนะนำ config"""
    
    def __init__(self, config_path: str = "config.json"):
        self.exchange_manager = ExchangeManager(config_path)
        self.logger = self._setup_logger()
        self.analysis_results = {}
        
    def _setup_logger(self) -> logging.Logger:
        """ตั้งค่า logger"""
        logger = logging.getLogger('MarketAnalyzer')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def initialize(self) -> bool:
        """เริ่มต้นการเชื่อมต่อกับ exchanges"""
        return self.exchange_manager.initialize_exchanges()
    
    async def fetch_ohlc_data(self, exchange_name: str, symbol: str, 
                             timeframe: str = "1m", limit: int = 100) -> Optional[pd.DataFrame]:
        """ดึงข้อมูล OHLC จาก exchange"""
        try:
            exchange = self.exchange_manager.get_exchange(exchange_name)
            if not exchange:
                self.logger.error(f"❌ ไม่พบ exchange: {exchange_name}")
                return None
            
            # สำหรับ CEX
            if exchange_name in self.exchange_manager.exchanges:
                ohlc_data = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                
                df = pd.DataFrame(ohlc_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df = df.set_index('timestamp')
                
                return df.sort_index()
            
            # สำหรับ DEX (ต้องการการพัฒนาเพิ่มเติม)
            else:
                self.logger.warning(f"⚠️ การดึงข้อมูล OHLC จาก DEX {exchange_name} ยังไม่รองรับ")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถดึงข้อมูล OHLC จาก {exchange_name}: {e}")
            return None
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """คำนวณ technical indicators"""
        try:
            # Moving Averages
            df['sma_20'] = ta.trend.sma_indicator(df['close'], window=20)
            df['ema_20'] = ta.trend.ema_indicator(df['close'], window=20)
            df['sma_50'] = ta.trend.sma_indicator(df['close'], window=50)
            
            # RSI
            df['rsi'] = ta.momentum.rsi(df['close'], window=14)
            
            # MACD
            macd = ta.trend.MACD(df['close'])
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            df['macd_histogram'] = macd.macd_diff()
            
            # Bollinger Bands
            bollinger = ta.volatility.BollingerBands(df['close'])
            df['bb_upper'] = bollinger.bollinger_hband()
            df['bb_middle'] = bollinger.bollinger_mavg()
            df['bb_lower'] = bollinger.bollinger_lband()
            
            # Volume indicators
            df['volume_sma'] = ta.volume.volume_sma(df['close'], df['volume'], window=20)
            
            # Volatility
            df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'])
            
            return df
            
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถคำนวณ technical indicators: {e}")
            return df
    
    def analyze_market_condition(self, df: pd.DataFrame, symbol: str) -> Dict:
        """วิเคราะห์สภาพตลาด"""
        if df is None or df.empty:
            return {"error": "ไม่มีข้อมูลสำหรับการวิเคราะห์"}
        
        latest = df.iloc[-1]
        
        # ข้อมูลพื้นฐาน
        current_price = latest['close']
        high_24h = df['high'].tail(24).max() if len(df) >= 24 else df['high'].max()
        low_24h = df['low'].tail(24).min() if len(df) >= 24 else df['low'].min()
        volume_24h = df['volume'].tail(24).sum() if len(df) >= 24 else df['volume'].sum()
        
        # คำนวณความผันผวน
        volatility = (high_24h - low_24h) / low_24h
        price_change_24h = (current_price - df['close'].iloc[-24]) / df['close'].iloc[-24] if len(df) >= 24 else 0
        
        # วิเคราะห์เทรนด์
        trend_signal = self._analyze_trend(df)
        
        # วิเคราะห์ momentum
        momentum_signal = self._analyze_momentum(df)
        
        # วิเคราะห์ support/resistance
        support_resistance = self._find_support_resistance(df)
        
        analysis = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "price_data": {
                "current_price": current_price,
                "high_24h": high_24h,
                "low_24h": low_24h,
                "volume_24h": volume_24h,
                "price_change_24h": price_change_24h,
                "volatility": volatility
            },
            "technical_analysis": {
                "trend": trend_signal,
                "momentum": momentum_signal,
                "support_resistance": support_resistance,
                "rsi": latest.get('rsi', 0),
                "macd_signal": latest.get('macd', 0) > latest.get('macd_signal', 0)
            },
            "market_condition": self._determine_market_condition(volatility, trend_signal, momentum_signal)
        }
        
        return analysis
    
    def _analyze_trend(self, df: pd.DataFrame) -> str:
        """วิเคราะห์เทรนด์"""
        latest = df.iloc[-1]
        
        if 'sma_20' not in df.columns or 'sma_50' not in df.columns:
            return "unknown"
        
        price = latest['close']
        sma_20 = latest['sma_20']
        sma_50 = latest['sma_50']
        
        if pd.isna(sma_20) or pd.isna(sma_50):
            return "unknown"
        
        if price > sma_20 > sma_50:
            return "bullish"
        elif price < sma_20 < sma_50:
            return "bearish"
        else:
            return "sideways"
    
    def _analyze_momentum(self, df: pd.DataFrame) -> str:
        """วิเคราะห์ momentum"""
        latest = df.iloc[-1]
        
        if 'rsi' not in df.columns:
            return "neutral"
        
        rsi = latest['rsi']
        
        if pd.isna(rsi):
            return "neutral"
        
        if rsi > 70:
            return "overbought"
        elif rsi < 30:
            return "oversold"
        else:
            return "neutral"
    
    def _find_support_resistance(self, df: pd.DataFrame) -> Dict:
        """หา support และ resistance levels"""
        try:
            # ใช้ pivot points แบบง่าย
            recent_data = df.tail(50)  # ดูข้อมูล 50 periods ล่าสุด
            
            # หา local highs และ lows
            highs = recent_data['high'].rolling(window=5, center=True).max()
            lows = recent_data['low'].rolling(window=5, center=True).min()
            
            resistance_levels = recent_data[recent_data['high'] == highs]['high'].unique()
            support_levels = recent_data[recent_data['low'] == lows]['low'].unique()
            
            # เอาเฉพาะ levels ที่ใกล้ราคาปัจจุบัน
            current_price = df['close'].iloc[-1]
            
            resistance = [r for r in resistance_levels if r > current_price and r < current_price * 1.1]
            support = [s for s in support_levels if s < current_price and s > current_price * 0.9]
            
            return {
                "resistance": sorted(resistance)[:3],  # เอา 3 levels ที่ใกล้ที่สุด
                "support": sorted(support, reverse=True)[:3]
            }
            
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถหา support/resistance: {e}")
            return {"resistance": [], "support": []}
    
    def _determine_market_condition(self, volatility: float, trend: str, momentum: str) -> str:
        """กำหนดสภาพตลาด"""
        if volatility > 0.05:  # 5%
            return "high_volatility"
        elif volatility < 0.01:  # 1%
            return "low_volatility"
        elif trend == "bullish" and momentum in ["neutral", "oversold"]:
            return "bullish_momentum"
        elif trend == "bearish" and momentum in ["neutral", "overbought"]:
            return "bearish_momentum"
        else:
            return "sideways"
    
    def generate_trading_config(self, analysis: Dict, exchange_name: str) -> Dict:
        """สร้างคำแนะนำ config สำหรับการเทรด"""
        if "error" in analysis:
            return {"error": analysis["error"]}
        
        market_condition = analysis["market_condition"]
        volatility = analysis["price_data"]["volatility"]
        current_price = analysis["price_data"]["current_price"]
        
        # ดึงการตั้งค่าพื้นฐานของ exchange
        exchange_config = self.exchange_manager.exchanges.get(exchange_name, {}).get('config', {})
        min_amount = exchange_config.get('min_order_amount', 10.0)
        max_amount = exchange_config.get('max_order_amount', 1000.0)
        fee_rate = exchange_config.get('fee_rate', 0.001)
        
        # กำหนด spread ตามสภาพตลาด
        if market_condition == "high_volatility":
            bid_spread = 0.003  # 0.3%
            ask_spread = 0.004  # 0.4%
            stop_loss = 0.02    # 2%
        elif market_condition == "low_volatility":
            bid_spread = 0.001  # 0.1%
            ask_spread = 0.0015 # 0.15%
            stop_loss = 0.01    # 1%
        elif market_condition == "bullish_momentum":
            bid_spread = 0.002  # 0.2%
            ask_spread = 0.0025 # 0.25%
            stop_loss = 0.015   # 1.5%
        elif market_condition == "bearish_momentum":
            bid_spread = 0.0025 # 0.25%
            ask_spread = 0.003  # 0.3%
            stop_loss = 0.015   # 1.5%
        else:  # sideways
            bid_spread = 0.0015 # 0.15%
            ask_spread = 0.002  # 0.2%
            stop_loss = 0.01    # 1%
        
        config = {
            "exchange": exchange_name,
            "symbol": analysis["symbol"],
            "strategy": "market_making",
            "market_condition": market_condition,
            "spreads": {
                "bid_spread": round(bid_spread, 4),
                "ask_spread": round(ask_spread, 4),
                "minimum_spread": round(bid_spread - 0.0005, 4)
            },
            "risk_management": {
                "stop_loss": round(stop_loss, 4),
                "take_profit": round(stop_loss * 2, 4),
                "max_position_size": min(max_amount, current_price * 0.1),
                "min_order_amount": min_amount
            },
            "order_settings": {
                "order_levels": 3 if volatility > 0.02 else 1,
                "order_refresh_time": 60 if volatility > 0.02 else 30,
                "filled_order_delay": 10
            },
            "fees": {
                "exchange_fee": fee_rate,
                "estimated_profit_margin": round((bid_spread + ask_spread) - (fee_rate * 2), 4)
            }
        }
        
        return config
    
    async def analyze_all_exchanges(self, symbol: str = "BTC/USDT") -> Dict:
        """วิเคราะห์ตลาดจากทุก exchange ที่เปิดใช้งาน"""
        results = {}
        enabled_exchanges = self.exchange_manager.get_enabled_exchanges()
        
        self.logger.info(f"🔍 เริ่มวิเคราะห์ {symbol} จาก {len(enabled_exchanges)} exchanges")
        
        for exchange_name in enabled_exchanges:
            try:
                # ตรวจสอบว่า exchange รองรับ symbol นี้หรือไม่
                trading_pairs = self.exchange_manager.get_trading_pairs(exchange_name)
                if symbol not in trading_pairs:
                    self.logger.warning(f"⚠️ {exchange_name} ไม่รองรับ {symbol}")
                    continue
                
                # ดึงข้อมูล OHLC
                df = await self.fetch_ohlc_data(exchange_name, symbol, "1m", 100)
                if df is None or df.empty:
                    continue
                
                # คำนวณ technical indicators
                df = self.calculate_technical_indicators(df)
                
                # วิเคราะห์ตลาด
                analysis = self.analyze_market_condition(df, symbol)
                
                # สร้าง config
                config = self.generate_trading_config(analysis, exchange_name)
                
                results[exchange_name] = {
                    "analysis": analysis,
                    "config": config,
                    "data_points": len(df)
                }
                
                self.logger.info(f"✅ วิเคราะห์ {exchange_name} เสร็จสิ้น")
                
            except Exception as e:
                self.logger.error(f"❌ ไม่สามารถวิเคราะห์ {exchange_name}: {e}")
                results[exchange_name] = {"error": str(e)}
        
        return results
    
    def print_analysis_summary(self, results: Dict):
        """แสดงสรุปผลการวิเคราะห์"""
        print("\n" + "="*80)
        print("📊 สรุปผลการวิเคราะห์ตลาดจากหลาย Exchange")
        print("="*80)
        
        for exchange_name, result in results.items():
            if "error" in result:
                print(f"\n❌ {exchange_name.upper()}: {result['error']}")
                continue
            
            analysis = result["analysis"]
            config = result["config"]
            
            print(f"\n🏢 {exchange_name.upper()}")
            print("-" * 40)
            
            # ข้อมูลราคา
            price_data = analysis["price_data"]
            print(f"💰 ราคาปัจจุบัน: ${price_data['current_price']:,.2f}")
            print(f"📈 เปลี่ยนแปลง 24h: {price_data['price_change_24h']:.2%}")
            print(f"📊 ความผันผวน: {price_data['volatility']:.2%}")
            
            # การวิเคราะห์เทคนิค
            tech = analysis["technical_analysis"]
            print(f"📈 เทรนด์: {tech['trend']}")
            print(f"⚡ Momentum: {tech['momentum']}")
            print(f"📊 RSI: {tech['rsi']:.1f}")
            
            # สภาพตลาด
            print(f"🌡️ สภาพตลาด: {analysis['market_condition']}")
            
            # คำแนะนำ config
            spreads = config["spreads"]
            print(f"\n💡 คำแนะนำการตั้งค่า:")
            print(f"   - Bid Spread: {spreads['bid_spread']:.2%}")
            print(f"   - Ask Spread: {spreads['ask_spread']:.2%}")
            print(f"   - Stop Loss: {config['risk_management']['stop_loss']:.2%}")
            print(f"   - กำไรคาดหวัง: {config['fees']['estimated_profit_margin']:.2%}")
        
        print("\n" + "="*80)
    
    async def run_continuous_analysis(self, symbol: str = "BTC/USDT", interval: int = 300):
        """รันการวิเคราะห์อย่างต่อเนื่อง"""
        self.logger.info(f"🔄 เริ่มการวิเคราะห์ต่อเนื่องทุก {interval} วินาที")
        
        while True:
            try:
                results = await self.analyze_all_exchanges(symbol)
                self.analysis_results = results
                self.print_analysis_summary(results)
                
                await asyncio.sleep(interval)
                
            except KeyboardInterrupt:
                self.logger.info("⏹️ หยุดการวิเคราะห์")
                break
            except Exception as e:
                self.logger.error(f"❌ เกิดข้อผิดพลาดในการวิเคราะห์: {e}")
                await asyncio.sleep(60)  # รอ 1 นาทีก่อนลองใหม่

# === Main function ===
async def run_market_analysis():
    """รันการวิเคราะห์ตลาดแบบใหม่"""
    analyzer = MultiExchangeMarketAnalyzer()
    
    # เริ่มต้นการเชื่อมต่อ
    if not await analyzer.initialize():
        print("❌ ไม่สามารถเชื่อมต่อกับ exchange ใดๆ ได้")
        return
    
    # วิเคราะห์ครั้งเดียว
    results = await analyzer.analyze_all_exchanges("BTC/USDT")
    analyzer.print_analysis_summary(results)
    
    return results

# === Run ===
if __name__ == "__main__":
    asyncio.run(run_market_analysis()) 