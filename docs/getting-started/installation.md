# 📦 Installation Guide - คู่มือการติดตั้ง

คู่มือการติดตั้งและตั้งค่าเริ่มต้นสำหรับ Multi-Exchange Trading Bot v2.0

## 🔧 ความต้องการของระบบ

### Python Version
- **Python 3.8+** (แนะนำ Python 3.10 หรือใหม่กว่า)
- **pip** package manager

### Operating System
- **macOS** 10.14+
- **Ubuntu** 18.04+
- **Windows** 10+
- **CentOS/RHEL** 7+

### Hardware Requirements
- **RAM**: 2GB ขั้นต่ำ, 4GB แนะนำ
- **Storage**: 1GB ว่าง
- **Network**: การเชื่อมต่ออินเทอร์เน็ตที่เสถียร

## 🚀 การติดตั้งแบบ Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/your-repo/trading-bots.git
cd trading-bots/gate_bot
```

### 2. สร้าง Virtual Environment
```bash
# สร้าง virtual environment
python -m venv venv

# เปิดใช้งาน virtual environment
# สำหรับ macOS/Linux:
source venv/bin/activate

# สำหรับ Windows:
venv\Scripts\activate
```

### 3. ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

### 4. ตั้งค่าเริ่มต้น
```bash
python cli.py setup
```

### 5. ทดสอบการติดตั้ง
```bash
python cli.py --help
python cli.py status
```

## 🔧 การติดตั้งแบบ Manual

### 1. ตรวจสอบ Python Version
```bash
python --version
# ควรแสดง Python 3.8 หรือใหม่กว่า
```

### 2. อัปเกรด pip
```bash
pip install --upgrade pip
```

### 3. ติดตั้ง Dependencies ทีละตัว
```bash
# Core dependencies
pip install pandas==2.2.0
pip install numpy==1.26.0
pip install ccxt==4.4.85
pip install web3==7.12.0

# Technical analysis
pip install ta==0.11.0

# CLI framework
pip install click==8.2.1

# Additional libraries
pip install python-dotenv==1.0.1
pip install requests==2.31.0
pip install aiohttp==3.9.1
pip install python-telegram-bot==21.0
pip install plotly==5.18.0
```

### 4. ตรวจสอบการติดตั้ง
```bash
python -c "import ccxt, pandas, ta, click; print('All dependencies installed successfully!')"
```

## ⚙️ การตั้งค่าเริ่มต้น

### 1. สร้างไฟล์ Configuration
```bash
python cli.py setup
```

หรือสร้างด้วยตนเอง:

```bash
cp config.json.example config.json
cp env_example.txt .env
```

### 2. แก้ไขไฟล์ .env
```bash
# CEX API Keys
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET=your_binance_secret_here
BINANCE_SANDBOX=true

GATEIO_API_KEY=your_gateio_api_key_here
GATEIO_SECRET=your_gateio_secret_here
GATEIO_SANDBOX=true

# DEX Settings (ถ้าใช้)
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
ETHEREUM_PRIVATE_KEY=your_ethereum_private_key_here

# Telegram Bot (ถ้าใช้)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
```

### 3. ทดสอบการเชื่อมต่อ
```bash
python cli.py test-connection
```

## 🐳 การติดตั้งด้วย Docker

### 1. สร้าง Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "cli.py", "--help"]
```

### 2. Build Docker Image
```bash
docker build -t trading-bot .
```

### 3. Run Container
```bash
docker run -it --rm \
  -v $(pwd)/config.json:/app/config.json \
  -v $(pwd)/.env:/app/.env \
  trading-bot python cli.py status
```

## 🔧 การแก้ไขปัญหาการติดตั้ง

### ปัญหา Python Version
```bash
# ติดตั้ง Python ใหม่
# macOS (ใช้ Homebrew)
brew install python@3.10

# Ubuntu
sudo apt update
sudo apt install python3.10 python3.10-pip

# Windows
# ดาวน์โหลดจาก python.org
```

### ปัญหา pip permissions
```bash
# ใช้ --user flag
pip install --user -r requirements.txt

# หรือใช้ virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# หรือ venv\Scripts\activate  # Windows
```

### ปัญหา Dependencies Conflicts
```bash
# ลบ virtual environment เก่า
rm -rf venv

# สร้างใหม่
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### ปัญหา Network/Firewall
```bash
# ใช้ proxy (ถ้าจำเป็น)
pip install --proxy http://proxy.company.com:8080 -r requirements.txt

# ใช้ mirror ที่เร็วกว่า
pip install -i https://pypi.douban.com/simple/ -r requirements.txt
```

## 🔐 การตั้งค่า API Keys

### Binance
1. เข้า [Binance API Management](https://www.binance.com/en/my/settings/api-management)
2. สร้าง API Key ใหม่
3. เปิดใช้งาน "Enable Trading" (สำหรับการเทรด)
4. เปิดใช้งาน "Enable Reading" (สำหรับดูข้อมูล)
5. ตั้งค่า IP Whitelist (แนะนำ)

### Gate.io
1. เข้า [Gate.io API Management](https://www.gate.io/myaccount/apiv4keys)
2. สร้าง API Key ใหม่
3. เลือก permissions ที่ต้องการ
4. บันทึก API Key และ Secret

### การทดสอบ API Keys
```bash
# ทดสอบการเชื่อมต่อ
python cli.py test-connection

# ดูยอดเงิน
python cli.py balance

# ทดสอบการดึงข้อมูล
python cli.py macd-check -s BTC/USDT -t 1h
```

## 📊 การตั้งค่า Monitoring

### 1. ตั้งค่า Logging
```bash
# สร้างโฟลเดอร์ logs
mkdir temp

# ตั้งค่าใน config.json
{
  "bot_settings": {
    "log_level": "INFO",
    "log_file": "temp/trading_bot.log"
  }
}
```

### 2. ตั้งค่า Telegram Notifications
```bash
# สร้าง Telegram Bot
# 1. หา @BotFather ใน Telegram
# 2. ส่งคำสั่ง /newbot
# 3. ตั้งชื่อบอท
# 4. ได้ Bot Token

# หา Chat ID
# 1. เพิ่มบอทเข้ากลุ่มหรือแชทส่วนตัว
# 2. ส่งข้อความใดๆ
# 3. เข้า https://api.telegram.org/bot<TOKEN>/getUpdates
# 4. หา chat.id
```

### 3. ตั้งค่า Database
```bash
# SQLite (เริ่มต้น)
# ไม่ต้องติดตั้งเพิ่ม

# PostgreSQL (ถ้าต้องการ)
pip install psycopg2-binary
```

## 🚀 การเริ่มใช้งาน

### 1. ทดสอบระบบ
```bash
# ตรวจสอบสถานะ
python cli.py status

# ทดสอบการสแกน
python cli.py scan -t 1h -s 50

# ทดสอบการเทรด (โหมดทดสอบ)
python cli.py trade --dry-run
```

### 2. การใช้งานจริง
```bash
# เปลี่ยน sandbox เป็น false ใน .env
BINANCE_SANDBOX=false
GATEIO_SANDBOX=false

# เริ่มการเทรดจริง
python cli.py trade
```

## 📚 ขั้นตอนถัดไป

หลังจากติดตั้งเสร็จแล้ว แนะนำให้อ่านเอกสารต่อไปนี้:

1. **[Quick Start Guide](QUICK_START.md)** - เริ่มใช้งานอย่างรวดเร็ว
2. **[Configuration Guide](CONFIGURATION.md)** - การตั้งค่าระบบ
3. **[Crypto Scanner Guide](CRYPTO_SCANNER_GUIDE.md)** - การใช้งาน MACD Scanner
4. **[CLI Commands](CLI_COMMANDS.md)** - คำสั่งทั้งหมด

## 🆘 การขอความช่วยเหลือ

หากพบปัญหาในการติดตั้ง:

1. ตรวจสอบ [Troubleshooting Guide](TROUBLESHOOTING.md)
2. ดู [FAQ](FAQ.md)
3. สร้าง Issue ใน GitHub
4. ติดต่อชุมชนใน Discussions

---

**Happy Trading! 🚀📈** 