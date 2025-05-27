#!/usr/bin/env python3
"""
ตัวอย่างการใช้งาน Crypto Pairs Scanner
แสดงวิธีการใช้งาน MACD Scanner ในรูปแบบต่างๆ
"""

import asyncio
import sys
import os
from datetime import datetime

# เพิ่ม path สำหรับ import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bots.crypto_scanner import CryptoPairsScanner, run_single_scan, run_continuous_scan

async def example_1_basic_scan():
    """ตัวอย่างที่ 1: การสแกนพื้นฐาน"""
    print("🔍 ตัวอย่างที่ 1: การสแกนพื้นฐาน")
    print("=" * 50)
    
    scanner = CryptoPairsScanner()
    
    if not await scanner.initialize():
        print("❌ ไม่สามารถเชื่อมต่อกับ exchange ได้")
        return
    
    # ตั้งค่าการสแกน
    scanner.update_config(
        timeframes=['1h', '4h'],
        exchanges=['binance'],
        min_signal_strength=50
    )
    
    # รันการสแกน
    results = await scanner.scan_all_pairs()
    scanner.print_scan_results()
    
    print("\n")

async def example_2_custom_pairs():
    """ตัวอย่างที่ 2: สแกนคู่เทรดที่กำหนดเอง"""
    print("🎯 ตัวอย่างที่ 2: สแกนคู่เทรดที่กำหนดเอง")
    print("=" * 50)
    
    scanner = CryptoPairsScanner()
    
    if not await scanner.initialize():
        print("❌ ไม่สามารถเชื่อมต่อกับ exchange ได้")
        return
    
    # กำหนดคู่เทรดที่สนใจ
    custom_pairs = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT']
    
    scanner.update_config(
        trading_pairs=custom_pairs,
        timeframes=['4h', '1d'],
        min_signal_strength=70,
        min_volume_24h=500000
    )
    
    results = await scanner.scan_all_pairs()
    
    # แสดงเฉพาะสัญญาณ Long
    long_signals = scanner.get_top_signals('long', 10)
    if long_signals:
        print("🟢 สัญญาณ LONG ที่พบ:")
        for i, signal in enumerate(long_signals, 1):
            print(f"{i}. {signal.symbol} ({signal.exchange}) - {signal.timeframe}")
            print(f"   ราคา: ${signal.price:,.4f} | ความแรง: {signal.strength:.1f}%")
    else:
        print("❌ ไม่พบสัญญาณ Long")
    
    print("\n")

async def example_3_single_pair_check():
    """ตัวอย่างที่ 3: ตรวจสอบคู่เทรดเดียว"""
    print("📊 ตัวอย่างที่ 3: ตรวจสอบคู่เทรดเดียว")
    print("=" * 50)
    
    scanner = CryptoPairsScanner()
    
    if not await scanner.initialize():
        print("❌ ไม่สามารถเชื่อมต่อกับ exchange ได้")
        return
    
    # ตรวจสอบ BTC/USDT ใน timeframes ต่างๆ
    symbol = "BTC/USDT"
    exchange = "binance"
    timeframes = ['1h', '4h', '1d']
    
    print(f"🔍 ตรวจสอบ {symbol} ใน {exchange.upper()}")
    print("-" * 40)
    
    for tf in timeframes:
        signals = await scanner.scan_single_pair(exchange, symbol, tf)
        
        if signals:
            signal = signals[0]
            signal_emoji = "🟢" if signal.signal_type == "long" else "🔴"
            print(f"{tf}: {signal_emoji} {signal.signal_type.upper()} (ความแรง: {signal.strength:.1f}%)")
        else:
            # แสดงข้อมูล MACD ปัจจุบัน
            df = await scanner.fetch_ohlcv_data(exchange, symbol, tf, 50)
            if df is not None and not df.empty:
                df = scanner.calculate_macd(df)
                latest = df.iloc[-1]
                
                macd_status = "🟢 บวก" if latest['macd'] > 0 else "🔴 ลบ"
                print(f"{tf}: ❌ ไม่มีสัญญาณ | MACD: {macd_status} ({latest['macd']:.6f})")
    
    print("\n")

async def example_4_timeframe_comparison():
    """ตัวอย่างที่ 4: เปรียบเทียบ timeframes"""
    print("⏰ ตัวอย่างที่ 4: เปรียบเทียบ timeframes")
    print("=" * 50)
    
    scanner = CryptoPairsScanner()
    
    if not await scanner.initialize():
        print("❌ ไม่สามารถเชื่อมต่อกับ exchange ได้")
        return
    
    # สแกนใน timeframes ต่างๆ
    timeframes = ['15m', '1h', '4h', '1d']
    
    for tf in timeframes:
        print(f"📊 สแกน Timeframe: {tf}")
        print("-" * 30)
        
        scanner.update_config(timeframes=[tf])
        results = await scanner.scan_all_pairs([tf])
        
        if results:
            total_signals = sum(len(signals) for signals in results.values())
            long_signals = len([s for signals in results.values() for s in signals if s.signal_type == 'long'])
            short_signals = len([s for signals in results.values() for s in signals if s.signal_type == 'short'])
            
            print(f"   สัญญาณทั้งหมด: {total_signals}")
            print(f"   Long: {long_signals} | Short: {short_signals}")
            
            # แสดงสัญญาณที่แรงที่สุด
            top_signal = scanner.get_top_signals(limit=1)
            if top_signal:
                signal = top_signal[0]
                signal_emoji = "🟢" if signal.signal_type == "long" else "🔴"
                print(f"   {signal_emoji} แรงที่สุด: {signal.symbol} ({signal.strength:.1f}%)")
        else:
            print("   ❌ ไม่พบสัญญาณ")
        
        print()

async def example_5_export_signals():
    """ตัวอย่างที่ 5: ส่งออกสัญญาณ"""
    print("📁 ตัวอย่างที่ 5: ส่งออกสัญญาณ")
    print("=" * 50)
    
    scanner = CryptoPairsScanner()
    
    if not await scanner.initialize():
        print("❌ ไม่สามารถเชื่อมต่อกับ exchange ได้")
        return
    
    # รันการสแกน
    results = await scanner.scan_all_pairs()
    
    if results:
        # ส่งออกเป็นไฟล์ JSON
        filename = scanner.export_signals_to_json()
        print(f"✅ ส่งออกสัญญาณไปยังไฟล์: {filename}")
        
        # แสดงสถิติ
        total_signals = sum(len(signals) for signals in results.values())
        print(f"📊 สัญญาณทั้งหมด: {total_signals}")
        
        # แสดงสัญญาณที่ดีที่สุด 3 อันดับ
        top_signals = scanner.get_top_signals(limit=3)
        if top_signals:
            print("\n🏆 TOP 3 สัญญาณที่ดีที่สุด:")
            for i, signal in enumerate(top_signals, 1):
                signal_emoji = "🟢" if signal.signal_type == "long" else "🔴"
                print(f"{i}. {signal_emoji} {signal.symbol} ({signal.exchange}) - {signal.timeframe}")
                print(f"   ประเภท: {signal.signal_type.upper()} | ความแรง: {signal.strength:.1f}%")
    else:
        print("❌ ไม่พบสัญญาณ")
    
    print("\n")

async def example_6_macd_settings():
    """ตัวอย่างที่ 6: ปรับการตั้งค่า MACD"""
    print("⚙️ ตัวอย่างที่ 6: ปรับการตั้งค่า MACD")
    print("=" * 50)
    
    scanner = CryptoPairsScanner()
    
    if not await scanner.initialize():
        print("❌ ไม่สามารถเชื่อมต่อกับ exchange ได้")
        return
    
    # ทดสอบการตั้งค่า MACD ต่างๆ
    macd_settings = [
        {"fast": 12, "slow": 26, "signal": 9, "name": "Standard"},
        {"fast": 8, "slow": 21, "signal": 5, "name": "Fast"},
        {"fast": 19, "slow": 39, "signal": 9, "name": "Slow"}
    ]
    
    symbol = "BTC/USDT"
    exchange = "binance"
    timeframe = "4h"
    
    print(f"🔍 ทดสอบการตั้งค่า MACD สำหรับ {symbol}")
    print("-" * 40)
    
    for setting in macd_settings:
        # อัปเดตการตั้งค่า MACD
        scanner.update_config(
            macd_fast=setting["fast"],
            macd_slow=setting["slow"],
            macd_signal_period=setting["signal"]
        )
        
        # ดึงข้อมูลและคำนวณ MACD
        df = await scanner.fetch_ohlcv_data(exchange, symbol, timeframe, 100)
        if df is not None and not df.empty:
            df = scanner.calculate_macd(df)
            latest = df.iloc[-1]
            
            # ตรวจสอบสัญญาณ
            signals = scanner.detect_macd_signals(df, symbol, exchange, timeframe)
            
            print(f"{setting['name']} ({setting['fast']},{setting['slow']},{setting['signal']}):")
            print(f"   MACD: {latest['macd']:.6f}")
            print(f"   Signal: {latest['macd_signal']:.6f}")
            
            if signals:
                signal = signals[0]
                signal_emoji = "🟢" if signal.signal_type == "long" else "🔴"
                print(f"   {signal_emoji} สัญญาณ: {signal.signal_type.upper()} (ความแรง: {signal.strength:.1f}%)")
            else:
                print("   ❌ ไม่มีสัญญาณ")
        
        print()

async def example_7_real_time_monitoring():
    """ตัวอย่างที่ 7: การติดตามแบบ real-time (จำลอง)"""
    print("📡 ตัวอย่างที่ 7: การติดตามแบบ real-time")
    print("=" * 50)
    print("จำลองการติดตาม 3 รอบ (ในการใช้งานจริงจะทำงานต่อเนื่อง)")
    print()
    
    scanner = CryptoPairsScanner()
    
    if not await scanner.initialize():
        print("❌ ไม่สามารถเชื่อมต่อกับ exchange ได้")
        return
    
    # ตั้งค่าสำหรับการติดตาม
    scanner.update_config(
        timeframes=['1h'],
        trading_pairs=['BTC/USDT', 'ETH/USDT', 'BNB/USDT'],
        min_signal_strength=60
    )
    
    for round_num in range(1, 4):
        print(f"🔄 รอบที่ {round_num} - {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 30)
        
        results = await scanner.scan_all_pairs()
        
        if results:
            total_signals = sum(len(signals) for signals in results.values())
            print(f"📊 พบสัญญาณ: {total_signals}")
            
            # แสดงสัญญาณใหม่
            top_signals = scanner.get_top_signals(limit=2)
            for signal in top_signals:
                signal_emoji = "🟢" if signal.signal_type == "long" else "🔴"
                print(f"   {signal_emoji} {signal.symbol}: {signal.signal_type.upper()} ({signal.strength:.1f}%)")
        else:
            print("📊 ไม่พบสัญญาณใหม่")
        
        print()
        
        # รอ 10 วินาที (ในการใช้งานจริงอาจเป็น 15 นาที)
        if round_num < 3:
            print("⏳ รอ 10 วินาที...")
            await asyncio.sleep(10)
            print()

async def main():
    """ฟังก์ชันหลักสำหรับรันตัวอย่างทั้งหมด"""
    print("🔍 Crypto Pairs Scanner - ตัวอย่างการใช้งาน")
    print("=" * 60)
    print()
    
    try:
        # รันตัวอย่างทีละอัน
        await example_1_basic_scan()
        await example_2_custom_pairs()
        await example_3_single_pair_check()
        await example_4_timeframe_comparison()
        await example_5_export_signals()
        await example_6_macd_settings()
        await example_7_real_time_monitoring()
        
        print("✅ รันตัวอย่างทั้งหมดเสร็จสิ้น!")
        
    except KeyboardInterrupt:
        print("\n⏹️ หยุดการทำงานโดยผู้ใช้")
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    # ตรวจสอบว่ามีไฟล์ config หรือไม่
    if not os.path.exists("config.json"):
        print("❌ ไม่พบไฟล์ config.json")
        print("💡 กรุณารันคำสั่ง: python cli.py setup")
        exit(1)
    
    # รันตัวอย่าง
    asyncio.run(main()) 