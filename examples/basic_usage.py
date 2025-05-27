#!/usr/bin/env python3
"""
ตัวอย่างการใช้งาน Multi-Exchange Trading Bot

ไฟล์นี้แสดงวิธีการใช้งานบอทในรูปแบบต่างๆ
"""

import asyncio
import sys
import os

# เพิ่ม path สำหรับ import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bots.exchange_manager import ExchangeManager
from bots.market_analyzer import MultiExchangeMarketAnalyzer
from bots.multi_exchange_bot import MultiExchangeTradingBot

async def example_1_basic_connection():
    """ตัวอย่างที่ 1: การเชื่อมต่อพื้นฐาน"""
    print("🔗 ตัวอย่างที่ 1: การเชื่อมต่อพื้นฐาน")
    print("=" * 50)
    
    # สร้าง ExchangeManager
    exchange_manager = ExchangeManager("config.json")
    
    # เชื่อมต่อกับ exchanges
    if exchange_manager.initialize_exchanges():
        print("✅ เชื่อมต่อสำเร็จ!")
        
        # แสดงรายการ exchanges ที่เชื่อมต่อได้
        enabled_exchanges = exchange_manager.get_enabled_exchanges()
        print(f"📋 Exchanges ที่เชื่อมต่อ: {enabled_exchanges}")
        
        # ดูยอดเงินในแต่ละ exchange
        for exchange_name in enabled_exchanges:
            try:
                balance = exchange_manager.get_balance(exchange_name)
                print(f"💰 {exchange_name}: {balance}")
            except Exception as e:
                print(f"❌ ไม่สามารถดึงยอดเงินจาก {exchange_name}: {e}")
    else:
        print("❌ ไม่สามารถเชื่อมต่อได้")
    
    print("\n")

async def example_2_market_analysis():
    """ตัวอย่างที่ 2: การวิเคราะห์ตลาด"""
    print("📊 ตัวอย่างที่ 2: การวิเคราะห์ตลาด")
    print("=" * 50)
    
    # สร้าง MarketAnalyzer
    analyzer = MultiExchangeMarketAnalyzer("config.json")
    
    # เริ่มต้นการเชื่อมต่อ
    if await analyzer.initialize():
        print("✅ เริ่มต้น MarketAnalyzer สำเร็จ!")
        
        # วิเคราะห์ตลาด BTC/USDT
        results = await analyzer.analyze_all_exchanges("BTC/USDT")
        
        # แสดงผลการวิเคราะห์
        analyzer.print_analysis_summary(results)
        
        # ดูรายละเอียดการวิเคราะห์ของ exchange หนึ่งๆ
        for exchange_name, result in results.items():
            if "error" not in result:
                analysis = result["analysis"]
                config = result["config"]
                
                print(f"\n🔍 รายละเอียดการวิเคราะห์ {exchange_name}:")
                print(f"   - Market Condition: {analysis['market_condition']}")
                print(f"   - Volatility: {analysis['price_data']['volatility']:.2%}")
                print(f"   - Recommended Bid Spread: {config['spreads']['bid_spread']:.2%}")
                print(f"   - Recommended Ask Spread: {config['spreads']['ask_spread']:.2%}")
                break
    else:
        print("❌ ไม่สามารถเริ่มต้น MarketAnalyzer ได้")
    
    print("\n")

async def example_3_single_exchange_data():
    """ตัวอย่างที่ 3: ดึงข้อมูลจาก exchange เดียว"""
    print("📈 ตัวอย่างที่ 3: ดึงข้อมูลจาก exchange เดียว")
    print("=" * 50)
    
    analyzer = MultiExchangeMarketAnalyzer("config.json")
    
    if await analyzer.initialize():
        # ดึงข้อมูล OHLC จาก Binance
        exchange_name = "binance"
        symbol = "BTC/USDT"
        
        print(f"📊 ดึงข้อมูล {symbol} จาก {exchange_name}...")
        
        df = await analyzer.fetch_ohlc_data(exchange_name, symbol, "1m", 50)
        
        if df is not None and not df.empty:
            print(f"✅ ดึงข้อมูลได้ {len(df)} แท่งเทียน")
            
            # คำนวณ technical indicators
            df = analyzer.calculate_technical_indicators(df)
            
            # แสดงข้อมูลล่าสุด
            latest = df.iloc[-1]
            print(f"💰 ราคาปิดล่าสุด: ${latest['close']:,.2f}")
            print(f"📊 RSI: {latest.get('rsi', 'N/A'):.1f}")
            print(f"📈 SMA 20: ${latest.get('sma_20', 'N/A'):,.2f}")
            print(f"📉 EMA 20: ${latest.get('ema_20', 'N/A'):,.2f}")
            
            # แสดงข้อมูล 5 แท่งล่าสุด
            print(f"\n📋 ข้อมูล 5 แท่งล่าสุด:")
            print(df[['open', 'high', 'low', 'close', 'volume']].tail())
        else:
            print("❌ ไม่สามารถดึงข้อมูลได้")
    
    print("\n")

async def example_4_price_comparison():
    """ตัวอย่างที่ 4: เปรียบเทียบราคาระหว่าง exchanges"""
    print("⚖️ ตัวอย่างที่ 4: เปรียบเทียบราคาระหว่าง exchanges")
    print("=" * 50)
    
    exchange_manager = ExchangeManager("config.json")
    
    if exchange_manager.initialize_exchanges():
        symbol = "BTC/USDT"
        enabled_exchanges = exchange_manager.get_enabled_exchanges()
        
        print(f"💱 เปรียบเทียบราคา {symbol}:")
        
        prices = {}
        
        for exchange_name in enabled_exchanges:
            try:
                # ตรวจสอบว่า exchange รองรับ symbol นี้หรือไม่
                trading_pairs = exchange_manager.get_trading_pairs(exchange_name)
                if symbol not in trading_pairs:
                    continue
                
                ticker = await exchange_manager.fetch_ticker(exchange_name, symbol)
                if ticker:
                    prices[exchange_name] = ticker['last']
                    print(f"   {exchange_name.upper()}: ${ticker['last']:,.2f}")
            except Exception as e:
                print(f"   {exchange_name.upper()}: ❌ {e}")
        
        # หาราคาสูงสุดและต่ำสุด
        if prices:
            max_price = max(prices.values())
            min_price = min(prices.values())
            spread = (max_price - min_price) / min_price * 100
            
            print(f"\n📊 สรุป:")
            print(f"   ราคาสูงสุด: ${max_price:,.2f}")
            print(f"   ราคาต่ำสุด: ${min_price:,.2f}")
            print(f"   ส่วนต่างราคา: {spread:.2f}%")
    
    print("\n")

async def example_5_custom_analysis():
    """ตัวอย่างที่ 5: การวิเคราะห์แบบกำหนดเอง"""
    print("🔬 ตัวอย่างที่ 5: การวิเคราะห์แบบกำหนดเอง")
    print("=" * 50)
    
    analyzer = MultiExchangeMarketAnalyzer("config.json")
    
    if await analyzer.initialize():
        exchange_name = "binance"
        symbol = "BTC/USDT"
        
        # ดึงข้อมูล
        df = await analyzer.fetch_ohlc_data(exchange_name, symbol, "1m", 100)
        
        if df is not None and not df.empty:
            # คำนวณ indicators
            df = analyzer.calculate_technical_indicators(df)
            
            # การวิเคราะห์แบบกำหนดเอง
            latest = df.iloc[-1]
            
            # ตรวจสอบสัญญาณ Golden Cross
            sma_20 = latest.get('sma_20', 0)
            sma_50 = latest.get('sma_50', 0)
            
            if sma_20 > sma_50:
                print("🟢 Golden Cross: SMA 20 อยู่เหนือ SMA 50 (สัญญาณบวก)")
            else:
                print("🔴 Death Cross: SMA 20 อยู่ใต้ SMA 50 (สัญญาณลบ)")
            
            # ตรวจสอบ RSI
            rsi = latest.get('rsi', 50)
            if rsi > 70:
                print(f"⚠️ RSI Overbought: {rsi:.1f} (อาจมีการขาย)")
            elif rsi < 30:
                print(f"💡 RSI Oversold: {rsi:.1f} (อาจมีการซื้อ)")
            else:
                print(f"📊 RSI Neutral: {rsi:.1f}")
            
            # ตรวจสอบ Bollinger Bands
            bb_upper = latest.get('bb_upper', 0)
            bb_lower = latest.get('bb_lower', 0)
            current_price = latest['close']
            
            if current_price > bb_upper:
                print(f"🔥 ราคาเหนือ Bollinger Band บน (${bb_upper:,.2f})")
            elif current_price < bb_lower:
                print(f"❄️ ราคาใต้ Bollinger Band ล่าง (${bb_lower:,.2f})")
            else:
                print(f"📊 ราคาอยู่ในช่วง Bollinger Bands")
    
    print("\n")

async def example_6_bot_simulation():
    """ตัวอย่างที่ 6: จำลองการทำงานของบอท (ไม่เทรดจริง)"""
    print("🤖 ตัวอย่างที่ 6: จำลองการทำงานของบอท")
    print("=" * 50)
    
    bot = MultiExchangeTradingBot("config.json")
    
    if await bot.initialize():
        print("✅ เริ่มต้นบอทสำเร็จ!")
        
        # แสดงการตั้งค่าที่โหลดได้
        print(f"📋 Trading Config ที่โหลด:")
        for exchange_name, symbols in bot.trading_config.items():
            print(f"   {exchange_name}: {list(symbols.keys())}")
        
        # จำลองการประมวลผล 1 รอบ
        print(f"\n🔄 จำลองการประมวลผล...")
        
        for exchange_name in bot.exchange_manager.get_enabled_exchanges():
            trading_pairs = bot.exchange_manager.get_trading_pairs(exchange_name)
            
            for symbol in trading_pairs[:1]:  # ทดสอบแค่ 1 symbol
                print(f"   📊 ประมวลผล {exchange_name}:{symbol}")
                
                # ดึง config
                config = bot.trading_config.get(exchange_name, {}).get(symbol)
                if config and "error" not in config:
                    spreads = config.get('spreads', {})
                    print(f"      - Bid Spread: {spreads.get('bid_spread', 0):.2%}")
                    print(f"      - Ask Spread: {spreads.get('ask_spread', 0):.2%}")
                    print(f"      - Market Condition: {config.get('market_condition', 'unknown')}")
                else:
                    print(f"      ❌ ไม่มี config หรือมีข้อผิดพลาด")
                
                break  # ทดสอบแค่ 1 symbol ต่อ exchange
    else:
        print("❌ ไม่สามารถเริ่มต้นบอทได้")
    
    print("\n")

async def main():
    """ฟังก์ชันหลักสำหรับรันตัวอย่างทั้งหมด"""
    print("🚀 Multi-Exchange Trading Bot - ตัวอย่างการใช้งาน")
    print("=" * 60)
    print()
    
    try:
        # รันตัวอย่างทีละอัน
        await example_1_basic_connection()
        await example_2_market_analysis()
        await example_3_single_exchange_data()
        await example_4_price_comparison()
        await example_5_custom_analysis()
        await example_6_bot_simulation()
        
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