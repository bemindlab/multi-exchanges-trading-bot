import asyncio
import json
import logging
import os
import subprocess
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
import paho.mqtt.client as mqtt
from pathlib import Path

@dataclass
class HummingbotStrategy:
    """คลาสสำหรับเก็บข้อมูล strategy ของ Hummingbot"""
    name: str
    strategy_type: str
    exchange: str
    trading_pair: str
    config: Dict[str, Any]
    status: str = "stopped"  # stopped, running, paused, error
    created_at: datetime = None
    last_updated: datetime = None
    performance: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_updated is None:
            self.last_updated = datetime.now()
        if self.performance is None:
            self.performance = {
                "total_trades": 0,
                "profitable_trades": 0,
                "total_pnl": 0.0,
                "win_rate": 0.0,
                "start_time": None,
                "end_time": None
            }

class HummingbotMQTTManager:
    """ตัวจัดการ Hummingbot strategies ผ่าน MQTT"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.logger = self._setup_logger()
        
        # MQTT settings
        self.mqtt_client = None
        self.mqtt_config = self.config.get("mqtt", {})
        self.mqtt_topics = {
            "command": "hummingbot/command",
            "status": "hummingbot/status", 
            "strategy": "hummingbot/strategy",
            "performance": "hummingbot/performance",
            "logs": "hummingbot/logs"
        }
        
        # Hummingbot settings
        self.hummingbot_config = self.config.get("hummingbot", {})
        self.hummingbot_path = self.hummingbot_config.get("path", "/opt/hummingbot")
        self.strategies_path = Path(self.hummingbot_path) / "conf" / "strategies"
        self.logs_path = Path(self.hummingbot_path) / "logs"
        
        # Strategy management
        self.strategies: Dict[str, HummingbotStrategy] = {}
        self.running_processes: Dict[str, subprocess.Popen] = {}
        self.command_handlers: Dict[str, Callable] = {}
        
        # Status
        self.is_connected = False
        self.last_heartbeat = datetime.now()
        
        self._setup_command_handlers()
    
    def _load_config(self) -> Dict:
        """โหลดการตั้งค่าจากไฟล์"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ ไม่สามารถโหลด config: {e}")
            return {}
    
    def _setup_logger(self) -> logging.Logger:
        """ตั้งค่า logger"""
        logger = logging.getLogger('HummingbotMQTT')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _setup_command_handlers(self):
        """ตั้งค่า command handlers"""
        self.command_handlers = {
            "create_strategy": self._handle_create_strategy,
            "start_strategy": self._handle_start_strategy,
            "stop_strategy": self._handle_stop_strategy,
            "pause_strategy": self._handle_pause_strategy,
            "resume_strategy": self._handle_resume_strategy,
            "delete_strategy": self._handle_delete_strategy,
            "get_strategies": self._handle_get_strategies,
            "get_strategy_status": self._handle_get_strategy_status,
            "update_strategy_config": self._handle_update_strategy_config,
            "get_performance": self._handle_get_performance,
            "restart_hummingbot": self._handle_restart_hummingbot,
            "get_logs": self._handle_get_logs
        }
    
    async def initialize(self) -> bool:
        """เริ่มต้นระบบ"""
        self.logger.info("🤖 เริ่มต้น Hummingbot MQTT Manager")
        
        # ตรวจสอบ Hummingbot path
        if not self._check_hummingbot_installation():
            return False
        
        # โหลด strategies ที่มีอยู่
        await self._load_existing_strategies()
        
        # เชื่อมต่อ MQTT
        if not await self._connect_mqtt():
            return False
        
        self.logger.info("✅ เริ่มต้น Hummingbot MQTT Manager สำเร็จ")
        return True
    
    def _check_hummingbot_installation(self) -> bool:
        """ตรวจสอบการติดตั้ง Hummingbot"""
        hummingbot_executable = Path(self.hummingbot_path) / "bin" / "hummingbot"
        
        if not hummingbot_executable.exists():
            self.logger.error(f"❌ ไม่พบ Hummingbot ที่ {hummingbot_executable}")
            return False
        
        # สร้างโฟลเดอร์ที่จำเป็น
        self.strategies_path.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"✅ พบ Hummingbot ที่ {self.hummingbot_path}")
        return True
    
    async def _load_existing_strategies(self):
        """โหลด strategies ที่มีอยู่"""
        try:
            if not self.strategies_path.exists():
                return
            
            for strategy_file in self.strategies_path.glob("*.yml"):
                try:
                    with open(strategy_file, 'r') as f:
                        config = yaml.safe_load(f)
                    
                    strategy_name = strategy_file.stem
                    strategy = HummingbotStrategy(
                        name=strategy_name,
                        strategy_type=config.get("strategy", "unknown"),
                        exchange=config.get("exchange", "unknown"),
                        trading_pair=config.get("trading_pair", "unknown"),
                        config=config,
                        status="stopped"
                    )
                    
                    self.strategies[strategy_name] = strategy
                    self.logger.info(f"📋 โหลด strategy: {strategy_name}")
                    
                except Exception as e:
                    self.logger.error(f"❌ ไม่สามารถโหลด strategy {strategy_file}: {e}")
        
        except Exception as e:
            self.logger.error(f"❌ ข้อผิดพลาดในการโหลด strategies: {e}")
    
    async def _connect_mqtt(self) -> bool:
        """เชื่อมต่อ MQTT broker"""
        try:
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_message = self._on_mqtt_message
            self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
            
            # ตั้งค่า authentication ถ้ามี
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
    
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """Callback เมื่อเชื่อมต่อ MQTT สำเร็จ"""
        if rc == 0:
            self.is_connected = True
            self.logger.info("🔗 เชื่อมต่อ MQTT สำเร็จ")
            
            # Subscribe topics
            for topic_name, topic in self.mqtt_topics.items():
                if topic_name == "command":
                    client.subscribe(f"{topic}/+")
                    self.logger.info(f"📡 Subscribe: {topic}/+")
        else:
            self.logger.error(f"❌ การเชื่อมต่อ MQTT ล้มเหลว: {rc}")
    
    def _on_mqtt_message(self, client, userdata, msg):
        """Callback เมื่อได้รับข้อความ MQTT"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            self.logger.info(f"📨 ได้รับข้อความ: {topic}")
            
            # ประมวลผล command
            if topic.startswith(self.mqtt_topics["command"]):
                asyncio.create_task(self._process_command(topic, payload))
                
        except Exception as e:
            self.logger.error(f"❌ ข้อผิดพลาดในการประมวลผลข้อความ MQTT: {e}")
    
    def _on_mqtt_disconnect(self, client, userdata, rc):
        """Callback เมื่อขาดการเชื่อมต่อ MQTT"""
        self.is_connected = False
        self.logger.warning("⚠️ ขาดการเชื่อมต่อ MQTT")
    
    async def _process_command(self, topic: str, payload: Dict):
        """ประมวลผล command ที่ได้รับ"""
        try:
            # แยก command จาก topic
            command = topic.split("/")[-1]
            
            if command in self.command_handlers:
                response = await self.command_handlers[command](payload)
                
                # ส่งผลลัพธ์กลับ
                response_topic = f"{self.mqtt_topics['status']}/{command}"
                self._publish_mqtt(response_topic, response)
            else:
                self.logger.warning(f"⚠️ ไม่รู้จัก command: {command}")
                
        except Exception as e:
            self.logger.error(f"❌ ข้อผิดพลาดในการประมวลผล command: {e}")
    
    def _publish_mqtt(self, topic: str, payload: Dict):
        """ส่งข้อความผ่าน MQTT"""
        try:
            if self.mqtt_client and self.is_connected:
                message = json.dumps(payload, default=str, ensure_ascii=False)
                self.mqtt_client.publish(topic, message)
                self.logger.debug(f"📤 ส่งข้อความ: {topic}")
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถส่งข้อความ MQTT: {e}")
    
    # === Command Handlers ===
    
    async def _handle_create_strategy(self, payload: Dict) -> Dict:
        """สร้าง strategy ใหม่"""
        try:
            strategy_name = payload.get("name")
            strategy_type = payload.get("strategy_type")
            exchange = payload.get("exchange")
            trading_pair = payload.get("trading_pair")
            config = payload.get("config", {})
            
            if not all([strategy_name, strategy_type, exchange, trading_pair]):
                return {"success": False, "error": "ข้อมูลไม่ครบถ้วน"}
            
            # ตรวจสอบว่ามี strategy นี้อยู่แล้วหรือไม่
            if strategy_name in self.strategies:
                return {"success": False, "error": f"Strategy {strategy_name} มีอยู่แล้ว"}
            
            # สร้าง strategy config
            strategy_config = {
                "strategy": strategy_type,
                "exchange": exchange,
                "trading_pair": trading_pair,
                **config
            }
            
            # บันทึกไฟล์ config
            config_file = self.strategies_path / f"{strategy_name}.yml"
            with open(config_file, 'w') as f:
                yaml.dump(strategy_config, f, default_flow_style=False)
            
            # สร้าง strategy object
            strategy = HummingbotStrategy(
                name=strategy_name,
                strategy_type=strategy_type,
                exchange=exchange,
                trading_pair=trading_pair,
                config=strategy_config
            )
            
            self.strategies[strategy_name] = strategy
            
            self.logger.info(f"✅ สร้าง strategy: {strategy_name}")
            return {
                "success": True,
                "message": f"สร้าง strategy {strategy_name} สำเร็จ",
                "strategy": asdict(strategy)
            }
            
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถสร้าง strategy: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_start_strategy(self, payload: Dict) -> Dict:
        """เริ่ม strategy"""
        try:
            strategy_name = payload.get("name")
            
            if not strategy_name or strategy_name not in self.strategies:
                return {"success": False, "error": "ไม่พบ strategy"}
            
            strategy = self.strategies[strategy_name]
            
            if strategy.status == "running":
                return {"success": False, "error": "Strategy กำลังทำงานอยู่แล้ว"}
            
            # เริ่ม Hummingbot process
            success = await self._start_hummingbot_process(strategy_name)
            
            if success:
                strategy.status = "running"
                strategy.last_updated = datetime.now()
                strategy.performance["start_time"] = datetime.now()
                
                self.logger.info(f"🚀 เริ่ม strategy: {strategy_name}")
                return {
                    "success": True,
                    "message": f"เริ่ม strategy {strategy_name} สำเร็จ"
                }
            else:
                return {"success": False, "error": "ไม่สามารถเริ่ม strategy ได้"}
                
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถเริ่ม strategy: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_stop_strategy(self, payload: Dict) -> Dict:
        """หยุด strategy"""
        try:
            strategy_name = payload.get("name")
            
            if not strategy_name or strategy_name not in self.strategies:
                return {"success": False, "error": "ไม่พบ strategy"}
            
            strategy = self.strategies[strategy_name]
            
            if strategy.status != "running":
                return {"success": False, "error": "Strategy ไม่ได้ทำงานอยู่"}
            
            # หยุด Hummingbot process
            success = await self._stop_hummingbot_process(strategy_name)
            
            if success:
                strategy.status = "stopped"
                strategy.last_updated = datetime.now()
                strategy.performance["end_time"] = datetime.now()
                
                self.logger.info(f"⏹️ หยุด strategy: {strategy_name}")
                return {
                    "success": True,
                    "message": f"หยุด strategy {strategy_name} สำเร็จ"
                }
            else:
                return {"success": False, "error": "ไม่สามารถหยุด strategy ได้"}
                
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถหยุด strategy: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_pause_strategy(self, payload: Dict) -> Dict:
        """หยุดชั่วคราว strategy"""
        try:
            strategy_name = payload.get("name")
            
            if not strategy_name or strategy_name not in self.strategies:
                return {"success": False, "error": "ไม่พบ strategy"}
            
            strategy = self.strategies[strategy_name]
            
            if strategy.status != "running":
                return {"success": False, "error": "Strategy ไม่ได้ทำงานอยู่"}
            
            # ส่งคำสั่ง pause ไปยัง Hummingbot
            success = await self._send_hummingbot_command(strategy_name, "stop")
            
            if success:
                strategy.status = "paused"
                strategy.last_updated = datetime.now()
                
                self.logger.info(f"⏸️ หยุดชั่วคราว strategy: {strategy_name}")
                return {
                    "success": True,
                    "message": f"หยุดชั่วคราว strategy {strategy_name} สำเร็จ"
                }
            else:
                return {"success": False, "error": "ไม่สามารถหยุดชั่วคราว strategy ได้"}
                
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถหยุดชั่วคราว strategy: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_resume_strategy(self, payload: Dict) -> Dict:
        """เริ่มต่อ strategy"""
        try:
            strategy_name = payload.get("name")
            
            if not strategy_name or strategy_name not in self.strategies:
                return {"success": False, "error": "ไม่พบ strategy"}
            
            strategy = self.strategies[strategy_name]
            
            if strategy.status != "paused":
                return {"success": False, "error": "Strategy ไม่ได้หยุดชั่วคราว"}
            
            # ส่งคำสั่ง start ไปยัง Hummingbot
            success = await self._send_hummingbot_command(strategy_name, "start")
            
            if success:
                strategy.status = "running"
                strategy.last_updated = datetime.now()
                
                self.logger.info(f"▶️ เริ่มต่อ strategy: {strategy_name}")
                return {
                    "success": True,
                    "message": f"เริ่มต่อ strategy {strategy_name} สำเร็จ"
                }
            else:
                return {"success": False, "error": "ไม่สามารถเริ่มต่อ strategy ได้"}
                
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถเริ่มต่อ strategy: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_delete_strategy(self, payload: Dict) -> Dict:
        """ลบ strategy"""
        try:
            strategy_name = payload.get("name")
            
            if not strategy_name or strategy_name not in self.strategies:
                return {"success": False, "error": "ไม่พบ strategy"}
            
            strategy = self.strategies[strategy_name]
            
            # หยุด strategy ก่อนลบ
            if strategy.status == "running":
                await self._stop_hummingbot_process(strategy_name)
            
            # ลบไฟล์ config
            config_file = self.strategies_path / f"{strategy_name}.yml"
            if config_file.exists():
                config_file.unlink()
            
            # ลบจาก memory
            del self.strategies[strategy_name]
            
            self.logger.info(f"🗑️ ลบ strategy: {strategy_name}")
            return {
                "success": True,
                "message": f"ลบ strategy {strategy_name} สำเร็จ"
            }
            
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถลบ strategy: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_get_strategies(self, payload: Dict) -> Dict:
        """ดึงรายการ strategies ทั้งหมด"""
        try:
            strategies_data = []
            
            for strategy_name, strategy in self.strategies.items():
                strategy_data = asdict(strategy)
                strategies_data.append(strategy_data)
            
            return {
                "success": True,
                "strategies": strategies_data,
                "total": len(strategies_data)
            }
            
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถดึงรายการ strategies: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_get_strategy_status(self, payload: Dict) -> Dict:
        """ดึงสถานะของ strategy"""
        try:
            strategy_name = payload.get("name")
            
            if not strategy_name or strategy_name not in self.strategies:
                return {"success": False, "error": "ไม่พบ strategy"}
            
            strategy = self.strategies[strategy_name]
            
            # อัปเดตสถานะจาก process
            if strategy_name in self.running_processes:
                process = self.running_processes[strategy_name]
                if process.poll() is None:
                    strategy.status = "running"
                else:
                    strategy.status = "stopped"
                    del self.running_processes[strategy_name]
            
            return {
                "success": True,
                "strategy": asdict(strategy)
            }
            
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถดึงสถานะ strategy: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_update_strategy_config(self, payload: Dict) -> Dict:
        """อัปเดต config ของ strategy"""
        try:
            strategy_name = payload.get("name")
            new_config = payload.get("config", {})
            
            if not strategy_name or strategy_name not in self.strategies:
                return {"success": False, "error": "ไม่พบ strategy"}
            
            strategy = self.strategies[strategy_name]
            
            if strategy.status == "running":
                return {"success": False, "error": "ไม่สามารถแก้ไข config ขณะ strategy ทำงานอยู่"}
            
            # อัปเดต config
            strategy.config.update(new_config)
            strategy.last_updated = datetime.now()
            
            # บันทึกไฟล์ config
            config_file = self.strategies_path / f"{strategy_name}.yml"
            with open(config_file, 'w') as f:
                yaml.dump(strategy.config, f, default_flow_style=False)
            
            self.logger.info(f"📝 อัปเดต config: {strategy_name}")
            return {
                "success": True,
                "message": f"อัปเดต config {strategy_name} สำเร็จ",
                "strategy": asdict(strategy)
            }
            
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถอัปเดต config: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_get_performance(self, payload: Dict) -> Dict:
        """ดึงข้อมูลผลการดำเนินงาน"""
        try:
            strategy_name = payload.get("name")
            
            if strategy_name and strategy_name not in self.strategies:
                return {"success": False, "error": "ไม่พบ strategy"}
            
            if strategy_name:
                # ดึงข้อมูลของ strategy เดียว
                strategy = self.strategies[strategy_name]
                performance = await self._get_strategy_performance(strategy_name)
                
                return {
                    "success": True,
                    "strategy": strategy_name,
                    "performance": performance
                }
            else:
                # ดึงข้อมูลของทุก strategies
                all_performance = {}
                
                for name in self.strategies.keys():
                    performance = await self._get_strategy_performance(name)
                    all_performance[name] = performance
                
                return {
                    "success": True,
                    "performance": all_performance
                }
                
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถดึงข้อมูลผลการดำเนินงาน: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_restart_hummingbot(self, payload: Dict) -> Dict:
        """รีสตาร์ท Hummingbot"""
        try:
            # หยุด strategies ทั้งหมด
            for strategy_name in list(self.running_processes.keys()):
                await self._stop_hummingbot_process(strategy_name)
            
            # รอสักครู่
            await asyncio.sleep(5)
            
            self.logger.info("🔄 รีสตาร์ท Hummingbot สำเร็จ")
            return {
                "success": True,
                "message": "รีสตาร์ท Hummingbot สำเร็จ"
            }
            
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถรีสตาร์ท Hummingbot: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_get_logs(self, payload: Dict) -> Dict:
        """ดึง logs"""
        try:
            strategy_name = payload.get("name")
            lines = payload.get("lines", 100)
            
            if strategy_name and strategy_name not in self.strategies:
                return {"success": False, "error": "ไม่พบ strategy"}
            
            if strategy_name:
                # ดึง logs ของ strategy เดียว
                log_file = self.logs_path / f"{strategy_name}.log"
                logs = await self._read_log_file(log_file, lines)
                
                return {
                    "success": True,
                    "strategy": strategy_name,
                    "logs": logs
                }
            else:
                # ดึง logs ทั่วไป
                log_file = self.logs_path / "hummingbot.log"
                logs = await self._read_log_file(log_file, lines)
                
                return {
                    "success": True,
                    "logs": logs
                }
                
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถดึง logs: {e}")
            return {"success": False, "error": str(e)}
    
    # === Helper Methods ===
    
    async def _start_hummingbot_process(self, strategy_name: str) -> bool:
        """เริ่ม Hummingbot process"""
        try:
            if strategy_name in self.running_processes:
                return False
            
            hummingbot_cmd = [
                str(Path(self.hummingbot_path) / "bin" / "hummingbot"),
                "--strategy-file-name", f"{strategy_name}.yml"
            ]
            
            # เริ่ม process
            process = subprocess.Popen(
                hummingbot_cmd,
                cwd=self.hummingbot_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.running_processes[strategy_name] = process
            
            # รอสักครู่เพื่อให้ process เริ่มต้น
            await asyncio.sleep(3)
            
            # ตรวจสอบว่า process ยังทำงานอยู่
            if process.poll() is None:
                return True
            else:
                del self.running_processes[strategy_name]
                return False
                
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถเริ่ม Hummingbot process: {e}")
            return False
    
    async def _stop_hummingbot_process(self, strategy_name: str) -> bool:
        """หยุด Hummingbot process"""
        try:
            if strategy_name not in self.running_processes:
                return True
            
            process = self.running_processes[strategy_name]
            
            # ส่งสัญญาณหยุด
            process.terminate()
            
            # รอให้ process หยุด
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                # ถ้ายังไม่หยุด ให้ kill
                process.kill()
                process.wait()
            
            del self.running_processes[strategy_name]
            return True
            
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถหยุด Hummingbot process: {e}")
            return False
    
    async def _send_hummingbot_command(self, strategy_name: str, command: str) -> bool:
        """ส่งคำสั่งไปยัง Hummingbot process"""
        try:
            if strategy_name not in self.running_processes:
                return False
            
            process = self.running_processes[strategy_name]
            
            if process.poll() is not None:
                return False
            
            # ส่งคำสั่ง
            process.stdin.write(f"{command}\n")
            process.stdin.flush()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถส่งคำสั่งไปยัง Hummingbot: {e}")
            return False
    
    async def _get_strategy_performance(self, strategy_name: str) -> Dict:
        """ดึงข้อมูลผลการดำเนินงานของ strategy"""
        try:
            strategy = self.strategies[strategy_name]
            
            # อ่านข้อมูลจาก log files หรือ database
            # สำหรับตัวอย่างนี้ จะใช้ข้อมูลจาก strategy object
            
            performance = strategy.performance.copy()
            
            # คำนวณ win rate
            if performance["total_trades"] > 0:
                performance["win_rate"] = (performance["profitable_trades"] / performance["total_trades"]) * 100
            
            # คำนวณระยะเวลาทำงาน
            if performance["start_time"] and performance["end_time"]:
                duration = performance["end_time"] - performance["start_time"]
                performance["duration_hours"] = duration.total_seconds() / 3600
            elif performance["start_time"]:
                duration = datetime.now() - performance["start_time"]
                performance["duration_hours"] = duration.total_seconds() / 3600
            
            return performance
            
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถดึงข้อมูลผลการดำเนินงาน: {e}")
            return {}
    
    async def _read_log_file(self, log_file: Path, lines: int = 100) -> List[str]:
        """อ่านไฟล์ log"""
        try:
            if not log_file.exists():
                return []
            
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
            
            # ดึงบรรทัดสุดท้าย
            return all_lines[-lines:] if len(all_lines) > lines else all_lines
            
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถอ่านไฟล์ log: {e}")
            return []
    
    async def start_monitoring(self):
        """เริ่มการตรวจสอบระบบ"""
        self.logger.info("🔍 เริ่มการตรวจสอบระบบ")
        
        while True:
            try:
                # ตรวจสอบสถานะ strategies
                await self._monitor_strategies()
                
                # ส่งข้อมูลสถานะผ่าน MQTT
                await self._publish_status_update()
                
                # ส่ง heartbeat
                self._publish_mqtt(
                    f"{self.mqtt_topics['status']}/heartbeat",
                    {
                        "timestamp": datetime.now(),
                        "status": "alive",
                        "strategies_count": len(self.strategies),
                        "running_count": len([s for s in self.strategies.values() if s.status == "running"])
                    }
                )
                
                # รอ 30 วินาที
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"❌ ข้อผิดพลาดในการตรวจสอบระบบ: {e}")
                await asyncio.sleep(60)
    
    async def _monitor_strategies(self):
        """ตรวจสอบสถานะ strategies"""
        for strategy_name, strategy in self.strategies.items():
            try:
                # ตรวจสอบ process
                if strategy_name in self.running_processes:
                    process = self.running_processes[strategy_name]
                    
                    if process.poll() is not None:
                        # Process หยุดทำงาน
                        strategy.status = "error"
                        del self.running_processes[strategy_name]
                        
                        self.logger.warning(f"⚠️ Strategy {strategy_name} หยุดทำงานโดยไม่คาดคิด")
                        
                        # ส่งการแจ้งเตือน
                        self._publish_mqtt(
                            f"{self.mqtt_topics['logs']}/error",
                            {
                                "strategy": strategy_name,
                                "message": "Strategy หยุดทำงานโดยไม่คาดคิด",
                                "timestamp": datetime.now()
                            }
                        )
                
            except Exception as e:
                self.logger.error(f"❌ ข้อผิดพลาดในการตรวจสอบ strategy {strategy_name}: {e}")
    
    async def _publish_status_update(self):
        """ส่งข้อมูลสถานะอัปเดต"""
        try:
            status_data = {
                "timestamp": datetime.now(),
                "strategies": {}
            }
            
            for strategy_name, strategy in self.strategies.items():
                status_data["strategies"][strategy_name] = {
                    "status": strategy.status,
                    "last_updated": strategy.last_updated,
                    "performance": strategy.performance
                }
            
            self._publish_mqtt(
                f"{self.mqtt_topics['status']}/update",
                status_data
            )
            
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถส่งข้อมูลสถานะอัปเดต: {e}")
    
    async def shutdown(self):
        """ปิดระบบ"""
        self.logger.info("🛑 ปิดระบบ Hummingbot MQTT Manager")
        
        # หยุด strategies ทั้งหมด
        for strategy_name in list(self.running_processes.keys()):
            await self._stop_hummingbot_process(strategy_name)
        
        # ปิดการเชื่อมต่อ MQTT
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        
        self.logger.info("✅ ปิดระบบเรียบร้อย")

# === Main function ===
async def run_hummingbot_manager():
    """รัน Hummingbot MQTT Manager"""
    manager = HummingbotMQTTManager()
    
    try:
        if await manager.initialize():
            # เริ่มการตรวจสอบระบบ
            await manager.start_monitoring()
        else:
            print("❌ ไม่สามารถเริ่มต้น Hummingbot MQTT Manager ได้")
    except KeyboardInterrupt:
        print("\n⏹️ หยุดการทำงานโดยผู้ใช้")
    finally:
        await manager.shutdown()

# === Run ===
if __name__ == "__main__":
    asyncio.run(run_hummingbot_manager()) 