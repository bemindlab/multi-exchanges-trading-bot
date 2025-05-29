# 📚 Multi-Exchange Trading Bot Documentation

ยินดีต้อนรับสู่เอกสารประกอบของ Multi-Exchange Trading Bot! เอกสารนี้จัดระเบียบตามหมวดหมู่เพื่อให้ง่ายต่อการค้นหาและใช้งาน

## 📖 สารบัญ

### 🚀 [Getting Started](./getting-started/)
เริ่มต้นใช้งาน Trading Bot อย่างรวดเร็ว

- **[Quick Start Guide](./getting-started/quick-start.md)** - เริ่มต้นใช้งานภายใน 5 นาที
- **[Installation Guide](./getting-started/installation.md)** - คู่มือการติดตั้งแบบละเอียด
- **[Overview](./getting-started/overview.md)** - ภาพรวมของระบบและคุณสมบัติ

### 👤 [User Guides](./user-guides/)
คู่มือการใช้งานสำหรับผู้ใช้

- **[User Guide](./user-guides/user-guide.md)** - คู่มือผู้ใช้งานฉบับสมบูรณ์
- **[CLI Commands](./user-guides/cli-commands.md)** - รายการคำสั่ง CLI ทั้งหมด
- **[Scanner Examples](./user-guides/scanner-examples.md)** - ตัวอย่างการใช้งาน Scanner
- **[Crypto Scanner Guide](./user-guides/crypto-scanner-guide.md)** - คู่มือการใช้งาน Crypto Scanner

### ⚙️ [Configuration](./configuration/)
การตั้งค่าและปรับแต่งระบบ

- **[Configuration Guide](./configuration/configuration-guide.md)** - คู่มือการตั้งค่าทั้งหมด
- **[Config Management](./configuration/config-management.md)** - การจัดการไฟล์คอนฟิก
- **[Hummingbot MQTT Setup](./configuration/hummingbot-mqtt-setup.md)** - การตั้งค่า Hummingbot กับ MQTT

### 🛠️ [Development](./development/)
สำหรับนักพัฒนา

- **[API Documentation](./development/api-documentation.md)** - เอกสาร API Reference
- **[Testing Guide](./development/testing-guide.md)** - คู่มือการทดสอบ
- **[Project Structure](./development/project-structure.md)** - โครงสร้างโปรเจ็กต์และ Best Practices

### 📋 [Operations](./operations/)
การดำเนินการและบำรุงรักษา

- **[Security Guide](./operations/security.md)** - แนวทางด้านความปลอดภัย
- **[Temp Folder Migration](./operations/temp-folder-migration.md)** - การย้ายโฟลเดอร์ชั่วคราว
- **[FAQ](./operations/faq.md)** - คำถามที่พบบ่อย

### 📝 [Release Notes](./release-notes/)
บันทึกการเปลี่ยนแปลง

- **[Changelog](./release-notes/changelog.md)** - ประวัติการเปลี่ยนแปลง
- **[Upgrade Summary](./release-notes/upgrade-summary.md)** - สรุปการอัปเกรด

---

## 🔍 Quick Links

### สำหรับผู้เริ่มต้น
1. อ่าน [Quick Start Guide](./getting-started/quick-start.md)
2. ติดตั้งระบบตาม [Installation Guide](./getting-started/installation.md)
3. ตั้งค่าระบบตาม [Configuration Guide](./configuration/configuration-guide.md)

### สำหรับผู้ใช้งาน
1. ศึกษา [User Guide](./user-guides/user-guide.md)
2. เรียนรู้ [CLI Commands](./user-guides/cli-commands.md)
3. ดูตัวอย่างใน [Scanner Examples](./user-guides/scanner-examples.md)

### สำหรับนักพัฒนา
1. อ่าน [Project Structure](./development/project-structure.md)
2. ศึกษา [API Documentation](./development/api-documentation.md)
3. ทำความเข้าใจ [Testing Guide](./development/testing-guide.md)

---

## 📊 Documentation Structure

```
docs/
├── README.md                 # หน้านี้
├── getting-started/         # เอกสารเริ่มต้น
│   ├── quick-start.md
│   ├── installation.md
│   └── overview.md
├── user-guides/            # คู่มือผู้ใช้
│   ├── user-guide.md
│   ├── cli-commands.md
│   ├── scanner-examples.md
│   └── crypto-scanner-guide.md
├── configuration/          # การตั้งค่า
│   ├── configuration-guide.md
│   ├── config-management.md
│   └── hummingbot-mqtt-setup.md
├── development/           # การพัฒนา
│   ├── api-documentation.md
│   ├── testing-guide.md
│   └── project-structure.md
├── operations/           # การดำเนินการ
│   ├── security.md
│   ├── temp-folder-migration.md
│   └── faq.md
└── release-notes/       # บันทึกการเปลี่ยนแปลง
    ├── changelog.md
    └── upgrade-summary.md
```

---

## 🤝 Contributing to Documentation

หากต้องการมีส่วนร่วมในการปรับปรุงเอกสาร:

1. Fork repository
2. สร้าง branch ใหม่สำหรับการแก้ไข
3. แก้ไขเอกสารตามต้องการ
4. ส่ง Pull Request

### การเขียนเอกสารที่ดี
- ใช้ภาษาที่เข้าใจง่าย
- เพิ่มตัวอย่างโค้ดเมื่อเหมาะสม
- ใช้รูปภาพหรือ diagram เพื่อช่วยอธิบาย
- ตรวจสอบ spelling และ grammar
- ใช้ Markdown formatting ที่ถูกต้อง

---

## 📞 Need Help?

- **GitHub Issues**: รายงานปัญหาหรือขอคุณสมบัติใหม่
- **Discord**: เข้าร่วมชุมชนเพื่อถามคำถาม
- **Email**: info@bemind.tech

---

**Last Updated**: {{ current_date }}
**Version**: 1.0.0 