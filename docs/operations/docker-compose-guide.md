# 🐳 Docker Compose Environment Management Guide

คู่มือการใช้งาน Docker Compose สำหรับจัดการ environments ต่างๆ ของ Multi-Exchange Trading Bot

## 📋 สารบัญ

- [ภาพรวม](#ภาพรวม)
- [Environments ที่รองรับ](#environments-ที่รองรับ)
- [การติดตั้งและเตรียมความพร้อม](#การติดตั้งและเตรียมความพร้อม)
- [การใช้งานพื้นฐาน](#การใช้งานพื้นฐาน)
- [คำสั่ง Makefile](#คำสั่ง-makefile)
- [การตั้งค่า Environment Variables](#การตั้งค่า-environment-variables)
- [Services ที่รวมอยู่](#services-ที่รวมอยู่)
- [การ Monitoring และ Logging](#การ-monitoring-และ-logging)
- [การ Backup และ Recovery](#การ-backup-และ-recovery)
- [Troubleshooting](#troubleshooting)

## 🎯 ภาพรวม

ระบบ Docker Compose ของเราออกแบบมาเพื่อรองรับการพัฒนา การทดสอบ และการใช้งานจริงผ่าน environments ที่แยกจากกันอย่างชัดเจน:

- **Development**: สำหรับการพัฒนาและ debugging
- **Production**: สำหรับการใช้งานจริงที่เน้นความเสถียรและความปลอดภัย
- **Test**: สำหรับการทดสอบอัตโนมัติและ CI/CD

## 🏗️ Environments ที่รองรับ

### 1. Development Environment (`docker-compose.yml`)

**จุดประสงค์**: การพัฒนาและ debugging

**คุณสมบัติ**:
- Hot reload สำหรับการพัฒนา
- Debug mode เปิดใช้งาน
- Ports เปิดให้เข้าถึงจากภายนอก
- Volume mounts สำหรับ live editing
- Development tools และ utilities

**Services**:
- Trading Bot (development mode)
- PostgreSQL Database
- Redis Cache
- MQTT Broker
- Hummingbot
- Grafana Dashboard
- Prometheus Monitoring
- Nginx Reverse Proxy

### 2. Production Environment (`docker-compose.prod.yml`)

**จุดประสงค์**: การใช้งานจริงในระดับ production

**คุณสมบัติ**:
- Optimized images และ resource limits
- Security hardening
- Health checks และ auto-restart
- SSL/TLS encryption
- Secrets management
- Log aggregation
- Backup services

**Services**:
- Trading Bot (production mode)
- PostgreSQL with HA configuration
- Redis with persistence
- MQTT Broker with authentication
- Hummingbot
- Grafana with security settings
- Prometheus with retention policies
- Nginx with SSL
- Fluentd for log aggregation
- Backup service

### 3. Test Environment (`docker-compose.test.yml`)

**จุดประสงค์**: การทดสอบอัตโนมัติและ CI/CD

**คุณสมบัติ**:
- Isolated test environment
- Mock services
- Test data generation
- Code quality checks
- Performance testing
- Security testing

**Services**:
- Test Runner
- Unit Test Runner
- Integration Test Runner
- Performance Test Runner
- Security Test Runner
- Test Database (PostgreSQL)
- Test Cache (Redis)
- Test MQTT Broker
- Mock Exchange API
- Code Quality Checker
- Load Test Runner

## 🚀 การติดตั้งและเตรียมความพร้อม

### ข้อกำหนดระบบ

```bash
# ตรวจสอบ Docker และ Docker Compose
docker --version          # >= 20.10.0
docker-compose --version  # >= 2.0.0

# ตรวจสอบ Make
make --version
```

### การเตรียมไฟล์คอนฟิก

```bash
# 1. สร้างไฟล์ environment variables
cp .env.example .env

# 2. แก้ไขค่าตั้งต่างๆ ใน .env
vim .env

# 3. สร้างโฟลเดอร์ที่จำเป็น
mkdir -p logs temp backups config/ssl secrets

# 4. สร้าง secrets สำหรับ production
echo "your_postgres_password" > secrets/postgres_password.txt
echo "your_hummingbot_password" > secrets/hummingbot_password.txt
echo "your_grafana_password" > secrets/grafana_password.txt
```

## 💻 การใช้งานพื้นฐาน

### Development Environment

```bash
# เริ่มต้น development environment
make compose-dev-up

# ตรวจสอบสถานะ
make compose-dev-ps

# ดู logs
make compose-dev-logs

# หยุดการทำงาน
make compose-dev-down
```

### Production Environment

```bash
# เริ่มต้น production environment
make compose-prod-up

# ตรวจสอบสถานะ
make compose-prod-ps

# ดู logs
make compose-prod-logs

# หยุดการทำงาน
make compose-prod-down
```

### Test Environment

```bash
# เริ่มต้น test environment
make compose-test-up

# รันการทดสอบ
make compose-test-run

# รัน unit tests เท่านั้น
docker-compose -f docker-compose.test.yml --profile unit up

# รัน integration tests
docker-compose -f docker-compose.test.yml --profile integration up

# หยุดการทำงาน
make compose-test-down
```

## 🛠️ คำสั่ง Makefile

### คำสั่งพื้นฐาน

```bash
# แสดงความช่วยเหลือ
make help
make compose-help

# เริ่ม/หยุด environments
make compose-up ENV=dev|prod|test
make compose-down ENV=dev|prod|test
make compose-restart ENV=dev|prod|test

# ดู logs และสถานะ
make compose-logs ENV=dev|prod|test
make compose-ps ENV=dev|prod|test
```

### คำสั่งบำรุงรักษา

```bash
# ทำความสะอาด
make compose-clean

# Rebuild images
make compose-rebuild ENV=dev|prod|test

# เข้าถึง shell ใน container
make compose-shell ENV=dev|prod|test

# Backup ข้อมูล
make compose-backup ENV=dev|prod|test
```

### คำสั่งติดตาม

```bash
# ตรวจสอบสุขภาพระบบ
make compose-health ENV=dev|prod|test

# ดูการใช้ทรัพยากร
make compose-stats ENV=dev|prod|test
```

## ⚙️ การตั้งค่า Environment Variables

### ไฟล์ Environment Variables

- `.env` - สำหรับ development และ production
- `.env.test` - สำหรับ testing environment

### ตัวแปรสำคัญ

```bash
# Application
ENVIRONMENT=development|production|test
DEBUG=0|1

# Database
POSTGRES_HOST=postgres
POSTGRES_DB=trading_db
POSTGRES_USER=trading_user
POSTGRES_PASSWORD=secure_password

# Redis
REDIS_HOST=redis
REDIS_PASSWORD=redis_password

# MQTT
MQTT_HOST=mqtt-broker
MQTT_PORT=1883

# Exchange APIs
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_api_secret
```

## 🔧 Services ที่รวมอยู่

### Core Services

#### Trading Bot
- **Port**: 8000 (API), 8080 (Dashboard)
- **Health Check**: `/health` endpoint
- **Volumes**: Source code, config, logs

#### PostgreSQL Database
- **Port**: 5432 (dev), 127.0.0.1:5432 (prod)
- **Health Check**: `pg_isready`
- **Volumes**: Data persistence, init scripts

#### Redis Cache
- **Port**: 6379 (dev), 127.0.0.1:6379 (prod)
- **Health Check**: `redis-cli ping`
- **Volumes**: Data persistence

#### MQTT Broker (Mosquitto)
- **Port**: 1883 (MQTT), 9001 (WebSocket)
- **Health Check**: Publish test message
- **Volumes**: Config, data, logs

### Monitoring Services

#### Grafana
- **Port**: 3000
- **Default Login**: admin/admin (dev), secrets (prod)
- **Volumes**: Dashboards, datasources

#### Prometheus
- **Port**: 9090
- **Volumes**: Configuration, data

### Support Services

#### Nginx (Reverse Proxy)
- **Port**: 80, 443
- **Features**: Load balancing, SSL termination
- **Volumes**: Configuration, SSL certificates

#### Hummingbot
- **Features**: MQTT integration
- **Volumes**: Configuration, logs, data

## 📊 การ Monitoring และ Logging

### Grafana Dashboards

เข้าถึงได้ที่: `http://localhost:3000`

**Dashboards ที่มี**:
- Trading Bot Performance
- System Resources
- Database Metrics
- MQTT Broker Status
- Exchange API Metrics

### Prometheus Metrics

เข้าถึงได้ที่: `http://localhost:9090`

**Metrics ที่เก็บ**:
- Application metrics
- System metrics
- Database metrics
- Custom trading metrics

### Log Management

```bash
# ดู logs แบบ real-time
make compose-logs ENV=dev

# ดู logs ของ service เฉพาะ
docker-compose logs -f trading-bot

# ดู logs ใน production (ผ่าน Fluentd)
docker-compose -f docker-compose.prod.yml logs fluentd
```

## 💾 การ Backup และ Recovery

### Automatic Backup (Production)

```bash
# รัน backup service
docker-compose -f docker-compose.prod.yml --profile backup up backup

# Backup แบบ manual
make compose-backup ENV=prod
```

### Manual Backup

```bash
# Backup database
docker-compose exec postgres pg_dump -U trading_user trading_db > backup.sql

# Backup Redis
docker-compose exec redis redis-cli BGSAVE

# Backup configuration
tar -czf config-backup.tar.gz config/
```

### Recovery

```bash
# Restore database
docker-compose exec -T postgres psql -U trading_user trading_db < backup.sql

# Restore Redis
docker cp backup.rdb redis-container:/data/dump.rdb
docker-compose restart redis
```

## 🔒 Security Best Practices

### Production Security

1. **Secrets Management**
   ```bash
   # ใช้ Docker secrets
   echo "secure_password" | docker secret create postgres_password -
   ```

2. **Network Security**
   ```bash
   # Bind services to localhost only
   ports:
     - "127.0.0.1:5432:5432"
   ```

3. **SSL/TLS**
   ```bash
   # Generate SSL certificates
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout config/ssl/private.key \
     -out config/ssl/certificate.crt
   ```

### Access Control

```bash
# Create restricted user
docker-compose exec postgres createuser --no-superuser --no-createdb --no-createrole trading_user

# Set up MQTT authentication
docker-compose exec mqtt-broker mosquitto_passwd -c /mosquitto/config/passwd username
```

## 🐛 Troubleshooting

### ปัญหาที่พบบ่อย

#### 1. Port Conflicts

```bash
# ตรวจสอบ ports ที่ใช้งาน
netstat -tulpn | grep :5432

# เปลี่ยน port ใน docker-compose.yml
ports:
  - "5433:5432"
```

#### 2. Permission Issues

```bash
# แก้ไข permissions
sudo chown -R $USER:$USER logs/ temp/ backups/

# ตรวจสอบ SELinux (CentOS/RHEL)
setsebool -P container_manage_cgroup on
```

#### 3. Memory Issues

```bash
# เพิ่ม memory limits
deploy:
  resources:
    limits:
      memory: 2G
```

#### 4. Database Connection Issues

```bash
# ตรวจสอบ database health
docker-compose exec postgres pg_isready -U trading_user

# ดู database logs
docker-compose logs postgres
```

### การ Debug

```bash
# เข้าถึง container shell
make compose-shell ENV=dev

# ตรวจสอบ network connectivity
docker-compose exec trading-bot ping postgres

# ดู environment variables
docker-compose exec trading-bot env | grep POSTGRES
```

### Performance Tuning

```bash
# ตรวจสอบการใช้ทรัพยากร
make compose-stats ENV=prod

# ปรับแต่ง PostgreSQL
# แก้ไข config/postgres/postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
```

## 📚 เอกสารเพิ่มเติม

- [Docker Compose Reference](https://docs.docker.com/compose/)
- [PostgreSQL Configuration](https://www.postgresql.org/docs/current/runtime-config.html)
- [Redis Configuration](https://redis.io/topics/config)
- [Mosquitto Configuration](https://mosquitto.org/man/mosquitto-conf-5.html)
- [Grafana Documentation](https://grafana.com/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)

## 🤝 การสนับสนุน

หากพบปัญหาหรือต้องการความช่วยเหลือ:

- 📖 ดู [FAQ](./faq.md)
- 🐛 รายงานปัญหาผ่าน GitHub Issues
- 💬 เข้าร่วม Discord Community
- 📧 ติดต่อ info@bemind.tech

---

**หมายเหตุ**: คู่มือนี้จะได้รับการอัปเดตเป็นประจำตามการพัฒนาของระบบ 