import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
from .exchange_manager import ExchangeManager
from .market_analyzer import MultiExchangeMarketAnalyzer
from .risk_manager import RiskManager

class MultiExchangeTradingBot:
    """บอทเทรดดิ้งที่รองรับหลาย Exchange ทั้ง CEX และ DEX"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.exchange_manager = ExchangeManager(config_path)
        self.market_analyzer = MultiExchangeMarketAnalyzer(config_path)
        self.risk_manager = RiskManager()
        self.logger = self._setup_logger()
        
        # สถานะบอท
        self.is_running = False
        self.active_orders = {}  # {exchange_name: {symbol: [orders]}}
        self.positions = {}      # {exchange_name: {symbol: position_info}}
        self.performance = {}    # {exchange_name: performance_data}
        
        # การตั้งค่าเทรด
        self.trading_config = {}
        self.last_analysis_time = {}
        
    def _setup_logger(self) -> logging.Logger:
        """ตั้งค่า logger"""
        logger = logging.getLogger('MultiExchangeBot')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def initialize(self) -> bool:
        """เริ่มต้นบอท"""
        self.logger.info("🤖 เริ่มต้นระบบ Multi-Exchange Trading Bot")
        
        # เริ่มต้น exchange manager
        if not self.exchange_manager.initialize_exchanges():
            self.logger.error("❌ ไม่สามารถเชื่อมต่อกับ exchange ใดๆ ได้")
            return False
        
        # เริ่มต้น market analyzer
        if not await self.market_analyzer.initialize():
            self.logger.error("❌ ไม่สามารถเริ่มต้น market analyzer ได้")
            return False
        
        # โหลดการตั้งค่าเทรด
        await self._load_trading_configs()
        
        # เริ่มต้นข้อมูลสำหรับแต่ละ exchange
        for exchange_name in self.exchange_manager.get_enabled_exchanges():
            self.active_orders[exchange_name] = {}
            self.positions[exchange_name] = {}
            self.performance[exchange_name] = {
                'total_trades': 0,
                'profitable_trades': 0,
                'total_profit': 0.0,
                'start_balance': await self._get_initial_balance(exchange_name)
            }
        
        self.logger.info("✅ เริ่มต้นบอทสำเร็จ")
        return True
    
    async def _load_trading_configs(self):
        """โหลดการตั้งค่าเทรดสำหรับแต่ละ exchange"""
        enabled_exchanges = self.exchange_manager.get_enabled_exchanges()
        
        for exchange_name in enabled_exchanges:
            trading_pairs = self.exchange_manager.get_trading_pairs(exchange_name)
            
            for symbol in trading_pairs:
                # วิเคราะห์ตลาดเพื่อสร้าง config
                try:
                    df = await self.market_analyzer.fetch_ohlc_data(exchange_name, symbol, "1m", 100)
                    if df is not None and not df.empty:
                        df = self.market_analyzer.calculate_technical_indicators(df)
                        analysis = self.market_analyzer.analyze_market_condition(df, symbol)
                        config = self.market_analyzer.generate_trading_config(analysis, exchange_name)
                        
                        if exchange_name not in self.trading_config:
                            self.trading_config[exchange_name] = {}
                        
                        self.trading_config[exchange_name][symbol] = config
                        self.logger.info(f"📋 โหลด config สำหรับ {exchange_name}:{symbol}")
                        
                except Exception as e:
                    self.logger.error(f"❌ ไม่สามารถโหลด config สำหรับ {exchange_name}:{symbol}: {e}")
    
    async def _get_initial_balance(self, exchange_name: str) -> Dict:
        """ดึงยอดเงินเริ่มต้น"""
        try:
            balance = self.exchange_manager.get_balance(exchange_name)
            return balance if balance else {}
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถดึงยอดเงินจาก {exchange_name}: {e}")
            return {}
    
    async def start_trading(self):
        """เริ่มการเทรด"""
        if self.is_running:
            self.logger.warning("⚠️ บอทกำลังทำงานอยู่แล้ว")
            return
        
        self.is_running = True
        self.logger.info("🚀 เริ่มการเทรด")
        
        # สร้าง tasks สำหรับแต่ละ exchange
        tasks = []
        
        for exchange_name in self.exchange_manager.get_enabled_exchanges():
            task = asyncio.create_task(self._trading_loop(exchange_name))
            tasks.append(task)
        
        # เพิ่ม task สำหรับการอัปเดต config
        config_update_task = asyncio.create_task(self._config_update_loop())
        tasks.append(config_update_task)
        
        # เพิ่ม task สำหรับการรายงานสถานะ
        status_task = asyncio.create_task(self._status_report_loop())
        tasks.append(status_task)
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            self.logger.info("⏹️ หยุดการเทรดโดยผู้ใช้")
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการเทรด: {e}")
        finally:
            await self.stop_trading()
    
    async def _trading_loop(self, exchange_name: str):
        """ลูปการเทรดสำหรับ exchange หนึ่งๆ"""
        self.logger.info(f"🔄 เริ่มลูปการเทรดสำหรับ {exchange_name}")
        
        while self.is_running:
            try:
                trading_pairs = self.exchange_manager.get_trading_pairs(exchange_name)
                
                for symbol in trading_pairs:
                    if not self.is_running:
                        break
                    
                    await self._process_symbol(exchange_name, symbol)
                
                # รอก่อนรอบถัดไป
                await asyncio.sleep(30)  # 30 วินาที
                
            except Exception as e:
                self.logger.error(f"❌ ข้อผิดพลาดในลูปการเทรด {exchange_name}: {e}")
                await asyncio.sleep(60)  # รอ 1 นาทีก่อนลองใหม่
    
    async def _process_symbol(self, exchange_name: str, symbol: str):
        """ประมวลผลการเทรดสำหรับ symbol หนึ่งๆ"""
        try:
            # ดึง config สำหรับ symbol นี้
            config = self.trading_config.get(exchange_name, {}).get(symbol)
            if not config or "error" in config:
                return
            
            # ตรวจสอบ risk management
            if not await self._check_risk_limits(exchange_name, symbol):
                return
            
            # ดึงข้อมูลตลาดปัจจุบัน
            ticker = await self.exchange_manager.fetch_ticker(exchange_name, symbol)
            if not ticker:
                return
            
            current_price = ticker['last']
            
            # ตรวจสอบออเดอร์ที่มีอยู่
            await self._check_existing_orders(exchange_name, symbol)
            
            # ตัดสินใจเทรด
            await self._make_trading_decision(exchange_name, symbol, current_price, config)
            
        except Exception as e:
            self.logger.error(f"❌ ข้อผิดพลาดในการประมวลผล {exchange_name}:{symbol}: {e}")
    
    async def _check_risk_limits(self, exchange_name: str, symbol: str) -> bool:
        """ตรวจสอบขอบเขตความเสี่ยง"""
        try:
            # ตรวจสอบยอดเงิน
            balance = self.exchange_manager.get_balance(exchange_name)
            if not balance:
                return False
            
            # ตรวจสอบการสูญเสียรายวัน
            performance = self.performance.get(exchange_name, {})
            daily_loss = performance.get('daily_loss', 0)
            max_daily_loss = 0.05  # 5%
            
            if daily_loss > max_daily_loss:
                self.logger.warning(f"⚠️ {exchange_name} เกินขีดจำกัดการสูญเสียรายวัน")
                return False
            
            # ตรวจสอบจำนวนออเดอร์ที่เปิดอยู่
            active_orders_count = len(self.active_orders.get(exchange_name, {}).get(symbol, []))
            max_orders = 5
            
            if active_orders_count >= max_orders:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ ข้อผิดพลาดในการตรวจสอบความเสี่ยง: {e}")
            return False
    
    async def _check_existing_orders(self, exchange_name: str, symbol: str):
        """ตรวจสอบและอัปเดตออเดอร์ที่มีอยู่"""
        try:
            if exchange_name not in self.active_orders:
                self.active_orders[exchange_name] = {}
            
            if symbol not in self.active_orders[exchange_name]:
                self.active_orders[exchange_name][symbol] = []
            
            # ตรวจสอบสถานะออเดอร์
            orders_to_remove = []
            
            for order in self.active_orders[exchange_name][symbol]:
                try:
                    # สำหรับ CEX
                    if exchange_name in self.exchange_manager.exchanges:
                        exchange = self.exchange_manager.get_exchange(exchange_name)
                        order_status = exchange.fetch_order(order['id'], symbol)
                        
                        if order_status['status'] in ['closed', 'canceled']:
                            orders_to_remove.append(order)
                            
                            if order_status['status'] == 'closed':
                                await self._handle_filled_order(exchange_name, symbol, order_status)
                    
                    # สำหรับ DEX (ต้องการการพัฒนาเพิ่มเติม)
                    else:
                        # ตรวจสอบสถานะ on-chain
                        pass
                        
                except Exception as e:
                    self.logger.error(f"❌ ไม่สามารถตรวจสอบออเดอร์ {order['id']}: {e}")
            
            # ลบออเดอร์ที่เสร็จสิ้นแล้ว
            for order in orders_to_remove:
                self.active_orders[exchange_name][symbol].remove(order)
                
        except Exception as e:
            self.logger.error(f"❌ ข้อผิดพลาดในการตรวจสอบออเดอร์: {e}")
    
    async def _handle_filled_order(self, exchange_name: str, symbol: str, order: Dict):
        """จัดการออเดอร์ที่เสร็จสิ้น"""
        try:
            side = order['side']
            amount = order['amount']
            price = order['price']
            
            self.logger.info(f"✅ ออเดอร์เสร็จสิ้น: {side} {amount} {symbol} @ {price} ใน {exchange_name}")
            
            # อัปเดตสถิติ
            performance = self.performance[exchange_name]
            performance['total_trades'] += 1
            
            # คำนวณกำไร/ขาดทุน (แบบง่าย)
            if side == 'sell':
                # สมมติว่าเป็นการขายที่ทำกำไร
                profit = amount * price * 0.001  # 0.1% กำไรโดยประมาณ
                performance['total_profit'] += profit
                
                if profit > 0:
                    performance['profitable_trades'] += 1
            
        except Exception as e:
            self.logger.error(f"❌ ข้อผิดพลาดในการจัดการออเดอร์ที่เสร็จสิ้น: {e}")
    
    async def _make_trading_decision(self, exchange_name: str, symbol: str, 
                                   current_price: float, config: Dict):
        """ตัดสินใจเทรด"""
        try:
            spreads = config.get('spreads', {})
            bid_spread = spreads.get('bid_spread', 0.001)
            ask_spread = spreads.get('ask_spread', 0.001)
            
            risk_mgmt = config.get('risk_management', {})
            min_amount = risk_mgmt.get('min_order_amount', 10.0)
            
            # คำนวณราคา bid และ ask
            bid_price = current_price * (1 - bid_spread)
            ask_price = current_price * (1 + ask_spread)
            
            # ตรวจสอบว่ามีออเดอร์ในระดับราคานี้อยู่แล้วหรือไม่
            existing_orders = self.active_orders.get(exchange_name, {}).get(symbol, [])
            
            has_buy_order = any(order['side'] == 'buy' and abs(order['price'] - bid_price) < current_price * 0.001 
                               for order in existing_orders)
            has_sell_order = any(order['side'] == 'sell' and abs(order['price'] - ask_price) < current_price * 0.001 
                                for order in existing_orders)
            
            # วางออเดอร์ buy ถ้ายังไม่มี
            if not has_buy_order:
                await self._place_order(exchange_name, symbol, 'buy', 'limit', min_amount, bid_price)
            
            # วางออเดอร์ sell ถ้ายังไม่มี
            if not has_sell_order:
                await self._place_order(exchange_name, symbol, 'sell', 'limit', min_amount, ask_price)
                
        except Exception as e:
            self.logger.error(f"❌ ข้อผิดพลาดในการตัดสินใจเทรด: {e}")
    
    async def _place_order(self, exchange_name: str, symbol: str, side: str, 
                          order_type: str, amount: float, price: float = None):
        """วางออเดอร์"""
        try:
            order = await self.exchange_manager.place_order(
                exchange_name, symbol, order_type, side, amount, price
            )
            
            if order:
                # เก็บข้อมูลออเดอร์
                if exchange_name not in self.active_orders:
                    self.active_orders[exchange_name] = {}
                if symbol not in self.active_orders[exchange_name]:
                    self.active_orders[exchange_name][symbol] = []
                
                self.active_orders[exchange_name][symbol].append(order)
                
                self.logger.info(f"📝 วางออเดอร์: {side} {amount} {symbol} @ {price} ใน {exchange_name}")
                
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถวางออเดอร์ได้: {e}")
    
    async def _config_update_loop(self):
        """ลูปการอัปเดต config"""
        while self.is_running:
            try:
                # อัปเดต config ทุก 5 นาที
                await asyncio.sleep(300)
                
                self.logger.info("🔄 อัปเดต trading config")
                await self._load_trading_configs()
                
            except Exception as e:
                self.logger.error(f"❌ ข้อผิดพลาดในการอัปเดต config: {e}")
                await asyncio.sleep(60)
    
    async def _status_report_loop(self):
        """ลูปการรายงานสถานะ"""
        while self.is_running:
            try:
                # รายงานสถานะทุก 10 นาที
                await asyncio.sleep(600)
                
                await self._print_status_report()
                
            except Exception as e:
                self.logger.error(f"❌ ข้อผิดพลาดในการรายงานสถานะ: {e}")
                await asyncio.sleep(60)
    
    async def _print_status_report(self):
        """แสดงรายงานสถานะ"""
        print("\n" + "="*80)
        print("📊 รายงานสถานะ Multi-Exchange Trading Bot")
        print("="*80)
        print(f"⏰ เวลา: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        for exchange_name in self.exchange_manager.get_enabled_exchanges():
            print(f"\n🏢 {exchange_name.upper()}")
            print("-" * 40)
            
            # สถิติการเทรด
            perf = self.performance.get(exchange_name, {})
            total_trades = perf.get('total_trades', 0)
            profitable_trades = perf.get('profitable_trades', 0)
            total_profit = perf.get('total_profit', 0)
            
            win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
            
            print(f"📈 การเทรดทั้งหมด: {total_trades}")
            print(f"✅ การเทรดที่ทำกำไร: {profitable_trades}")
            print(f"📊 อัตราชนะ: {win_rate:.1f}%")
            print(f"💰 กำไรรวม: ${total_profit:.2f}")
            
            # ออเดอร์ที่เปิดอยู่
            active_orders_count = sum(len(orders) for orders in self.active_orders.get(exchange_name, {}).values())
            print(f"📋 ออเดอร์ที่เปิดอยู่: {active_orders_count}")
            
            # ยอดเงินปัจจุบัน
            try:
                balance = self.exchange_manager.get_balance(exchange_name)
                if balance and 'total' in balance:
                    for currency, amount in balance['total'].items():
                        if amount > 0:
                            print(f"💳 {currency}: {amount:.4f}")
            except:
                pass
        
        print("\n" + "="*80)
    
    async def stop_trading(self):
        """หยุดการเทรด"""
        self.logger.info("⏹️ หยุดการเทรด")
        self.is_running = False
        
        # ยกเลิกออเดอร์ที่เปิดอยู่ (ถ้าต้องการ)
        # await self._cancel_all_orders()
        
        # ปิดการเชื่อมต่อ
        self.exchange_manager.close_all_connections()
        
        self.logger.info("✅ หยุดการเทรดเรียบร้อย")
    
    async def _cancel_all_orders(self):
        """ยกเลิกออเดอร์ทั้งหมด"""
        for exchange_name, symbols in self.active_orders.items():
            for symbol, orders in symbols.items():
                for order in orders:
                    try:
                        if exchange_name in self.exchange_manager.exchanges:
                            exchange = self.exchange_manager.get_exchange(exchange_name)
                            exchange.cancel_order(order['id'], symbol)
                            self.logger.info(f"❌ ยกเลิกออเดอร์ {order['id']} ใน {exchange_name}")
                    except Exception as e:
                        self.logger.error(f"❌ ไม่สามารถยกเลิกออเดอร์ {order['id']}: {e}")

# === Main function ===
async def run_multi_exchange_bot():
    """รันบอทเทรดดิ้งหลาย exchange"""
    bot = MultiExchangeTradingBot()
    
    if await bot.initialize():
        await bot.start_trading()
    else:
        print("❌ ไม่สามารถเริ่มต้นบอทได้")

# === Run ===
if __name__ == "__main__":
    asyncio.run(run_multi_exchange_bot()) 