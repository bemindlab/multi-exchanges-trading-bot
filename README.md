# 🤖 Multi-Exchange Trading Bot v2.0

บอทเทรดดิ้งอัตโนมัติที่รองรับการเทรดใน **CEX และ DEX หลายแห่งพร้อมกัน** พร้อมระบบวิเคราะห์ตลาดแบบ real-time และการจัดการความเสี่ยงอัตโนมัติ

## ✨ ฟีเจอร์หลัก

### 🏢 รองรับ Exchanges หลายแห่ง
- **CEX (Centralized Exchanges):**
  - Binance
  - Gate.io
  - OKX
  - KuCoin
  - Bybit
  - Huobi

- **DEX (Decentralized Exchanges):**
  - Uniswap V3 (Ethereum)
  - PancakeSwap (BSC)
  - SushiSwap (Multi-chain)
  - QuickSwap (Polygon)

### 🔍 Crypto Pairs Scanner
- **MACD Signal Detection**: หาสัญญาณ Long/Short จาก MACD crosses
- **Multi-Timeframe Scanning**: สแกนใน timeframes หลายช่วง
- **Signal Strength Calculation**: คำนวณความแรงสัญญาณ 0-100%
- **Volume Filtering**: กรองตามปริมาณการเทรด
- **Real-time Monitoring**: ติดตามสัญญาณแบบต่อเนื่อง
- **Export Results**: ส่งออกผลลัพธ์เป็น JSON

### 📊 ระบบวิเคราะห์ตลาดขั้นสูง
- **Technical Indicators:**
  - Moving Averages (SMA, EMA)
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - Bollinger Bands
  - ATR (Average True Range)

- **Market Analysis:**
  - Trend Analysis (Bullish/Bearish/Sideways)
  - Momentum Analysis
  - Support/Resistance Levels
  - Volatility Assessment

### 🎯 กลยุทธ์การเทรด
- **Market Making:** วางออเดอร์ bid/ask อัตโนมัติ
- **Dynamic Spread Adjustment:** ปรับ spread ตามสภาพตลาด
- **Multi-Level Orders:** วางออเดอร์หลายระดับ
- **Auto Config Generation:** สร้างการตั้งค่าอัตโนมัติตามการวิเคราะห์

### 🛡️ การจัดการความเสี่ยง
- **Stop Loss/Take Profit:** ตั้งค่าอัตโนมัติ
- **Position Size Management:** จำกัดขนาดการเทรด
- **Daily Loss Limits:** จำกัดการสูญเสียรายวัน
- **Balance Monitoring:** ติดตามยอดเงินแบบ real-time

## 🚀 การติดตั้ง

### 1. Clone Repository
```bash
git clone https://github.com/your-repo/multi-exchanges-trading-bot.git
cd multi-exchanges-trading-bot
```

### 2. ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

### 3. ตั้งค่าเริ่มต้น
```bash
# Copy environment template
cp env.example .env

# Setup configuration (auto-creates from template)
python cli.py setup
```

### 4. ตรวจสอบการตั้งค่า
```bash
# Check configuration
python cli.py config --action summary

# Test connections (if API keys provided)
python cli.py test-connection
```

**📖 สำหรับคำแนะนำการติดตั้งแบบละเอียด ดู [QUICK_START.md](QUICK_START.md)**

### 5. แก้ไขไฟล์ .env (ถ้าต้องการใช้ API จริง)
```bash
# CEX API Keys
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET=your_binance_secret_here
BINANCE_SANDBOX=true

GATEIO_API_KEY=your_gateio_api_key_here
GATEIO_SECRET=your_gateio_secret_here
GATEIO_SANDBOX=true

# DEX Settings
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
ETHEREUM_PRIVATE_KEY=your_ethereum_private_key_here

# Telegram Bot (สำหรับการแจ้งเตือน)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
```

## 📖 การใช้งาน

### คำสั่ง CLI พื้นฐาน

#### 1. ดูรายการ Exchanges ที่รองรับ
```bash
python cli.py list-exchanges
```

#### 2. ตรวจสอบสถานะการเชื่อมต่อ
```bash
python cli.py status
```

#### 3. ทดสอบการเชื่อมต่อ
```bash
python cli.py test-connection
```

#### 4. ดูยอดเงินคงเหลือ
```bash
# ดูทุก exchanges
python cli.py balance

# ดูเฉพาะ exchange ที่ระบุ
python cli.py balance -e binance
```

### 🔍 คำสั่ง Crypto Scanner

#### 1. ดูคำสั่งที่มี
```bash
python cli.py scan --help
python cli.py macd-check --help
python cli.py scan-continuous --help
```

#### 2. สแกนหาสัญญาณ MACD
```bash
# สแกนพื้นฐาน (timeframes: 1h, 4h, 1d)
python cli.py scan

# สแกนใน timeframes เฉพาะ
python cli.py scan -t 15m -t 1h -t 4h

# กำหนดความแรงสัญญาณขั้นต่ำ
python cli.py scan -s 70

# สแกนเฉพาะ exchanges ที่ต้องการ
python cli.py scan -e binance -e gateio
```

#### 3. ตรวจสอบคู่เทรดเฉพาะ
```bash
# ตรวจสอบ BTC/USDT ใน timeframe 1h
python cli.py macd-check -s BTC/USDT -t 1h

# ตรวจสอบใน exchange เฉพาะ
python cli.py macd-check -s ETH/USDT -t 4h -e binance
```

#### 4. การสแกนอย่างต่อเนื่อง
```bash
# สแกนทุก 15 นาที
python cli.py scan-continuous

# สแกนทุก 30 นาที
python cli.py scan-continuous -i 30
```

### การวิเคราะห์ตลาด

#### 1. วิเคราะห์ครั้งเดียว
```bash
python cli.py analyze -s BTC/USDT
```

#### 2. ติดตามตลาดแบบต่อเนื่อง
```bash
# ติดตามทุก 5 นาที (300 วินาที)
python cli.py monitor -s BTC/USDT -i 300
```

### 🔍 Crypto Pairs Scanner (ใหม่!)

#### 1. สแกนหาสัญญาณ MACD
```bash
# สแกนพื้นฐาน
python cli.py scan

# สแกนใน timeframes เฉพาะ
python cli.py scan -t 1h -t 4h -s 60

# สแกนอย่างต่อเนื่อง
python cli.py scan-continuous -i 15
```

#### 2. ตรวจสอบคู่เทรดเฉพาะ
```bash
# ตรวจสอบสัญญาณ MACD ของ BTC/USDT
python cli.py macd-check -s BTC/USDT -t 1h

# ตรวจสอบใน exchange เฉพาะ
python cli.py macd-check -s ETH/USDT -t 4h -e binance
```

### การเทรดอัตโนมัติ

#### 1. เริ่มการเทรด (โหมดทดสอบ)
```bash
python cli.py trade --dry-run
```

#### 2. เริ่มการเทรดจริง
```bash
python cli.py trade
```

## ⚙️ การตั้งค่า

### ไฟล์ config.json
```json
{
    "exchanges": {
        "binance": {
            "enabled": true,
            "type": "cex",
            "trading_pairs": ["BTC/USDT", "ETH/USDT"],
            "min_order_amount": 10.0,
            "max_order_amount": 1000.0,
            "fee_rate": 0.001
        },
        "uniswap_v3": {
            "enabled": true,
            "type": "dex",
            "network": "ethereum",
            "trading_pairs": ["WETH/USDC"],
            "slippage": 0.005,
            "gas_limit": 300000
        }
    },
    "trading_strategy": {
        "strategy_type": "market_making",
        "timeframe": "1m",
        "risk_management": {
            "max_position_size": 0.1,
            "stop_loss": 0.02,
            "take_profit": 0.03,
            "max_daily_loss": 0.05
        }
    }
}
```

### การตั้งค่า Spread แบบ Dynamic
บอทจะปรับ spread อัตโนมัติตามสภาพตลาด:

- **High Volatility:** Bid 0.3%, Ask 0.4%
- **Low Volatility:** Bid 0.1%, Ask 0.15%
- **Bullish Momentum:** Bid 0.2%, Ask 0.25%
- **Bearish Momentum:** Bid 0.25%, Ask 0.3%
- **Sideways:** Bid 0.15%, Ask 0.2%

## 📊 ตัวอย่างผลลัพธ์

### การวิเคราะห์ตลาด
```
================================================================================
📊 สรุปผลการวิเคราะห์ตลาดจากหลาย Exchange
================================================================================

🏢 BINANCE
----------------------------------------
💰 ราคาปัจจุบัน: $43,250.50
📈 เปลี่ยนแปลง 24h: +2.35%
📊 ความผันผวน: 3.20%
📈 เทรนด์: bullish
⚡ Momentum: neutral
📊 RSI: 65.2
🌡️ สภาพตลาด: bullish_momentum

💡 คำแนะนำการตั้งค่า:
   - Bid Spread: 0.20%
   - Ask Spread: 0.25%
   - Stop Loss: 1.50%
   - กำไรคาดหวัง: 0.25%
```

### รายงานสถานะการเทรด
```
================================================================================
📊 รายงานสถานะ Multi-Exchange Trading Bot
================================================================================
⏰ เวลา: 2024-01-15 14:30:25

🏢 BINANCE
----------------------------------------
📈 การเทรดทั้งหมด: 45
✅ การเทรดที่ทำกำไร: 32
📊 อัตราชนะ: 71.1%
💰 กำไรรวม: $125.50
📋 ออเดอร์ที่เปิดอยู่: 6
💳 USDT: 1250.0000
💳 BTC: 0.0285
```

## 🔧 การพัฒนาเพิ่มเติม

### เพิ่ม Exchange ใหม่
1. เพิ่มการตั้งค่าใน `config.json`
2. อัปเดต `ExchangeManager` สำหรับ CEX
3. สำหรับ DEX ต้องเพิ่ม smart contract integration

### เพิ่มกลยุทธ์ใหม่
1. สร้างคลาสใหม่ใน `bots/strategies/`
2. อัปเดต `MultiExchangeTradingBot`
3. เพิ่มการตั้งค่าใน config

### เพิ่ม Indicator ใหม่
1. อัปเดต `calculate_technical_indicators()` ใน `MarketAnalyzer`
2. เพิ่มการวิเคราะห์ใน `analyze_market_condition()`

## 🛡️ ความปลอดภัย

### การจัดเก็บ API Keys
- ใช้ไฟล์ `.env` สำหรับเก็บ API keys
- ไม่เก็บ private keys ในโค้ด
- รองรับ sandbox mode สำหรับการทดสอบ

### การจัดการความเสี่ยง
- จำกัดขนาดออเดอร์สูงสุด
- ตั้งค่า stop loss อัตโนมัติ
- ติดตามการสูญเสียรายวัน
- ยกเลิกออเดอร์อัตโนมัติเมื่อหยุดบอท

## 📚 เอกสารประกอบ

📖 **เอกสารครบถ้วนอยู่ในโฟลเดอร์ [docs/](docs/)**

### 🚀 เริ่มต้นใช้งาน
- **[Installation Guide](docs/INSTALLATION.md)** - คู่มือการติดตั้งและตั้งค่า
- **[CLI Commands](docs/CLI_COMMANDS.md)** - คำสั่ง Command Line ทั้งหมด
- **[FAQ](docs/FAQ.md)** - คำถามที่พบบ่อย

### 🔍 Crypto Scanner
- **[Crypto Scanner Guide](docs/CRYPTO_SCANNER_GUIDE.md)** - คู่มือการใช้งาน MACD Scanner
- **[Scanner Examples](docs/SCANNER_EXAMPLES.md)** - ตัวอย่างการใช้งาน Scanner

### 📊 การพัฒนาและอัปเดต
- **[Changelog](docs/CHANGELOG.md)** - บันทึกการเปลี่ยนแปลง
- **[Upgrade Summary](docs/UPGRADE_SUMMARY.md)** - สรุปการอัปเกรดเป็น v2.0

## 📞 การสนับสนุน

### การแจ้งปัญหา
- ตรวจสอบ **[FAQ](docs/FAQ.md)** ก่อน
- ดูเอกสารใน **[docs/](docs/)** folder
- สร้าง Issue ใน GitHub พร้อม log files และการตั้งค่า
- อธิบายขั้นตอนการทำซ้ำ

### การพัฒนา
- Fork repository
- สร้าง feature branch
- ส่ง Pull Request
- ดู **[Contributing Guide](docs/CONTRIBUTING.md)**

## 📄 License

MIT License - ดูรายละเอียดใน [LICENSE](LICENSE)

## ⚠️ คำเตือน

**การเทรดมีความเสี่ยง** - โปรดทำความเข้าใจและทดสอบในโหมด sandbox ก่อนใช้เงินจริง

- ทดสอบกลยุทธ์ในโหมด dry-run ก่อน
- เริ่มต้นด้วยจำนวนเงินน้อย
- ติดตามผลการเทรดอย่างสม่ำเสมอ
- ตั้งค่า stop loss ที่เหมาะสม

---

**Happy Trading! 🚀📈** 

**สนใจบริจาก เมื่อคุณได้กำไรจากเทรด**
- นำไปใช้พัฒนาต่อยอด
- นำไปบริจาคให้มูลนิธิ ต่างๆเพื่อสังคม

**สามารถบริจาคได้ทุกเหรียญที่คุณสะดวกมาที่**

BTC: 3FyZeWU8tSdAZ81zX18knePSXEooGYPZsY
  
SOLANA: EFgZDyosYVzf8afx68qYFaeDWHhVbFs7wXJNh2x4NTzP

EVM (ETH,BNB,Polygon,etc): 0x2aBf33658053eF646aeA29F067783Ab1a9Cf5025

TRON: TRvC3bMfm5dtjMUmDfQZyHELf7SqtrjN2e

TON: UQBXaFHEwFHOOTmiTrGwA8DSgoofTO1KlAWl42Pui47Roxnd