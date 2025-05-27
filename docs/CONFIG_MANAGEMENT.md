# Config Management Guide

## 📋 ภาพรวม

ระบบ Config Management ใหม่ใช้ **template-based configuration** เพื่อความปลอดภัยและความสะดวกในการจัดการ

## 🏗️ โครงสร้างไฟล์

```
├── config.template.json    # Template สำหรับสร้าง config
├── config.json            # Config จริง (ถูก ignore ใน git)
├── config_manager.py      # ตัวจัดการ config
└── .env                   # Environment variables
```

## 🚀 การใช้งาน

### 1. การสร้าง Config ครั้งแรก

```bash
# วิธีที่ 1: ใช้ CLI
python cli.py setup

# วิธีที่ 2: ใช้ config command
python cli.py config --action create

# วิธีที่ 3: ใช้ main.py
python main.py --create-config
```

### 2. การจัดการ Config

```bash
# แสดงข้อมูล config
python cli.py config --action show

# ตรวจสอบความถูกต้อง
python cli.py config --action validate

# สำรองไฟล์ config
python cli.py config --action backup

# สร้างใหม่ (บังคับเขียนทับ)
python cli.py config --action create --force
```

## 🔧 Environment Variables

สร้างไฟล์ `.env` และใส่ข้อมูลดังนี้:

```env
# CEX API Keys
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET=your_binance_secret_here

GATEIO_API_KEY=your_gateio_api_key_here
GATEIO_SECRET=your_gateio_secret_here

OKX_API_KEY=your_okx_api_key_here
OKX_SECRET=your_okx_secret_here
OKX_PASSPHRASE=your_okx_passphrase_here

KUCOIN_API_KEY=your_kucoin_api_key_here
KUCOIN_SECRET=your_kucoin_secret_here
KUCOIN_PASSPHRASE=your_kucoin_passphrase_here

# DEX Settings
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
ETHEREUM_PRIVATE_KEY=your_ethereum_private_key_here
ETHEREUM_WALLET_ADDRESS=your_ethereum_wallet_address_here

BSC_RPC_URL=https://bsc-dataseed.binance.org/
BSC_PRIVATE_KEY=your_bsc_private_key_here
BSC_WALLET_ADDRESS=your_bsc_wallet_address_here

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
```

## 🔄 การทำงานของระบบ

### 1. Auto-Enable Exchanges
ระบบจะเปิดใช้งาน exchanges อัตโนมัติเมื่อพบ API keys ที่ถูกต้อง:

- **CEX**: ต้องมี `api_key` และ `secret`
- **DEX**: ต้องมี `rpc_url` และ `private_key`

### 2. Template Substitution
ระบบจะแทนที่ `${VARIABLE_NAME}` ด้วยค่าจาก environment variables

### 3. Validation
ระบบจะตรวจสอบ:
- JSON syntax ถูกต้อง
- มีส่วนที่จำเป็นครบถ้วน
- มี exchange ที่เปิดใช้งานอย่างน้อย 1 ตัว

## 📁 Template Structure

```json
{
  "exchanges": {
    "binance": {
      "enabled": false,
      "api_key": "${BINANCE_API_KEY}",
      "secret": "${BINANCE_SECRET}",
      ...
    }
  },
  "trading_strategy": { ... },
  "bot_settings": { ... },
  "scanner_settings": { ... }
}
```

## 🛡️ ความปลอดภัย

1. **ไฟล์ `config.json` ถูก ignore ใน git**
2. **API keys เก็บใน `.env` file**
3. **Template ไม่มีข้อมูลที่ sensitive**
4. **Auto backup เมื่อมีการเปลี่ยนแปลง**

## 🔧 การใช้งานใน Code

```python
from config_manager import ConfigManager, ensure_config_exists

# ตรวจสอบและสร้าง config ถ้าจำเป็น
ensure_config_exists()

# ใช้ ConfigManager
config_manager = ConfigManager()
config_data = config_manager.load_config()

# อัปเดต config
config_manager.update_config({
    "bot_settings": {
        "check_interval": 60
    }
})
```

## 🚨 Troubleshooting

### ปัญหา: ไม่สามารถสร้าง config ได้

```bash
# ตรวจสอบว่ามี template
ls -la config.template.json

# ตรวจสอบ environment variables
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('BINANCE_API_KEY'))"

# สร้างใหม่แบบบังคับ
python cli.py config --action create --force
```

### ปัญหา: Config ไม่ถูกต้อง

```bash
# ตรวจสอบ syntax
python cli.py config --action validate

# ดู config ปัจจุบัน
python cli.py config --action show

# สำรองและสร้างใหม่
python cli.py config --action backup
python cli.py config --action create --force
```

## 📝 Best Practices

1. **ใช้ environment variables สำหรับข้อมูล sensitive**
2. **สำรอง config ก่อนแก้ไข**
3. **ตรวจสอบ validation หลังแก้ไข**
4. **ไม่ commit ไฟล์ config.json**
5. **ใช้ sandbox mode สำหรับการทดสอบ**

## 🔄 Migration จาก Config เก่า

หากมีไฟล์ `config.json` เก่าอยู่:

```bash
# สำรองไฟล์เก่า
cp config.json config.json.old

# สร้าง config ใหม่จาก template
python cli.py config --action create --force

# เปรียบเทียบและปรับแต่งตามต้องการ
``` 