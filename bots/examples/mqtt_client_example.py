import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any
import paho.mqtt.client as mqtt

class HummingbotMQTTClient:
    """Client สำหรับควบคุม Hummingbot strategies ผ่าน MQTT"""
    
    def __init__(self, mqtt_config: Dict[str, Any]):
        self.mqtt_config = mqtt_config
        self.mqtt_client = None
        self.is_connected = False
        self.logger = self._setup_logger()
        
        # MQTT topics
        self.topics = {
            "command": "hummingbot/command",
            "status": "hummingbot/status",
            "strategy": "hummingbot/strategy", 
            "performance": "hummingbot/performance",
            "logs": "hummingbot/logs"
        }
        
        # Response storage
        self.responses = {}
        self.response_timeout = 30  # วินาที
    
    def _setup_logger(self) -> logging.Logger:
        """ตั้งค่า logger"""
        logger = logging.getLogger('HummingbotClient')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def connect(self) -> bool:
        """เชื่อมต่อ MQTT broker"""
        try:
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.on_connect = self._on_connect
            self.mqtt_client.on_message = self._on_message
            self.mqtt_client.on_disconnect = self._on_disconnect
            
            # ตั้งค่า authentication
            if self.mqtt_config.get("username"):
                self.mqtt_client.username_pw_set(
                    self.mqtt_config["username"],
                    self.mqtt_config.get("password", "")
                )
            
            # เชื่อมต่อ
            host = self.mqtt_config.get("host", "localhost")
            port = self.mqtt_config.get("port", 1883)
            
            self.mqtt_client.connect(host, port, 60)
            self.mqtt_client.loop_start()
            
            # รอการเชื่อมต่อ
            await asyncio.sleep(2)
            
            if self.is_connected:
                self.logger.info(f"✅ เชื่อมต่อ MQTT broker: {host}:{port}")
                return True
            else:
                self.logger.error("❌ ไม่สามารถเชื่อมต่อ MQTT broker")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ ข้อผิดพลาดในการเชื่อมต่อ MQTT: {e}")
            return False
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback เมื่อเชื่อมต่อ MQTT สำเร็จ"""
        if rc == 0:
            self.is_connected = True
            self.logger.info("🔗 เชื่อมต่อ MQTT สำเร็จ")
            
            # Subscribe status topics
            client.subscribe(f"{self.topics['status']}/+")
            client.subscribe(f"{self.topics['logs']}/+")
            self.logger.info("📡 Subscribe status และ logs topics")
        else:
            self.logger.error(f"❌ การเชื่อมต่อ MQTT ล้มเหลว: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """Callback เมื่อได้รับข้อความ MQTT"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            self.logger.info(f"📨 ได้รับข้อความ: {topic}")
            
            # เก็บ response
            if topic.startswith(self.topics["status"]):
                command = topic.split("/")[-1]
                self.responses[command] = payload
                
            # แสดงข้อมูลสำคัญ
            if "heartbeat" in topic:
                self._handle_heartbeat(payload)
            elif "update" in topic:
                self._handle_status_update(payload)
            elif "error" in topic:
                self._handle_error(payload)
                
        except Exception as e:
            self.logger.error(f"❌ ข้อผิดพลาดในการประมวลผลข้อความ: {e}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback เมื่อขาดการเชื่อมต่อ MQTT"""
        self.is_connected = False
        self.logger.warning("⚠️ ขาดการเชื่อมต่อ MQTT")
    
    def _handle_heartbeat(self, payload: Dict):
        """จัดการ heartbeat"""
        status = payload.get("status", "unknown")
        strategies_count = payload.get("strategies_count", 0)
        running_count = payload.get("running_count", 0)
        
        self.logger.info(f"💓 Heartbeat: {status} | Strategies: {strategies_count} | Running: {running_count}")
    
    def _handle_status_update(self, payload: Dict):
        """จัดการ status update"""
        strategies = payload.get("strategies", {})
        
        print("\n📊 สถานะ Strategies:")
        print("-" * 50)
        
        for strategy_name, strategy_data in strategies.items():
            status = strategy_data.get("status", "unknown")
            performance = strategy_data.get("performance", {})
            total_trades = performance.get("total_trades", 0)
            total_pnl = performance.get("total_pnl", 0.0)
            
            print(f"🤖 {strategy_name}: {status} | Trades: {total_trades} | PnL: ${total_pnl:.2f}")
    
    def _handle_error(self, payload: Dict):
        """จัดการ error"""
        strategy = payload.get("strategy", "unknown")
        message = payload.get("message", "")
        timestamp = payload.get("timestamp", "")
        
        self.logger.error(f"🚨 Error in {strategy}: {message} at {timestamp}")
    
    def _publish_command(self, command: str, payload: Dict) -> bool:
        """ส่งคำสั่งผ่าน MQTT"""
        try:
            if not self.is_connected:
                self.logger.error("❌ ไม่ได้เชื่อมต่อ MQTT")
                return False
            
            topic = f"{self.topics['command']}/{command}"
            message = json.dumps(payload, default=str, ensure_ascii=False)
            
            self.mqtt_client.publish(topic, message)
            self.logger.info(f"📤 ส่งคำสั่ง: {command}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถส่งคำสั่ง: {e}")
            return False
    
    async def _wait_for_response(self, command: str) -> Dict:
        """รอ response จากคำสั่ง"""
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < self.response_timeout:
            if command in self.responses:
                response = self.responses.pop(command)
                return response
            
            await asyncio.sleep(0.5)
        
        return {"success": False, "error": "Timeout waiting for response"}
    
    # === Strategy Management Commands ===
    
    async def create_strategy(self, name: str, strategy_type: str, exchange: str, 
                            trading_pair: str, config: Dict = None) -> Dict:
        """สร้าง strategy ใหม่"""
        payload = {
            "name": name,
            "strategy_type": strategy_type,
            "exchange": exchange,
            "trading_pair": trading_pair,
            "config": config or {}
        }
        
        if self._publish_command("create_strategy", payload):
            return await self._wait_for_response("create_strategy")
        
        return {"success": False, "error": "Failed to send command"}
    
    async def start_strategy(self, name: str) -> Dict:
        """เริ่ม strategy"""
        payload = {"name": name}
        
        if self._publish_command("start_strategy", payload):
            return await self._wait_for_response("start_strategy")
        
        return {"success": False, "error": "Failed to send command"}
    
    async def stop_strategy(self, name: str) -> Dict:
        """หยุด strategy"""
        payload = {"name": name}
        
        if self._publish_command("stop_strategy", payload):
            return await self._wait_for_response("stop_strategy")
        
        return {"success": False, "error": "Failed to send command"}
    
    async def pause_strategy(self, name: str) -> Dict:
        """หยุดชั่วคราว strategy"""
        payload = {"name": name}
        
        if self._publish_command("pause_strategy", payload):
            return await self._wait_for_response("pause_strategy")
        
        return {"success": False, "error": "Failed to send command"}
    
    async def resume_strategy(self, name: str) -> Dict:
        """เริ่มต่อ strategy"""
        payload = {"name": name}
        
        if self._publish_command("resume_strategy", payload):
            return await self._wait_for_response("resume_strategy")
        
        return {"success": False, "error": "Failed to send command"}
    
    async def delete_strategy(self, name: str) -> Dict:
        """ลบ strategy"""
        payload = {"name": name}
        
        if self._publish_command("delete_strategy", payload):
            return await self._wait_for_response("delete_strategy")
        
        return {"success": False, "error": "Failed to send command"}
    
    async def get_strategies(self) -> Dict:
        """ดึงรายการ strategies ทั้งหมด"""
        payload = {}
        
        if self._publish_command("get_strategies", payload):
            return await self._wait_for_response("get_strategies")
        
        return {"success": False, "error": "Failed to send command"}
    
    async def get_strategy_status(self, name: str) -> Dict:
        """ดึงสถานะของ strategy"""
        payload = {"name": name}
        
        if self._publish_command("get_strategy_status", payload):
            return await self._wait_for_response("get_strategy_status")
        
        return {"success": False, "error": "Failed to send command"}
    
    async def update_strategy_config(self, name: str, config: Dict) -> Dict:
        """อัปเดต config ของ strategy"""
        payload = {
            "name": name,
            "config": config
        }
        
        if self._publish_command("update_strategy_config", payload):
            return await self._wait_for_response("update_strategy_config")
        
        return {"success": False, "error": "Failed to send command"}
    
    async def get_performance(self, name: str = None) -> Dict:
        """ดึงข้อมูลผลการดำเนินงาน"""
        payload = {}
        if name:
            payload["name"] = name
        
        if self._publish_command("get_performance", payload):
            return await self._wait_for_response("get_performance")
        
        return {"success": False, "error": "Failed to send command"}
    
    async def restart_hummingbot(self) -> Dict:
        """รีสตาร์ท Hummingbot"""
        payload = {}
        
        if self._publish_command("restart_hummingbot", payload):
            return await self._wait_for_response("restart_hummingbot")
        
        return {"success": False, "error": "Failed to send command"}
    
    async def get_logs(self, name: str = None, lines: int = 100) -> Dict:
        """ดึง logs"""
        payload = {"lines": lines}
        if name:
            payload["name"] = name
        
        if self._publish_command("get_logs", payload):
            return await self._wait_for_response("get_logs")
        
        return {"success": False, "error": "Failed to send command"}
    
    def disconnect(self):
        """ปิดการเชื่อมต่อ"""
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        
        self.logger.info("✅ ปิดการเชื่อมต่อ MQTT")

# === Example Usage ===
async def example_usage():
    """ตัวอย่างการใช้งาน"""
    
    # การตั้งค่า MQTT
    mqtt_config = {
        "host": "localhost",
        "port": 1883,
        "username": None,  # ถ้ามี authentication
        "password": None
    }
    
    # สร้าง client
    client = HummingbotMQTTClient(mqtt_config)
    
    try:
        # เชื่อมต่อ
        if not await client.connect():
            print("❌ ไม่สามารถเชื่อมต่อได้")
            return
        
        print("🚀 เริ่มต้นการทดสอบ Hummingbot MQTT Client")
        
        # รอสักครู่เพื่อให้ระบบเริ่มต้น
        await asyncio.sleep(3)
        
        # 1. ดึงรายการ strategies ที่มีอยู่
        print("\n1️⃣ ดึงรายการ strategies...")
        result = await client.get_strategies()
        if result.get("success"):
            strategies = result.get("strategies", [])
            print(f"📋 พบ {len(strategies)} strategies")
            for strategy in strategies:
                print(f"   - {strategy['name']}: {strategy['status']}")
        else:
            print(f"❌ ไม่สามารถดึงรายการ strategies: {result.get('error')}")
        
        # 2. สร้าง strategy ใหม่
        print("\n2️⃣ สร้าง strategy ใหม่...")
        strategy_config = {
            "bid_spread": 0.001,
            "ask_spread": 0.001,
            "order_amount": 10.0,
            "inventory_skew_enabled": True,
            "filled_order_delay": 60.0
        }
        
        result = await client.create_strategy(
            name="test_strategy_1",
            strategy_type="pure_market_making",
            exchange="binance",
            trading_pair="BTC-USDT",
            config=strategy_config
        )
        
        if result.get("success"):
            print("✅ สร้าง strategy สำเร็จ")
        else:
            print(f"❌ ไม่สามารถสร้าง strategy: {result.get('error')}")
        
        # 3. เริ่ม strategy
        print("\n3️⃣ เริ่ม strategy...")
        result = await client.start_strategy("test_strategy_1")
        if result.get("success"):
            print("✅ เริ่ม strategy สำเร็จ")
        else:
            print(f"❌ ไม่สามารถเริ่ม strategy: {result.get('error')}")
        
        # 4. ตรวจสอบสถานะ
        print("\n4️⃣ ตรวจสอบสถานะ strategy...")
        result = await client.get_strategy_status("test_strategy_1")
        if result.get("success"):
            strategy = result.get("strategy", {})
            print(f"📊 สถานะ: {strategy.get('status')}")
            print(f"📈 Performance: {strategy.get('performance', {})}")
        else:
            print(f"❌ ไม่สามารถดึงสถานะ: {result.get('error')}")
        
        # 5. รอสักครู่แล้วหยุด strategy
        print("\n5️⃣ รอ 10 วินาที แล้วหยุด strategy...")
        await asyncio.sleep(10)
        
        result = await client.stop_strategy("test_strategy_1")
        if result.get("success"):
            print("✅ หยุด strategy สำเร็จ")
        else:
            print(f"❌ ไม่สามารถหยุด strategy: {result.get('error')}")
        
        # 6. ดึงข้อมูลผลการดำเนินงาน
        print("\n6️⃣ ดึงข้อมูลผลการดำเนินงาน...")
        result = await client.get_performance("test_strategy_1")
        if result.get("success"):
            performance = result.get("performance", {})
            print(f"📊 ผลการดำเนินงาน:")
            print(f"   - Total Trades: {performance.get('total_trades', 0)}")
            print(f"   - Win Rate: {performance.get('win_rate', 0):.2f}%")
            print(f"   - Total PnL: ${performance.get('total_pnl', 0):.2f}")
        else:
            print(f"❌ ไม่สามารถดึงข้อมูลผลการดำเนินงาน: {result.get('error')}")
        
        # 7. ลบ strategy
        print("\n7️⃣ ลบ strategy...")
        result = await client.delete_strategy("test_strategy_1")
        if result.get("success"):
            print("✅ ลบ strategy สำเร็จ")
        else:
            print(f"❌ ไม่สามารถลบ strategy: {result.get('error')}")
        
        print("\n🎉 การทดสอบเสร็จสิ้น!")
        
        # รอ status updates
        print("\n⏳ รอ status updates (กด Ctrl+C เพื่อหยุด)...")
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ หยุดการทำงานโดยผู้ใช้")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
    finally:
        client.disconnect()

# === Interactive CLI ===
async def interactive_cli():
    """CLI แบบ interactive สำหรับควบคุม Hummingbot"""
    
    mqtt_config = {
        "host": "localhost",
        "port": 1883,
        "username": None,
        "password": None
    }
    
    client = HummingbotMQTTClient(mqtt_config)
    
    if not await client.connect():
        print("❌ ไม่สามารถเชื่อมต่อได้")
        return
    
    print("🤖 Hummingbot MQTT Controller")
    print("=" * 50)
    print("Commands:")
    print("  list                    - แสดงรายการ strategies")
    print("  create <name> <type> <exchange> <pair> - สร้าง strategy")
    print("  start <name>           - เริ่ม strategy")
    print("  stop <name>            - หยุด strategy")
    print("  pause <name>           - หยุดชั่วคราว strategy")
    print("  resume <name>          - เริ่มต่อ strategy")
    print("  status <name>          - ดูสถานะ strategy")
    print("  performance [name]     - ดูผลการดำเนินงาน")
    print("  logs [name] [lines]    - ดู logs")
    print("  delete <name>          - ลบ strategy")
    print("  restart                - รีสตาร์ท Hummingbot")
    print("  quit                   - ออกจากโปรแกรม")
    print("=" * 50)
    
    try:
        while True:
            command = input("\n> ").strip().split()
            
            if not command:
                continue
            
            cmd = command[0].lower()
            
            if cmd == "quit":
                break
            elif cmd == "list":
                result = await client.get_strategies()
                if result.get("success"):
                    strategies = result.get("strategies", [])
                    print(f"\n📋 Strategies ({len(strategies)}):")
                    for strategy in strategies:
                        print(f"  {strategy['name']}: {strategy['status']} ({strategy['strategy_type']})")
                else:
                    print(f"❌ Error: {result.get('error')}")
            
            elif cmd == "create" and len(command) >= 5:
                name, strategy_type, exchange, trading_pair = command[1:5]
                result = await client.create_strategy(name, strategy_type, exchange, trading_pair)
                if result.get("success"):
                    print(f"✅ สร้าง strategy {name} สำเร็จ")
                else:
                    print(f"❌ Error: {result.get('error')}")
            
            elif cmd == "start" and len(command) >= 2:
                name = command[1]
                result = await client.start_strategy(name)
                if result.get("success"):
                    print(f"✅ เริ่ม strategy {name} สำเร็จ")
                else:
                    print(f"❌ Error: {result.get('error')}")
            
            elif cmd == "stop" and len(command) >= 2:
                name = command[1]
                result = await client.stop_strategy(name)
                if result.get("success"):
                    print(f"✅ หยุด strategy {name} สำเร็จ")
                else:
                    print(f"❌ Error: {result.get('error')}")
            
            elif cmd == "pause" and len(command) >= 2:
                name = command[1]
                result = await client.pause_strategy(name)
                if result.get("success"):
                    print(f"✅ หยุดชั่วคราว strategy {name} สำเร็จ")
                else:
                    print(f"❌ Error: {result.get('error')}")
            
            elif cmd == "resume" and len(command) >= 2:
                name = command[1]
                result = await client.resume_strategy(name)
                if result.get("success"):
                    print(f"✅ เริ่มต่อ strategy {name} สำเร็จ")
                else:
                    print(f"❌ Error: {result.get('error')}")
            
            elif cmd == "status" and len(command) >= 2:
                name = command[1]
                result = await client.get_strategy_status(name)
                if result.get("success"):
                    strategy = result.get("strategy", {})
                    print(f"\n📊 Status of {name}:")
                    print(f"  Status: {strategy.get('status')}")
                    print(f"  Type: {strategy.get('strategy_type')}")
                    print(f"  Exchange: {strategy.get('exchange')}")
                    print(f"  Trading Pair: {strategy.get('trading_pair')}")
                    print(f"  Last Updated: {strategy.get('last_updated')}")
                else:
                    print(f"❌ Error: {result.get('error')}")
            
            elif cmd == "performance":
                name = command[1] if len(command) >= 2 else None
                result = await client.get_performance(name)
                if result.get("success"):
                    if name:
                        performance = result.get("performance", {})
                        print(f"\n📈 Performance of {name}:")
                        print(f"  Total Trades: {performance.get('total_trades', 0)}")
                        print(f"  Profitable Trades: {performance.get('profitable_trades', 0)}")
                        print(f"  Win Rate: {performance.get('win_rate', 0):.2f}%")
                        print(f"  Total PnL: ${performance.get('total_pnl', 0):.2f}")
                    else:
                        all_performance = result.get("performance", {})
                        print(f"\n📈 All Performance:")
                        for strategy_name, performance in all_performance.items():
                            print(f"  {strategy_name}: {performance.get('total_trades', 0)} trades, ${performance.get('total_pnl', 0):.2f} PnL")
                else:
                    print(f"❌ Error: {result.get('error')}")
            
            elif cmd == "logs":
                name = command[1] if len(command) >= 2 else None
                lines = int(command[2]) if len(command) >= 3 else 20
                result = await client.get_logs(name, lines)
                if result.get("success"):
                    logs = result.get("logs", [])
                    print(f"\n📝 Logs ({len(logs)} lines):")
                    for log_line in logs[-lines:]:
                        print(f"  {log_line.strip()}")
                else:
                    print(f"❌ Error: {result.get('error')}")
            
            elif cmd == "delete" and len(command) >= 2:
                name = command[1]
                confirm = input(f"⚠️ ต้องการลบ strategy {name} หรือไม่? (y/N): ")
                if confirm.lower() == 'y':
                    result = await client.delete_strategy(name)
                    if result.get("success"):
                        print(f"✅ ลบ strategy {name} สำเร็จ")
                    else:
                        print(f"❌ Error: {result.get('error')}")
                else:
                    print("❌ ยกเลิกการลบ")
            
            elif cmd == "restart":
                confirm = input("⚠️ ต้องการรีสตาร์ท Hummingbot หรือไม่? (y/N): ")
                if confirm.lower() == 'y':
                    result = await client.restart_hummingbot()
                    if result.get("success"):
                        print("✅ รีสตาร์ท Hummingbot สำเร็จ")
                    else:
                        print(f"❌ Error: {result.get('error')}")
                else:
                    print("❌ ยกเลิกการรีสตาร์ท")
            
            else:
                print("❌ คำสั่งไม่ถูกต้อง หรือพารามิเตอร์ไม่ครบ")
    
    except KeyboardInterrupt:
        print("\n⏹️ หยุดการทำงานโดยผู้ใช้")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        asyncio.run(interactive_cli())
    else:
        asyncio.run(example_usage()) 