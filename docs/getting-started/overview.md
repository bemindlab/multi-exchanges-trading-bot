# 🤖 Multi-Exchange Trading Bot v2.0 - Documentation

ยินดีต้อนรับสู่เอกสารประกอบของ Multi-Exchange Trading Bot v2.0 ระบบบอทเทรดดิ้งอัตโนมัติที่รองรับการเทรดใน CEX และ DEX หลายแห่งพร้อมกัน

## 📚 เอกสารทั้งหมด

### 🚀 การเริ่มต้น
- **[Installation Guide](INSTALLATION.md)** - คู่มือการติดตั้งและตั้งค่าเริ่มต้น
- **[Quick Start](QUICK_START.md)** - เริ่มใช้งานอย่างรวดเร็ว
- **[Configuration](CONFIGURATION.md)** - การตั้งค่าระบบ

### 🔍 Crypto Scanner
- **[Crypto Scanner Guide](CRYPTO_SCANNER_GUIDE.md)** - คู่มือการใช้งาน MACD Scanner
- **[Scanner Examples](SCANNER_EXAMPLES.md)** - ตัวอย่างการใช้งาน Scanner

### 🏢 Exchange Integration
- **[Exchange Setup](EXCHANGE_SETUP.md)** - การตั้งค่า API keys สำหรับ exchanges
- **[Supported Exchanges](SUPPORTED_EXCHANGES.md)** - รายการ exchanges ที่รองรับ

### 📊 Trading Strategies
- **[Market Making Strategy](MARKET_MAKING.md)** - กลยุทธ์ Market Making
- **[Risk Management](RISK_MANAGEMENT.md)** - การจัดการความเสี่ยง
- **[Technical Analysis](TECHNICAL_ANALYSIS.md)** - การวิเคราะห์ทางเทคนิค

### 🔧 Development
- **[API Reference](API_REFERENCE.md)** - เอกสาร API และฟังก์ชัน
- **[Architecture](ARCHITECTURE.md)** - สถาปัตยกรรมของระบบ
- **[Contributing](CONTRIBUTING.md)** - การมีส่วนร่วมในการพัฒนา

### 📈 Advanced Features
- **[Dashboard Guide](DASHBOARD.md)** - การใช้งาน Web Dashboard
- **[CLI Commands](CLI_COMMANDS.md)** - คำสั่ง Command Line Interface
- **[Automation](AUTOMATION.md)** - การทำงานอัตโนมัติ

### 🔄 Migration & Updates
- **[Upgrade Summary](UPGRADE_SUMMARY.md)** - สรุปการปรับปรุงเป็น v2.0
- **[Migration Guide](MIGRATION.md)** - คู่มือการย้ายจากเวอร์ชันเก่า
- **[Changelog](CHANGELOG.md)** - บันทึกการเปลี่ยนแปลง

### 🛠️ Troubleshooting
- **[FAQ](FAQ.md)** - คำถามที่พบบ่อย
- **[Troubleshooting](TROUBLESHOOTING.md)** - การแก้ไขปัญหา
- **[Error Codes](ERROR_CODES.md)** - รหัสข้อผิดพลาดและการแก้ไข

## 🎯 ฟีเจอร์หลัก

### 🏢 Multi-Exchange Support
- **6 CEX**: Binance, Gate.io, OKX, KuCoin, Bybit, Huobi
- **4 DEX**: Uniswap V3, PancakeSwap, SushiSwap, QuickSwap
- **Unified API**: ใช้งานผ่าน interface เดียว

### 🔍 Crypto Pairs Scanner
- **MACD Signal Detection**: หาสัญญาณ Long/Short
- **Multi-Timeframe**: สแกนหลาย timeframes พร้อมกัน
- **Signal Strength**: คำนวณความแรงสัญญาณ 0-100%
- **Real-time Monitoring**: ติดตามแบบต่อเนื่อง

### 📊 Advanced Analytics
- **Technical Indicators**: SMA, EMA, RSI, MACD, Bollinger Bands
- **Market Analysis**: Trend, Momentum, Support/Resistance
- **Performance Tracking**: ติดตามผลการเทรด
- **Risk Metrics**: วัดความเสี่ยงแบบ real-time

### 🎯 Trading Strategies
- **Market Making**: วางออเดอร์ bid/ask อัตโนมัติ
- **Dynamic Spread**: ปรับ spread ตามสภาพตลาด
- **Risk Management**: Stop loss, Take profit, Position sizing
- **Multi-Level Orders**: วางออเดอร์หลายระดับ

## 🚀 Quick Start

### 1. ติดตั้งระบบ
```bash
# Clone repository
git clone https://github.com/your-repo/trading-bots.git
cd trading-bots/gate_bot

# ติดตั้ง dependencies
pip install -r requirements.txt

# ตั้งค่าเริ่มต้น
python cli.py setup
```

### 2. การใช้งานพื้นฐาน
```bash
# ตรวจสอบสถานะ
python cli.py status

# สแกนหาสัญญาณ MACD
python cli.py scan

# ตรวจสอบคู่เทรดเฉพาะ
python cli.py macd-check -s BTC/USDT -t 1h

# เริ่มการเทรด (โหมดทดสอบ)
python cli.py trade --dry-run
```

### 3. การตั้งค่า API Keys
```bash
# แก้ไขไฟล์ .env
BINANCE_API_KEY=your_api_key
BINANCE_SECRET=your_secret
GATEIO_API_KEY=your_api_key
GATEIO_SECRET=your_secret
```

## 📊 ตัวอย่างผลลัพธ์

### MACD Scanner Results
```
🔍 ผลการสแกน MACD Signals
================================================================================
📊 สรุป: สัญญาณทั้งหมด 15 | Long: 8 | Short: 7

🟢 TOP 5 LONG SIGNALS (MACD Cross Up)
--------------------------------------------------------------------------------
1. BTC/USDT (BINANCE) - 1h
   💰 ราคา: $43,250.50 | 📊 ความแรง: 75.2%
   📈 MACD: 0.000123 | Signal: -0.000045
   📅 เวลา: 2024-01-15 14:30:00

2. ETH/USDT (GATEIO) - 4h
   💰 ราคา: $2,580.75 | 📊 ความแรง: 68.9%
   📈 MACD: 0.000089 | Signal: -0.000034
   📅 เวลา: 2024-01-15 12:00:00
```

### Trading Performance
```
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
```

## 🔧 การพัฒนาและปรับแต่ง

### เพิ่ม Exchange ใหม่
1. อัปเดต `exchange_manager.py`
2. เพิ่มการตั้งค่าใน `config.json`
3. ทดสอบการเชื่อมต่อ

### เพิ่ม Indicator ใหม่
1. อัปเดต `market_analyzer.py`
2. เพิ่มการคำนวณใน `calculate_technical_indicators()`
3. อัปเดต `analyze_market_condition()`

### เพิ่มกลยุทธ์ใหม่
1. สร้างไฟล์ใหม่ใน `bots/strategies/`
2. อัปเดต `multi_exchange_bot.py`
3. เพิ่มการตั้งค่าใน config

## 🛡️ ความปลอดภัย

### การจัดเก็บ Credentials
- ใช้ environment variables
- ไม่เก็บ private keys ในโค้ด
- รองรับ sandbox mode

### Risk Management
- จำกัดขนาดออเดอร์
- ตั้งค่า stop loss อัตโนมัติ
- ติดตามการสูญเสียรายวัน

## 📞 การสนับสนุน

### Community
- **GitHub Issues**: รายงานปัญหาและขอฟีเจอร์ใหม่
- **Discussions**: พูดคุยและแลกเปลี่ยนประสบการณ์
- **Wiki**: เอกสารเพิ่มเติมจากชุมชน

### Contributing
- **Bug Reports**: แจ้งปัญหาที่พบ
- **Feature Requests**: เสนอฟีเจอร์ใหม่
- **Pull Requests**: ส่งโค้ดปรับปรุง
- **Documentation**: ช่วยปรับปรุงเอกสาร

## ⚠️ คำเตือน

**การเทรดมีความเสี่ยง** - โปรดทำความเข้าใจและทดสอบในโหมด sandbox ก่อนใช้เงินจริง

- ทดสอบกลยุทธ์ในโหมด dry-run ก่อน
- เริ่มต้นด้วยจำนวนเงินน้อย
- ติดตามผลการเทรดอย่างสม่ำเสมอ
- ตั้งค่า stop loss ที่เหมาะสม

## 📄 License

MIT License - ดูรายละเอียดใน [LICENSE](../LICENSE)

---

**Happy Trading! 🚀📈**

*สร้างด้วย ❤️ โดยชุมชน crypto traders* 