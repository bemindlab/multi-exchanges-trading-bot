# Hummingbot MQTT Strategy Manager

ระบบจัดการ Hummingbot strategies ผ่าน MQTT protocol ที่ช่วยให้คุณสามารถควบคุม Hummingbot strategies จากระยะไกลได้

## ✨ Features

- 🤖 **Strategy Management**: สร้าง, เริ่ม, หยุด, และลบ strategies
- 📡 **MQTT Communication**: ควบคุมผ่าน MQTT protocol
- 📊 **Real-time Monitoring**: ติดตามสถานะและผลการดำเนินงานแบบ real-time
- 🔧 **Configuration Management**: จัดการ config ของ strategies
- 📝 **Logging**: ดู logs และ error messages
- 🔒 **Security**: ระบบรักษาความปลอดภัยและการจำกัดสิทธิ์
- 🎯 **Multiple Strategy Types**: รองรับ strategy หลายประเภท

## 🚀 Quick Start

### 1. ติดตั้ง Dependencies

```bash
pip install -r requirements_hummingbot.txt
```

### 2. ตั้งค่า Configuration

แก้ไขไฟล์ `config_hummingbot.json`:

```json
{
  "mqtt": {
    "host": "localhost",
    "port": 1883,
    "username": null,
    "password": null
  },
  "hummingbot": {
    "path": "/opt/hummingbot",
    "strategies_path": "/opt/hummingbot/conf/strategies"
  }
}
```

### 3. เริ่มต้น MQTT Manager

```bash
python -m bots.hummingbot_manager
```

### 4. ใช้งาน Client

```bash
# Interactive CLI
python -m bots.mqtt_client_example cli

# หรือใช้ในโค้ด
python -m bots.mqtt_client_example
```

## 📡 MQTT Topics

### Command Topics (Publish)
- `hummingbot/command/create_strategy` - สร้าง strategy ใหม่
- `hummingbot/command/start_strategy` - เริ่ม strategy
- `hummingbot/command/stop_strategy` - หยุด strategy
- `hummingbot/command/pause_strategy` - หยุดชั่วคราว
- `hummingbot/command/resume_strategy` - เริ่มต่อ
- `hummingbot/command/delete_strategy` - ลบ strategy
- `hummingbot/command/get_strategies` - ดึงรายการ strategies
- `hummingbot/command/get_strategy_status` - ดูสถานะ
- `hummingbot/command/update_strategy_config` - อัปเดต config
- `hummingbot/command/get_performance` - ดูผลการดำเนินงาน
- `hummingbot/command/get_logs` - ดู logs
- `hummingbot/command/restart_hummingbot` - รีสตาร์ท

### Status Topics (Subscribe)
- `hummingbot/status/+` - Response จาก commands
- `hummingbot/status/heartbeat` - Heartbeat signal
- `hummingbot/status/update` - Status updates
- `hummingbot/logs/error` - Error notifications

## 🎯 Strategy Types

รองรับ strategy types ต่อไปนี้:

- **pure_market_making** - Market making แบบพื้นฐาน
- **cross_exchange_market_making** - Market making ข้าม exchange
- **arbitrage** - Arbitrage trading
- **avellaneda_market_making** - Advanced market making
- **liquidity_mining** - Liquidity mining

## 💻 การใช้งาน

### สร้าง Strategy

```python
from bots.mqtt_client_example import HummingbotMQTTClient

client = HummingbotMQTTClient({
    "host": "localhost",
    "port": 1883
})

await client.connect()

# สร้าง strategy
result = await client.create_strategy(
    name="my_strategy",
    strategy_type="pure_market_making",
    exchange="binance",
    trading_pair="BTC-USDT",
    config={
        "bid_spread": 0.001,
        "ask_spread": 0.001,
        "order_amount": 10.0
    }
)
```

### เริ่ม Strategy

```python
result = await client.start_strategy("my_strategy")
```

### ตรวจสอบสถานะ

```python
result = await client.get_strategy_status("my_strategy")
print(result["strategy"]["status"])
```

### ดูผลการดำเนินงาน

```python
result = await client.get_performance("my_strategy")
performance = result["performance"]
print(f"Total Trades: {performance['total_trades']}")
print(f"Win Rate: {performance['win_rate']:.2f}%")
print(f"Total PnL: ${performance['total_pnl']:.2f}")
```

## 🔧 Command Line Interface

ใช้ CLI แบบ interactive:

```bash
python -m bots.mqtt_client_example cli
```

Commands ที่ใช้ได้:
- `list` - แสดงรายการ strategies
- `create <name> <type> <exchange> <pair>` - สร้าง strategy
- `start <name>` - เริ่ม strategy
- `stop <name>` - หยุด strategy
- `status <name>` - ดูสถานะ
- `performance [name]` - ดูผลการดำเนินงาน
- `logs [name] [lines]` - ดู logs
- `delete <name>` - ลบ strategy
- `quit` - ออกจากโปรแกรม

## 📊 Monitoring

### Heartbeat
ระบบส่ง heartbeat ทุก 30 วินาที:

```json
{
  "timestamp": "2024-01-01T12:00:00",
  "status": "alive",
  "strategies_count": 5,
  "running_count": 3
}
```

### Status Updates
ส่งข้อมูลสถานะทุก 60 วินาที:

```json
{
  "timestamp": "2024-01-01T12:00:00",
  "strategies": {
    "strategy_1": {
      "status": "running",
      "last_updated": "2024-01-01T11:59:00",
      "performance": {
        "total_trades": 10,
        "total_pnl": 15.50
      }
    }
  }
}
```

## 🔒 Security

### การจำกัดสิทธิ์
- จำกัดจำนวน strategies ที่ทำงานพร้อมกัน
- จำกัดขนาดออเดอร์สูงสุด
- จำกัดการสูญเสียรายวัน
- ระบบ timeout สำหรับ strategies

### Commands ที่จำกัด
บาง commands ต้องการสิทธิ์พิเศษ:
- `restart_hummingbot` - รีสตาร์ทระบบ

## 🐛 Troubleshooting

### ปัญหาการเชื่อมต่อ MQTT
```bash
# ตรวจสอบ MQTT broker
mosquitto_pub -h localhost -t test -m "hello"
```

### ปัญหา Hummingbot path
```bash
# ตรวจสอบ path
ls -la /opt/hummingbot/bin/hummingbot
```

### ปัญหา permissions
```bash
# ตั้งค่า permissions
chmod +x /opt/hummingbot/bin/hummingbot
```

## 📝 Logs

Logs จะถูกเก็บไว้ที่:
- `logs/hummingbot_mqtt.log` - Main logs
- `/opt/hummingbot/logs/` - Hummingbot logs

## 🔄 Integration

### กับระบบอื่น
สามารถ integrate กับ:
- **Telegram Bot** - รับการแจ้งเตือน
- **Discord Webhook** - ส่งข้อความไปยัง Discord
- **Web Dashboard** - สร้าง web interface
- **Database** - เก็บข้อมูลประวัติ

### API Integration
```python
# ใช้กับ FastAPI
from fastapi import FastAPI
from bots.hummingbot_manager import HummingbotMQTTManager

app = FastAPI()
manager = HummingbotMQTTManager()

@app.post("/strategies")
async def create_strategy(strategy_data: dict):
    # สร้าง strategy ผ่าน MQTT
    pass
```

## 📚 Examples

ดูตัวอย่างเพิ่มเติมในโฟลเดอร์ `examples/`:
- `basic_usage.py` - การใช้งานพื้นฐาน
- `advanced_monitoring.py` - การติดตามขั้นสูง
- `batch_operations.py` - การจัดการหลาย strategies
- `custom_strategies.py` - การสร้าง custom strategies

## 🤝 Contributing

1. Fork repository
2. สร้าง feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

MIT License - ดูไฟล์ LICENSE สำหรับรายละเอียด

## 🆘 Support

- 📧 Email: info@bemind.tech
- 💬 Discord: [Discord Server](https://discord.gg/example)
- 📖 Documentation: [Wiki](https://github.com/example/wiki)

---

**⚠️ คำเตือน**: การเทรดมีความเสี่ยง กรุณาทดสอบในสภาพแวดล้อม testnet ก่อนใช้งานจริง 