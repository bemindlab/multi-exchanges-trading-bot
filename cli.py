#!/usr/bin/env python3
import asyncio
import click
import json
import os
from datetime import datetime
from bots.exchange_manager import ExchangeManager
from bots.market_analyzer import MultiExchangeMarketAnalyzer, run_market_analysis
from bots.multi_exchange_bot import MultiExchangeTradingBot, run_multi_exchange_bot
from bots.crypto_scanner import CryptoPairsScanner, run_single_scan, run_continuous_scan
from config_manager import ConfigManager, ensure_config_exists

@click.group()
@click.version_option(version='2.0.0')
def cli():
    """🤖 Multi-Exchange Trading Bot CLI
    
    รองรับการเทรดใน CEX และ DEX หลายแห่งพร้อมกัน
    """
    pass

@cli.command()
@click.option('--config', '-c', default='config.json', help='ไฟล์ config')
def list_exchanges(config):
    """📋 แสดงรายการ exchanges ที่รองรับ"""
    click.echo("🏢 รายการ Exchanges ที่รองรับ:")
    click.echo("=" * 50)
    
    # CEX
    click.echo("\n💱 Centralized Exchanges (CEX):")
    cex_list = [
        "binance - Binance",
        "gateio - Gate.io", 
        "okx - OKX",
        "kucoin - KuCoin",
        "bybit - Bybit",
        "huobi - Huobi"
    ]
    for exchange in cex_list:
        click.echo(f"  ✅ {exchange}")
    
    # DEX
    click.echo("\n🔄 Decentralized Exchanges (DEX):")
    dex_list = [
        "uniswap_v3 - Uniswap V3 (Ethereum)",
        "pancakeswap - PancakeSwap (BSC)",
        "sushiswap - SushiSwap (Multi-chain)",
        "quickswap - QuickSwap (Polygon)"
    ]
    for exchange in dex_list:
        click.echo(f"  🔄 {exchange}")
    
    click.echo("\n💡 ใช้คำสั่ง 'setup' เพื่อตั้งค่า exchanges")

@cli.command()
@click.option('--config', '-c', default='config.json', help='ไฟล์ config')
def status(config):
    """📊 แสดงสถานะการเชื่อมต่อ exchanges"""
    try:
        exchange_manager = ExchangeManager(config)
        
        if exchange_manager.initialize_exchanges():
            click.echo("✅ สถานะการเชื่อมต่อ:")
            click.echo("=" * 40)
            
            enabled_exchanges = exchange_manager.get_enabled_exchanges()
            for exchange_name in enabled_exchanges:
                trading_pairs = exchange_manager.get_trading_pairs(exchange_name)
                click.echo(f"🏢 {exchange_name.upper()}: ✅ เชื่อมต่อแล้ว ({len(trading_pairs)} คู่เทรด)")
                
                # แสดงยอดเงิน
                try:
                    balance = exchange_manager.get_balance(exchange_name)
                    if balance and 'total' in balance:
                        for currency, amount in balance['total'].items():
                            if amount > 0:
                                click.echo(f"  💰 {currency}: {amount:.4f}")
                except:
                    click.echo("  💰 ไม่สามารถดึงยอดเงินได้ (อาจเป็นโหมดอ่านอย่างเดียว)")
        else:
            click.echo("❌ ไม่สามารถเชื่อมต่อกับ exchange ใดๆ ได้")
            
    except Exception as e:
        click.echo(f"❌ เกิดข้อผิดพลาด: {e}")

@cli.command()
@click.option('--symbol', '-s', default='BTC/USDT', help='Trading pair')
@click.option('--config', '-c', default='config.json', help='ไฟล์ config')
def analyze(symbol, config):
    """🔍 วิเคราะห์ตลาดจากทุก exchanges"""
    click.echo(f"🔍 กำลังวิเคราะห์ {symbol} จากทุก exchanges...")
    
    try:
        results = asyncio.run(run_market_analysis())
        if results:
            click.echo("✅ การวิเคราะห์เสร็จสิ้น")
        else:
            click.echo("❌ ไม่สามารถวิเคราะห์ได้")
    except Exception as e:
        click.echo(f"❌ เกิดข้อผิดพลาด: {e}")

@cli.command()
@click.option('--symbol', '-s', default='BTC/USDT', help='Trading pair')
@click.option('--interval', '-i', default=300, help='ช่วงเวลาการวิเคราะห์ (วินาที)')
@click.option('--config', '-c', default='config.json', help='ไฟล์ config')
def monitor(symbol, interval, config):
    """📊 ติดตามตลาดแบบต่อเนื่อง"""
    click.echo(f"📊 เริ่มติดตาม {symbol} ทุก {interval} วินาที")
    click.echo("กด Ctrl+C เพื่อหยุด")
    
    try:
        analyzer = MultiExchangeMarketAnalyzer(config)
        asyncio.run(analyzer.run_continuous_analysis(symbol, interval))
    except KeyboardInterrupt:
        click.echo("\n⏹️ หยุดการติดตาม")
    except Exception as e:
        click.echo(f"❌ เกิดข้อผิดพลาด: {e}")

@cli.command()
@click.option('--config', '-c', default='config.json', help='ไฟล์ config')
@click.option('--dry-run', is_flag=True, help='ทดสอบโดยไม่เทรดจริง')
def trade(config, dry_run):
    """🚀 เริ่มการเทรดอัตโนมัติ"""
    if dry_run:
        click.echo("🧪 โหมดทดสอบ (ไม่เทรดจริง)")
    else:
        click.echo("🚀 เริ่มการเทรดจริง")
        
    click.echo("กด Ctrl+C เพื่อหยุด")
    
    try:
        asyncio.run(run_multi_exchange_bot())
    except KeyboardInterrupt:
        click.echo("\n⏹️ หยุดการเทรด")
    except Exception as e:
        click.echo(f"❌ เกิดข้อผิดพลาด: {e}")

@cli.command()
@click.option('--force', is_flag=True, help='บังคับเขียนทับไฟล์ config ที่มีอยู่')
def setup(force):
    """⚙️ ตั้งค่าเริ่มต้น"""
    click.echo("⚙️ ตั้งค่า Multi-Exchange Trading Bot")
    click.echo("=" * 50)
    
    # ใช้ ConfigManager
    config_manager = ConfigManager()
    
    # ตรวจสอบไฟล์ config
    if config_manager.config_exists() and not force:
        if not click.confirm('พบไฟล์ config.json อยู่แล้ว ต้องการเขียนทับหรือไม่?'):
            click.echo("ยกเลิกการตั้งค่า")
            click.echo("💡 ใช้ --force เพื่อบังคับเขียนทับ")
            return
        force = True
    
    # สร้าง config พื้นฐาน
    config = {
        "exchanges": {},
        "trading_strategy": {
            "strategy_type": "market_making",
            "timeframe": "1m",
            "indicators": ["sma", "ema", "rsi", "macd"],
            "risk_management": {
                "max_position_size": 0.1,
                "stop_loss": 0.02,
                "take_profit": 0.03,
                "max_daily_loss": 0.05
            }
        },
        "bot_settings": {
            "check_interval": 30,
            "log_level": "INFO",
            "log_file": "temp/trading_bot.log",
            "telegram_notifications": {
                "enabled": False,
                "bot_token": "",
                "chat_id": ""
            },
            "database": {
                "enabled": True,
                "type": "sqlite",
                "path": "temp/trading_data.db"
            }
        }
    }
    
    # ตั้งค่า exchanges
    click.echo("\n🏢 ตั้งค่า Exchanges:")
    
    # Binance
    if click.confirm('ต้องการเปิดใช้ Binance?'):
        config["exchanges"]["binance"] = {
            "enabled": True,
            "type": "cex",
            "api_key": "",
            "secret": "",
            "sandbox": True,
            "trading_pairs": ["BTC/USDT", "ETH/USDT"],
            "min_order_amount": 10.0,
            "max_order_amount": 1000.0,
            "fee_rate": 0.001
        }
    
    # Gate.io
    if click.confirm('ต้องการเปิดใช้ Gate.io?'):
        config["exchanges"]["gateio"] = {
            "enabled": True,
            "type": "cex",
            "api_key": "",
            "secret": "",
            "sandbox": True,
            "trading_pairs": ["BTC/USDT", "ETH/USDT"],
            "min_order_amount": 10.0,
            "max_order_amount": 1000.0,
            "fee_rate": 0.002
        }
    
    # DEX
    if click.confirm('ต้องการเปิดใช้ DEX (Uniswap V3)?'):
        config["exchanges"]["uniswap_v3"] = {
            "enabled": True,
            "type": "dex",
            "network": "ethereum",
            "rpc_url": "https://mainnet.infura.io/v3/YOUR_PROJECT_ID",
            "private_key": "",
            "wallet_address": "",
            "trading_pairs": ["WETH/USDC"],
            "slippage": 0.005,
            "gas_limit": 300000,
            "max_gas_price": 50
        }
    
    # ลองสร้างจาก template ก่อน
    if config_manager.template_exists():
        click.echo("\n🔧 พบไฟล์ template กำลังสร้าง config จาก template...")
        if config_manager.create_config_from_template(force=force):
            click.echo("✅ สร้างไฟล์ config.json จาก template เรียบร้อย")
        else:
            click.echo("⚠️ ไม่สามารถสร้างจาก template ได้ กำลังสร้างแบบ interactive...")
            # บันทึก config แบบเดิม
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            click.echo("✅ สร้างไฟล์ config.json เรียบร้อย")
    else:
        # บันทึก config แบบเดิม
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        click.echo("\n✅ สร้างไฟล์ config.json เรียบร้อย")
    
    # สร้างไฟล์ .env ตัวอย่าง
    if not os.path.exists('.env'):
        env_content = """# CEX API Keys
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET=your_binance_secret_here
BINANCE_SANDBOX=true

GATEIO_API_KEY=your_gateio_api_key_here
GATEIO_SECRET=your_gateio_secret_here
GATEIO_SANDBOX=true

# DEX Settings
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
ETHEREUM_PRIVATE_KEY=your_ethereum_private_key_here

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
"""
        with open('.env', 'w') as f:
            f.write(env_content)
        
        click.echo("✅ สร้างไฟล์ .env ตัวอย่างเรียบร้อย")
    
    click.echo("\n📝 ขั้นตอนถัดไป:")
    click.echo("1. แก้ไขไฟล์ .env ใส่ API keys ของคุณ")
    click.echo("2. ใช้คำสั่ง 'status' เพื่อตรวจสอบการเชื่อมต่อ")
    click.echo("3. ใช้คำสั่ง 'analyze' เพื่อวิเคราะห์ตลาด")
    click.echo("4. ใช้คำสั่ง 'trade' เพื่อเริ่มเทรด")

@cli.command()
@click.option('--exchange', '-e', help='ชื่อ exchange')
@click.option('--symbol', '-s', help='Trading pair')
@click.option('--config', '-c', default='config.json', help='ไฟล์ config')
def balance(exchange, symbol, config):
    """💰 แสดงยอดเงินคงเหลือ"""
    try:
        exchange_manager = ExchangeManager(config)
        
        if not exchange_manager.initialize_exchanges():
            click.echo("❌ ไม่สามารถเชื่อมต่อกับ exchange ได้")
            return
        
        enabled_exchanges = exchange_manager.get_enabled_exchanges()
        
        if exchange and exchange not in enabled_exchanges:
            click.echo(f"❌ ไม่พบ exchange: {exchange}")
            return
        
        exchanges_to_check = [exchange] if exchange else enabled_exchanges
        
        click.echo("💰 ยอดเงินคงเหลือ:")
        click.echo("=" * 40)
        
        for exchange_name in exchanges_to_check:
            click.echo(f"\n🏢 {exchange_name.upper()}:")
            
            balance_data = exchange_manager.get_balance(exchange_name)
            if balance_data and 'total' in balance_data:
                for currency, amount in balance_data['total'].items():
                    if amount > 0:
                        free_amount = balance_data.get('free', {}).get(currency, 0)
                        used_amount = balance_data.get('used', {}).get(currency, 0)
                        click.echo(f"  {currency}: {amount:.6f} (ว่าง: {free_amount:.6f}, ใช้งาน: {used_amount:.6f})")
            else:
                click.echo("  ไม่สามารถดึงข้อมูลยอดเงินได้")
                
    except Exception as e:
        click.echo(f"❌ เกิดข้อผิดพลาด: {e}")

@cli.command()
@click.option('--config', '-c', default='config.json', help='ไฟล์ config')
def test_connection(config):
    """🔧 ทดสอบการเชื่อมต่อ exchanges"""
    click.echo("🔧 ทดสอบการเชื่อมต่อ...")
    
    try:
        exchange_manager = ExchangeManager(config)
        
        # โหลด config
        with open(config, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        exchanges_config = config_data.get('exchanges', {})
        
        for exchange_name, exchange_config in exchanges_config.items():
            if not exchange_config.get('enabled', False):
                click.echo(f"⏭️ {exchange_name}: ปิดใช้งาน")
                continue
            
            click.echo(f"🔍 ทดสอบ {exchange_name}...")
            
            if exchange_config.get('type') == 'cex':
                # ทดสอบ CEX
                try:
                    if exchange_manager._initialize_cex(exchange_name, exchange_config):
                        click.echo(f"✅ {exchange_name}: เชื่อมต่อสำเร็จ")
                    else:
                        click.echo(f"❌ {exchange_name}: เชื่อมต่อไม่สำเร็จ")
                except Exception as e:
                    click.echo(f"❌ {exchange_name}: {e}")
            
            elif exchange_config.get('type') == 'dex':
                # ทดสอบ DEX
                try:
                    if exchange_manager._initialize_dex(exchange_name, exchange_config):
                        click.echo(f"✅ {exchange_name}: เชื่อมต่อสำเร็จ")
                    else:
                        click.echo(f"❌ {exchange_name}: เชื่อมต่อไม่สำเร็จ")
                except Exception as e:
                    click.echo(f"❌ {exchange_name}: {e}")
        
    except Exception as e:
        click.echo(f"❌ เกิดข้อผิดพลาด: {e}")

@cli.command()
@click.option('--timeframes', '-t', multiple=True, help='Timeframes ที่ต้องการสแกน (เช่น 1h,4h,1d)')
@click.option('--exchanges', '-e', multiple=True, help='Exchanges ที่ต้องการสแกน')
@click.option('--pairs', '-p', multiple=True, help='Trading pairs ที่ต้องการสแกน')
@click.option('--min-strength', '-s', default=60, help='ความแรงสัญญาณขั้นต่ำ (0-100)')
@click.option('--min-volume', '-v', default=100000, help='ปริมาณการเทรดขั้นต่ำ 24h')
@click.option('--config', '-c', default='config.json', help='ไฟล์ config')
def scan(timeframes, exchanges, pairs, min_strength, min_volume, config):
    """🔍 สแกนคู่เทรด crypto ด้วยสัญญาณ MACD"""
    click.echo("🔍 เริ่มสแกนคู่เทรด crypto ด้วยสัญญาณ MACD")
    click.echo("=" * 60)
    
    try:
        # แปลง timeframes
        tf_list = list(timeframes) if timeframes else ['1h', '4h', '1d']
        ex_list = list(exchanges) if exchanges else None
        
        click.echo(f"📊 Timeframes: {', '.join(tf_list)}")
        click.echo(f"🏢 Exchanges: {', '.join(ex_list) if ex_list else 'ทั้งหมด'}")
        click.echo(f"📈 ความแรงสัญญาณขั้นต่ำ: {min_strength}%")
        click.echo(f"📊 ปริมาณการเทรดขั้นต่ำ: {min_volume:,}")
        click.echo()
        
        # รันการสแกน
        results = asyncio.run(run_single_scan(tf_list, ex_list))
        
        if results:
            total_signals = sum(len(signals) for signals in results.values())
            click.echo(f"✅ สแกนเสร็จสิ้น พบสัญญาณทั้งหมด: {total_signals}")
        else:
            click.echo("❌ ไม่พบสัญญาณ")
            
    except Exception as e:
        click.echo(f"❌ เกิดข้อผิดพลาด: {e}")

@cli.command()
@click.option('--interval', '-i', default=15, help='ช่วงเวลาการสแกน (นาที)')
@click.option('--timeframes', '-t', multiple=True, help='Timeframes ที่ต้องการสแกน')
@click.option('--config', '-c', default='config.json', help='ไฟล์ config')
def scan_continuous(interval, timeframes, config):
    """🔄 สแกนคู่เทรด crypto อย่างต่อเนื่อง"""
    click.echo(f"🔄 เริ่มสแกนคู่เทรด crypto อย่างต่อเนื่องทุก {interval} นาที")
    click.echo("กด Ctrl+C เพื่อหยุด")
    
    try:
        asyncio.run(run_continuous_scan(interval))
    except KeyboardInterrupt:
        click.echo("\n⏹️ หยุดการสแกน")
    except Exception as e:
        click.echo(f"❌ เกิดข้อผิดพลาด: {e}")

@cli.command()
@click.option('--symbol', '-s', required=True, help='Trading pair (เช่น BTC/USDT)')
@click.option('--timeframe', '-t', default='1h', help='Timeframe (เช่น 1h, 4h, 1d)')
@click.option('--exchange', '-e', default='binance', help='Exchange name')
@click.option('--config', '-c', default='config.json', help='ไฟล์ config')
def macd_check(symbol, timeframe, exchange, config):
    """📊 ตรวจสอบสัญญาณ MACD ของคู่เทรดเฉพาะ"""
    click.echo(f"📊 ตรวจสอบสัญญาณ MACD: {symbol} ({exchange.upper()}) - {timeframe}")
    click.echo("=" * 60)
    
    try:
        async def check_single():
            scanner = CryptoPairsScanner(config)
            if not await scanner.initialize():
                click.echo("❌ ไม่สามารถเชื่อมต่อกับ exchange ได้")
                return
            
            # สแกนคู่เทรดเดียว
            signals = await scanner.scan_single_pair(exchange, symbol, timeframe)
            
            if signals:
                for signal in signals:
                    signal_emoji = "🟢" if signal.signal_type == "long" else "🔴"
                    click.echo(f"{signal_emoji} สัญญาณ {signal.signal_type.upper()} พบ!")
                    click.echo(f"   💰 ราคา: ${signal.price:,.4f}")
                    click.echo(f"   📊 ความแรง: {signal.strength:.1f}%")
                    click.echo(f"   📈 MACD: {signal.macd_value:.6f}")
                    click.echo(f"   📉 Signal: {signal.macd_signal:.6f}")
                    click.echo(f"   📊 Histogram: {signal.macd_histogram:.6f}")
                    click.echo(f"   📅 เวลา: {signal.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                click.echo("❌ ไม่พบสัญญาณ MACD")
                
                # แสดงข้อมูล MACD ปัจจุบัน
                df = await scanner.fetch_ohlcv_data(exchange, symbol, timeframe, 50)
                if df is not None and not df.empty:
                    df = scanner.calculate_macd(df)
                    latest = df.iloc[-1]
                    
                    click.echo("\n📊 ข้อมูล MACD ปัจจุบัน:")
                    click.echo(f"   💰 ราคา: ${latest['close']:,.4f}")
                    click.echo(f"   📈 MACD: {latest['macd']:.6f}")
                    click.echo(f"   📉 Signal: {latest['macd_signal']:.6f}")
                    click.echo(f"   📊 Histogram: {latest['macd_histogram']:.6f}")
                    
                    if latest['macd'] > 0:
                        click.echo("   🟢 MACD อยู่เหนือ 0 (แนวโน้มบวก)")
                    else:
                        click.echo("   🔴 MACD อยู่ใต้ 0 (แนวโน้มลบ)")
        
        asyncio.run(check_single())
        
    except Exception as e:
        click.echo(f"❌ เกิดข้อผิดพลาด: {e}")

@cli.command()
@click.option('--action', type=click.Choice(['create', 'validate', 'backup', 'show', 'export', 'summary']), 
              default='show', help='การดำเนินการกับ config')
@click.option('--config', '-c', default='config.json', help='ไฟล์ config')
@click.option('--template', default='config.template.json', help='ไฟล์ template')
@click.option('--force', is_flag=True, help='บังคับเขียนทับ')
@click.option('--output', '-o', help='ไฟล์ output สำหรับ export')
@click.option('--verbose', '-v', is_flag=True, help='แสดงข้อมูลละเอียด')
def config(action, config, template, force, output, verbose):
    """⚙️ จัดการไฟล์ config"""
    config_manager = ConfigManager(config, template)
    
    if action == 'create':
        click.echo("🔧 สร้างไฟล์ config จาก template...")
        if config_manager.create_config_from_template(force=force):
            click.echo("✅ สร้างเรียบร้อย")
            # แสดงสรุปหลังสร้าง
            summary = config_manager.get_config_summary()
            if summary.get('enabled_exchanges'):
                click.echo(f"🏢 เปิดใช้งาน: {', '.join(summary['enabled_exchanges'])}")
        else:
            click.echo("❌ ไม่สามารถสร้างได้")
            
    elif action == 'validate':
        click.echo("🔍 ตรวจสอบไฟล์ config...")
        if config_manager.validate_config():
            click.echo("✅ Config ถูกต้อง")
        else:
            click.echo("❌ Config มีปัญหา")
            
    elif action == 'backup':
        click.echo("💾 สำรองไฟล์ config...")
        if config_manager.backup_config():
            click.echo("✅ สำรองเรียบร้อย")
        else:
            click.echo("❌ ไม่สามารถสำรองได้")
    
    elif action == 'export':
        click.echo("📤 ส่งออก config template...")
        if config_manager.export_config_template(output):
            click.echo("✅ ส่งออกเรียบร้อย")
        else:
            click.echo("❌ ไม่สามารถส่งออกได้")
    
    elif action == 'summary':
        click.echo("📊 สรุปข้อมูล Config:")
        click.echo("=" * 50)
        
        summary = config_manager.get_config_summary()
        if summary:
            click.echo(f"📁 Config file: {'✅ มี' if summary['config_exists'] else '❌ ไม่มี'}")
            click.echo(f"📄 Template file: {'✅ มี' if summary['template_exists'] else '❌ ไม่มี'}")
            click.echo(f"🏢 Exchanges: {summary['total_exchanges']} ทั้งหมด, {len(summary['enabled_exchanges'])} เปิดใช้งาน")
            if summary['enabled_exchanges']:
                click.echo(f"   ├─ เปิดใช้งาน: {', '.join(summary['enabled_exchanges'])}")
            click.echo(f"📈 Strategy: {summary['trading_strategy']} ({summary['timeframe']})")
            click.echo(f"📝 Log file: {summary['log_file']}")
            click.echo(f"📱 Telegram: {'✅ เปิด' if summary['telegram_enabled'] else '❌ ปิด'}")
            click.echo(f"🗄️ Database: {'✅ เปิด' if summary['database_enabled'] else '❌ ปิด'}")
        else:
            click.echo("❌ ไม่สามารถโหลด config ได้")
            
    elif action == 'show':
        click.echo("📋 ข้อมูล Config:")
        click.echo("=" * 40)
        
        if config_manager.config_exists():
            click.echo(f"✅ Config file: {config}")
            enabled_exchanges = config_manager.get_enabled_exchanges()
            if enabled_exchanges:
                click.echo(f"🏢 Exchanges ที่เปิดใช้งาน: {', '.join(enabled_exchanges)}")
            else:
                click.echo("⚠️ ไม่มี exchange ที่เปิดใช้งาน")
                
            if verbose:
                # แสดงข้อมูลละเอียดโดยซ่อน sensitive data
                config_data = config_manager.load_config()
                if config_data:
                    sanitized = config_manager.sanitize_config_for_display(config_data)
                    click.echo("\n📄 Config content (sensitive data masked):")
                    click.echo(json.dumps(sanitized, indent=2, ensure_ascii=False))
        else:
            click.echo(f"❌ ไม่พบไฟล์: {config}")
            
        if config_manager.template_exists():
            click.echo(f"📄 Template file: {template}")
        else:
            click.echo(f"❌ ไม่พบ template: {template}")
            click.echo("💡 ใช้คำสั่ง 'setup' เพื่อสร้าง template")

@cli.command()
def version():
    """📋 แสดงเวอร์ชัน"""
    click.echo("🤖 Multi-Exchange Trading Bot v2.0.0")
    click.echo("รองรับ CEX และ DEX หลายแห่ง")
    click.echo("พัฒนาด้วย Python + CCXT + Web3")
    click.echo("🔍 รองรับ Crypto Scanner ด้วยสัญญาณ MACD")

if __name__ == '__main__':
    cli() 