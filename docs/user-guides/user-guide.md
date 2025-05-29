# คู่มือผู้ใช้งาน

## 📚 ภาพรวม

คู่มือนี้จะแนะนำวิธีการใช้งาน Multi-Exchange Trading Bot สำหรับการจัดการ Hummingbot strategies ผ่าน MQTT

## 🚀 การเริ่มต้นใช้งาน

### 1. การติดตั้ง

```bash
# คลอนโปรเจค
git clone https://github.com/your-username/multi-exchanges-trading-bot.git
cd multi-exchanges-trading-bot

# สร้าง virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# หรือ
.\venv\Scripts\activate  # Windows

# ติดตั้ง dependencies
pip install -r requirements.txt
pip install -r requirements_hummingbot.txt
```

### 2. การตั้งค่า

1. คัดลอกไฟล์คอนฟิก:
```bash
cp config/config_hummingbot.json config/config_hummingbot_local.json
```

2. แก้ไขไฟล์คอนฟิก:
```json
{
  "hummingbot": {
    "path": "/your/hummingbot/installation/path"
  },
  "exchanges": {
    "binance": {
      "api_key": "your_api_key",
      "api_secret": "your_api_secret",
      "testnet": true
    }
  }
}
```

### 3. เริ่มต้นตัวจัดการ

```bash
python -m bots.hummingbot_manager --config config/config_hummingbot_local.json
```

## 📋 การใช้งานพื้นฐาน

### การสร้างกลยุทธ์

1. ผ่าน MQTT:
```python
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("localhost", 1883)

payload = {
    "strategy_name": "my_strategy",
    "strategy_type": "pure_market_making",
    "exchange": "binance",
    "trading_pair": "BTC-USDT",
    "config": {
        "bid_spread": 0.001,
        "ask_spread": 0.001,
        "order_amount": 10.0
    }
}

client.publish("hummingbot/strategy/create", json.dumps(payload))
```

2. ผ่าน CLI:
```bash
python cli.py create-strategy --name my_strategy --type pure_market_making --exchange binance --pair BTC-USDT
```

### การจัดการกลยุทธ์

1. เริ่มกลยุทธ์:
```bash
python cli.py start-strategy --name my_strategy
```

2. หยุดกลยุทธ์:
```bash
python cli.py stop-strategy --name my_strategy
```

3. ดูสถานะ:
```bash
python cli.py get-strategy-status --name my_strategy
```

## 🔧 การตั้งค่าขั้นสูง

### การตั้งค่าการแจ้งเตือน

1. Telegram:
```json
{
  "monitoring": {
    "telegram_notifications": {
      "enabled": true,
      "bot_token": "your_bot_token",
      "chat_id": "your_chat_id"
    }
  }
}
```

2. Discord:
```json
{
  "monitoring": {
    "discord_notifications": {
      "enabled": true,
      "webhook_url": "your_webhook_url"
    }
  }
}
```

### การตั้งค่าฐานข้อมูล

```json
{
  "database": {
    "enabled": true,
    "type": "sqlite",
    "path": "data/hummingbot_mqtt.db"
  }
}
```

## 📊 การติดตามและวิเคราะห์

### การดูประสิทธิภาพ

```bash
# ดูประสิทธิภาพของกลยุทธ์
python cli.py get-performance --name my_strategy

# ดูล็อก
python cli.py get-logs --name my_strategy
```

### การวิเคราะห์ข้อมูล

```python
import pandas as pd

# โหลดข้อมูลประสิทธิภาพ
df = pd.read_sql("SELECT * FROM strategy_performance", conn)

# วิเคราะห์ win rate
win_rate = df['profitable_trades'].sum() / df['total_trades'].sum()
print(f"Win Rate: {win_rate:.2%}")
```

## 🔒 ความปลอดภัย

### การจัดการ API Keys

1. ใช้ตัวแปรสภาพแวดล้อม:
```bash
export BINANCE_API_KEY=your_api_key
export BINANCE_API_SECRET=your_api_secret
```

2. ใช้ไฟล์ .env:
```bash
# .env
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_api_secret
```

### การจำกัดสิทธิ์

```json
{
  "security": {
    "max_concurrent_strategies": 10,
    "max_order_amount": 1000.0,
    "daily_loss_limit": 0.05
  }
}
```

## 🚨 การแก้ไขปัญหา

### ปัญหาทั่วไป

1. **การเชื่อมต่อล้มเหลว**
   - ตรวจสอบการตั้งค่า MQTT broker
   - ตรวจสอบการยืนยันตัวตน
   - ตรวจสอบไฟร์วอลล์

2. **กลยุทธ์ไม่ทำงาน**
   - ตรวจสอบการตั้งค่ากลยุทธ์
   - ตรวจสอบ API keys
   - ตรวจสอบล็อก

3. **การแจ้งเตือนไม่ทำงาน**
   - ตรวจสอบการตั้งค่าการแจ้งเตือน
   - ตรวจสอบการเชื่อมต่อ
   - ตรวจสอบสิทธิ์

### โหมด Debug

```bash
# เปิดใช้งาน debug logging
python -m bots.hummingbot_manager --config config/config_hummingbot_local.json --debug
```

## 📚 ทรัพยากรเพิ่มเติม

- [API Documentation](API_Documentation.md)
- [Configuration Guide](README_Configuration.md)
- [Testing Guide](Testing_Guide.md)
- [Hummingbot Documentation](https://docs.hummingbot.org/)

## 🤝 การสนับสนุน

- **Discord**: [Hummingbot Discord](https://discord.gg/hummingbot)
- **GitHub Issues**: รายงานบั๊กและคำขอฟีเจอร์
- **Documentation**: มีส่วนร่วมในการปรับปรุงเอกสาร
- **Code**: ส่ง pull requests สำหรับการปรับปรุง

## สารบัญ

1. [การติดตั้ง](#การติดตั้ง)
2. [การตั้งค่าเริ่มต้น](#การตั้งค่าเริ่มต้น)
3. [การใช้งานพื้นฐาน](#การใช้งานพื้นฐาน)
4. [การจัดการ Strategies](#การจัดการ-strategies)
5. [การตรวจสอบและติดตาม](#การตรวจสอบและติดตาม)
6. [การแก้ไขปัญหา](#การแก้ไขปัญหา)
7. [เคล็ดลับและแนวทางปฏิบัติที่ดี](#เคล็ดลับและแนวทางปฏิบัติที่ดี)

## การติดตั้ง

### ความต้องการของระบบ

- Python 3.8 หรือสูงกว่า
- Hummingbot ติดตั้งแล้ว
- MQTT Broker (เช่น Mosquitto)
- RAM อย่างน้อย 2GB
- พื้นที่ดิสก์ว่าง 1GB

### ขั้นตอนการติดตั้ง

#### 1. ติดตั้ง Dependencies

```bash
# ติดตั้ง Python packages
pip install -r requirements_hummingbot.txt

# ติดตั้ง MQTT Broker (Ubuntu/Debian)
sudo apt update
sudo apt install mosquitto mosquitto-clients

# เริ่มต้น Mosquitto service
sudo systemctl start mosquitto
sudo systemctl enable mosquitto
```

#### 2. ตรวจสอบการติดตั้ง Hummingbot

```bash
# ตรวจสอบว่า Hummingbot ติดตั้งอยู่ที่ไหน
which hummingbot

# หรือตรวจสอบใน path ปกติ
ls -la /opt/hummingbot/bin/hummingbot
```

#### 3. ดาวน์โหลดและติดตั้ง Hummingbot MQTT Manager

```bash
# Clone repository
git clone <repository-url>
cd multi-exchanges-trading-bot

# ติดตั้ง package
pip install -e .
```

## การตั้งค่าเริ่มต้น

### 1. การตั้งค่า Configuration

สร้างไฟล์ `config_hummingbot.json`:

```json
{
  "mqtt": {
    "host": "localhost",
    "port": 1883,
    "username": null,
    "password": null,
    "keepalive": 60,
    "qos": 1
  },
  "hummingbot": {
    "path": "/opt/hummingbot",
    "config_path": "/opt/hummingbot/conf",
    "logs_path": "/opt/hummingbot/logs",
    "strategies_path": "/opt/hummingbot/conf/strategies"
  },
  "exchanges": {
    "binance": {
      "enabled": true,
      "api_key": "YOUR_API_KEY",
      "api_secret": "YOUR_API_SECRET",
      "testnet": true
    }
  },
  "security": {
    "max_concurrent_strategies": 10,
    "max_order_amount": 1000.0,
    "daily_loss_limit": 0.05
  }
}
```

### 2. การตั้งค่า MQTT Broker

#### การตั้งค่า Mosquitto

สร้างไฟล์ `/etc/mosquitto/conf.d/hummingbot.conf`:

```
# Basic settings
listener 1883
allow_anonymous true

# Logging
log_dest file /var/log/mosquitto/mosquitto.log
log_type error
log_type warning
log_type notice
log_type information

# Persistence
persistence true
persistence_location /var/lib/mosquitto/

# Security (optional)
# password_file /etc/mosquitto/passwd
# acl_file /etc/mosquitto/acl
```

รีสตาร์ท Mosquitto:

```bash
sudo systemctl restart mosquitto
```

### 3. การตั้งค่า Hummingbot

ตรวจสอบว่า Hummingbot สามารถทำงานได้:

```bash
# ทดสอบรัน Hummingbot
/opt/hummingbot/bin/hummingbot --help

# ตรวจสอบ permissions
sudo chown -R $USER:$USER /opt/hummingbot
chmod +x /opt/hummingbot/bin/hummingbot
```

## การใช้งานพื้นฐาน

### 1. เริ่มต้น MQTT Manager

```bash
# เริ่มต้น manager
python -m bots.hummingbot_manager

# หรือใช้ config file เฉพาะ
python -m bots.hummingbot_manager --config config_hummingbot.json
```

คุณจะเห็นข้อความแสดงสถานะ:

```
🤖 เริ่มต้น Hummingbot MQTT Manager
✅ พบ Hummingbot ที่ /opt/hummingbot
📋 โหลด strategy: existing_strategy_1
🔗 เชื่อมต่อ MQTT สำเร็จ
✅ เริ่มต้น Hummingbot MQTT Manager สำเร็จ
🔍 เริ่มการตรวจสอบระบบ
```

### 2. ใช้งาน Client

#### แบบ Interactive CLI

```bash
# เริ่มต้น CLI
python -m bots.mqtt_client_example cli
```

คุณจะเห็นหน้าจอ CLI:

```
🤖 Hummingbot MQTT Controller
==================================================
Commands:
  list                    - แสดงรายการ strategies
  create <name> <type> <exchange> <pair> - สร้าง strategy
  start <name>           - เริ่ม strategy
  stop <name>            - หยุด strategy
  status <name>          - ดูสถานะ strategy
  quit                   - ออกจากโปรแกรม
==================================================

> 
```

#### แบบ Python Script

```python
import asyncio
from bots.mqtt_client_example import HummingbotMQTTClient

async def main():
    # สร้าง client
    client = HummingbotMQTTClient({
        "host": "localhost",
        "port": 1883
    })
    
    # เชื่อมต่อ
    await client.connect()
    
    # ดูรายการ strategies
    strategies = await client.get_strategies()
    print(f"พบ {strategies['total']} strategies")
    
    # ปิดการเชื่อมต่อ
    client.disconnect()

asyncio.run(main())
```

## การจัดการ Strategies

### 1. การสร้าง Strategy

#### ผ่าน CLI

```bash
> create my_pmm_strategy pure_market_making binance BTC-USDT
✅ สร้าง strategy my_pmm_strategy สำเร็จ
```

#### ผ่าน Python

```python
result = await client.create_strategy(
    name="my_pmm_strategy",
    strategy_type="pure_market_making",
    exchange="binance",
    trading_pair="BTC-USDT",
    config={
        "bid_spread": 0.001,
        "ask_spread": 0.001,
        "order_amount": 10.0,
        "inventory_skew_enabled": True,
        "filled_order_delay": 60.0
    }
)
```

### 2. การเริ่มและหยุด Strategy

#### เริ่ม Strategy

```bash
# CLI
> start my_pmm_strategy
✅ เริ่ม strategy my_pmm_strategy สำเร็จ

# Python
result = await client.start_strategy("my_pmm_strategy")
```

#### หยุด Strategy

```bash
# CLI
> stop my_pmm_strategy
✅ หยุด strategy my_pmm_strategy สำเร็จ

# Python
result = await client.stop_strategy("my_pmm_strategy")
```

#### หยุดชั่วคราว (Pause)

```bash
# CLI
> pause my_pmm_strategy
✅ หยุดชั่วคราว strategy my_pmm_strategy สำเร็จ

# Python
result = await client.pause_strategy("my_pmm_strategy")
```

#### เริ่มต่อ (Resume)

```bash
# CLI
> resume my_pmm_strategy
✅ เริ่มต่อ strategy my_pmm_strategy สำเร็จ

# Python
result = await client.resume_strategy("my_pmm_strategy")
```

### 3. การแก้ไข Configuration

```python
# อัปเดต config
new_config = {
    "bid_spread": 0.002,
    "ask_spread": 0.002,
    "order_amount": 15.0
}

result = await client.update_strategy_config("my_pmm_strategy", new_config)
```

**หมายเหตุ:** ไม่สามารถแก้ไข config ขณะ strategy กำลังทำงานอยู่

### 4. การลบ Strategy

```bash
# CLI
> delete my_pmm_strategy
⚠️ ต้องการลบ strategy my_pmm_strategy หรือไม่? (y/N): y
✅ ลบ strategy my_pmm_strategy สำเร็จ

# Python
result = await client.delete_strategy("my_pmm_strategy")
```

## การตรวจสอบและติดตาม

### 1. การดูสถานะ Strategies

#### ดูรายการทั้งหมด

```bash
# CLI
> list

📋 Strategies (3):
  strategy1: running (pure_market_making)
  strategy2: stopped (arbitrage)
  strategy3: paused (cross_exchange_market_making)
```

#### ดูสถานะเฉพาะ

```bash
# CLI
> status strategy1

📊 Status of strategy1:
  Status: running
  Type: pure_market_making
  Exchange: binance
  Trading Pair: BTC-USDT
  Last Updated: 2024-01-01 12:30:00
```

### 2. การดูผลการดำเนินงาน

#### ดูผลการดำเนินงานเฉพาะ strategy

```bash
# CLI
> performance strategy1

📈 Performance of strategy1:
  Total Trades: 25
  Profitable Trades: 18
  Win Rate: 72.00%
  Total PnL: $125.75
```

#### ดูผลการดำเนินงานทั้งหมด

```bash
# CLI
> performance

📈 All Performance:
  strategy1: 25 trades, $125.75 PnL
  strategy2: 10 trades, $-15.25 PnL
  strategy3: 5 trades, $8.50 PnL
```

### 3. การดู Logs

#### ดู logs ของ strategy เฉพาะ

```bash
# CLI
> logs strategy1 50

📝 Logs (50 lines):
  2024-01-01 12:00:00 - INFO - Strategy started
  2024-01-01 12:01:00 - INFO - Order placed: BUY 0.01 BTC at $45000
  2024-01-01 12:02:00 - INFO - Order filled: BUY 0.01 BTC at $45000
  ...
```

#### ดู logs ทั่วไป

```bash
# CLI
> logs

📝 Logs (100 lines):
  2024-01-01 12:00:00 - INFO - Hummingbot started
  2024-01-01 12:00:01 - INFO - Connected to binance
  ...
```

### 4. การตรวจสอบ Real-time

Manager จะส่งข้อมูลสถานะแบบ real-time:

- **Heartbeat**: ทุก 30 วินาที
- **Status Update**: ทุก 60 วินาที
- **Error Notifications**: เมื่อเกิดข้อผิดพลาด

```python
# ตัวอย่างการรับ real-time updates
def handle_status_update(payload):
    strategies = payload.get("strategies", {})
    for name, data in strategies.items():
        print(f"{name}: {data['status']} | PnL: ${data['performance']['total_pnl']:.2f}")

# Client จะเรียก handle_status_update อัตโนมัติ
```

## การแก้ไขปัญหา

### 1. ปัญหาการเชื่อมต่อ MQTT

#### ตรวจสอบ MQTT Broker

```bash
# ตรวจสอบว่า Mosquitto ทำงานอยู่
sudo systemctl status mosquitto

# ทดสอบการเชื่อมต่อ
mosquitto_pub -h localhost -t test -m "hello"
mosquitto_sub -h localhost -t test
```

#### ตรวจสอบ Firewall

```bash
# เปิด port 1883 สำหรับ MQTT
sudo ufw allow 1883
```

### 2. ปัญหา Hummingbot

#### ตรวจสอบ Path

```bash
# ตรวจสอบว่า Hummingbot อยู่ที่ไหน
which hummingbot
ls -la /opt/hummingbot/bin/hummingbot
```

#### ตรวจสอบ Permissions

```bash
# ตั้งค่า permissions
sudo chown -R $USER:$USER /opt/hummingbot
chmod +x /opt/hummingbot/bin/hummingbot
```

#### ตรวจสอบ Dependencies

```bash
# ตรวจสอบ Python environment
/opt/hummingbot/bin/python --version

# ตรวจสอบ packages
/opt/hummingbot/bin/pip list
```

### 3. ปัญหา Strategy

#### Strategy ไม่เริ่มต้น

1. ตรวจสอบ config file
2. ตรวจสอบ API keys
3. ตรวจสอบ network connection
4. ดู logs เพื่อหาสาเหตุ

```bash
> logs strategy_name 100
```

#### Strategy หยุดทำงานเอง

1. ตรวจสอบ error logs
2. ตรวจสอบ balance
3. ตรวจสอบ market conditions
4. ตรวจสอบ risk management settings

### 4. ปัญหา Performance

#### Manager ใช้ CPU/Memory สูง

1. ลดจำนวน strategies ที่ทำงานพร้อมกัน
2. เพิ่ม interval ของ monitoring
3. ปิด strategies ที่ไม่จำเป็น

#### การเชื่อมต่อช้า

1. ตรวจสอบ network latency
2. ใช้ MQTT broker ที่ใกล้กว่า
3. ปรับ timeout settings

## เคล็ดลับและแนวทางปฏิบัติที่ดี

### 1. การจัดการ Strategies

#### การตั้งชื่อ Strategy

```python
# ใช้ชื่อที่บ่งบอกถึงเนื้อหา
"pmm_btc_usdt_001"  # pure_market_making, BTC-USDT, spread 0.1%
"arb_binance_kucoin_btc"  # arbitrage, binance-kucoin, BTC
"xemm_eth_usdt_tight"  # cross_exchange_market_making, ETH-USDT, tight spread
```

#### การจัดกลุม Strategies

```python
# จัดกลุ่มตาม exchange
strategies_binance = ["pmm_btc_binance", "pmm_eth_binance"]
strategies_kucoin = ["pmm_btc_kucoin", "arb_btc_kucoin"]

# เริ่ม strategies ทีละกลุ่ม
for strategy in strategies_binance:
    await client.start_strategy(strategy)
    await asyncio.sleep(5)  # รอ 5 วินาทีระหว่าง strategies
```

### 2. การตรวจสอบและ Monitoring

#### การตั้งค่า Alerts

```python
async def monitor_performance():
    while True:
        result = await client.get_performance()
        
        for strategy_name, perf in result["performance"].items():
            # แจ้งเตือนเมื่อขาดทุนเกิน 5%
            if perf["total_pnl"] < -50:
                print(f"⚠️ {strategy_name} ขาดทุน ${perf['total_pnl']:.2f}")
                await client.pause_strategy(strategy_name)
            
            # แจ้งเตือนเมื่อ win rate ต่ำ
            if perf["win_rate"] < 30:
                print(f"⚠️ {strategy_name} win rate ต่ำ: {perf['win_rate']:.1f}%")
        
        await asyncio.sleep(300)  # ตรวจสอบทุก 5 นาที
```

#### การสำรองข้อมูล

```python
import json
from datetime import datetime

async def backup_strategies():
    """สำรองข้อมูล strategies"""
    strategies = await client.get_strategies()
    
    backup_data = {
        "timestamp": datetime.now().isoformat(),
        "strategies": strategies["strategies"]
    }
    
    filename = f"strategies_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(backup_data, f, indent=2, default=str)
    
    print(f"✅ สำรองข้อมูลเรียบร้อย: {filename}")

# เรียกใช้ทุกวัน
await backup_strategies()
```

### 3. การจัดการความเสี่ยง

#### การตั้งค่า Stop Loss

```python
async def check_stop_loss():
    """ตรวจสอบและหยุด strategies ที่ขาดทุนเกินกำหนด"""
    result = await client.get_performance()
    
    for strategy_name, perf in result["performance"].items():
        # หยุดเมื่อขาดทุนเกิน 2%
        if perf["total_pnl"] < -100:  # $100
            print(f"🛑 Stop loss triggered for {strategy_name}")
            await client.stop_strategy(strategy_name)
```

#### การกระจายความเสี่ยง

```python
# ไม่ใช้ strategy เดียวกันในหลาย exchanges พร้อมกัน
# แยก capital ตาม strategy type
capital_allocation = {
    "pure_market_making": 0.6,    # 60%
    "arbitrage": 0.3,             # 30%
    "cross_exchange": 0.1         # 10%
}
```

### 4. การปรับแต่ง Performance

#### การปรับ Config ตามสภาพตลาด

```python
async def adjust_spreads_by_volatility():
    """ปรับ spread ตาม volatility ของตลาด"""
    
    # ดึงข้อมูล market volatility (ต้องเพิ่ม API)
    volatility = get_market_volatility("BTC-USDT")
    
    if volatility > 0.02:  # 2%
        # ตลาดผันผวน - เพิ่ม spread
        new_config = {
            "bid_spread": 0.003,
            "ask_spread": 0.003
        }
    else:
        # ตลาดเสถียร - ลด spread
        new_config = {
            "bid_spread": 0.001,
            "ask_spread": 0.001
        }
    
    await client.update_strategy_config("pmm_btc_usdt", new_config)
```

#### การจัดการ Resources

```python
# จำกัดจำนวน strategies ที่ทำงานพร้อมกัน
MAX_CONCURRENT_STRATEGIES = 5

async def manage_strategy_resources():
    strategies = await client.get_strategies()
    running_count = len([s for s in strategies["strategies"] if s["status"] == "running"])
    
    if running_count >= MAX_CONCURRENT_STRATEGIES:
        print(f"⚠️ มี strategies ทำงานครบ {MAX_CONCURRENT_STRATEGIES} แล้ว")
        return False
    
    return True
```

### 5. การ Debug และ Troubleshooting

#### การเก็บ Logs

```python
import logging

# ตั้งค่า logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hummingbot_client.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('HummingbotClient')

# ใช้งาน
logger.info("Starting strategy management")
logger.error(f"Failed to start strategy: {error_message}")
```

#### การทดสอบ Connection

```python
async def test_connection():
    """ทดสอบการเชื่อมต่อและ response time"""
    import time
    
    start_time = time.time()
    
    try:
        result = await client.get_strategies()
        response_time = time.time() - start_time
        
        if result.get("success"):
            print(f"✅ Connection OK (Response time: {response_time:.2f}s)")
            return True
        else:
            print(f"❌ Connection failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

# ทดสอบทุก 5 นาที
while True:
    await test_connection()
    await asyncio.sleep(300)
```

## การใช้งานขั้นสูง

### 1. การสร้าง Custom Strategy Configurations

```python
# สร้าง configuration templates สำหรับ strategies ที่ใช้บ่อย
STRATEGY_CONFIGS = {
    "conservative_pmm": {
        "strategy_type": "pure_market_making",
        "config": {
            "bid_spread": 0.002,
            "ask_spread": 0.002,
            "order_amount": 10.0,
            "inventory_skew_enabled": True,
            "filled_order_delay": 120.0
        }
    },
    "aggressive_pmm": {
        "strategy_type": "pure_market_making",
        "config": {
            "bid_spread": 0.0005,
            "ask_spread": 0.0005,
            "order_amount": 20.0,
            "inventory_skew_enabled": False,
            "filled_order_delay": 30.0
        }
    }
}

async def create_from_config(name, config_name, exchange, trading_pair):
    config_template = STRATEGY_CONFIGS[config_name]
    
    result = await client.create_strategy(
        name=name,
        strategy_type=config_template["strategy_type"],
        exchange=exchange,
        trading_pair=trading_pair,
        config=config_template["config"]
    )
    
    return result
```

### 2. การทำ Batch Operations

```python
async def batch_start_strategies(strategy_names, delay=5):
    """เริ่ม strategies หลายตัวพร้อมกัน"""
    results = []
    
    for name in strategy_names:
        result = await client.start_strategy(name)
        results.append((name, result))
        
        if delay > 0:
            await asyncio.sleep(delay)
    
    return results

async def batch_update_config(strategy_names, config_updates):
    """อัปเดต config หลาย strategies"""
    results = []
    
    for name in strategy_names:
        result = await client.update_strategy_config(name, config_updates)
        results.append((name, result))
    
    return results
```

### 3. การสร้าง Dashboard

```python
import asyncio
from datetime import datetime

async def display_dashboard():
    """แสดง dashboard แบบ real-time"""
    while True:
        # Clear screen
        print("\033[2J\033[H")
        
        print("🤖 Hummingbot MQTT Manager Dashboard")
        print("=" * 60)
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # ดึงข้อมูล strategies
        strategies = await client.get_strategies()
        
        if strategies.get("success"):
            print(f"📊 Strategies Overview ({strategies['total']} total)")
            print("-" * 60)
            
            running = stopped = paused = error = 0
            total_pnl = 0
            
            for strategy in strategies["strategies"]:
                status = strategy["status"]
                pnl = strategy["performance"]["total_pnl"]
                
                if status == "running":
                    running += 1
                elif status == "stopped":
                    stopped += 1
                elif status == "paused":
                    paused += 1
                elif status == "error":
                    error += 1
                
                total_pnl += pnl
                
                # แสดงรายละเอียด strategy
                print(f"🤖 {strategy['name']:<20} {status:<10} ${pnl:>8.2f}")
            
            print("-" * 60)
            print(f"🟢 Running: {running}  🔴 Stopped: {stopped}  ⏸️ Paused: {paused}  ❌ Error: {error}")
            print(f"💰 Total PnL: ${total_pnl:.2f}")
        
        await asyncio.sleep(10)  # อัปเดตทุก 10 วินาที

# เรียกใช้ dashboard
asyncio.run(display_dashboard())
```

---

**หมายเหตุ:** คู่มือนี้จะได้รับการอัปเดตเป็นระยะ ๆ เมื่อมีฟีเจอร์ใหม่หรือการปรับปรุง กรุณาตรวจสอบเวอร์ชันล่าสุดเสมอ 