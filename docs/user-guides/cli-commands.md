# 💻 CLI Commands Reference - คำสั่ง Command Line

เอกสารอ้างอิงคำสั่ง Command Line Interface ทั้งหมดสำหรับ Multi-Exchange Trading Bot v2.0

## 📋 คำสั่งหลัก

### `--help` - ดูความช่วยเหลือ
```bash
python cli.py --help
python cli.py [COMMAND] --help
```

### `--version` - ดูเวอร์ชัน
```bash
python cli.py --version
```

## 🏢 คำสั่งจัดการ Exchanges

### `list-exchanges` - แสดงรายการ exchanges ที่รองรับ
```bash
python cli.py list-exchanges
```

**ผลลัพธ์:**
```
🏢 รายการ Exchanges ที่รองรับ:
==================================================

💱 Centralized Exchanges (CEX):
  ✅ binance - Binance
  ✅ gateio - Gate.io
  ✅ okx - OKX
  ✅ kucoin - KuCoin
  ✅ bybit - Bybit
  ✅ huobi - Huobi

🔄 Decentralized Exchanges (DEX):
  🔄 uniswap_v3 - Uniswap V3 (Ethereum)
  🔄 pancakeswap - PancakeSwap (BSC)
  🔄 sushiswap - SushiSwap (Multi-chain)
  🔄 quickswap - QuickSwap (Polygon)
```

### `status` - แสดงสถานะการเชื่อมต่อ
```bash
python cli.py status [OPTIONS]
```

**Options:**
- `-c, --config TEXT` - ไฟล์ config (เริ่มต้น: config.json)

**ตัวอย่าง:**
```bash
python cli.py status
python cli.py status -c custom_config.json
```

### `test-connection` - ทดสอบการเชื่อมต่อ exchanges
```bash
python cli.py test-connection [OPTIONS]
```

**Options:**
- `-c, --config TEXT` - ไฟล์ config

**ตัวอย่าง:**
```bash
python cli.py test-connection
```

### `balance` - แสดงยอดเงินคงเหลือ
```bash
python cli.py balance [OPTIONS]
```

**Options:**
- `-e, --exchange TEXT` - ชื่อ exchange เฉพาะ
- `-s, --symbol TEXT` - Trading pair เฉพาะ
- `-c, --config TEXT` - ไฟล์ config

**ตัวอย่าง:**
```bash
# ดูยอดเงินทุก exchanges
python cli.py balance

# ดูยอดเงินเฉพาะ exchange
python cli.py balance -e binance

# ดูยอดเงินหลาย exchanges
python cli.py balance -e binance -e gateio
```

## 🔍 คำสั่ง Crypto Scanner

### `scan` - สแกนหาสัญญาณ MACD
```bash
python cli.py scan [OPTIONS]
```

**Options:**
- `-t, --timeframes TEXT` - Timeframes ที่ต้องการสแกน (หลายค่าได้)
- `-e, --exchanges TEXT` - Exchanges ที่ต้องการสแกน (หลายค่าได้)
- `-p, --pairs TEXT` - Trading pairs ที่ต้องการสแกน (หลายค่าได้)
- `-s, --min-strength INTEGER` - ความแรงสัญญาณขั้นต่ำ (0-100)
- `-v, --min-volume INTEGER` - ปริมาณการเทรดขั้นต่ำ 24h
- `-c, --config TEXT` - ไฟล์ config

**ตัวอย่าง:**
```bash
# สแกนพื้นฐาน
python cli.py scan

# สแกนใน timeframes เฉพาะ
python cli.py scan -t 1h -t 4h -t 1d

# สแกนเฉพาะ exchanges
python cli.py scan -e binance -e gateio

# กำหนดความแรงสัญญาณขั้นต่ำ
python cli.py scan -s 70

# กำหนดปริมาณการเทรดขั้นต่ำ
python cli.py scan -v 500000

# รวมหลายตัวเลือก
python cli.py scan -t 1h -t 4h -s 60 -v 200000 -e binance
```

### `scan-continuous` - สแกนอย่างต่อเนื่อง
```bash
python cli.py scan-continuous [OPTIONS]
```

**Options:**
- `-i, --interval INTEGER` - ช่วงเวลาการสแกน (นาที) [เริ่มต้น: 15]
- `-t, --timeframes TEXT` - Timeframes ที่ต้องการสแกน
- `-c, --config TEXT` - ไฟล์ config

**ตัวอย่าง:**
```bash
# สแกนทุก 15 นาที (เริ่มต้น)
python cli.py scan-continuous

# สแกนทุก 30 นาที
python cli.py scan-continuous -i 30

# สแกนใน timeframes เฉพาะ
python cli.py scan-continuous -t 1h -t 4h

# รวมตัวเลือก
python cli.py scan-continuous -i 10 -t 15m -t 1h
```

### `macd-check` - ตรวจสอบสัญญาณ MACD ของคู่เทรดเฉพาะ
```bash
python cli.py macd-check [OPTIONS]
```

**Options:**
- `-s, --symbol TEXT` - Trading pair (เช่น BTC/USDT) **[Required]**
- `-t, --timeframe TEXT` - Timeframe (เริ่มต้น: 1h)
- `-e, --exchange TEXT` - Exchange name (เริ่มต้น: binance)
- `-c, --config TEXT` - ไฟล์ config

**ตัวอย่าง:**
```bash
# ตรวจสอบ BTC/USDT ใน timeframe 1h
python cli.py macd-check -s BTC/USDT

# ตรวจสอบใน timeframe เฉพาะ
python cli.py macd-check -s BTC/USDT -t 4h

# ตรวจสอบใน exchange เฉพาะ
python cli.py macd-check -s ETH/USDT -t 1h -e gateio

# ตรวจสอบหลายคู่เทรด
python cli.py macd-check -s BTC/USDT -t 1d -e binance
python cli.py macd-check -s ETH/USDT -t 1d -e binance
```

## 📊 คำสั่งการวิเคราะห์ตลาด

### `analyze` - วิเคราะห์ตลาดจากทุก exchanges
```bash
python cli.py analyze [OPTIONS]
```

**Options:**
- `-s, --symbol TEXT` - Trading pair (เริ่มต้น: BTC/USDT)
- `-c, --config TEXT` - ไฟล์ config

**ตัวอย่าง:**
```bash
# วิเคราะห์ BTC/USDT
python cli.py analyze

# วิเคราะห์คู่เทรดอื่น
python cli.py analyze -s ETH/USDT
```

### `monitor` - ติดตามตลาดแบบต่อเนื่อง
```bash
python cli.py monitor [OPTIONS]
```

**Options:**
- `-s, --symbol TEXT` - Trading pair (เริ่มต้น: BTC/USDT)
- `-i, --interval INTEGER` - ช่วงเวลาการวิเคราะห์ (วินาที) [เริ่มต้น: 300]
- `-c, --config TEXT` - ไฟล์ config

**ตัวอย่าง:**
```bash
# ติดตาม BTC/USDT ทุก 5 นาที
python cli.py monitor

# ติดตามทุก 10 นาที
python cli.py monitor -i 600

# ติดตามคู่เทรดอื่น
python cli.py monitor -s ETH/USDT -i 300
```

## 🚀 คำสั่งการเทรด

### `trade` - เริ่มการเทรดอัตโนมัติ
```bash
python cli.py trade [OPTIONS]
```

**Options:**
- `-c, --config TEXT` - ไฟล์ config
- `--dry-run` - ทดสอบโดยไม่เทรดจริง

**ตัวอย่าง:**
```bash
# เริ่มการเทรดจริง
python cli.py trade

# ทดสอบการเทรด (ไม่เทรดจริง)
python cli.py trade --dry-run

# ใช้ config เฉพาะ
python cli.py trade -c production_config.json
```

## ⚙️ คำสั่งการตั้งค่า

### `setup` - ตั้งค่าเริ่มต้น
```bash
python cli.py setup
```

**การทำงาน:**
1. สร้างไฟล์ `config.json`
2. สร้างไฟล์ `.env` ตัวอย่าง
3. ตั้งค่า exchanges แบบ interactive
4. ตั้งค่า trading strategy
5. ตั้งค่า bot settings

**ตัวอย่างการใช้งาน:**
```bash
python cli.py setup
# จะมีการถามตอบแบบ interactive
```

### `version` - แสดงเวอร์ชัน
```bash
python cli.py version
```

**ผลลัพธ์:**
```
🤖 Multi-Exchange Trading Bot v2.0.0
รองรับ CEX และ DEX หลายแห่ง
พัฒนาด้วย Python + CCXT + Web3
🔍 รองรับ Crypto Scanner ด้วยสัญญาณ MACD
```

## 🔧 ตัวอย่างการใช้งานขั้นสูง

### Workflow การสแกนและเทรด
```bash
# 1. ตรวจสอบสถานะระบบ
python cli.py status

# 2. สแกนหาสัญญาณ
python cli.py scan -t 1h -t 4h -s 65

# 3. ตรวจสอบสัญญาณเฉพาะ
python cli.py macd-check -s BTC/USDT -t 1h

# 4. ทดสอบการเทรด
python cli.py trade --dry-run

# 5. เริ่มการเทรดจริง
python cli.py trade
```

### การติดตามแบบ Real-time
```bash
# Terminal 1: สแกนต่อเนื่อง
python cli.py scan-continuous -i 15 -t 1h

# Terminal 2: ติดตามตลาด
python cli.py monitor -s BTC/USDT -i 300

# Terminal 3: ตรวจสอบยอดเงิน
watch -n 60 "python cli.py balance"
```

### การใช้งานหลาย Config
```bash
# สำหรับ production
python cli.py trade -c production_config.json

# สำหรับ testing
python cli.py trade --dry-run -c test_config.json

# สำหรับ development
python cli.py scan -c dev_config.json
```

## 🔍 การใช้งาน Filters และ Options

### Timeframes ที่รองรับ
- `1m`, `3m`, `5m`, `15m`, `30m`
- `1h`, `2h`, `4h`, `6h`, `8h`, `12h`
- `1d`, `3d`, `1w`, `1M`

### Exchanges ที่รองรับ
- **CEX**: `binance`, `gateio`, `okx`, `kucoin`, `bybit`, `huobi`
- **DEX**: `uniswap_v3`, `pancakeswap`, `sushiswap`, `quickswap`

### Trading Pairs ตัวอย่าง
- Major: `BTC/USDT`, `ETH/USDT`, `BNB/USDT`
- Altcoins: `ADA/USDT`, `SOL/USDT`, `DOT/USDT`
- DeFi: `UNI/USDT`, `LINK/USDT`, `AAVE/USDT`

## 🚨 การจัดการ Errors

### Exit Codes
- `0` - สำเร็จ
- `1` - ข้อผิดพลาดทั่วไป
- `2` - ข้อผิดพลาดการตั้งค่า
- `3` - ข้อผิดพลาดการเชื่อมต่อ

### การจัดการ Interruption
```bash
# หยุดการทำงานด้วย Ctrl+C
# ระบบจะปิดการเชื่อมต่ออย่างปลอดภัย

# สำหรับ background processes
nohup python cli.py scan-continuous > scanner.log 2>&1 &

# หยุด background process
pkill -f "python cli.py scan-continuous"
```

## 📝 Logging และ Output

### การเปิด Verbose Mode
```bash
# เพิ่ม logging level ใน config.json
{
  "bot_settings": {
    "log_level": "DEBUG"
  }
}
```

### การบันทึก Output
```bash
# บันทึกผลลัพธ์ลงไฟล์
python cli.py scan > scan_results.txt 2>&1

# บันทึกเฉพาะ output
python cli.py scan 2>/dev/null > scan_results.txt

# บันทึกพร้อมแสดงผล
python cli.py scan | tee scan_results.txt
```

## 🔄 การใช้งานแบบ Automation

### Cron Jobs
```bash
# แก้ไข crontab
crontab -e

# สแกนทุก 15 นาที
*/15 * * * * cd /path/to/gate_bot && python cli.py scan >> temp/scan.log 2>&1

# ตรวจสอบสถานะทุกชั่วโมง
0 * * * * cd /path/to/gate_bot && python cli.py status >> temp/status.log 2>&1
```

### Systemd Service
```bash
# สร้างไฟล์ /etc/systemd/system/trading-bot.service
[Unit]
Description=Multi-Exchange Trading Bot
After=network.target

[Service]
Type=simple
User=trader
WorkingDirectory=/path/to/gate_bot
ExecStart=/path/to/venv/bin/python cli.py trade
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# เปิดใช้งาน service
sudo systemctl enable trading-bot
sudo systemctl start trading-bot
```

---

**Happy Trading! 🚀📈**

*สำหรับข้อมูลเพิ่มเติม ดู [Documentation](README.md)* 