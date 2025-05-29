#!/usr/bin/env python3
"""
Crypto Pairs Scanner with MACD Signals
สแกนคู่เทรด crypto ด้วยสัญญาณ MACD เพื่อหาโอกาสการเทรด
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
import ta
from dataclasses import dataclass
from .exchange_manager import ExchangeManager
import json

@dataclass
class MACDSignal:
    """คลาสสำหรับเก็บข้อมูล MACD Signal"""
    symbol: str
    exchange: str
    timeframe: str
    signal_type: str  # 'long' หรือ 'short'
    macd_value: float
    macd_signal: float
    macd_histogram: float
    price: float
    volume: float
    timestamp: datetime
    strength: float  # ความแรงของสัญญาณ 0-100

@dataclass
class ScannerConfig:
    """การตั้งค่าสำหรับ Scanner"""
    timeframes: List[str] = None
    exchanges: List[str] = None
    trading_pairs: List[str] = None
    min_volume_24h: float = 100000  # ปริมาณการเทรดขั้นต่ำ 24 ชั่วโมง
    min_signal_strength: float = 60  # ความแรงสัญญาณขั้นต่ำ
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal_period: int = 9
    
    def __post_init__(self):
        if self.timeframes is None:
            self.timeframes = ['1h', '4h', '1d']
        if self.exchanges is None:
            self.exchanges = ['binance', 'gateio']
        if self.trading_pairs is None:
            self.trading_pairs = [
                'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT',
                'XRP/USDT', 'DOT/USDT', 'AVAX/USDT', 'MATIC/USDT', 'LINK/USDT',
                'UNI/USDT', 'LTC/USDT', 'BCH/USDT', 'ALGO/USDT', 'VET/USDT',
                'FTM/USDT', 'ATOM/USDT', 'NEAR/USDT', 'SAND/USDT', 'MANA/USDT'
            ]

class CryptoPairsScanner:
    """สแกนเนอร์สำหรับหาสัญญาณ MACD ในคู่เทรด crypto"""
    
    def __init__(self, config_path: str = "config.json"):
        self.exchange_manager = ExchangeManager(config_path)
        self.config = ScannerConfig()
        self.logger = self._setup_logger()
        self.scan_results = {}
        self.is_scanning = False
        
    def _setup_logger(self) -> logging.Logger:
        """ตั้งค่า logger"""
        logger = logging.getLogger('CryptoScanner')
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
        self.logger.info("🔍 เริ่มต้น Crypto Pairs Scanner")
        return self.exchange_manager.initialize_exchanges()
    
    def update_config(self, **kwargs):
        """อัปเดตการตั้งค่า scanner"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                self.logger.info(f"📝 อัปเดตการตั้งค่า {key}: {value}")
    
    async def fetch_ohlcv_data(self, exchange_name: str, symbol: str, 
                              timeframe: str, limit: int = 100) -> Optional[pd.DataFrame]:
        """ดึงข้อมูล OHLCV จาก exchange"""
        try:
            exchange = self.exchange_manager.get_exchange(exchange_name)
            if not exchange:
                return None
            
            # สำหรับ CEX เท่านั้น (DEX ยังไม่รองรับ)
            if exchange_name not in self.exchange_manager.exchanges:
                return None
            
            ohlcv_data = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df.set_index('timestamp')
            
            return df.sort_index()
            
        except Exception as e:
            self.logger.debug(f"ไม่สามารถดึงข้อมูล {symbol} จาก {exchange_name}: {e}")
            return None
    
    def calculate_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """คำนวณ MACD indicators"""
        try:
            # คำนวณ MACD
            macd_indicator = ta.trend.MACD(
                close=df['close'],
                window_fast=self.config.macd_fast,
                window_slow=self.config.macd_slow,
                window_sign=self.config.macd_signal_period
            )
            
            df['macd'] = macd_indicator.macd()
            df['macd_signal'] = macd_indicator.macd_signal()
            df['macd_histogram'] = macd_indicator.macd_diff()
            
            # คำนวณ MACD crosses
            df['macd_cross_up'] = (
                (df['macd'] > 0) & 
                (df['macd'].shift(1) <= 0)
            )
            
            df['macd_cross_down'] = (
                (df['macd'] < 0) & 
                (df['macd'].shift(1) >= 0)
            )
            
            # คำนวณความแรงของสัญญาณ
            df['signal_strength'] = self._calculate_signal_strength(df)
            
            return df
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถคำนวณ MACD: {e}")
            return df
    
    def _calculate_signal_strength(self, df: pd.DataFrame) -> pd.Series:
        """คำนวณความแรงของสัญญาณ MACD (0-100)"""
        try:
            # ใช้ histogram และ momentum ในการคำนวณ
            histogram_abs = df['macd_histogram'].abs()
            histogram_max = histogram_abs.rolling(window=20).max()
            
            # ความแรงจาก histogram (0-50)
            histogram_strength = (histogram_abs / histogram_max * 50).fillna(0)
            
            # ความแรงจาก momentum (0-50)
            macd_momentum = df['macd'] - df['macd'].shift(1)
            momentum_abs = macd_momentum.abs()
            momentum_max = momentum_abs.rolling(window=20).max()
            momentum_strength = (momentum_abs / momentum_max * 50).fillna(0)
            
            # รวมความแรง
            total_strength = histogram_strength + momentum_strength
            
            return total_strength.clip(0, 100)
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถคำนวณความแรงสัญญาณ: {e}")
            return pd.Series([0] * len(df), index=df.index)
    
    def detect_macd_signals(self, df: pd.DataFrame, symbol: str, 
                           exchange: str, timeframe: str) -> List[MACDSignal]:
        """ตรวจหาสัญญาณ MACD"""
        signals = []
        
        if df is None or df.empty or len(df) < 2:
            return signals
        
        try:
            latest = df.iloc[-1]
            previous = df.iloc[-2]
            
            # ตรวจสอบ volume ขั้นต่ำ
            volume_24h = df['volume'].tail(24).sum() if len(df) >= 24 else df['volume'].sum()
            if volume_24h < self.config.min_volume_24h:
                return signals
            
            # ตรวจสอบ MACD Cross Up (Long Signal)
            if latest['macd_cross_up'] and latest['signal_strength'] >= self.config.min_signal_strength:
                signal = MACDSignal(
                    symbol=symbol,
                    exchange=exchange,
                    timeframe=timeframe,
                    signal_type='long',
                    macd_value=latest['macd'],
                    macd_signal=latest['macd_signal'],
                    macd_histogram=latest['macd_histogram'],
                    price=latest['close'],
                    volume=volume_24h,
                    timestamp=latest.name,
                    strength=latest['signal_strength']
                )
                signals.append(signal)
            
            # ตรวจสอบ MACD Cross Down (Short Signal)
            elif latest['macd_cross_down'] and latest['signal_strength'] >= self.config.min_signal_strength:
                signal = MACDSignal(
                    symbol=symbol,
                    exchange=exchange,
                    timeframe=timeframe,
                    signal_type='short',
                    macd_value=latest['macd'],
                    macd_signal=latest['macd_signal'],
                    macd_histogram=latest['macd_histogram'],
                    price=latest['close'],
                    volume=volume_24h,
                    timestamp=latest.name,
                    strength=latest['signal_strength']
                )
                signals.append(signal)
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถตรวจหาสัญญาณ {symbol}: {e}")
        
        return signals
    
    async def scan_single_pair(self, exchange_name: str, symbol: str, 
                              timeframe: str) -> List[MACDSignal]:
        """สแกนคู่เทรดเดียว"""
        signals = []
        
        try:
            # ดึงข้อมูล OHLCV
            df = await self.fetch_ohlcv_data(exchange_name, symbol, timeframe, 100)
            if df is None or df.empty:
                return signals
            
            # คำนวณ MACD
            df = self.calculate_macd(df)
            
            # ตรวจหาสัญญาณ
            signals = self.detect_macd_signals(df, symbol, exchange_name, timeframe)
            
        except Exception as e:
            self.logger.debug(f"ไม่สามารถสแกน {symbol} ใน {exchange_name}: {e}")
        
        return signals
    
    async def scan_all_pairs(self, timeframes: List[str] = None) -> Dict[str, List[MACDSignal]]:
        """สแกนคู่เทรดทั้งหมด"""
        if timeframes is None:
            timeframes = self.config.timeframes
        
        self.logger.info(f"🔍 เริ่มสแกนคู่เทรด {len(self.config.trading_pairs)} คู่ ใน {len(timeframes)} timeframes")
        
        all_signals = {}
        tasks = []
        
        # สร้าง tasks สำหรับการสแกนแบบ concurrent
        for exchange_name in self.config.exchanges:
            if exchange_name not in self.exchange_manager.get_enabled_exchanges():
                continue
                
            for symbol in self.config.trading_pairs:
                for timeframe in timeframes:
                    task = self.scan_single_pair(exchange_name, symbol, timeframe)
                    tasks.append(task)
        
        # รันการสแกนแบบ concurrent
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # รวบรวมผลลัพธ์
        for result in results:
            if isinstance(result, list):
                for signal in result:
                    key = f"{signal.exchange}_{signal.timeframe}"
                    if key not in all_signals:
                        all_signals[key] = []
                    all_signals[key].append(signal)
        
        # เรียงลำดับตามความแรงสัญญาณ
        for key in all_signals:
            all_signals[key].sort(key=lambda x: x.strength, reverse=True)
        
        self.scan_results = all_signals
        
        total_signals = sum(len(signals) for signals in all_signals.values())
        self.logger.info(f"✅ สแกนเสร็จสิ้น พบสัญญาณทั้งหมด: {total_signals}")
        
        return all_signals
    
    def get_top_signals(self, signal_type: str = None, limit: int = 10) -> List[MACDSignal]:
        """ดึงสัญญาณที่ดีที่สุด"""
        all_signals = []
        
        for signals in self.scan_results.values():
            all_signals.extend(signals)
        
        # กรองตามประเภทสัญญาณ
        if signal_type:
            all_signals = [s for s in all_signals if s.signal_type == signal_type]
        
        # เรียงตามความแรงสัญญาณ
        all_signals.sort(key=lambda x: x.strength, reverse=True)
        
        return all_signals[:limit]
    
    def print_scan_results(self, timeframes: List[str] = None):
        """แสดงผลการสแกน"""
        if not self.scan_results:
            print("❌ ยังไม่มีผลการสแกน กรุณารันการสแกนก่อน")
            return
        
        print("\n" + "="*100)
        print("🔍 ผลการสแกน MACD Signals")
        print("="*100)
        
        # แสดงสรุป
        total_signals = sum(len(signals) for signals in self.scan_results.values())
        long_signals = len([s for signals in self.scan_results.values() for s in signals if s.signal_type == 'long'])
        short_signals = len([s for signals in self.scan_results.values() for s in signals if s.signal_type == 'short'])
        
        print(f"📊 สรุป: สัญญาณทั้งหมด {total_signals} | Long: {long_signals} | Short: {short_signals}")
        print()
        
        # แสดงสัญญาณ Long ที่ดีที่สุด
        top_long = self.get_top_signals('long', 5)
        if top_long:
            print("🟢 TOP 5 LONG SIGNALS (MACD Cross Up)")
            print("-" * 80)
            for i, signal in enumerate(top_long, 1):
                print(f"{i}. {signal.symbol} ({signal.exchange.upper()}) - {signal.timeframe}")
                print(f"   💰 ราคา: ${signal.price:,.4f} | 📊 ความแรง: {signal.strength:.1f}%")
                print(f"   📈 MACD: {signal.macd_value:.6f} | Signal: {signal.macd_signal:.6f}")
                print(f"   📅 เวลา: {signal.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                print()
        
        # แสดงสัญญาณ Short ที่ดีที่สุด
        top_short = self.get_top_signals('short', 5)
        if top_short:
            print("🔴 TOP 5 SHORT SIGNALS (MACD Cross Down)")
            print("-" * 80)
            for i, signal in enumerate(top_short, 1):
                print(f"{i}. {signal.symbol} ({signal.exchange.upper()}) - {signal.timeframe}")
                print(f"   💰 ราคา: ${signal.price:,.4f} | 📊 ความแรง: {signal.strength:.1f}%")
                print(f"   📉 MACD: {signal.macd_value:.6f} | Signal: {signal.macd_signal:.6f}")
                print(f"   📅 เวลา: {signal.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                print()
        
        # แสดงสรุปตาม timeframe
        print("📊 สรุปตาม Timeframe:")
        print("-" * 40)
        for key, signals in self.scan_results.items():
            if signals:
                exchange, timeframe = key.split('_', 1)
                long_count = len([s for s in signals if s.signal_type == 'long'])
                short_count = len([s for s in signals if s.signal_type == 'short'])
                print(f"{exchange.upper()} - {timeframe}: {len(signals)} สัญญาณ (Long: {long_count}, Short: {short_count})")
        
        print("\n" + "="*100)
    
    def export_signals_to_json(self, filename: str = None) -> str:
        """ส่งออกสัญญาณเป็นไฟล์ JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"temp/macd_signals_{timestamp}.json"
        
        export_data = {
            "scan_time": datetime.now().isoformat(),
            "config": {
                "timeframes": self.config.timeframes,
                "exchanges": self.config.exchanges,
                "min_signal_strength": self.config.min_signal_strength,
                "macd_settings": {
                    "fast": self.config.macd_fast,
                    "slow": self.config.macd_slow,
                    "signal": self.config.macd_signal_period
                }
            },
            "signals": {}
        }
        
        for key, signals in self.scan_results.items():
            export_data["signals"][key] = []
            for signal in signals:
                export_data["signals"][key].append({
                    "symbol": signal.symbol,
                    "exchange": signal.exchange,
                    "timeframe": signal.timeframe,
                    "signal_type": signal.signal_type,
                    "price": signal.price,
                    "strength": signal.strength,
                    "macd_value": signal.macd_value,
                    "macd_signal": signal.macd_signal,
                    "macd_histogram": signal.macd_histogram,
                    "volume_24h": signal.volume,
                    "timestamp": signal.timestamp.isoformat()
                })
        
        # สร้างโฟลเดอร์ temp ถ้ายังไม่มี
        import os
        os.makedirs('temp', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📁 ส่งออกสัญญาณไปยังไฟล์: {filename}")
        return filename
    
    async def start_continuous_scan(self, interval_minutes: int = 15):
        """เริ่มการสแกนอย่างต่อเนื่อง"""
        self.is_scanning = True
        self.logger.info(f"🔄 เริ่มการสแกนต่อเนื่องทุก {interval_minutes} นาที")
        
        while self.is_scanning:
            try:
                await self.scan_all_pairs()
                self.print_scan_results()
                
                # ส่งออกสัญญาณที่ดี
                top_signals = self.get_top_signals(limit=20)
                if top_signals:
                    self.export_signals_to_json()
                
                # รอก่อนรอบถัดไป
                await asyncio.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                self.logger.info("⏹️ หยุดการสแกนโดยผู้ใช้")
                break
            except Exception as e:
                self.logger.error(f"❌ เกิดข้อผิดพลาดในการสแกน: {e}")
                await asyncio.sleep(60)  # รอ 1 นาทีก่อนลองใหม่
        
        self.is_scanning = False
    
    def stop_scanning(self):
        """หยุดการสแกน"""
        self.is_scanning = False
        self.logger.info("⏹️ หยุดการสแกน")

# === Main Functions ===
async def run_single_scan(timeframes: List[str] = None, exchanges: List[str] = None):
    """รันการสแกนครั้งเดียว"""
    scanner = CryptoPairsScanner()
    
    if not await scanner.initialize():
        print("❌ ไม่สามารถเชื่อมต่อกับ exchange ได้")
        return
    
    # อัปเดตการตั้งค่า
    if timeframes:
        scanner.update_config(timeframes=timeframes)
    if exchanges:
        scanner.update_config(exchanges=exchanges)
    
    # รันการสแกน
    await scanner.scan_all_pairs()
    scanner.print_scan_results()
    
    # ส่งออกผลลัพธ์
    scanner.export_signals_to_json()
    
    return scanner.scan_results

async def run_continuous_scan(interval_minutes: int = 15):
    """รันการสแกนอย่างต่อเนื่อง"""
    scanner = CryptoPairsScanner()
    
    if not await scanner.initialize():
        print("❌ ไม่สามารถเชื่อมต่อกับ exchange ได้")
        return
    
    try:
        await scanner.start_continuous_scan(interval_minutes)
    except KeyboardInterrupt:
        scanner.stop_scanning()

# === Run ===
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "continuous":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 15
        asyncio.run(run_continuous_scan(interval))
    else:
        # รันการสแกนครั้งเดียว
        timeframes = ['1h', '4h', '1d']  # สามารถปรับได้
        asyncio.run(run_single_scan(timeframes)) 