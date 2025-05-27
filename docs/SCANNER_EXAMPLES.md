# 🔍 Crypto Scanner Examples - ตัวอย่างการใช้งาน

ตัวอย่างการใช้งาน Crypto Pairs Scanner ด้วยสัญญาณ MACD ในสถานการณ์ต่างๆ

## 📚 ตัวอย่างทั้งหมด

### 🎯 ตัวอย่างที่ 1: การสแกนพื้นฐาน
การสแกนหาสัญญาณ MACD แบบพื้นฐานที่สุด

```python
#!/usr/bin/env python3
import asyncio
from bots.crypto_scanner import CryptoPairsScanner

async def basic_scan_example():
    """ตัวอย่างการสแกนพื้นฐาน"""
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

# รันตัวอย่าง
asyncio.run(basic_scan_example())
```

**ผลลัพธ์ที่คาดหวัง:**
```
🔍 ผลการสแกน MACD Signals
================================================================================
📊 สรุป: สัญญาณทั้งหมด 8 | Long: 5 | Short: 3

🟢 TOP 5 LONG SIGNALS (MACD Cross Up)
--------------------------------------------------------------------------------
1. BTC/USDT (BINANCE) - 1h
   💰 ราคา: $43,250.50 | 📊 ความแรง: 75.2%
   📈 MACD: 0.000123 | Signal: -0.000045
   📅 เวลา: 2024-01-15 14:30:00
```

### 🎯 ตัวอย่างที่ 2: สแกนคู่เทรดที่กำหนดเอง
การเลือกคู่เทรดที่สนใจเฉพาะ

```python
async def custom_pairs_example():
    """ตัวอย่างการสแกนคู่เทรดที่กำหนดเอง"""
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
```

### 🎯 ตัวอย่างที่ 3: ตรวจสอบคู่เทรดเดียว
การวิเคราะห์คู่เทรดเฉพาะอย่างละเอียด

```python
async def single_pair_check_example():
    """ตัวอย่างการตรวจสอบคู่เทรดเดียว"""
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
```

### 🎯 ตัวอย่างที่ 4: เปรียบเทียบ Timeframes
การวิเคราะห์สัญญาณในช่วงเวลาต่างๆ

```python
async def timeframe_comparison_example():
    """ตัวอย่างการเปรียบเทียบ timeframes"""
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
```

### 🎯 ตัวอย่างที่ 5: ส่งออกสัญญาณ
การบันทึกและส่งออกผลลัพธ์

```python
async def export_signals_example():
    """ตัวอย่างการส่งออกสัญญาณ"""
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
```

### 🎯 ตัวอย่างที่ 6: ปรับการตั้งค่า MACD
การทดสอบการตั้งค่า MACD ต่างๆ

```python
async def macd_settings_example():
    """ตัวอย่างการปรับการตั้งค่า MACD"""
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
```

### 🎯 ตัวอย่างที่ 7: การติดตามแบบ Real-time
การติดตามสัญญาณแบบต่อเนื่อง

```python
async def real_time_monitoring_example():
    """ตัวอย่างการติดตามแบบ real-time"""
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
```

## 🚀 การใช้งานผ่าน CLI

### ตัวอย่างคำสั่ง CLI พื้นฐาน

```bash
# สแกนพื้นฐาน
python cli.py scan

# สแกนใน timeframes เฉพาะ
python cli.py scan -t 1h -t 4h

# สแกนเฉพาะ exchanges
python cli.py scan -e binance -e gateio

# กำหนดความแรงสัญญาณขั้นต่ำ
python cli.py scan -s 70

# ตรวจสอบคู่เทรดเฉพาะ
python cli.py macd-check -s BTC/USDT -t 1h

# สแกนอย่างต่อเนื่อง
python cli.py scan-continuous -i 15
```

### ตัวอย่างการใช้งานขั้นสูง

```bash
# สแกนหาสัญญาณแรงๆ ในคู่เทรดหลัก
python cli.py scan -t 1h -t 4h -s 75 -v 1000000 -e binance

# ติดตามสัญญาณ BTC และ ETH
python cli.py macd-check -s BTC/USDT -t 1h -e binance
python cli.py macd-check -s ETH/USDT -t 1h -e binance

# สแกนต่อเนื่องทุก 10 นาที
python cli.py scan-continuous -i 10 -t 15m -t 1h
```

## 📊 การตีความผลลัพธ์

### สัญญาณ Long (MACD Cross Up)
```
🟢 LONG SIGNAL
Symbol: BTC/USDT (BINANCE) - 1h
Price: $43,250.50 | Strength: 75.2%
MACD: 0.000123 | Signal: -0.000045
Time: 2024-01-15 14:30:00
```

**การตีความ:**
- **MACD > 0**: แนวโน้มขาขึ้น
- **MACD > Signal**: momentum เพิ่มขึ้น
- **Strength 75.2%**: สัญญาณแรงมาก
- **แนะนำ**: พิจารณา Long position

### สัญญาณ Short (MACD Cross Down)
```
🔴 SHORT SIGNAL
Symbol: ETH/USDT (GATEIO) - 4h
Price: $2,580.75 | Strength: 68.9%
MACD: -0.000089 | Signal: 0.000034
Time: 2024-01-15 12:00:00
```

**การตีความ:**
- **MACD < 0**: แนวโน้มขาลง
- **MACD < Signal**: momentum ลดลง
- **Strength 68.9%**: สัญญาณค่อนข้างแรง
- **แนะนำ**: พิจารณา Short position

## 🎯 กลยุทธ์การใช้งาน

### 1. Scalping Strategy (15m - 1h)
```bash
# สแกนหาสัญญาณระยะสั้น
python cli.py scan -t 15m -t 1h -s 80 -v 2000000

# ติดตามต่อเนื่องทุก 5 นาที
python cli.py scan-continuous -i 5 -t 15m
```

### 2. Swing Trading Strategy (4h - 1d)
```bash
# สแกนหาสัญญาณระยะกลาง
python cli.py scan -t 4h -t 1d -s 65 -v 500000

# ติดตามทุก 30 นาที
python cli.py scan-continuous -i 30 -t 4h
```

### 3. Position Trading Strategy (1d - 1w)
```bash
# สแกนหาสัญญาณระยะยาว
python cli.py scan -t 1d -t 1w -s 60 -v 1000000

# ติดตามทุก 2 ชั่วโมง
python cli.py scan-continuous -i 120 -t 1d
```

## 🔧 การปรับแต่งขั้นสูง

### การตั้งค่า MACD สำหรับ Timeframes ต่างๆ

```python
# สำหรับ Scalping (15m - 1h)
scanner.update_config(
    macd_fast=8,
    macd_slow=21,
    macd_signal_period=5,
    min_signal_strength=80
)

# สำหรับ Swing Trading (4h - 1d)
scanner.update_config(
    macd_fast=12,
    macd_slow=26,
    macd_signal_period=9,
    min_signal_strength=65
)

# สำหรับ Position Trading (1d+)
scanner.update_config(
    macd_fast=19,
    macd_slow=39,
    macd_signal_period=9,
    min_signal_strength=60
)
```

### การกรองสัญญาณคุณภาพสูง

```python
# กรองเฉพาะสัญญาณที่แรงและมีปริมาณการเทรดสูง
scanner.update_config(
    min_signal_strength=75,
    min_volume_24h=1000000,
    trading_pairs=['BTC/USDT', 'ETH/USDT', 'BNB/USDT']  # เฉพาะคู่หลัก
)
```

## 📈 การรวมกับกลยุทธ์อื่น

### การใช้ร่วมกับ RSI
```python
# ตรวจสอบ RSI เพิ่มเติม
df = await scanner.fetch_ohlcv_data('binance', 'BTC/USDT', '1h', 100)
df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()

# สัญญาณ Long + RSI < 30 (Oversold)
# สัญญาณ Short + RSI > 70 (Overbought)
```

### การใช้ร่วมกับ Volume
```python
# ตรวจสอบ Volume spike
df['volume_sma'] = df['volume'].rolling(20).mean()
df['volume_ratio'] = df['volume'] / df['volume_sma']

# สัญญาณ + Volume > 1.5x average = สัญญาณแรงขึ้น
```

## ⚠️ ข้อควรระวัง

### 1. False Signals
- MACD อาจให้สัญญาณผิดในตลาด sideways
- ใช้ร่วมกับ indicators อื่นเพื่อยืนยัน

### 2. Market Conditions
- สัญญาณใน trending market มีความแม่นยำสูงกว่า
- ระวังสัญญาณใน ranging market

### 3. Risk Management
- ตั้ง stop loss เสมอ
- ไม่ใช้เงินทั้งหมดในการเทรด
- กระจายความเสี่ยงในหลายคู่เทรด

---

**Happy Trading! 🚀📈**

*สำหรับข้อมูลเพิ่มเติม ดู [Crypto Scanner Guide](CRYPTO_SCANNER_GUIDE.md)* 