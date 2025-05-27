# ❓ FAQ - คำถามที่พบบ่อย

คำถามและคำตอบที่พบบ่อยสำหรับ Multi-Exchange Trading Bot v2.0

## 🚀 การติดตั้งและตั้งค่า

### Q: ต้องใช้ Python เวอร์ชันอะไร?
**A:** ต้องใช้ Python 3.8 หรือใหม่กว่า แนะนำ Python 3.10+ สำหรับประสิทธิภาพที่ดีที่สุด

```bash
python --version
# ควรแสดง Python 3.8.x หรือสูงกว่า
```

### Q: ติดตั้ง dependencies แล้วเกิด error?
**A:** ลองใช้ virtual environment และอัปเกรด pip

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# หรือ venv\Scripts\activate  # Windows
pip install --upgrade pip
pip install -r requirements.txt
```

### Q: ไฟล์ config.json หายไป?
**A:** รันคำสั่ง setup เพื่อสร้างใหม่

```bash
python cli.py setup
```

### Q: API Keys ใส่แล้วยังเชื่อมต่อไม่ได้?
**A:** ตรวจสอบ:
1. API Key และ Secret ถูกต้อง
2. เปิดใช้งาน permissions ที่จำเป็น
3. IP Whitelist (ถ้ามี)
4. ใช้ sandbox mode สำหรับการทดสอบ

```bash
# ทดสอบการเชื่อมต่อ
python cli.py test-connection
```

## 🔍 Crypto Scanner

### Q: ทำไมไม่พบสัญญาณ MACD?
**A:** อาจเป็นเพราะ:
1. ความแรงสัญญาณต่ำกว่าที่กำหนด
2. ปริมาณการเทรดต่ำ
3. ไม่มีการ cross ใน timeframe ที่เลือก

```bash
# ลองลดความแรงสัญญาณขั้นต่ำ
python cli.py scan -s 40

# ตรวจสอบข้อมูล MACD ปัจจุบัน
python cli.py macd-check -s BTC/USDT -t 1h
```

### Q: สัญญาณ MACD หมายความว่าอย่างไร?
**A:** 
- **Long Signal**: MACD cross ขึ้นเหนือ 0 = แนวโน้มขาขึ้น
- **Short Signal**: MACD cross ลงใต้ 0 = แนวโน้มขาลง
- **Strength**: ความแรงสัญญาณ 0-100% (ยิ่งสูงยิ่งแรง)

### Q: ควรใช้ timeframe ไหน?
**A:** ขึ้นอยู่กับกลยุทธ์:
- **Scalping**: 15m, 1h
- **Swing Trading**: 4h, 1d
- **Position Trading**: 1d, 1w

### Q: ทำไมสัญญาณใน exchange ต่างๆ ไม่เหมือนกัน?
**A:** เป็นเรื่องปกติเพราะ:
1. ราคาใน exchange แต่ละแห่งอาจต่างกันเล็กน้อย
2. ปริมาณการเทรดต่างกัน
3. Liquidity ต่างกัน

## 🏢 Exchange Integration

### Q: รองรับ exchange ไหนบ้าง?
**A:** 
- **CEX**: Binance, Gate.io, OKX, KuCoin, Bybit, Huobi
- **DEX**: Uniswap V3, PancakeSwap, SushiSwap, QuickSwap

### Q: ทำไม DEX เชื่อมต่อไม่ได้?
**A:** DEX ต้องการ:
1. RPC URL ที่ถูกต้อง
2. Private key ของ wallet
3. Gas fee เพียงพอ
4. Network ที่ถูกต้อง

### Q: Sandbox mode คืออะไร?
**A:** โหมดทดสอบที่ไม่ใช้เงินจริง เหมาะสำหรับ:
- ทดสอบ API connection
- ทดสอบกลยุทธ์
- เรียนรู้การใช้งาน

```bash
# ตั้งค่าใน .env
BINANCE_SANDBOX=true
GATEIO_SANDBOX=true
```

## 📊 การเทรด

### Q: Dry-run mode คืออะไร?
**A:** โหมดจำลองการเทรดโดยไม่วางออเดอร์จริง

```bash
python cli.py trade --dry-run
```

### Q: ทำไมบอทไม่วางออเดอร์?
**A:** ตรวจสอบ:
1. ยอดเงินเพียงพอ
2. ขนาดออเดอร์ขั้นต่ำ
3. การตั้งค่า risk management
4. สัญญาณมีความแรงเพียงพอ

### Q: จะหยุดบอทอย่างปลอดภัยได้อย่างไร?
**A:** กด Ctrl+C ระบบจะ:
1. ยกเลิกออเดอร์ที่ค้างอยู่
2. บันทึกสถานะ
3. ปิดการเชื่อมต่ออย่างปลอดภัย

### Q: Risk Management ทำงานอย่างไร?
**A:** ระบบจะ:
- จำกัดขนาดออเดอร์ตาม max_position_size
- ตั้ง stop loss อัตโนมัติ
- ติดตามการสูญเสียรายวัน
- หยุดเทรดเมื่อถึงขีดจำกัด

## 🔧 การแก้ไขปัญหา

### Q: เกิด "ModuleNotFoundError"?
**A:** ติดตั้ง dependencies ที่ขาดหาย

```bash
pip install -r requirements.txt

# หรือติดตั้งทีละตัว
pip install ccxt pandas ta click
```

### Q: เกิด "Permission denied"?
**A:** ใช้ virtual environment หรือ --user flag

```bash
pip install --user -r requirements.txt
```

### Q: การเชื่อมต่อ network ช้า?
**A:** ลองใช้:
1. VPN (ถ้าจำเป็น)
2. DNS server อื่น
3. Mirror repository ที่เร็วกว่า

### Q: Memory usage สูง?
**A:** ปรับการตั้งค่า:
1. ลดจำนวน trading pairs
2. ลดจำนวน timeframes
3. เพิ่ม interval ของการสแกน

### Q: CPU usage สูง?
**A:** 
1. ลดความถี่การสแกน
2. ใช้ timeframe ที่ยาวขึ้น
3. จำกัดจำนวน exchanges

## 📱 การแจ้งเตือน

### Q: ตั้งค่า Telegram Bot อย่างไร?
**A:** 
1. หา @BotFather ใน Telegram
2. ส่งคำสั่ง `/newbot`
3. ตั้งชื่อบอท
4. ได้ Bot Token
5. หา Chat ID จาก getUpdates API

```bash
# ใส่ใน .env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### Q: ไม่ได้รับการแจ้งเตือน?
**A:** ตรวจสอบ:
1. Bot Token ถูกต้อง
2. Chat ID ถูกต้อง
3. เปิดใช้งาน notifications ใน config
4. บอทถูกเพิ่มเข้าแชทแล้ว

## 💾 ข้อมูลและการบันทึก

### Q: ข้อมูลการเทรดเก็บที่ไหน?
**A:** เก็บใน:
- SQLite database (เริ่มต้น)
- Log files ใน folder `temp/`
- JSON exports จาก scanner

### Q: จะ backup ข้อมูลอย่างไร?
**A:** สำรองไฟล์:
- `config.json`
- `.env`
- `trading_data.db`
- `temp/` folder

### Q: จะดู log files อย่างไร?
**A:** 
```bash
# ดู log ล่าสุด
tail -f temp/trading_bot.log

# ค้นหา error
grep "ERROR" temp/trading_bot.log

# ดู log ทั้งหมด
cat temp/trading_bot.log
```

## 🔐 ความปลอดภัย

### Q: API Keys ปลอดภัยหรือไม่?
**A:** ระบบ:
- เก็บใน environment variables
- ไม่แสดงใน log files
- ใช้ HTTPS เท่านั้น
- รองรับ IP whitelist

### Q: ควรใช้ permissions อะไรสำหรับ API?
**A:** 
- **อ่านข้อมูล**: Enable Reading
- **การเทรด**: Enable Trading (ถ้าต้องการ)
- **ถอนเงิน**: ไม่แนะนำให้เปิด

### Q: จะป้องกัน unauthorized access อย่างไร?
**A:** 
1. ใช้ IP whitelist
2. ตั้งรหัสผ่านที่แข็งแรง
3. เปิด 2FA
4. ตรวจสอบ log เป็นประจำ

## 📈 ประสิทธิภาพ

### Q: ทำไมการสแกนช้า?
**A:** อาจเป็นเพราะ:
1. Network latency
2. API rate limits
3. จำนวน pairs มาก
4. Timeframes หลายตัว

**แก้ไข:**
```bash
# ลดจำนวน pairs
python cli.py scan -p BTC/USDT -p ETH/USDT

# ใช้ timeframe เดียว
python cli.py scan -t 1h

# เพิ่ม interval
python cli.py scan-continuous -i 30
```

### Q: จะเพิ่มความเร็วได้อย่างไร?
**A:** 
1. ใช้ SSD แทน HDD
2. เพิ่ม RAM
3. ใช้ internet ที่เร็วกว่า
4. ลด concurrent requests

## 🔄 การอัปเดต

### Q: จะอัปเดตเป็นเวอร์ชันใหม่อย่างไร?
**A:** 
```bash
# Backup ข้อมูลเก่า
cp config.json config.json.backup
cp .env .env.backup

# Pull อัปเดตใหม่
git pull origin main

# อัปเดต dependencies
pip install -r requirements.txt

# ตรวจสอบการทำงาน
python cli.py status
```

### Q: Config เก่าใช้ได้กับเวอร์ชันใหม่หรือไม่?
**A:** ส่วนใหญ่ใช้ได้ แต่อาจต้องเพิ่มการตั้งค่าใหม่ ดู [Migration Guide](MIGRATION.md)

## 🆘 การขอความช่วยเหลือ

### Q: จะรายงานปัญหาอย่างไร?
**A:** สร้าง GitHub Issue พร้อม:
1. คำอธิบายปัญหา
2. ขั้นตอนการทำซ้ำ
3. Log files ที่เกี่ยวข้อง
4. ข้อมูลระบบ (OS, Python version)

### Q: จะขอฟีเจอร์ใหม่อย่างไร?
**A:** สร้าง Feature Request ใน GitHub Issues

### Q: มีชุมชนหรือไม่?
**A:** มี:
- GitHub Discussions
- Issues และ Pull Requests
- Community Wiki

### Q: จะมีส่วนร่วมในการพัฒนาอย่างไร?
**A:** 
1. Fork repository
2. สร้าง feature branch
3. ทำการเปลี่ยนแปลง
4. ส่ง Pull Request
5. ดู [Contributing Guide](CONTRIBUTING.md)

## 💡 เทคนิคและคำแนะนำ

### Q: กลยุทธ์ไหนดีที่สุด?
**A:** ไม่มีกลยุทธ์ที่ดีที่สุดเสมอ ขึ้นอยู่กับ:
- สภาพตลาด
- ความเสี่ยงที่ยอมรับได้
- เป้าหมายการลงทุน
- ประสบการณ์

### Q: ควรเริ่มต้นอย่างไร?
**A:** แนะนำ:
1. เริ่มด้วย sandbox mode
2. ใช้เงินน้อยๆ ก่อน
3. ทดสอบกลยุทธ์ใน dry-run
4. เรียนรู้จากผลลัพธ์

### Q: จะปรับปรุงผลการเทรดอย่างไร?
**A:** 
1. วิเคราะห์ผลการเทรดเก่า
2. ปรับการตั้งค่า risk management
3. ใช้ indicators หลายตัวร่วมกัน
4. ติดตามข่าวสารตลาด

---

**ยังมีคำถามอื่นๆ?** 

ดู [Troubleshooting Guide](TROUBLESHOOTING.md) หรือสร้าง Issue ใน GitHub

**Happy Trading! 🚀📈** 