import ccxt
import asyncio
import logging
from typing import Dict, List, Optional, Any
from web3 import Web3
import json
import os
from dotenv import load_dotenv

load_dotenv()

class ExchangeManager:
    """จัดการการเชื่อมต่อกับหลาย Exchange ทั้ง CEX และ DEX"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.exchanges = {}
        self.dex_connections = {}
        self.logger = self._setup_logger()
        
    def _load_config(self, config_path: str) -> Dict:
        """โหลดการตั้งค่าจากไฟล์ config"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถโหลด config ได้: {e}")
            return {}
    
    def _setup_logger(self) -> logging.Logger:
        """ตั้งค่า logger"""
        logger = logging.getLogger('ExchangeManager')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def initialize_exchanges(self) -> bool:
        """เริ่มต้นการเชื่อมต่อกับ exchanges ทั้งหมด"""
        success_count = 0
        total_count = 0
        
        for exchange_name, exchange_config in self.config.get('exchanges', {}).items():
            if not exchange_config.get('enabled', False):
                continue
                
            total_count += 1
            
            if exchange_config.get('type') == 'cex':
                if self._initialize_cex(exchange_name, exchange_config):
                    success_count += 1
            elif exchange_config.get('type') == 'dex':
                if self._initialize_dex(exchange_name, exchange_config):
                    success_count += 1
        
        self.logger.info(f"🔗 เชื่อมต่อ Exchange สำเร็จ: {success_count}/{total_count}")
        return success_count > 0
    
    def _initialize_cex(self, exchange_name: str, config: Dict) -> bool:
        """เริ่มต้นการเชื่อมต่อกับ CEX"""
        try:
            # ดึง API credentials จาก environment variables
            api_key = os.getenv(f"{exchange_name.upper()}_API_KEY", config.get('api_key', ''))
            secret = os.getenv(f"{exchange_name.upper()}_SECRET", config.get('secret', ''))
            passphrase = os.getenv(f"{exchange_name.upper()}_PASSPHRASE", config.get('passphrase', ''))
            sandbox = os.getenv(f"{exchange_name.upper()}_SANDBOX", str(config.get('sandbox', True))).lower() == 'true'
            
            # สร้าง exchange instance
            exchange_class = getattr(ccxt, exchange_name)
            exchange_params = {
                'apiKey': api_key,
                'secret': secret,
                'sandbox': sandbox,
                'enableRateLimit': True,
                'timeout': 30000,
            }
            
            # เพิ่ม passphrase สำหรับ exchanges ที่ต้องการ (เช่น OKX)
            if passphrase and exchange_name in ['okx', 'kucoin']:
                exchange_params['password'] = passphrase
            
            exchange = exchange_class(exchange_params)
            
            # ทดสอบการเชื่อมต่อ
            if api_key and secret:
                balance = exchange.fetch_balance()
                self.logger.info(f"✅ เชื่อมต่อ {exchange_name.upper()} สำเร็จ")
            else:
                self.logger.warning(f"⚠️ {exchange_name.upper()}: ไม่มี API credentials (ใช้โหมดอ่านอย่างเดียว)")
            
            self.exchanges[exchange_name] = {
                'instance': exchange,
                'config': config,
                'type': 'cex'
            }
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถเชื่อมต่อ {exchange_name} ได้: {e}")
            return False
    
    def _initialize_dex(self, dex_name: str, config: Dict) -> bool:
        """เริ่มต้นการเชื่อมต่อกับ DEX"""
        try:
            network = config.get('network', 'ethereum')
            rpc_url = os.getenv(f"{network.upper()}_RPC_URL", config.get('rpc_url', ''))
            private_key = os.getenv(f"{network.upper()}_PRIVATE_KEY", config.get('private_key', ''))
            
            if not rpc_url:
                self.logger.error(f"❌ ไม่มี RPC URL สำหรับ {dex_name}")
                return False
            
            # เชื่อมต่อกับ Web3
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            
            if not w3.is_connected():
                self.logger.error(f"❌ ไม่สามารถเชื่อมต่อ {network} network ได้")
                return False
            
            # สร้าง account จาก private key (ถ้ามี)
            account = None
            if private_key:
                account = w3.eth.account.from_key(private_key)
                self.logger.info(f"✅ เชื่อมต่อ {dex_name} สำเร็จ (Address: {account.address[:10]}...)")
            else:
                self.logger.warning(f"⚠️ {dex_name}: ไม่มี private key (ใช้โหมดอ่านอย่างเดียว)")
            
            self.dex_connections[dex_name] = {
                'w3': w3,
                'account': account,
                'config': config,
                'type': 'dex'
            }
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถเชื่อมต่อ {dex_name} ได้: {e}")
            return False
    
    def get_exchange(self, exchange_name: str):
        """ดึง exchange instance"""
        if exchange_name in self.exchanges:
            return self.exchanges[exchange_name]['instance']
        elif exchange_name in self.dex_connections:
            return self.dex_connections[exchange_name]
        return None
    
    def get_enabled_exchanges(self) -> List[str]:
        """ดึงรายชื่อ exchanges ที่เปิดใช้งาน"""
        enabled = []
        enabled.extend(list(self.exchanges.keys()))
        enabled.extend(list(self.dex_connections.keys()))
        return enabled
    
    def get_trading_pairs(self, exchange_name: str) -> List[str]:
        """ดึงรายการ trading pairs ของ exchange"""
        if exchange_name in self.exchanges:
            return self.exchanges[exchange_name]['config'].get('trading_pairs', [])
        elif exchange_name in self.dex_connections:
            return self.dex_connections[exchange_name]['config'].get('trading_pairs', [])
        return []
    
    async def fetch_ticker(self, exchange_name: str, symbol: str) -> Optional[Dict]:
        """ดึงข้อมูล ticker จาก exchange"""
        try:
            if exchange_name in self.exchanges:
                exchange = self.exchanges[exchange_name]['instance']
                return exchange.fetch_ticker(symbol)
            elif exchange_name in self.dex_connections:
                # สำหรับ DEX จะต้องใช้วิธีการอื่น (เช่น ดึงจาก subgraph หรือ on-chain)
                return await self._fetch_dex_price(exchange_name, symbol)
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถดึง ticker {symbol} จาก {exchange_name}: {e}")
        return None
    
    async def _fetch_dex_price(self, dex_name: str, symbol: str) -> Optional[Dict]:
        """ดึงราคาจาก DEX (ตัวอย่างพื้นฐาน)"""
        # นี่เป็นตัวอย่างพื้นฐาน ในการใช้งานจริงควรใช้ subgraph หรือ price oracle
        try:
            dex_config = self.dex_connections[dex_name]
            w3 = dex_config['w3']
            
            # ตัวอย่าง: ดึงราคาจาก Chainlink price feed (สำหรับ ETH/USD)
            if symbol == "WETH/USDC":
                # ใช้ mock data สำหรับตัวอย่าง
                return {
                    'symbol': symbol,
                    'last': 2000.0,
                    'bid': 1999.5,
                    'ask': 2000.5,
                    'timestamp': w3.eth.get_block('latest')['timestamp'] * 1000
                }
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถดึงราคาจาก DEX {dex_name}: {e}")
        
        return None
    
    async def place_order(self, exchange_name: str, symbol: str, order_type: str, 
                         side: str, amount: float, price: float = None) -> Optional[Dict]:
        """วางออเดอร์"""
        try:
            if exchange_name in self.exchanges:
                exchange = self.exchanges[exchange_name]['instance']
                
                if order_type == 'market':
                    if side == 'buy':
                        return exchange.create_market_buy_order(symbol, amount)
                    else:
                        return exchange.create_market_sell_order(symbol, amount)
                elif order_type == 'limit' and price:
                    if side == 'buy':
                        return exchange.create_limit_buy_order(symbol, amount, price)
                    else:
                        return exchange.create_limit_sell_order(symbol, amount, price)
            
            elif exchange_name in self.dex_connections:
                return await self._place_dex_order(exchange_name, symbol, order_type, side, amount, price)
                
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถวางออเดอร์ {symbol} ใน {exchange_name}: {e}")
        
        return None
    
    async def _place_dex_order(self, dex_name: str, symbol: str, order_type: str,
                              side: str, amount: float, price: float = None) -> Optional[Dict]:
        """วางออเดอร์ใน DEX (ต้องการการพัฒนาเพิ่มเติม)"""
        # นี่เป็นโครงสร้างพื้นฐาน สำหรับการใช้งานจริงต้องใช้ smart contract interaction
        self.logger.info(f"📝 DEX Order: {side} {amount} {symbol} ใน {dex_name}")
        return {
            'id': f"dex_{dex_name}_{symbol}_{side}_{amount}",
            'symbol': symbol,
            'side': side,
            'amount': amount,
            'price': price,
            'status': 'pending',
            'timestamp': asyncio.get_event_loop().time() * 1000
        }
    
    def get_balance(self, exchange_name: str) -> Optional[Dict]:
        """ดึงยอดเงินคงเหลือ"""
        try:
            if exchange_name in self.exchanges:
                exchange = self.exchanges[exchange_name]['instance']
                return exchange.fetch_balance()
            elif exchange_name in self.dex_connections:
                return self._get_dex_balance(exchange_name)
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถดึงยอดเงินจาก {exchange_name}: {e}")
        return None
    
    def _get_dex_balance(self, dex_name: str) -> Optional[Dict]:
        """ดึงยอดเงินจาก DEX wallet"""
        try:
            dex_config = self.dex_connections[dex_name]
            w3 = dex_config['w3']
            account = dex_config['account']
            
            if not account:
                return None
            
            # ดึงยอด ETH/BNB
            native_balance = w3.eth.get_balance(account.address)
            native_balance_ether = w3.from_wei(native_balance, 'ether')
            
            network = dex_config['config'].get('network', 'ethereum')
            native_symbol = 'ETH' if network == 'ethereum' else 'BNB' if network == 'bsc' else 'MATIC'
            
            return {
                'free': {native_symbol: float(native_balance_ether)},
                'used': {native_symbol: 0.0},
                'total': {native_symbol: float(native_balance_ether)}
            }
            
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถดึงยอดเงิน DEX: {e}")
        return None
    
    def close_all_connections(self):
        """ปิดการเชื่อมต่อทั้งหมด"""
        for exchange_name, exchange_data in self.exchanges.items():
            try:
                if hasattr(exchange_data['instance'], 'close'):
                    exchange_data['instance'].close()
            except:
                pass
        
        self.logger.info("🔌 ปิดการเชื่อมต่อทั้งหมดแล้ว") 