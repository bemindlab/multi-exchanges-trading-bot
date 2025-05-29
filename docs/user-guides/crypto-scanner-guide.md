# 🔍 Crypto Pairs Scanner - คู่มือการใช้งาน

ระบบสแกนคู่เทรด cryptocurrency ด้วยสัญญาณ MACD เพื่อหาโอกาสการเทรด Long และ Short positions

## ✨ ฟีเจอร์หลัก

### 📊 MACD Signal Detection
- **MACD Cross Up (Long Signal)**: เมื่อ MACD เส้นหลักข้ามขึ้นเหนือ 0
- **MACD Cross Down (Short Signal)**: เมื่อ MACD เส้นหลักข้ามลงใต้ 0
- **Signal Strength**: คำนวณความแรงของสัญญาณ 0-100%
- **Volume Filter**: กรองตามปริมาณการเทรด 24 ชั่วโมง

### 🎯 การปรับแต่งได้
- **Timeframes**: เลือก timeframes ที่ต้องการ (15m, 1h, 4h, 1d, etc.)
- **Exchanges**: รองรับหลาย CEX (Binance, Gate.io, OKX, etc.)
- **Trading Pairs**: กำหนดคู่เทรดที่สนใจ
- **MACD Settings**: ปรับค่า Fast, Slow, Signal periods
- **Filters**: ตั้งค่าความแรงสัญญาณและปริมาณขั้นต่ำ

### 🔄 โหมดการทำงาน
- **Single Scan**: สแกนครั้งเดียว
- **Continuous Scan**: สแกนอย่างต่อเนื่อง
- **Single Pair Check**: ตรวจสอบคู่เทรดเฉพาะ
- **Export Results**: ส่งออกผลลัพธ์เป็น JSON

## 🚀 การใช้งาน

### 1. การสแกนพื้นฐาน

```bash
# สแกนด้วยการตั้งค่าเริ่มต้น
python cli.py scan

# สแกนใน timeframes เฉพาะ
python cli.py scan -t 1h -t 4h -t 1d

# กำหนดความแรงสัญญาณขั้นต่ำ
python cli.py scan -s 70

# กำหนดปริมาณการเทรดขั้นต่ำ
python cli.py scan -v 500000
```

### 2. การตรวจสอบคู่เทรดเฉพาะ

```bash
# ตรวจสอบ BTC/USDT ใน timeframe 1h
python cli.py macd-check -s BTC/USDT -t 1h

# ตรวจสอบใน exchange เฉพาะ
python cli.py macd-check -s ETH/USDT -t 4h -e binance

# ตรวจสอบใน timeframe 1d
python cli.py macd-check -s BNB/USDT -t 1d
```

### 3. การสแกนอย่างต่อเนื่อง

```bash
# สแกนทุก 15 นาที (เริ่มต้น)
python cli.py scan-continuous

# สแกนทุก 30 นาที
python cli.py scan-continuous -i 30

# สแกนใน timeframes เฉพาะ
python cli.py scan-continuous -t 1h -t 4h
```

### 4. การใช้งานแบบ Advanced

```bash
# สแกนเฉพาะ exchanges ที่ต้องการ
python cli.py scan -e binance -e gateio

# รวมการตั้งค่าหลายอย่าง
python cli.py scan -t 1h -t 4h -s 60 -v 200000 -e binance
```

## 📊 การตีความผลลัพธ์

### สัญญาณ Long (🟢)
```
🟢 TOP 5 LONG SIGNALS (MACD Cross Up)
--------------------------------------------------------------------------------
1. BTC/USDT (BINANCE) - 1h
   💰 ราคา: $43,250.50 | 📊 ความแรง: 75.2%
   📈 MACD: 0.000123 | Signal: -0.000045
   📅 เวลา: 2024-01-15 14:30:00
```

**การตีความ:**
- MACD เพิ่งข้ามขึ้นเหนือ 0 (สัญญาณ bullish)
- ความแรงสัญญาณ 75.2% (ค่อนข้างแรง)
- เหมาะสำหรับการเปิด Long position

### สัญญาณ Short (🔴)
```
🔴 TOP 5 SHORT SIGNALS (MACD Cross Down)
--------------------------------------------------------------------------------
1. ETH/USDT (BINANCE) - 4h
   💰 ราคา: $2,580.75 | 📊 ความแรง: 68.9%
   📉 MACD: -0.000089 | Signal: 0.000034
   📅 เวลา: 2024-01-15 12:00:00
```

**การตีความ:**
- MACD เพิ่งข้ามลงใต้ 0 (สัญญาณ bearish)
- ความแรงสัญญาณ 68.9% (ค่อนข้างแรง)
- เหมาะสำหรับการเปิด Short position

## ⚙️ การตั้งค่า

### การปรับแต่ง MACD
```python
# ใน crypto_scanner.py
scanner.update_config(
    macd_fast=12,        # EMA เร็ว (เริ่มต้น: 12)
    macd_slow=26,        # EMA ช้า (เริ่มต้น: 26)
    macd_signal_period=9 # Signal line (เริ่มต้น: 9)
)
```

### การกรองสัญญาณ
```python
scanner.update_config(
    min_signal_strength=60,  # ความแรงขั้นต่ำ 60%
    min_volume_24h=100000,   # ปริมาณขั้นต่ำ 100,000 USDT
    timeframes=['1h', '4h'], # Timeframes ที่ต้องการ
    exchanges=['binance']    # Exchanges ที่ต้องการ
)
```

### คู่เทรดที่รองรับ (เริ่มต้น)
```python
trading_pairs = [
    'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT',
    'XRP/USDT', 'DOT/USDT', 'AVAX/USDT', 'MATIC/USDT', 'LINK/USDT',
    'UNI/USDT', 'LTC/USDT', 'BCH/USDT', 'ALGO/USDT', 'VET/USDT',
    'FTM/USDT', 'ATOM/USDT', 'NEAR/USDT', 'SAND/USDT', 'MANA/USDT'
]
```

## 📁 ไฟล์ผลลัพธ์

### JSON Export Format
```json
{
  "scan_time": "2024-01-15T14:30:00",
  "config": {
    "timeframes": ["1h", "4h"],
    "exchanges": ["binance", "gateio"],
    "min_signal_strength": 60,
    "macd_settings": {
      "fast": 12,
      "slow": 26,
      "signal": 9
    }
  },
  "signals": {
    "binance_1h": [
      {
        "symbol": "BTC/USDT",
        "exchange": "binance",
        "timeframe": "1h",
        "signal_type": "long",
        "price": 43250.50,
        "strength": 75.2,
        "macd_value": 0.000123,
        "macd_signal": -0.000045,
        "macd_histogram": 0.000168,
        "volume_24h": 1250000,
        "timestamp": "2024-01-15T14:30:00"
      }
    ]
  }
}
```

## 🎯 กลยุทธ์การใช้งาน

### 1. Scalping (15m - 1h)
```bash
python cli.py scan -t 15m -t 1h -s 70 -v 500000
```
- ใช้ timeframes สั้น
- ความแรงสัญญาณสูง (70%+)
- ปริมาณการเทรดสูง

### 2. Swing Trading (4h - 1d)
```bash
python cli.py scan -t 4h -t 1d -s 60 -v 200000
```
- ใช้ timeframes ยาว
- ความแรงสัญญาณปานกลาง (60%+)
- เน้นเทรนด์ระยะกลาง

### 3. Position Trading (1d - 1w)
```bash
python cli.py scan -t 1d -s 50 -v 100000
```
- ใช้ timeframes ยาวมาก
- ความแรงสัญญาณต่ำ (50%+)
- เน้นเทรนด์ระยะยาว

## 🔧 การแก้ไขปัญหา

### ไม่พบสัญญาณ
1. **ลดความแรงสัญญาณ**: `-s 30` แทน `-s 60`
2. **เพิ่ม timeframes**: `-t 15m -t 1h -t 4h -t 1d`
3. **ลดปริมาณขั้นต่ำ**: `-v 50000` แทน `-v 100000`

### ข้อผิดพลาดการเชื่อมต่อ
1. **ตรวจสอบ internet connection**
2. **ตรวจสอบ API limits** ของ exchange
3. **ใช้ VPN** หากมีการบล็อก IP

### สัญญาณไม่แม่นยำ
1. **ปรับการตั้งค่า MACD**: ทดสอบค่า fast/slow ต่างๆ
2. **เพิ่มความแรงสัญญาณ**: ใช้ `-s 70` หรือสูงกว่า
3. **รวมกับ indicators อื่น**: ใช้ร่วมกับ RSI, Volume

## 📚 ตัวอย่างการใช้งาน

### ตัวอย่างที่ 1: หาสัญญาณ Long ใน Major Coins
```bash
python cli.py scan -t 1h -t 4h -s 65 -e binance
```

### ตัวอย่างที่ 2: ตรวจสอบ BTC ทุก timeframes
```bash
python cli.py macd-check -s BTC/USDT -t 15m
python cli.py macd-check -s BTC/USDT -t 1h
python cli.py macd-check -s BTC/USDT -t 4h
python cli.py macd-check -s BTC/USDT -t 1d
```

### ตัวอย่างที่ 3: การติดตามแบบ Real-time
```bash
# เริ่มการสแกนต่อเนื่อง
python cli.py scan-continuous -i 15 -t 1h -s 60

# ใน terminal อื่น ตรวจสอบสัญญาณเฉพาะ
python cli.py macd-check -s ETH/USDT -t 1h
```

## ⚠️ ข้อควรระวัง

### การใช้งานสัญญาณ
1. **ไม่ใช่คำแนะนำการลงทุน**: สัญญาณเป็นเพียงเครื่องมือช่วยวิเคราะห์
2. **ใช้ร่วมกับ indicators อื่น**: MACD เพียงอย่างเดียวอาจไม่เพียงพอ
3. **จัดการความเสี่ยง**: ตั้ง stop loss และ take profit เสมอ
4. **ทดสอบก่อนใช้จริง**: ใช้ paper trading ก่อนลงทุนจริง

### ข้อจำกัดทางเทคนิค
1. **Rate Limits**: อาจมีการจำกัดการเรียก API
2. **Market Hours**: บาง exchanges อาจมีช่วงเวลาปิด
3. **Data Delays**: ข้อมูลอาจล่าช้าเล็กน้อย
4. **False Signals**: สัญญาณอาจผิดพลาดในตลาดที่ผันผวนสูง

## 🔄 การอัปเดตและพัฒนา

### ฟีเจอร์ที่กำลังพัฒนา
- [ ] รองรับ indicators เพิ่มเติม (RSI, Bollinger Bands)
- [ ] การแจ้งเตือนผ่าน Telegram
- [ ] Web dashboard สำหรับดูผลลัพธ์
- [ ] Backtesting สำหรับทดสอบกลยุทธ์
- [ ] การเชื่อมต่อกับ DEX

### การมีส่วนร่วม
1. **Report Issues**: แจ้งปัญหาผ่าน GitHub Issues
2. **Feature Requests**: เสนอฟีเจอร์ใหม่
3. **Code Contributions**: ส่ง Pull Requests
4. **Documentation**: ช่วยปรับปรุงเอกสาร

---

**Happy Trading! 🚀📈**

*หมายเหตุ: การเทรดมีความเสี่ยง กรุณาศึกษาและทำความเข้าใจก่อนลงทุน* 