# Hummingbot MQTT Manager - คู่มือการตั้งค่า

## 🚀 เริ่มต้นอย่างรวดเร็ว

### 1. คัดลอกไฟล์คอนฟิก

```bash
# คัดลอกเทมเพลตไปยังคอนฟิกส่วนตัว
cp config/config_hummingbot.json config/config_hummingbot_local.json

# เพิ่มคอนฟิกส่วนตัวใน .gitignore เพื่อป้องกันการ commit ข้อมูลที่สำคัญ
echo "config/config_hummingbot_local.json" >> .gitignore
```

### 2. การตั้งค่าพื้นฐาน

แก้ไขไฟล์ `config/config_hummingbot_local.json` และอัปเดตการตั้งค่าที่สำคัญ:

```json
{
  "hummingbot": {
    "path": "/your/hummingbot/installation/path"
  },
  "exchanges": {
    "binance": {
      "api_key": "your_actual_api_key",
      "api_secret": "your_actual_api_secret",
      "testnet": true
    }
  }
}
```

### 3. เริ่มต้นตัวจัดการ

```bash
# ใช้คอนฟิกส่วนตัว
python -m bots.hummingbot_manager --config config/config_hummingbot_local.json
```

## 📋 ส่วนประกอบการตั้งค่า

### การตั้งค่า MQTT

ตั้งค่าการเชื่อมต่อ MQTT broker:

```json
{
  "mqtt": {
    "host": "localhost",        // IP/hostname ของ MQTT broker
    "port": 1883,              // พอร์ต MQTT (1883 สำหรับ non-SSL, 8883 สำหรับ SSL)
    "username": null,          // ตั้งค่าถ้าต้องการการยืนยันตัวตน
    "password": null,          // ตั้งค่าถ้าต้องการการยืนยันตัวตน
    "keepalive": 60,           // การเชื่อมต่อคงอยู่เป็นวินาที
    "qos": 1                   // คุณภาพการให้บริการ (0, 1, หรือ 2)
  }
}
```

**MQTT Brokers ที่ใช้กันทั่วไป:**
- **Local Mosquitto**: `localhost:1883`
- **Cloud MQTT**: ใช้ hostname และ credentials ที่ให้มา
- **AWS IoT Core**: ใช้ IoT endpoint พร้อม certificates
- **Azure IoT Hub**: ใช้ connection string

### เส้นทาง Hummingbot

อัปเดตเส้นทางตามการติดตั้ง Hummingbot ของคุณ:

```json
{
  "hummingbot": {
    "path": "/opt/hummingbot",                    // ไดเรกทอรีการติดตั้งหลัก
    "config_path": "/opt/hummingbot/conf",        // ไฟล์คอนฟิก
    "logs_path": "/opt/hummingbot/logs",          // ไฟล์ล็อก
    "strategies_path": "/opt/hummingbot/conf/strategies"  // คอนฟิกกลยุทธ์
  }
}
```

**เส้นทางการติดตั้งที่ใช้กันทั่วไป:**
- **Docker**: `/opt/hummingbot`
- **Source**: `~/hummingbot` หรือ `/home/user/hummingbot`
- **Binary**: `/usr/local/hummingbot`
- **Windows**: `C:\hummingbot`

### การตั้งค่า Exchange

เพิ่ม API credentials ของ exchange:

```json
{
  "exchanges": {
    "binance": {
      "enabled": true,
      "api_key": "YOUR_BINANCE_API_KEY",
      "api_secret": "YOUR_BINANCE_API_SECRET",
      "testnet": true                           // เริ่มต้นด้วย testnet!
    },
    "kucoin": {
      "enabled": false,                         // เปิดใช้งานเมื่อพร้อม
      "api_key": "YOUR_KUCOIN_API_KEY",
      "api_secret": "YOUR_KUCOIN_API_SECRET",
      "passphrase": "YOUR_KUCOIN_PASSPHRASE",   // เฉพาะ KuCoin
      "testnet": false
    }
  }
}
```

**⚠️ แนวทางปฏิบัติด้านความปลอดภัยที่ดีที่สุด:**
- อย่า commit API keys จริงไปยัง version control
- ใช้ testnet สำหรับการทดสอบเริ่มต้น
- ตั้งค่าสิทธิ์ API key ให้เป็นเฉพาะการเทรด (ไม่อนุญาตการถอน)
- ใช้การจำกัด IP ถ้า exchange รองรับ

### คอนฟิกกลยุทธ์เริ่มต้น

เทมเพลตรวมถึงคอนฟิกเริ่มต้นสำหรับทุกประเภทกลยุทธ์ที่รองรับ:

#### Pure Market Making
```json
{
  "pure_market_making": {
    "bid_spread": 0.001,        // spread 0.1%
    "ask_spread": 0.001,        // spread 0.1%
    "order_amount": 10.0,       // ขนาดคำสั่งในสกุลเงินฐาน
    "inventory_skew_enabled": true,
    "filled_order_delay": 60.0  // รอ 60 วินาทีหลังการเติม
  }
}
```

#### Cross Exchange Market Making
```json
{
  "cross_exchange_market_making": {
    "maker_market": "binance",
    "taker_market": "kucoin",
    "min_profitability": 0.003, // กำไรขั้นต่ำ 0.3%
    "order_amount": 0.01
  }
}
```

#### Arbitrage
```json
{
  "arbitrage": {
    "primary_market": "binance",
    "secondary_market": "kucoin",
    "min_profitability": 0.003, // กำไรขั้นต่ำหลังหักค่าธรรมเนียม 0.3%
    "order_amount": 0.01
  }
}
```

## 🔐 การตั้งค่าความปลอดภัย

### การจัดการความเสี่ยง

```json
{
  "security": {
    "max_concurrent_strategies": 10,    // จำกัดกลยุทธ์ที่ทำงานพร้อมกัน
    "max_order_amount": 1000.0,        // ขนาดคำสั่งสูงสุด
    "daily_loss_limit": 0.05,          // จำกัดการขาดทุนรายวัน 5%
    "strategy_timeout": 3600           // timeout 1 ชั่วโมง
  }
}
```

### การจำกัดคำสั่ง

```json
{
  "security": {
    "allowed_commands": [
      "create_strategy",
      "start_strategy",
      "stop_strategy",
      // ... คำสั่งที่ปลอดภัยอื่นๆ
    ],
    "restricted_commands": [
      "restart_hummingbot"              // ต้องการสิทธิ์พิเศษ
    ]
  }
}
```

## 📊 การติดตามและแจ้งเตือน

### การแจ้งเตือน Telegram

1. สร้าง Telegram bot:
   - ส่งข้อความถึง @BotFather บน Telegram
   - ใช้คำสั่ง `/newbot`
   - รับ bot token

2. รับ chat ID:
   - ส่งข้อความถึง @userinfobot
   - รับ chat ID

3. ตั้งค่า:
```json
{
  "monitoring": {
    "telegram_notifications": {
      "enabled": true,
      "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
      "chat_id": "123456789"
    }
  }
}
```

### การแจ้งเตือน Discord

1. สร้าง Discord webhook:
   - ไปที่การตั้งค่าเซิร์ฟเวอร์ Discord
   - ไปที่ Integrations > Webhooks
   - สร้าง webhook ใหม่
   - คัดลอก webhook URL

2. ตั้งค่า:
```json
{
  "monitoring": {
    "discord_notifications": {
      "enabled": true,
      "webhook_url": "https://discord.com/api/webhooks/..."
    }
  }
}
```

## 🌍 ตัวแปรสภาพแวดล้อม

เพื่อความปลอดภัยที่ดีกว่า ให้ใช้ตัวแปรสภาพแวดล้อมแทนการเขียนข้อมูลที่สำคัญลงในโค้ด:

### 1. สร้างไฟล์ .env

```bash
# ไฟล์ .env (เพิ่มใน .gitignore)
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret
KUCOIN_API_KEY=your_kucoin_api_key
KUCOIN_API_SECRET=your_kucoin_api_secret
KUCOIN_PASSPHRASE=your_kucoin_passphrase
MQTT_USERNAME=your_mqtt_username
MQTT_PASSWORD=your_mqtt_password
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

### 2. อัปเดตคอนฟิกให้ใช้ตัวแปรสภาพแวดล้อม

```json
{
  "exchanges": {
    "binance": {
      "api_key": "${BINANCE_API_KEY}",
      "api_secret": "${BINANCE_API_SECRET}"
    }
  },
  "mqtt": {
    "username": "${MQTT_USERNAME}",
    "password": "${MQTT_PASSWORD}"
  }
}
```

### 3. โหลดตัวแปรสภาพแวดล้อม

```bash
# โหลดไฟล์ .env
export $(cat .env | xargs)

# หรือใช้ python-dotenv
pip install python-dotenv
```

## 🗄️ การตั้งค่าฐานข้อมูล (ไม่บังคับ)

เปิดใช้งานการจัดเก็บข้อมูลกลยุทธ์ในฐานข้อมูล:

### SQLite (แนะนำสำหรับผู้เริ่มต้น)
```json
{
  "database": {
    "enabled": true,
    "type": "sqlite",
    "path": "data/hummingbot_mqtt.db"
  }
}
```

### PostgreSQL (สำหรับการใช้งานจริง)
```json
{
  "database": {
    "enabled": true,
    "type": "postgresql",
    "path": "postgresql://user:password@localhost:5432/hummingbot"
  }
}
```

## 📝 การตั้งค่าการบันทึก

### การบันทึกพื้นฐาน
```json
{
  "logging": {
    "level": "INFO",                    // DEBUG, INFO, WARNING, ERROR
    "file_enabled": true,
    "file_path": "logs/hummingbot_mqtt.log",
    "max_file_size": "10MB",
    "backup_count": 5
  }
}
```

### การบันทึกขั้นสูง
```json
{
  "logging": {
    "level": "DEBUG",                   // รายละเอียดมากขึ้นสำหรับการแก้ไขปัญหา
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
    "file_enabled": true,
    "file_path": "/var/log/hummingbot/mqtt.log",  // ไดเรกทอรีล็อกระบบ
    "max_file_size": "50MB",
    "backup_count": 10
  }
}
```

## 🔧 ตัวอย่างการตั้งค่าทั่วไป

### การตั้งค่าการเทรดแบบระมัดระวัง
```json
{
  "hummingbot": {
    "default_strategy_configs": {
      "pure_market_making": {
        "bid_spread": 0.002,            // spread กว้างขึ้น
        "ask_spread": 0.002,
        "order_amount": 5.0,            // คำสั่งขนาดเล็ก
        "filled_order_delay": 120.0     // รอเวลานานขึ้น
      }
    }
  },
  "security": {
    "max_order_amount": 100.0,          // จำกัดต่ำลง
    "daily_loss_limit": 0.02            // จำกัดการขาดทุนรายวัน 2%
  }
}
```

### การตั้งค่าการเทรดแบบก้าวร้าว
```json
{
  "hummingbot": {
    "default_strategy_configs": {
      "pure_market_making": {
        "bid_spread": 0.0005,           // spread แคบลง
        "ask_spread": 0.0005,
        "order_amount": 20.0,           // คำสั่งขนาดใหญ่
        "filled_order_delay": 30.0      // รอเวลาสั้นลง
      }
    }
  },
  "security": {
    "max_order_amount": 5000.0,         // จำกัดสูงขึ้น
    "daily_loss_limit": 0.10            // จำกัดการขาดทุนรายวัน 10%
  }
}
```

### การตั้งค่า Arbitrage หลาย Exchange
```json
{
  "exchanges": {
    "binance": {
      "enabled": true,
      "testnet": false
    },
    "kucoin": {
      "enabled": true,
      "testnet": false
    },
    "gate_io": {
      "enabled": true,
      "testnet": false
    }
  },
  "hummingbot": {
    "default_strategy_configs": {
      "arbitrage": {
        "min_profitability": 0.005,     // กำไรขั้นต่ำ 0.5%
        "order_amount": 0.01,
        "market_1_slippage_buffer": 0.02,
        "market_2_slippage_buffer": 0.02
      }
    }
  }
}
```

## 🚨 การแก้ไขปัญหา

### ปัญหาทั่วไป

#### 1. ไม่พบเส้นทาง Hummingbot
```bash
# ค้นหาการติดตั้ง Hummingbot
which hummingbot
find / -name "hummingbot" -type f 2>/dev/null

# อัปเดตคอนฟิกด้วยเส้นทางที่ถูกต้อง
```

#### 2. การเชื่อมต่อ MQTT ล้มเหลว
```bash
# ทดสอบ MQTT broker
mosquitto_pub -h localhost -t test -m "hello"
mosquitto_sub -h localhost -t test

# ตรวจสอบไฟร์วอลล์
sudo ufw allow 1883
```

#### 3. ข้อผิดพลาด API Key
- ตรวจสอบสิทธิ์ API key
- ตรวจสอบการจำกัด IP
- ตรวจสอบให้แน่ใจว่าใช้ testnet keys สำหรับการเทรด testnet
- ตรวจสอบข้อกำหนดเฉพาะของ exchange (KuCoin passphrase)

#### 4. ข้อผิดพลาดสิทธิ์
```bash
# แก้ไขสิทธิ์ Hummingbot
sudo chown -R $USER:$USER /opt/hummingbot
chmod +x /opt/hummingbot/bin/hummingbot
```

### โหมด Debug

เปิดใช้งานการบันทึก debug สำหรับการแก้ไขปัญหา:

```json
{
  "logging": {
    "level": "DEBUG"
  }
}
```

## 📚 ทรัพยากรเพิ่มเติม

- [Hummingbot Documentation](https://docs.hummingbot.org/)
- [MQTT Protocol Guide](https://mqtt.org/)
- [API Documentation](docs/API_Documentation.md)
- [User Guide](docs/User_Guide.md)
- [Testing Guide](docs/Testing_Guide.md)

## 🤝 การสนับสนุนชุมชน

- **Discord**: [Hummingbot Discord](https://discord.gg/hummingbot)
- **GitHub Issues**: รายงานบั๊กและคำขอฟีเจอร์
- **Documentation**: มีส่วนร่วมในการปรับปรุงเอกสาร
- **Code**: ส่ง pull requests สำหรับการปรับปรุง

---

**⚠️ ข้อจำกัดความรับผิดชอบที่สำคัญ:**

1. **ความเสี่ยงในการเทรด**: การเทรดคริปโตเคอเรนซี่มีความเสี่ยงสูงต่อการสูญเสีย
2. **ความปลอดภัยของ API**: อย่าแชร์หรือ commit API keys ของคุณ
3. **การทดสอบ**: ทดสอบด้วยจำนวนเล็กน้อยและ testnet ก่อนเสมอ
4. **การติดตาม**: ติดตามกลยุทธ์ของคุณอย่างกระตือรือร้น
5. **การอัปเดต**: รักษา Hummingbot และตัวจัดการนี้ให้ทันสมัย

**📄 ใบอนุญาต**: โปรเจคนี้เป็นโอเพนซอร์สภายใต้ MIT License 