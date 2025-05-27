#!/usr/bin/env python3
"""
Config Manager สำหรับจัดการการสร้างและโหลด config จาก template
"""

import os
import json
import shutil
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import re
from pathlib import Path

class ConfigManager:
    """จัดการการสร้างและโหลด configuration"""
    
    def __init__(self, config_path: str = "config.json", template_path: str = "config.template.json"):
        self.config_path = Path(config_path)
        self.template_path = Path(template_path)
        self.env_loaded = False
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """ตั้งค่า logger สำหรับ ConfigManager"""
        logger = logging.getLogger('ConfigManager')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
        
    def load_env(self) -> bool:
        """โหลด environment variables"""
        if not self.env_loaded:
            load_dotenv()
            self.env_loaded = True
        return True
    
    def template_exists(self) -> bool:
        """ตรวจสอบว่ามี template file หรือไม่"""
        return self.template_path.exists()
    
    def config_exists(self) -> bool:
        """ตรวจสอบว่ามี config file หรือไม่"""
        return self.config_path.exists()
    
    def substitute_env_vars(self, text: str) -> str:
        """แทนที่ environment variables ใน text"""
        def replace_var(match):
            var_name = match.group(1)
            # ตรวจสอบชื่อ variable ที่ปลอดภัย
            if not re.match(r'^[A-Z_][A-Z0-9_]*$', var_name):
                self.logger.warning(f"Potentially unsafe environment variable name: {var_name}")
                return f"${{{var_name}}}"
            
            env_value = os.getenv(var_name)
            if env_value is None:
                self.logger.debug(f"Environment variable not found: {var_name}")
                return f"${{{var_name}}}"  # คืนค่าเดิมถ้าไม่พบ env var
            
            return env_value
        
        return re.sub(r'\$\{([^}]+)\}', replace_var, text)
    
    def create_config_from_template(self, force: bool = False) -> bool:
        """สร้าง config.json จาก template"""
        if not self.template_exists():
            self.logger.error(f"Template file not found: {self.template_path}")
            print(f"❌ ไม่พบไฟล์ template: {self.template_path}")
            print("💡 กรุณาตรวจสอบว่าไฟล์ config.template.json อยู่ในโฟลเดอร์เดียวกัน")
            return False
        
        if self.config_exists() and not force:
            self.logger.warning(f"Config file already exists: {self.config_path}")
            print(f"⚠️ ไฟล์ {self.config_path} มีอยู่แล้ว ใช้ --force เพื่อเขียนทับ")
            return False
        
        try:
            # โหลด environment variables
            self.load_env()
            
            # อ่าน template
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # แทนที่ environment variables
            config_content = self.substitute_env_vars(template_content)
            
            # แปลงเป็น JSON เพื่อตรวจสอบ syntax
            config_data = json.loads(config_content)
            
            # เปิดใช้งาน exchanges ที่มี API keys
            self.auto_enable_exchanges(config_data)
            
            # บันทึกไฟล์ config
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Successfully created config file: {self.config_path}")
            print(f"✅ สร้างไฟล์ {self.config_path} จาก template เรียบร้อย")
            return True
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON syntax error: {e}")
            print(f"❌ ข้อผิดพลาดใน JSON syntax: {e}")
            print("💡 กรุณาตรวจสอบ template file หรือ environment variables")
            return False
        except Exception as e:
            self.logger.error(f"Error creating config: {e}")
            print(f"❌ เกิดข้อผิดพลาดในการสร้าง config: {e}")
            return False
    
    def sanitize_config_for_display(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """ซ่อนข้อมูล sensitive สำหรับการแสดงผล"""
        import copy
        sanitized = copy.deepcopy(config_data)
        
        sensitive_keys = ['api_key', 'secret', 'private_key', 'passphrase', 'bot_token']
        
        def sanitize_recursive(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key.lower() in sensitive_keys and isinstance(value, str) and value:
                        if value.startswith('${') and value.endswith('}'):
                            # Keep placeholder as is
                            continue
                        else:
                            # Mask actual values
                            obj[key] = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
                    else:
                        sanitize_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    sanitize_recursive(item)
        
        sanitize_recursive(sanitized)
        return sanitized
    
    def auto_enable_exchanges(self, config_data: Dict[str, Any]) -> None:
        """เปิดใช้งาน exchanges อัตโนมัติถ้ามี API keys"""
        exchanges = config_data.get('exchanges', {})
        
        for exchange_name, exchange_config in exchanges.items():
            if exchange_config.get('type') == 'cex':
                # ตรวจสอบ CEX
                api_key = exchange_config.get('api_key', '')
                secret = exchange_config.get('secret', '')
                
                # ถ้าไม่ใช่ placeholder และมีค่า
                if (api_key and not api_key.startswith('${') and 
                    secret and not secret.startswith('${')):
                    exchange_config['enabled'] = True
                    print(f"🔑 เปิดใช้งาน {exchange_name.upper()} (พบ API keys)")
                    
            elif exchange_config.get('type') == 'dex':
                # ตรวจสอบ DEX
                rpc_url = exchange_config.get('rpc_url', '')
                private_key = exchange_config.get('private_key', '')
                
                # ถ้าไม่ใช่ placeholder และมีค่า
                if (rpc_url and not rpc_url.startswith('${') and 
                    private_key and not private_key.startswith('${')):
                    exchange_config['enabled'] = True
                    print(f"🔗 เปิดใช้งาน {exchange_name.upper()} (พบ RPC และ Private Key)")
    
    def load_config(self) -> Optional[Dict[str, Any]]:
        """โหลด config file"""
        if not self.config_exists():
            print(f"❌ ไม่พบไฟล์ {self.config_path}")
            return None
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ ข้อผิดพลาดใน JSON syntax: {e}")
            return None
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการโหลด config: {e}")
            return None
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """อัปเดต config file"""
        config_data = self.load_config()
        if config_data is None:
            return False
        
        try:
            # อัปเดตข้อมูล
            self._deep_update(config_data, updates)
            
            # บันทึกไฟล์
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ อัปเดต {self.config_path} เรียบร้อย")
            return True
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการอัปเดต config: {e}")
            return False
    
    def _deep_update(self, base_dict: Dict, update_dict: Dict) -> None:
        """อัปเดต dictionary แบบ deep merge"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def backup_config(self, backup_suffix: str = None) -> bool:
        """สำรองไฟล์ config"""
        if not self.config_exists():
            print(f"❌ ไม่พบไฟล์ {self.config_path} ที่จะสำรอง")
            return False
        
        try:
            if backup_suffix is None:
                from datetime import datetime
                backup_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            backup_path = f"{self.config_path}.backup.{backup_suffix}"
            shutil.copy2(self.config_path, backup_path)
            
            print(f"✅ สำรองไฟล์ config ไปยัง: {backup_path}")
            return True
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการสำรอง config: {e}")
            return False
    
    def validate_config(self) -> bool:
        """ตรวจสอบความถูกต้องของ config"""
        config_data = self.load_config()
        if config_data is None:
            return False
        
        validation_errors = []
        
        # ตรวจสอบ required sections
        required_sections = ['exchanges', 'trading_strategy', 'bot_settings']
        for section in required_sections:
            if section not in config_data:
                validation_errors.append(f"Missing required section: '{section}'")
        
        # ตรวจสอบ exchanges configuration
        exchanges = config_data.get('exchanges', {})
        enabled_exchanges = []
        
        for exchange_name, exchange_config in exchanges.items():
            if not isinstance(exchange_config, dict):
                validation_errors.append(f"Invalid exchange config for '{exchange_name}': must be object")
                continue
                
            if exchange_config.get('enabled', False):
                enabled_exchanges.append(exchange_name)
                
                # ตรวจสอบ required fields สำหรับ enabled exchanges
                exchange_type = exchange_config.get('type')
                if exchange_type == 'cex':
                    required_fields = ['api_key', 'secret']
                    for field in required_fields:
                        if not exchange_config.get(field):
                            validation_errors.append(f"Missing {field} for enabled exchange '{exchange_name}'")
                elif exchange_type == 'dex':
                    required_fields = ['rpc_url', 'private_key']
                    for field in required_fields:
                        if not exchange_config.get(field):
                            validation_errors.append(f"Missing {field} for enabled DEX '{exchange_name}'")
        
        # ตรวจสอบ trading strategy
        strategy = config_data.get('trading_strategy', {})
        if 'timeframe' not in strategy:
            validation_errors.append("Missing 'timeframe' in trading_strategy")
        
        # ตรวจสอบ bot settings
        bot_settings = config_data.get('bot_settings', {})
        if 'log_file' not in bot_settings:
            validation_errors.append("Missing 'log_file' in bot_settings")
        
        # แสดงผลลัพธ์
        if validation_errors:
            self.logger.error(f"Config validation failed with {len(validation_errors)} errors")
            print("❌ Config validation failed:")
            for error in validation_errors:
                print(f"  • {error}")
            return False
        
        if not enabled_exchanges:
            self.logger.warning("No exchanges enabled")
            print("⚠️ ไม่มี exchange ที่เปิดใช้งาน")
            print("💡 กรุณาตั้งค่า API keys ใน .env file และรัน config create ใหม่")
            return False
        
        self.logger.info(f"Config validation passed. Enabled exchanges: {enabled_exchanges}")
        print(f"✅ Config ถูกต้อง (exchanges ที่เปิดใช้งาน: {', '.join(enabled_exchanges)})")
        return True
    
    def get_enabled_exchanges(self) -> list:
        """ดึงรายการ exchanges ที่เปิดใช้งาน"""
        config_data = self.load_config()
        if config_data is None:
            return []
        
        return [
            name for name, config in config_data.get('exchanges', {}).items() 
            if config.get('enabled', False)
        ]
    
    def export_config_template(self, output_path: str = None) -> bool:
        """ส่งออก config เป็น template (ซ่อนข้อมูล sensitive)"""
        config_data = self.load_config()
        if config_data is None:
            return False
        
        if output_path is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"config.template.{timestamp}.json"
        
        try:
            # สร้าง template โดยแทนที่ค่าจริงด้วย placeholders
            template_data = self._convert_to_template(config_data)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Config template exported to: {output_path}")
            print(f"✅ ส่งออก template ไปยัง: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting template: {e}")
            print(f"❌ เกิดข้อผิดพลาดในการส่งออก template: {e}")
            return False
    
    def _convert_to_template(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """แปลง config เป็น template format"""
        import copy
        template_data = copy.deepcopy(config_data)
        
        # Mapping ของ sensitive fields กับ env variable names
        env_mappings = {
            'api_key': {
                'binance': 'BINANCE_API_KEY',
                'gateio': 'GATEIO_API_KEY',
                'okx': 'OKX_API_KEY',
                'kucoin': 'KUCOIN_API_KEY'
            },
            'secret': {
                'binance': 'BINANCE_SECRET',
                'gateio': 'GATEIO_SECRET',
                'okx': 'OKX_SECRET',
                'kucoin': 'KUCOIN_SECRET'
            },
            'passphrase': {
                'okx': 'OKX_PASSPHRASE',
                'kucoin': 'KUCOIN_PASSPHRASE'
            },
            'private_key': {
                'uniswap_v3': 'ETHEREUM_PRIVATE_KEY',
                'pancakeswap': 'BSC_PRIVATE_KEY'
            },
            'rpc_url': {
                'uniswap_v3': 'ETHEREUM_RPC_URL',
                'pancakeswap': 'BSC_RPC_URL'
            },
            'wallet_address': {
                'uniswap_v3': 'ETHEREUM_WALLET_ADDRESS',
                'pancakeswap': 'BSC_WALLET_ADDRESS'
            }
        }
        
        # แปลง exchanges
        for exchange_name, exchange_config in template_data.get('exchanges', {}).items():
            exchange_config['enabled'] = False  # ปิดใช้งานใน template
            
            for field, mapping in env_mappings.items():
                if field in exchange_config and exchange_name in mapping:
                    exchange_config[field] = f"${{{mapping[exchange_name]}}}"
        
        # แปลง telegram settings
        bot_settings = template_data.get('bot_settings', {})
        telegram = bot_settings.get('telegram_notifications', {})
        if 'bot_token' in telegram:
            telegram['bot_token'] = "${TELEGRAM_BOT_TOKEN}"
        if 'chat_id' in telegram:
            telegram['chat_id'] = "${TELEGRAM_CHAT_ID}"
        
        return template_data
    
    def get_config_summary(self) -> Dict[str, Any]:
        """ดึงสรุปข้อมูล config"""
        config_data = self.load_config()
        if config_data is None:
            return {}
        
        enabled_exchanges = self.get_enabled_exchanges()
        
        summary = {
            'config_exists': True,
            'template_exists': self.template_exists(),
            'enabled_exchanges': enabled_exchanges,
            'total_exchanges': len(config_data.get('exchanges', {})),
            'trading_strategy': config_data.get('trading_strategy', {}).get('strategy_type', 'unknown'),
            'timeframe': config_data.get('trading_strategy', {}).get('timeframe', 'unknown'),
            'log_file': config_data.get('bot_settings', {}).get('log_file', 'unknown'),
            'telegram_enabled': config_data.get('bot_settings', {}).get('telegram_notifications', {}).get('enabled', False),
            'database_enabled': config_data.get('bot_settings', {}).get('database', {}).get('enabled', False)
        }
        
        return summary

def ensure_config_exists(config_path: str = "config.json", template_path: str = "config.template.json") -> bool:
    """ตรวจสอบและสร้าง config ถ้าจำเป็น"""
    manager = ConfigManager(config_path, template_path)
    
    if not manager.config_exists():
        print("🔧 ไม่พบไฟล์ config กำลังสร้างจาก template...")
        return manager.create_config_from_template()
    
    return True

# CLI Commands
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Config Manager - จัดการการตั้งค่า Multi-Exchange Trading Bot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python config_manager.py create --force
  python config_manager.py validate
  python config_manager.py backup
  python config_manager.py export --output my_template.json
        """
    )
    
    parser.add_argument('action', 
                       choices=['create', 'validate', 'backup', 'export', 'summary'], 
                       help='การดำเนินการ')
    parser.add_argument('--config', default='config.json', 
                       help='ไฟล์ config (default: config.json)')
    parser.add_argument('--template', default='config.template.json', 
                       help='ไฟล์ template (default: config.template.json)')
    parser.add_argument('--force', action='store_true', 
                       help='บังคับเขียนทับไฟล์ที่มีอยู่')
    parser.add_argument('--output', '-o', 
                       help='ไฟล์ output สำหรับ export')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='แสดงข้อมูลละเอียด')
    
    args = parser.parse_args()
    
    manager = ConfigManager(args.config, args.template)
    
    if args.action == 'create':
        print("🔧 สร้างไฟล์ config จาก template...")
        if manager.create_config_from_template(force=args.force):
            print("✅ สร้างเรียบร้อย")
        else:
            print("❌ ไม่สามารถสร้างได้")
            
    elif args.action == 'validate':
        print("🔍 ตรวจสอบไฟล์ config...")
        if manager.validate_config():
            print("✅ Config ถูกต้อง")
        else:
            print("❌ Config มีปัญหา")
            
    elif args.action == 'backup':
        print("💾 สำรองไฟล์ config...")
        if manager.backup_config():
            print("✅ สำรองเรียบร้อย")
        else:
            print("❌ ไม่สามารถสำรองได้")
            
    elif args.action == 'export':
        print("📤 ส่งออก config template...")
        if manager.export_config_template(args.output):
            print("✅ ส่งออกเรียบร้อย")
        else:
            print("❌ ไม่สามารถส่งออกได้")
            
    elif args.action == 'summary':
        print("📊 สรุปข้อมูล Config:")
        print("=" * 50)
        
        summary = manager.get_config_summary()
        if summary:
            print(f"📁 Config file: {'✅ มี' if summary['config_exists'] else '❌ ไม่มี'}")
            print(f"📄 Template file: {'✅ มี' if summary['template_exists'] else '❌ ไม่มี'}")
            print(f"🏢 Exchanges: {summary['total_exchanges']} ทั้งหมด, {len(summary['enabled_exchanges'])} เปิดใช้งาน")
            if summary['enabled_exchanges']:
                print(f"   ├─ เปิดใช้งาน: {', '.join(summary['enabled_exchanges'])}")
            print(f"📈 Strategy: {summary['trading_strategy']} ({summary['timeframe']})")
            print(f"📝 Log file: {summary['log_file']}")
            print(f"📱 Telegram: {'✅ เปิด' if summary['telegram_enabled'] else '❌ ปิด'}")
            print(f"🗄️ Database: {'✅ เปิด' if summary['database_enabled'] else '❌ ปิด'}")
        else:
            print("❌ ไม่สามารถโหลด config ได้") 