# 🚀 Quick Start Guide

## 📋 Prerequisites

- Python 3.8+
- Git
- Exchange API keys (optional for testing)

## ⚡ Quick Setup (5 minutes)

### 1. Clone & Install

```bash
git clone https://github.com/your-username/multi-exchanges-trading-bot.git
cd multi-exchanges-trading-bot
pip install -r requirements.txt
```

### 2. Setup Environment

```bash
# Copy environment template
cp env.example .env

# Edit .env with your API keys (optional for testing)
nano .env
```

### 3. Create Configuration

```bash
# Create config from template
python cli.py setup

# Or use the config command
python cli.py config --action create
```

### 4. Verify Setup

```bash
# Check configuration
python cli.py config --action summary

# Test connections (if API keys provided)
python cli.py test-connection
```

## 🎯 Basic Usage

### Scan for Trading Signals

```bash
# Quick scan
python cli.py scan

# Continuous scanning
python cli.py scan-continuous --interval 15
```

### Check MACD Signals

```bash
# Check specific pair
python cli.py macd-check --symbol BTC/USDT --exchange binance

# Check with different timeframe
python cli.py macd-check --symbol ETH/USDT --timeframe 4h
```

### Monitor Markets

```bash
# Monitor specific symbol
python cli.py monitor --symbol BTC/USDT

# Analyze market
python cli.py analyze --symbol BTC/USDT
```

## 🔧 Configuration Management

```bash
# Show config info
python cli.py config --action show

# Validate config
python cli.py config --action validate

# Backup config
python cli.py config --action backup

# Export template (for sharing)
python cli.py config --action export
```

## 📊 Available Commands

| Command | Description |
|---------|-------------|
| `setup` | Interactive setup wizard |
| `config` | Manage configuration |
| `scan` | Scan for trading signals |
| `monitor` | Monitor markets |
| `analyze` | Analyze specific symbols |
| `balance` | Check account balances |
| `status` | Show exchange status |

## 🛡️ Security Best Practices

1. **Never commit `.env` file**
2. **Use sandbox/testnet for testing**
3. **Start with small amounts**
4. **Enable IP restrictions on APIs**
5. **Use read-only API keys initially**

## 🚨 Troubleshooting

### Config Issues
```bash
# Recreate config
python cli.py config --action create --force

# Check for errors
python cli.py config --action validate
```

### Connection Issues
```bash
# Test connections
python cli.py test-connection

# Check API keys in .env file
cat .env | grep API_KEY
```

### Permission Issues
```bash
# Check file permissions
ls -la config.json .env

# Fix permissions if needed
chmod 600 .env
```

## 📚 Next Steps

1. **Read the full documentation**: `docs/CONFIG_MANAGEMENT.md`
2. **Explore examples**: `examples/` directory
3. **Join the community**: [Discord/Telegram link]
4. **Report issues**: [GitHub Issues]

## ⚠️ Disclaimer

This software is for educational purposes. Trading cryptocurrencies involves risk. Always:
- Test with small amounts
- Use sandbox/testnet first
- Understand the risks
- Never invest more than you can afford to lose

---

**Happy Trading! 🎉** 