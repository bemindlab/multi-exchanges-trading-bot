# ⚙️ Configuration

คู่มือการตั้งค่าและปรับแต่ง Multi-Exchange Trading Bot ให้เหมาะสมกับความต้องการของคุณ

## 📋 เอกสารในหมวดนี้

### 1. [Configuration Guide](./configuration-guide.md)
คู่มือการตั้งค่าระบบอย่างละเอียด
- การตั้งค่าพื้นฐาน
- การตั้งค่าขั้นสูง
- Environment variables
- Exchange configurations

### 2. [Config Management](./config-management.md)
การจัดการไฟล์คอนฟิกและ best practices
- โครงสร้างไฟล์คอนฟิก
- การจัดการ multiple configurations
- การ backup และ restore
- Version control

### 3. [Hummingbot MQTT Setup](./hummingbot-mqtt-setup.md)
การตั้งค่า Hummingbot ผ่าน MQTT
- การติดตั้ง MQTT broker
- การเชื่อมต่อ Hummingbot
- การส่งคำสั่งผ่าน MQTT
- Troubleshooting

## 🎯 Configuration Workflow

### 🆕 การตั้งค่าเริ่มต้น
1. สร้างไฟล์ config จาก template
2. ตั้งค่า API keys สำหรับ exchanges
3. กำหนด trading parameters พื้นฐาน
4. ทดสอบการเชื่อมต่อ

### 🔧 การปรับแต่งขั้นสูง
1. ปรับแต่ง risk management parameters
2. ตั้งค่า notification channels
3. กำหนด custom strategies
4. เพิ่ม performance monitoring

### 🤖 การตั้งค่า Automation
1. ตั้งค่า MQTT สำหรับ remote control
2. กำหนด scheduled tasks
3. ตั้งค่า auto-restart และ failover
4. เพิ่ม monitoring และ alerting

## 📝 ไฟล์คอนฟิกที่สำคัญ

### `/config/config.json`
ไฟล์คอนฟิกหลักของระบบ
```json
{
  "exchanges": {},
  "strategies": {},
  "risk_management": {},
  "notifications": {}
}
```

### `.env`
ตัวแปรสภาพแวดล้อมและ API keys
```env
EXCHANGE_API_KEY=your_key
EXCHANGE_API_SECRET=your_secret
```

### `/config/strategies/`
ไฟล์คอนฟิกสำหรับแต่ละ strategy

## 🔒 Security Best Practices

### API Keys
- ใช้ read-only keys เมื่อเป็นไปได้
- จำกัด IP whitelist
- Rotate keys เป็นประจำ
- ไม่ commit keys ลง version control

### File Permissions
- จำกัดสิทธิ์การอ่านไฟล์ config
- ใช้ encrypted storage สำหรับ sensitive data
- Regular security audits

### Network Security
- ใช้ VPN สำหรับ remote access
- Enable firewall rules
- Monitor suspicious activities

## 💡 Configuration Tips

### Performance
- ปรับ polling intervals ตามความต้องการ
- จำกัดจำนวน concurrent operations
- ใช้ caching อย่างเหมาะสม

### Reliability
- ตั้งค่า proper timeouts
- Enable retry mechanisms
- Configure error handling

### Monitoring
- Enable comprehensive logging
- Set up alerts สำหรับ critical events
- Monitor resource usage

## 🔗 ทรัพยากรที่เกี่ยวข้อง

- **[Environment Variables Reference](./configuration-guide.md#environment-variables)**
- **[Strategy Configuration](../user-guides/user-guide.md#strategies)**
- **[Security Guide](../operations/security.md)**

## ❓ ปัญหาที่พบบ่อย

### Connection Issues
- ตรวจสอบ API credentials
- ตรวจสอบ network connectivity
- ดู rate limits

### Configuration Errors
- Validate JSON syntax
- ตรวจสอบ required fields
- Check data types

### Performance Problems
- ปรับ polling intervals
- ลด concurrent requests
- Optimize database queries

## 📞 การสนับสนุน

- 📖 ดู [FAQ](../operations/faq.md) สำหรับคำถามที่พบบ่อย
- 💬 เข้าร่วม Discord Community
- 📧 ติดต่อ info@bemind.tech 