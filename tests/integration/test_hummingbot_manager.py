import pytest
import asyncio
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
import importlib.util

import sys
import os

# Import โดยตรงจากไฟล์เพื่อหลีกเลี่ยง __init__.py
def import_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Import hummingbot_manager โดยตรง
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
hummingbot_manager_path = os.path.join(parent_dir, "bots", "hummingbot_manager.py")
hummingbot_manager = import_from_file("hummingbot_manager", hummingbot_manager_path)

HummingbotMQTTManager = hummingbot_manager.HummingbotMQTTManager
HummingbotStrategy = hummingbot_manager.HummingbotStrategy


class TestHummingbotStrategy:
    """Test cases สำหรับ HummingbotStrategy dataclass"""
    
    def test_strategy_creation(self):
        """ทดสอบการสร้าง strategy object"""
        strategy = HummingbotStrategy(
            name="test_strategy",
            strategy_type="pure_market_making",
            exchange="binance",
            trading_pair="BTC-USDT",
            config={"bid_spread": 0.001}
        )
        
        assert strategy.name == "test_strategy"
        assert strategy.strategy_type == "pure_market_making"
        assert strategy.exchange == "binance"
        assert strategy.trading_pair == "BTC-USDT"
        assert strategy.status == "stopped"
        assert strategy.created_at is not None
        assert strategy.last_updated is not None
        assert strategy.performance is not None
        assert strategy.performance["total_trades"] == 0
    
    def test_strategy_performance_initialization(self):
        """ทดสอบการเริ่มต้น performance data"""
        strategy = HummingbotStrategy(
            name="test",
            strategy_type="pure_market_making",
            exchange="binance",
            trading_pair="BTC-USDT",
            config={}
        )
        
        expected_performance = {
            "total_trades": 0,
            "profitable_trades": 0,
            "total_pnl": 0.0,
            "win_rate": 0.0,
            "start_time": None,
            "end_time": None
        }
        
        assert strategy.performance == expected_performance


class TestHummingbotMQTTManager:
    """Test cases สำหรับ HummingbotMQTTManager"""
    
    @pytest.fixture
    def temp_config(self):
        """สร้าง temporary config file"""
        config_data = {
            "mqtt": {
                "host": "localhost",
                "port": 1883,
                "username": None,
                "password": None
            },
            "hummingbot": {
                "path": "/tmp/test_hummingbot",
                "config_path": "/tmp/test_hummingbot/conf",
                "logs_path": "/tmp/test_hummingbot/logs",
                "strategies_path": "/tmp/test_hummingbot/conf/strategies"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name
        
        yield config_path
        
        # Cleanup
        os.unlink(config_path)
    
    @pytest.fixture
    def temp_hummingbot_dir(self):
        """สร้าง temporary Hummingbot directory structure"""
        temp_dir = tempfile.mkdtemp()
        hummingbot_path = Path(temp_dir) / "hummingbot"
        
        # สร้างโครงสร้างโฟลเดอร์
        (hummingbot_path / "bin").mkdir(parents=True)
        (hummingbot_path / "conf" / "strategies").mkdir(parents=True)
        (hummingbot_path / "logs").mkdir(parents=True)
        
        # สร้างไฟล์ hummingbot executable (mock)
        executable = hummingbot_path / "bin" / "hummingbot"
        executable.write_text("#!/bin/bash\necho 'Mock Hummingbot'")
        executable.chmod(0o755)
        
        yield str(hummingbot_path)
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def manager(self, temp_config, temp_hummingbot_dir):
        """สร้าง HummingbotMQTTManager instance สำหรับ testing"""
        # อัปเดต config ให้ใช้ temp directory
        with open(temp_config, 'r') as f:
            config = json.load(f)
        
        config["hummingbot"]["path"] = temp_hummingbot_dir
        config["hummingbot"]["strategies_path"] = f"{temp_hummingbot_dir}/conf/strategies"
        config["hummingbot"]["logs_path"] = f"{temp_hummingbot_dir}/logs"
        
        with open(temp_config, 'w') as f:
            json.dump(config, f)
        
        return HummingbotMQTTManager(temp_config)
    
    def test_manager_initialization(self, manager):
        """ทดสอบการเริ่มต้น manager"""
        assert manager.config_path is not None
        assert manager.config is not None
        assert manager.logger is not None
        assert manager.strategies == {}
        assert manager.running_processes == {}
        assert manager.command_handlers is not None
        assert not manager.is_connected
    
    def test_load_config(self, temp_config):
        """ทดสอบการโหลด config"""
        manager = HummingbotMQTTManager(temp_config)
        
        assert "mqtt" in manager.config
        assert "hummingbot" in manager.config
        assert manager.config["mqtt"]["host"] == "localhost"
        assert manager.config["mqtt"]["port"] == 1883
    
    def test_load_config_file_not_found(self):
        """ทดสอบการโหลด config เมื่อไฟล์ไม่พบ"""
        manager = HummingbotMQTTManager("nonexistent.json")
        assert manager.config == {}
    
    def test_check_hummingbot_installation_success(self, manager):
        """ทดสอบการตรวจสอบ Hummingbot installation (สำเร็จ)"""
        result = manager._check_hummingbot_installation()
        assert result is True
    
    def test_check_hummingbot_installation_failure(self, temp_config):
        """ทดสอบการตรวจสอบ Hummingbot installation (ล้มเหลว)"""
        # ใช้ path ที่ไม่มี hummingbot executable
        with open(temp_config, 'r') as f:
            config = json.load(f)
        
        config["hummingbot"]["path"] = "/nonexistent/path"
        
        with open(temp_config, 'w') as f:
            json.dump(config, f)
        
        manager = HummingbotMQTTManager(temp_config)
        result = manager._check_hummingbot_installation()
        assert result is False
    
    @pytest.mark.asyncio
    async def test_load_existing_strategies(self, manager):
        """ทดสอบการโหลด strategies ที่มีอยู่"""
        # สร้างไฟล์ strategy ตัวอย่าง
        strategy_config = {
            "strategy": "pure_market_making",
            "exchange": "binance",
            "trading_pair": "BTC-USDT",
            "bid_spread": 0.001,
            "ask_spread": 0.001
        }
        
        strategy_file = manager.strategies_path / "test_strategy.yml"
        with open(strategy_file, 'w') as f:
            import yaml
            yaml.dump(strategy_config, f)
        
        await manager._load_existing_strategies()
        
        assert "test_strategy" in manager.strategies
        strategy = manager.strategies["test_strategy"]
        assert strategy.name == "test_strategy"
        assert strategy.strategy_type == "pure_market_making"
        assert strategy.exchange == "binance"
        assert strategy.trading_pair == "BTC-USDT"
        assert strategy.status == "stopped"
    
    @pytest.mark.asyncio
    async def test_handle_create_strategy_success(self, manager):
        """ทดสอบการสร้าง strategy (สำเร็จ)"""
        payload = {
            "name": "new_strategy",
            "strategy_type": "pure_market_making",
            "exchange": "binance",
            "trading_pair": "ETH-USDT",
            "config": {
                "bid_spread": 0.002,
                "ask_spread": 0.002
            }
        }
        
        result = await manager._handle_create_strategy(payload)
        
        assert result["success"] is True
        assert "new_strategy" in manager.strategies
        
        # ตรวจสอบว่าไฟล์ config ถูกสร้าง
        config_file = manager.strategies_path / "new_strategy.yml"
        assert config_file.exists()
    
    @pytest.mark.asyncio
    async def test_handle_create_strategy_missing_data(self, manager):
        """ทดสอบการสร้าง strategy (ข้อมูลไม่ครบ)"""
        payload = {
            "name": "incomplete_strategy",
            "strategy_type": "pure_market_making"
            # ขาด exchange และ trading_pair
        }
        
        result = await manager._handle_create_strategy(payload)
        
        assert result["success"] is False
        assert "ข้อมูลไม่ครบถ้วน" in result["error"]
    
    @pytest.mark.asyncio
    async def test_handle_create_strategy_duplicate(self, manager):
        """ทดสอบการสร้าง strategy (ชื่อซ้ำ)"""
        # สร้าง strategy แรก
        manager.strategies["existing_strategy"] = HummingbotStrategy(
            name="existing_strategy",
            strategy_type="pure_market_making",
            exchange="binance",
            trading_pair="BTC-USDT",
            config={}
        )
        
        payload = {
            "name": "existing_strategy",
            "strategy_type": "pure_market_making",
            "exchange": "binance",
            "trading_pair": "ETH-USDT",
            "config": {}
        }
        
        result = await manager._handle_create_strategy(payload)
        
        assert result["success"] is False
        assert "มีอยู่แล้ว" in result["error"]
    
    @pytest.mark.asyncio
    async def test_handle_get_strategies(self, manager):
        """ทดสอบการดึงรายการ strategies"""
        # เพิ่ม strategies ตัวอย่าง
        manager.strategies["strategy1"] = HummingbotStrategy(
            name="strategy1",
            strategy_type="pure_market_making",
            exchange="binance",
            trading_pair="BTC-USDT",
            config={}
        )
        
        manager.strategies["strategy2"] = HummingbotStrategy(
            name="strategy2",
            strategy_type="arbitrage",
            exchange="kucoin",
            trading_pair="ETH-USDT",
            config={}
        )
        
        result = await manager._handle_get_strategies({})
        
        assert result["success"] is True
        assert result["total"] == 2
        assert len(result["strategies"]) == 2
    
    @pytest.mark.asyncio
    async def test_handle_get_strategy_status_success(self, manager):
        """ทดสอบการดึงสถานะ strategy (สำเร็จ)"""
        # เพิ่ม strategy ตัวอย่าง
        manager.strategies["test_strategy"] = HummingbotStrategy(
            name="test_strategy",
            strategy_type="pure_market_making",
            exchange="binance",
            trading_pair="BTC-USDT",
            config={}
        )
        
        payload = {"name": "test_strategy"}
        result = await manager._handle_get_strategy_status(payload)
        
        assert result["success"] is True
        assert result["strategy"]["name"] == "test_strategy"
        assert result["strategy"]["status"] == "stopped"
    
    @pytest.mark.asyncio
    async def test_handle_get_strategy_status_not_found(self, manager):
        """ทดสอบการดึงสถานะ strategy (ไม่พบ)"""
        payload = {"name": "nonexistent_strategy"}
        result = await manager._handle_get_strategy_status(payload)
        
        assert result["success"] is False
        assert "ไม่พบ strategy" in result["error"]
    
    @pytest.mark.asyncio
    async def test_handle_delete_strategy_success(self, manager):
        """ทดสอบการลบ strategy (สำเร็จ)"""
        # สร้าง strategy และไฟล์ config
        strategy_name = "delete_test_strategy"
        manager.strategies[strategy_name] = HummingbotStrategy(
            name=strategy_name,
            strategy_type="pure_market_making",
            exchange="binance",
            trading_pair="BTC-USDT",
            config={}
        )
        
        config_file = manager.strategies_path / f"{strategy_name}.yml"
        config_file.write_text("test config")
        
        payload = {"name": strategy_name}
        result = await manager._handle_delete_strategy(payload)
        
        assert result["success"] is True
        assert strategy_name not in manager.strategies
        assert not config_file.exists()
    
    @pytest.mark.asyncio
    async def test_handle_update_strategy_config_success(self, manager):
        """ทดสอบการอัปเดต strategy config (สำเร็จ)"""
        # สร้าง strategy
        strategy_name = "update_test_strategy"
        manager.strategies[strategy_name] = HummingbotStrategy(
            name=strategy_name,
            strategy_type="pure_market_making",
            exchange="binance",
            trading_pair="BTC-USDT",
            config={"bid_spread": 0.001}
        )
        
        payload = {
            "name": strategy_name,
            "config": {
                "bid_spread": 0.002,
                "ask_spread": 0.002
            }
        }
        
        result = await manager._handle_update_strategy_config(payload)
        
        assert result["success"] is True
        strategy = manager.strategies[strategy_name]
        assert strategy.config["bid_spread"] == 0.002
        assert strategy.config["ask_spread"] == 0.002
    
    @pytest.mark.asyncio
    async def test_handle_update_strategy_config_running_strategy(self, manager):
        """ทดสอบการอัปเดต config ของ strategy ที่กำลังทำงาน"""
        # สร้าง strategy ที่กำลังทำงาน
        strategy_name = "running_strategy"
        strategy = HummingbotStrategy(
            name=strategy_name,
            strategy_type="pure_market_making",
            exchange="binance",
            trading_pair="BTC-USDT",
            config={}
        )
        strategy.status = "running"
        manager.strategies[strategy_name] = strategy
        
        payload = {
            "name": strategy_name,
            "config": {"bid_spread": 0.002}
        }
        
        result = await manager._handle_update_strategy_config(payload)
        
        assert result["success"] is False
        assert "ไม่สามารถแก้ไข config ขณะ strategy ทำงานอยู่" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_strategy_performance(self, manager):
        """ทดสอบการดึงข้อมูลผลการดำเนินงาน"""
        # สร้าง strategy พร้อม performance data
        strategy = HummingbotStrategy(
            name="perf_test_strategy",
            strategy_type="pure_market_making",
            exchange="binance",
            trading_pair="BTC-USDT",
            config={}
        )
        
        strategy.performance = {
            "total_trades": 10,
            "profitable_trades": 7,
            "total_pnl": 150.50,
            "win_rate": 0.0,
            "start_time": datetime.now(),
            "end_time": None
        }
        
        manager.strategies["perf_test_strategy"] = strategy
        
        performance = await manager._get_strategy_performance("perf_test_strategy")
        
        assert performance["total_trades"] == 10
        assert performance["profitable_trades"] == 7
        assert performance["total_pnl"] == 150.50
        assert performance["win_rate"] == 70.0  # คำนวณจาก profitable_trades/total_trades
        assert "duration_hours" in performance
    
    @pytest.mark.asyncio
    async def test_read_log_file_exists(self, manager):
        """ทดสอบการอ่านไฟล์ log (ไฟล์มีอยู่)"""
        # สร้างไฟล์ log ตัวอย่าง
        log_file = manager.logs_path / "test.log"
        log_content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n"
        log_file.write_text(log_content)
        
        logs = await manager._read_log_file(log_file, 3)
        
        assert len(logs) == 3
        assert logs[-1].strip() == "Line 5"
        assert logs[-2].strip() == "Line 4"
        assert logs[-3].strip() == "Line 3"
    
    @pytest.mark.asyncio
    async def test_read_log_file_not_exists(self, manager):
        """ทดสอบการอ่านไฟล์ log (ไฟล์ไม่มีอยู่)"""
        log_file = manager.logs_path / "nonexistent.log"
        logs = await manager._read_log_file(log_file, 10)
        
        assert logs == []
    
    @patch('subprocess.Popen')
    @pytest.mark.asyncio
    async def test_start_hummingbot_process_success(self, mock_popen, manager):
        """ทดสอบการเริ่ม Hummingbot process (สำเร็จ)"""
        # Mock process ที่ทำงานอยู่
        mock_process = Mock()
        mock_process.poll.return_value = None  # Process ยังทำงานอยู่
        mock_popen.return_value = mock_process
        
        result = await manager._start_hummingbot_process("test_strategy")
        
        assert result is True
        assert "test_strategy" in manager.running_processes
        mock_popen.assert_called_once()
    
    @patch('subprocess.Popen')
    @pytest.mark.asyncio
    async def test_start_hummingbot_process_failure(self, mock_popen, manager):
        """ทดสอบการเริ่ม Hummingbot process (ล้มเหลว)"""
        # Mock process ที่หยุดทำงานทันที
        mock_process = Mock()
        mock_process.poll.return_value = 1  # Process หยุดแล้ว
        mock_popen.return_value = mock_process
        
        result = await manager._start_hummingbot_process("test_strategy")
        
        assert result is False
        assert "test_strategy" not in manager.running_processes
    
    @pytest.mark.asyncio
    async def test_stop_hummingbot_process_success(self, manager):
        """ทดสอบการหยุด Hummingbot process (สำเร็จ)"""
        # Mock running process
        mock_process = Mock()
        mock_process.terminate = Mock()
        mock_process.wait = Mock()
        manager.running_processes["test_strategy"] = mock_process
        
        result = await manager._stop_hummingbot_process("test_strategy")
        
        assert result is True
        assert "test_strategy" not in manager.running_processes
        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_stop_hummingbot_process_not_running(self, manager):
        """ทดสอบการหยุด process ที่ไม่ได้ทำงาน"""
        result = await manager._stop_hummingbot_process("nonexistent_strategy")
        assert result is True  # ถือว่าสำเร็จเพราะ process ไม่ได้ทำงานอยู่แล้ว
    
    @pytest.mark.asyncio
    async def test_send_hummingbot_command_success(self, manager):
        """ทดสอบการส่งคำสั่งไปยัง Hummingbot process (สำเร็จ)"""
        # Mock running process
        mock_process = Mock()
        mock_process.poll.return_value = None  # Process ยังทำงานอยู่
        mock_process.stdin = Mock()
        mock_process.stdin.write = Mock()
        mock_process.stdin.flush = Mock()
        manager.running_processes["test_strategy"] = mock_process
        
        result = await manager._send_hummingbot_command("test_strategy", "start")
        
        assert result is True
        mock_process.stdin.write.assert_called_once_with("start\n")
        mock_process.stdin.flush.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_hummingbot_command_process_not_running(self, manager):
        """ทดสอบการส่งคำสั่งไปยัง process ที่ไม่ได้ทำงาน"""
        result = await manager._send_hummingbot_command("nonexistent_strategy", "start")
        assert result is False
    
    def test_publish_mqtt_success(self, manager):
        """ทดสอบการส่งข้อความผ่าน MQTT (สำเร็จ)"""
        # Mock MQTT client
        mock_client = Mock()
        mock_client.publish = Mock()
        manager.mqtt_client = mock_client
        manager.is_connected = True
        
        payload = {"test": "data"}
        manager._publish_mqtt("test/topic", payload)
        
        mock_client.publish.assert_called_once()
        args, kwargs = mock_client.publish.call_args
        assert args[0] == "test/topic"
        assert json.loads(args[1]) == payload
    
    def test_publish_mqtt_not_connected(self, manager):
        """ทดสอบการส่งข้อความผ่าน MQTT (ไม่ได้เชื่อมต่อ)"""
        manager.mqtt_client = None
        manager.is_connected = False
        
        # ไม่ควรเกิด exception
        manager._publish_mqtt("test/topic", {"test": "data"})


class TestIntegration:
    """Integration tests สำหรับระบบทั้งหมด"""
    
    @pytest.fixture
    def mock_mqtt_client(self):
        """Mock MQTT client สำหรับ integration testing"""
        with patch('paho.mqtt.client.Client') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            yield mock_client
    
    @pytest.mark.asyncio
    async def test_full_strategy_lifecycle(self, manager, mock_mqtt_client):
        """ทดสอบ lifecycle ของ strategy ตั้งแต่สร้างจนลบ"""
        # Mock MQTT client
        manager.mqtt_client = mock_mqtt_client
        manager.is_connected = True
        
        # 1. สร้าง strategy
        create_payload = {
            "name": "lifecycle_test",
            "strategy_type": "pure_market_making",
            "exchange": "binance",
            "trading_pair": "BTC-USDT",
            "config": {"bid_spread": 0.001}
        }
        
        result = await manager._handle_create_strategy(create_payload)
        assert result["success"] is True
        assert "lifecycle_test" in manager.strategies
        
        # 2. ตรวจสอบสถานะ
        status_payload = {"name": "lifecycle_test"}
        result = await manager._handle_get_strategy_status(status_payload)
        assert result["success"] is True
        assert result["strategy"]["status"] == "stopped"
        
        # 3. อัปเดต config
        update_payload = {
            "name": "lifecycle_test",
            "config": {"bid_spread": 0.002}
        }
        result = await manager._handle_update_strategy_config(update_payload)
        assert result["success"] is True
        
        # 4. ดูผลการดำเนินงาน
        perf_payload = {"name": "lifecycle_test"}
        result = await manager._handle_get_performance(perf_payload)
        assert result["success"] is True
        
        # 5. ลบ strategy
        delete_payload = {"name": "lifecycle_test"}
        result = await manager._handle_delete_strategy(delete_payload)
        assert result["success"] is True
        assert "lifecycle_test" not in manager.strategies


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 