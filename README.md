# Multi-Exchange Trading Bot

A comprehensive trading bot system for managing multiple cryptocurrency exchanges with advanced strategies, risk management, and workflow automation.

## 🚀 Features

- **Multi-Exchange Support**: Trade across multiple cryptocurrency exchanges
- **Advanced Strategies**: MACD, RSI, Arbitrage, and custom strategies
- **Risk Management**: Position sizing, stop-loss, take-profit
- **Real-time Monitoring**: Live dashboard and alerts
- **MQTT Integration**: Real-time communication and event handling
- **Hummingbot Integration**: Professional trading bot framework
- **Workflow Automation**: n8n integration for complex trading workflows
- **Comprehensive Testing**: Unit, integration, and performance tests
- **Production Ready**: Docker containerization with monitoring

## 🐳 Docker Compose Quick Start

### Development Environment
```bash
# Start all services including n8n workflows
make compose-dev-up

# Access services
# Trading Bot: http://localhost:8000
# Dashboard: http://localhost:8080
# n8n Workflows: http://localhost:5678 (admin/n8n_pass)
# Grafana: http://localhost:3000
# Prometheus: http://localhost:9090
```

### Production Environment
```bash
# Start production environment
make compose-prod-up

# Access via Nginx reverse proxy
# Main App: https://your-domain.com
# n8n: https://your-domain.com/n8n
# Grafana: https://your-domain.com/grafana
```

### Testing Environment
```bash
# Run all tests
make compose-test-run

# Run specific test types
make compose-test-unit
make compose-test-integration
make compose-test-n8n  # Test n8n workflows
```

## 📊 Services Overview

| Service | Development Port | Production | Description |
|---------|------------------|------------|-------------|
| Trading Bot | 8000, 8080 | 8000 | Main application and dashboard |
| PostgreSQL | 5432 | localhost:5432 | Database |
| Redis | 6379 | localhost:6379 | Cache and session store |
| MQTT Broker | 1883, 9001 | localhost:1883 | Message broker |
| **n8n** | **5678** | **localhost:5678** | **Workflow automation** |
| Hummingbot | - | - | Trading bot framework |
| Grafana | 3000 | localhost:3000 | Monitoring dashboard |
| Prometheus | 9090 | localhost:9090 | Metrics collection |
| Nginx | 80, 443 | 80, 443 | Reverse proxy |

## 🔄 n8n Workflow Automation

n8n provides powerful workflow automation capabilities for your trading bot:

### Features
- **Visual Workflow Editor**: Drag-and-drop interface for creating complex workflows
- **Trading Triggers**: React to market events, price changes, and trading signals
- **Multi-Exchange Coordination**: Coordinate actions across multiple exchanges
- **Alert Management**: Send notifications via Telegram, Discord, email, etc.
- **Data Processing**: Transform and analyze market data
- **API Integration**: Connect with external services and APIs

### Quick Access
```bash
# Development
make n8n-dev
# Opens: http://localhost:5678 (admin/n8n_pass)

# Production
make n8n-prod
# Check production URL and credentials
```

### Workflow Management
```bash
# Backup workflows
make n8n-backup ENV=prod

# Restore workflows
make n8n-restore BACKUP_FILE=path/to/backup.json ENV=prod

# Test workflows
make compose-test-n8n
```

### Example Workflows
- **Price Alert**: Monitor price changes and send notifications
- **Arbitrage Detection**: Find arbitrage opportunities across exchanges
- **Risk Management**: Automatically adjust positions based on market conditions
- **Portfolio Rebalancing**: Maintain target asset allocations
- **Trading Signal Processing**: Execute trades based on external signals

## 🛠️ Available Commands

### Environment Management
```bash
# Development
make compose-dev-up          # Start development environment
make compose-dev-down        # Stop development environment
make compose-dev-logs        # View logs
make compose-dev-restart     # Restart services

# Production
make compose-prod-up         # Start production environment
make compose-prod-down       # Stop production environment
make compose-prod-logs       # View logs

# Testing
make compose-test-run        # Run all tests
make compose-test-unit       # Run unit tests only
make compose-test-integration # Run integration tests only
```

### Generic Commands
```bash
# Use ENV=dev|prod|test
make compose-up ENV=prod     # Start environment
make compose-down ENV=test   # Stop environment
make compose-logs ENV=dev    # View logs
make compose-restart ENV=prod # Restart environment
```

### Maintenance
```bash
make compose-clean           # Clean Docker resources
make compose-rebuild ENV=dev # Rebuild and restart
make compose-backup          # Backup database and volumes
make compose-health ENV=prod # Check service health
make compose-stats           # Show resource usage
```

### Container Access
```bash
# Access container shell
make compose-shell SERVICE=trading-bot ENV=dev
make compose-shell SERVICE=n8n ENV=prod
make compose-shell SERVICE=postgres ENV=test
```

### n8n Specific
```bash
make n8n-dev                 # Access development interface
make n8n-prod                # Production interface info
make n8n-backup ENV=prod     # Backup workflows
make n8n-restore BACKUP_FILE=backup.json # Restore workflows
```

## 📚 Documentation

For complete documentation, see the [docs/](docs/) directory:

- [Getting Started](docs/getting-started/)
- [Configuration Guide](docs/configuration/)
- [Docker Compose Guide](docs/operations/docker-compose-guide.md)
- [Development Guide](docs/development/)
- [User Guides](docs/user-guides/)

## 🔧 Configuration

### Environment Variables
Create `.env` file for development or use Docker secrets for production:

```bash
# Database
POSTGRES_HOST=postgres
POSTGRES_DB=trading_db
POSTGRES_USER=trading_user
POSTGRES_PASSWORD=your_password

# Redis
REDIS_HOST=redis
REDIS_PASSWORD=your_redis_password

# MQTT
MQTT_HOST=mqtt-broker
MQTT_PORT=1883

# n8n
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your_n8n_password
N8N_ENCRYPTION_KEY=your_encryption_key

# Trading
EXCHANGE_API_KEY=your_api_key
EXCHANGE_SECRET=your_secret
```

### Production Secrets
For production, create secret files:
```bash
mkdir -p secrets/
echo "your_password" > secrets/postgres_password.txt
echo "admin" > secrets/n8n_user.txt
echo "secure_password" > secrets/n8n_password.txt
echo "your_encryption_key" > secrets/n8n_encryption_key.txt
```

## 🚨 Security

- All production services bind to localhost only
- Secrets management for sensitive data
- SSL/TLS support for external access
- Authentication required for all admin interfaces
- Regular security updates and monitoring

## 📞 Support

For support and questions:
- **Email**: info@bemind.tech
- **Issues**: Create an issue in the repository
- **Documentation**: Check the [docs/](docs/) directory

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Bemind Technology Co., Ltd.** - Advanced Trading Solutions