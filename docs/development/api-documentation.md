# API Documentation

## 📚 ภาพรวม

เอกสารนี้อธิบาย API ที่ใช้สำหรับการจัดการ Hummingbot strategies ผ่าน MQTT

## 🔌 MQTT Topics

### การจัดการกลยุทธ์

| Topic | Description | Payload Format |
|-------|-------------|----------------|
| `hummingbot/strategy/create` | สร้างกลยุทธ์ใหม่ | JSON |
| `hummingbot/strategy/start` | เริ่มกลยุทธ์ | JSON |
| `hummingbot/strategy/stop` | หยุดกลยุทธ์ | JSON |
| `hummingbot/strategy/pause` | ระงับกลยุทธ์ | JSON |
| `hummingbot/strategy/resume` | ดำเนินกลยุทธ์ต่อ | JSON |
| `hummingbot/strategy/delete` | ลบกลยุทธ์ | JSON |
| `hummingbot/strategy/update` | อัปเดตการตั้งค่ากลยุทธ์ | JSON |

### การติดตามสถานะ

| Topic | Description | Payload Format |
|-------|-------------|----------------|
| `hummingbot/status` | สถานะของ Hummingbot | JSON |
| `hummingbot/performance` | ประสิทธิภาพของกลยุทธ์ | JSON |
| `hummingbot/logs` | ล็อกของ Hummingbot | JSON |

### การแจ้งเตือน

| Topic | Description | Payload Format |
|-------|-------------|----------------|
| `hummingbot/notifications/telegram` | การแจ้งเตือนผ่าน Telegram | JSON |
| `hummingbot/notifications/discord` | การแจ้งเตือนผ่าน Discord | JSON |

## 📝 รูปแบบ Payload

### การสร้างกลยุทธ์

```json
{
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
```

### การอัปเดตกลยุทธ์

```json
{
  "strategy_name": "my_strategy",
  "config": {
    "bid_spread": 0.002,
    "ask_spread": 0.002
  }
}
```

### การแจ้งเตือน

```json
{
  "message": "Strategy started successfully",
  "level": "INFO",
  "timestamp": "2024-03-20T10:00:00Z"
}
```

## 🔒 การยืนยันตัวตน

### MQTT Authentication

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

### API Key Authentication

```json
{
  "api_key": "your_api_key",
  "api_secret": "your_api_secret"
}
```

## 📊 การตอบกลับ

### การตอบกลับที่สำเร็จ

```json
{
  "status": "success",
  "message": "Strategy created successfully",
  "data": {
    "strategy_name": "my_strategy",
    "strategy_id": "123456"
  }
}
```

### การตอบกลับที่ล้มเหลว

```json
{
  "status": "error",
  "message": "Invalid strategy configuration",
  "error_code": "INVALID_CONFIG",
  "details": {
    "field": "order_amount",
    "reason": "Must be greater than 0"
  }
}
```

## 🚀 ตัวอย่างการใช้งาน

### Python

```python
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("hummingbot/status")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)
client.loop_forever()
```

### Node.js

```javascript
const mqtt = require('mqtt')
const client = mqtt.connect('mqtt://localhost')

client.on('connect', function () {
  client.subscribe('hummingbot/status')
})

client.on('message', function (topic, message) {
  console.log(topic, message.toString())
})
```

## 🔧 การแก้ไขปัญหา

### ข้อผิดพลาดทั่วไป

1. **การเชื่อมต่อล้มเหลว**
   - ตรวจสอบการตั้งค่า MQTT broker
   - ตรวจสอบการยืนยันตัวตน
   - ตรวจสอบไฟร์วอลล์

2. **การตอบกลับไม่ถูกต้อง**
   - ตรวจสอบรูปแบบ payload
   - ตรวจสอบการตั้งค่ากลยุทธ์
   - ตรวจสอบสิทธิ์

3. **การแจ้งเตือนไม่ทำงาน**
   - ตรวจสอบการตั้งค่าการแจ้งเตือน
   - ตรวจสอบการเชื่อมต่อ
   - ตรวจสอบสิทธิ์

## 📚 ทรัพยากรเพิ่มเติม

- [MQTT Protocol Guide](https://mqtt.org/)
- [Hummingbot Documentation](https://docs.hummingbot.org/)
- [Paho MQTT Client](https://www.eclipse.org/paho/)
- [MQTT.js](https://github.com/mqttjs/MQTT.js) 