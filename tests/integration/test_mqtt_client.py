import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
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

# Import mqtt_client_example โดยตรง
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
mqtt_client_path = os.path.join(parent_dir, "bots", "mqtt_client_example.py")
mqtt_client_module = import_from_file("mqtt_client_example", mqtt_client_path)

HummingbotMQTTClient = mqtt_client_module.HummingbotMQTTClient

class TestHummingbotMQTTClient:
    """Test cases สำหรับ HummingbotMQTTClient"""
    
    @pytest.fixture
    def mqtt_config(self):
        """การตั้งค่า MQTT สำหรับ testing"""
        return {
            "host": "localhost",
            "port": 1883,
            "username": None,
            "password": None
        }
    
    @pytest.fixture
    def client(self, mqtt_config):
        """สร้าง HummingbotMQTTClient instance สำหรับ testing"""
        return HummingbotMQTTClient(mqtt_config)
    
    def test_client_initialization(self, client):
        """ทดสอบการเริ่มต้น client"""
        assert client.mqtt_config is not None
        assert client.mqtt_client is None
        assert client.is_connected is False
        assert client.logger is not None
        assert client.topics is not None
        assert client.responses == {}
        assert client.response_timeout == 30
    
    def test_topics_configuration(self, client):
        """ทดสอบการตั้งค่า MQTT topics"""
        expected_topics = {
            "command": "hummingbot/command",
            "status": "hummingbot/status",
            "strategy": "hummingbot/strategy",
            "performance": "hummingbot/performance",
            "logs": "hummingbot/logs"
        }
        
        assert client.topics == expected_topics
    
    @patch('paho.mqtt.client.Client')
    @pytest.mark.asyncio
    async def test_connect_success(self, mock_client_class, client):
        """ทดสอบการเชื่อมต่อ MQTT (สำเร็จ)"""
        # Mock MQTT client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock การเชื่อมต่อสำเร็จ
        def mock_on_connect(callback):
            client._on_connect(None, None, None, 0)  # rc=0 หมายถึงสำเร็จ
        
        mock_client.on_connect = mock_on_connect
        
        result = await client.connect()
        
        assert result is True
        assert client.is_connected is True
        mock_client.connect.assert_called_once_with("localhost", 1883, 60)
        mock_client.loop_start.assert_called_once()
    
    @patch('paho.mqtt.client.Client')
    @pytest.mark.asyncio
    async def test_connect_failure(self, mock_client_class, client):
        """ทดสอบการเชื่อมต่อ MQTT (ล้มเหลว)"""
        # Mock MQTT client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock การเชื่อมต่อล้มเหลว
        def mock_on_connect(callback):
            client._on_connect(None, None, None, 1)  # rc=1 หมายถึงล้มเหลว
        
        mock_client.on_connect = mock_on_connect
        
        result = await client.connect()
        
        assert result is False
        assert client.is_connected is False
    
    @patch('paho.mqtt.client.Client')
    @pytest.mark.asyncio
    async def test_connect_with_authentication(self, mock_client_class):
        """ทดสอบการเชื่อมต่อ MQTT พร้อม authentication"""
        mqtt_config = {
            "host": "localhost",
            "port": 1883,
            "username": "test_user",
            "password": "test_pass"
        }
        
        client = HummingbotMQTTClient(mqtt_config)
        
        # Mock MQTT client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock การเชื่อมต่อสำเร็จ
        def mock_on_connect(callback):
            client._on_connect(None, None, None, 0)
        
        mock_client.on_connect = mock_on_connect
        
        await client.connect()
        
        mock_client.username_pw_set.assert_called_once_with("test_user", "test_pass")
    
    def test_on_connect_success(self, client):
        """ทดสอบ callback เมื่อเชื่อมต่อสำเร็จ"""
        mock_client = Mock()
        
        client._on_connect(mock_client, None, None, 0)
        
        assert client.is_connected is True
        mock_client.subscribe.assert_any_call("hummingbot/status/+")
        mock_client.subscribe.assert_any_call("hummingbot/logs/+")
    
    def test_on_connect_failure(self, client):
        """ทดสอบ callback เมื่อเชื่อมต่อล้มเหลว"""
        mock_client = Mock()
        
        client._on_connect(mock_client, None, None, 1)
        
        assert client.is_connected is False
        mock_client.subscribe.assert_not_called()
    
    def test_on_disconnect(self, client):
        """ทดสอบ callback เมื่อขาดการเชื่อมต่อ"""
        client.is_connected = True
        
        client._on_disconnect(None, None, None)
        
        assert client.is_connected is False
    
    def test_on_message_heartbeat(self, client):
        """ทดสอบการจัดการข้อความ heartbeat"""
        mock_msg = Mock()
        mock_msg.topic = "hummingbot/status/heartbeat"
        mock_msg.payload.decode.return_value = json.dumps({
            "status": "alive",
            "strategies_count": 5,
            "running_count": 3
        })
        
        # Mock logger เพื่อตรวจสอบการเรียกใช้
        client.logger = Mock()
        
        client._on_message(None, None, mock_msg)
        
        # ตรวจสอบว่า heartbeat ถูกจัดการ
        client.logger.info.assert_called()
    
    def test_on_message_status_response(self, client):
        """ทดสอบการจัดการ response จาก status topic"""
        mock_msg = Mock()
        mock_msg.topic = "hummingbot/status/create_strategy"
        response_data = {"success": True, "message": "Strategy created"}
        mock_msg.payload.decode.return_value = json.dumps(response_data)
        
        client._on_message(None, None, mock_msg)
        
        # ตรวจสอบว่า response ถูกเก็บไว้
        assert "create_strategy" in client.responses
        assert client.responses["create_strategy"] == response_data
    
    def test_on_message_error(self, client):
        """ทดสอบการจัดการข้อความ error"""
        mock_msg = Mock()
        mock_msg.topic = "hummingbot/logs/error"
        mock_msg.payload.decode.return_value = json.dumps({
            "strategy": "test_strategy",
            "message": "Error occurred",
            "timestamp": "2024-01-01T12:00:00"
        })
        
        # Mock logger เพื่อตรวจสอบการเรียกใช้
        client.logger = Mock()
        
        client._on_message(None, None, mock_msg)
        
        # ตรวจสอบว่า error ถูกจัดการ
        client.logger.error.assert_called()
    
    def test_publish_command_success(self, client):
        """ทดสอบการส่งคำสั่งผ่าน MQTT (สำเร็จ)"""
        # Mock MQTT client
        mock_client = Mock()
        client.mqtt_client = mock_client
        client.is_connected = True
        
        payload = {"name": "test_strategy"}
        result = client._publish_command("start_strategy", payload)
        
        assert result is True
        mock_client.publish.assert_called_once()
        
        # ตรวจสอบ topic และ payload
        args, kwargs = mock_client.publish.call_args
        assert args[0] == "hummingbot/command/start_strategy"
        assert json.loads(args[1]) == payload
    
    def test_publish_command_not_connected(self, client):
        """ทดสอบการส่งคำสั่งเมื่อไม่ได้เชื่อมต่อ"""
        client.is_connected = False
        
        result = client._publish_command("start_strategy", {})
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_wait_for_response_success(self, client):
        """ทดสอบการรอ response (สำเร็จ)"""
        # เพิ่ม response ลงใน responses dict
        response_data = {"success": True}
        client.responses["test_command"] = response_data
        
        result = await client._wait_for_response("test_command")
        
        assert result == response_data
        assert "test_command" not in client.responses  # ควรถูกลบออกหลังใช้
    
    @pytest.mark.asyncio
    async def test_wait_for_response_timeout(self, client):
        """ทดสอบการรอ response (timeout)"""
        # ตั้งค่า timeout สั้นๆ สำหรับ testing
        client.response_timeout = 1
        
        result = await client._wait_for_response("nonexistent_command")
        
        assert result["success"] is False
        assert "Timeout" in result["error"]
    
    @pytest.mark.asyncio
    async def test_create_strategy(self, client):
        """ทดสอบการสร้าง strategy"""
        # Mock การส่งคำสั่งและรับ response
        client._publish_command = Mock(return_value=True)
        client._wait_for_response = AsyncMock(return_value={"success": True})
        
        result = await client.create_strategy(
            name="test_strategy",
            strategy_type="pure_market_making",
            exchange="binance",
            trading_pair="BTC-USDT",
            config={"bid_spread": 0.001}
        )
        
        assert result["success"] is True
        client._publish_command.assert_called_once_with("create_strategy", {
            "name": "test_strategy",
            "strategy_type": "pure_market_making",
            "exchange": "binance",
            "trading_pair": "BTC-USDT",
            "config": {"bid_spread": 0.001}
        })
    
    @pytest.mark.asyncio
    async def test_start_strategy(self, client):
        """ทดสอบการเริ่ม strategy"""
        client._publish_command = Mock(return_value=True)
        client._wait_for_response = AsyncMock(return_value={"success": True})
        
        result = await client.start_strategy("test_strategy")
        
        assert result["success"] is True
        client._publish_command.assert_called_once_with("start_strategy", {
            "name": "test_strategy"
        })
    
    @pytest.mark.asyncio
    async def test_stop_strategy(self, client):
        """ทดสอบการหยุด strategy"""
        client._publish_command = Mock(return_value=True)
        client._wait_for_response = AsyncMock(return_value={"success": True})
        
        result = await client.stop_strategy("test_strategy")
        
        assert result["success"] is True
        client._publish_command.assert_called_once_with("stop_strategy", {
            "name": "test_strategy"
        })
    
    @pytest.mark.asyncio
    async def test_pause_strategy(self, client):
        """ทดสอบการหยุดชั่วคราว strategy"""
        client._publish_command = Mock(return_value=True)
        client._wait_for_response = AsyncMock(return_value={"success": True})
        
        result = await client.pause_strategy("test_strategy")
        
        assert result["success"] is True
        client._publish_command.assert_called_once_with("pause_strategy", {
            "name": "test_strategy"
        })
    
    @pytest.mark.asyncio
    async def test_resume_strategy(self, client):
        """ทดสอบการเริ่มต่อ strategy"""
        client._publish_command = Mock(return_value=True)
        client._wait_for_response = AsyncMock(return_value={"success": True})
        
        result = await client.resume_strategy("test_strategy")
        
        assert result["success"] is True
        client._publish_command.assert_called_once_with("resume_strategy", {
            "name": "test_strategy"
        })
    
    @pytest.mark.asyncio
    async def test_delete_strategy(self, client):
        """ทดสอบการลบ strategy"""
        client._publish_command = Mock(return_value=True)
        client._wait_for_response = AsyncMock(return_value={"success": True})
        
        result = await client.delete_strategy("test_strategy")
        
        assert result["success"] is True
        client._publish_command.assert_called_once_with("delete_strategy", {
            "name": "test_strategy"
        })
    
    @pytest.mark.asyncio
    async def test_get_strategies(self, client):
        """ทดสอบการดึงรายการ strategies"""
        client._publish_command = Mock(return_value=True)
        client._wait_for_response = AsyncMock(return_value={
            "success": True,
            "strategies": [],
            "total": 0
        })
        
        result = await client.get_strategies()
        
        assert result["success"] is True
        client._publish_command.assert_called_once_with("get_strategies", {})
    
    @pytest.mark.asyncio
    async def test_get_strategy_status(self, client):
        """ทดสอบการดึงสถานะ strategy"""
        client._publish_command = Mock(return_value=True)
        client._wait_for_response = AsyncMock(return_value={
            "success": True,
            "strategy": {"name": "test_strategy", "status": "running"}
        })
        
        result = await client.get_strategy_status("test_strategy")
        
        assert result["success"] is True
        client._publish_command.assert_called_once_with("get_strategy_status", {
            "name": "test_strategy"
        })
    
    @pytest.mark.asyncio
    async def test_update_strategy_config(self, client):
        """ทดสอบการอัปเดต strategy config"""
        client._publish_command = Mock(return_value=True)
        client._wait_for_response = AsyncMock(return_value={"success": True})
        
        config = {"bid_spread": 0.002}
        result = await client.update_strategy_config("test_strategy", config)
        
        assert result["success"] is True
        client._publish_command.assert_called_once_with("update_strategy_config", {
            "name": "test_strategy",
            "config": config
        })
    
    @pytest.mark.asyncio
    async def test_get_performance_single_strategy(self, client):
        """ทดสอบการดึงข้อมูลผลการดำเนินงานของ strategy เดียว"""
        client._publish_command = Mock(return_value=True)
        client._wait_for_response = AsyncMock(return_value={
            "success": True,
            "strategy": "test_strategy",
            "performance": {"total_trades": 10}
        })
        
        result = await client.get_performance("test_strategy")
        
        assert result["success"] is True
        client._publish_command.assert_called_once_with("get_performance", {
            "name": "test_strategy"
        })
    
    @pytest.mark.asyncio
    async def test_get_performance_all_strategies(self, client):
        """ทดสอบการดึงข้อมูลผลการดำเนินงานของ strategies ทั้งหมด"""
        client._publish_command = Mock(return_value=True)
        client._wait_for_response = AsyncMock(return_value={
            "success": True,
            "performance": {}
        })
        
        result = await client.get_performance()
        
        assert result["success"] is True
        client._publish_command.assert_called_once_with("get_performance", {})
    
    @pytest.mark.asyncio
    async def test_restart_hummingbot(self, client):
        """ทดสอบการรีสตาร์ท Hummingbot"""
        client._publish_command = Mock(return_value=True)
        client._wait_for_response = AsyncMock(return_value={"success": True})
        
        result = await client.restart_hummingbot()
        
        assert result["success"] is True
        client._publish_command.assert_called_once_with("restart_hummingbot", {})
    
    @pytest.mark.asyncio
    async def test_get_logs_single_strategy(self, client):
        """ทดสอบการดึง logs ของ strategy เดียว"""
        client._publish_command = Mock(return_value=True)
        client._wait_for_response = AsyncMock(return_value={
            "success": True,
            "strategy": "test_strategy",
            "logs": ["log line 1", "log line 2"]
        })
        
        result = await client.get_logs("test_strategy", 50)
        
        assert result["success"] is True
        client._publish_command.assert_called_once_with("get_logs", {
            "name": "test_strategy",
            "lines": 50
        })
    
    @pytest.mark.asyncio
    async def test_get_logs_all(self, client):
        """ทดสอบการดึง logs ทั่วไป"""
        client._publish_command = Mock(return_value=True)
        client._wait_for_response = AsyncMock(return_value={
            "success": True,
            "logs": ["general log line 1"]
        })
        
        result = await client.get_logs(lines=100)
        
        assert result["success"] is True
        client._publish_command.assert_called_once_with("get_logs", {
            "lines": 100
        })
    
    @pytest.mark.asyncio
    async def test_command_failure_to_send(self, client):
        """ทดสอบเมื่อไม่สามารถส่งคำสั่งได้"""
        client._publish_command = Mock(return_value=False)
        
        result = await client.start_strategy("test_strategy")
        
        assert result["success"] is False
        assert "Failed to send command" in result["error"]
    
    def test_disconnect(self, client):
        """ทดสอบการปิดการเชื่อมต่อ"""
        # Mock MQTT client
        mock_client = Mock()
        client.mqtt_client = mock_client
        client.logger = Mock()
        
        client.disconnect()
        
        mock_client.loop_stop.assert_called_once()
        mock_client.disconnect.assert_called_once()
        client.logger.info.assert_called_once()
    
    def test_disconnect_no_client(self, client):
        """ทดสอบการปิดการเชื่อมต่อเมื่อไม่มี client"""
        client.mqtt_client = None
        client.logger = Mock()
        
        # ไม่ควรเกิด exception
        client.disconnect()
        
        client.logger.info.assert_called_once()
    
    def test_handle_heartbeat(self, client):
        """ทดสอบการจัดการ heartbeat"""
        client.logger = Mock()
        
        payload = {
            "status": "alive",
            "strategies_count": 5,
            "running_count": 3
        }
        
        client._handle_heartbeat(payload)
        
        client.logger.info.assert_called_once()
        args = client.logger.info.call_args[0][0]
        assert "alive" in args
        assert "5" in args
        assert "3" in args
    
    def test_handle_error(self, client):
        """ทดสอบการจัดการ error"""
        client.logger = Mock()
        
        payload = {
            "strategy": "test_strategy",
            "message": "Something went wrong",
            "timestamp": "2024-01-01T12:00:00"
        }
        
        client._handle_error(payload)
        
        client.logger.error.assert_called_once()
        args = client.logger.error.call_args[0][0]
        assert "test_strategy" in args
        assert "Something went wrong" in args


class TestMQTTClientIntegration:
    """Integration tests สำหรับ MQTT Client"""
    
    @pytest.mark.asyncio
    async def test_full_client_workflow(self):
        """ทดสอบ workflow ทั้งหมดของ client"""
        mqtt_config = {
            "host": "localhost",
            "port": 1883,
            "username": None,
            "password": None
        }
        
        client = HummingbotMQTTClient(mqtt_config)
        
        # Mock การเชื่อมต่อและการส่งคำสั่ง
        with patch('paho.mqtt.client.Client') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            # Mock การเชื่อมต่อสำเร็จ
            def mock_on_connect(callback):
                client._on_connect(None, None, None, 0)
            
            mock_client.on_connect = mock_on_connect
            
            # เชื่อมต่อ
            connected = await client.connect()
            assert connected is True
            
            # Mock การส่งคำสั่งและรับ response
            client._publish_command = Mock(return_value=True)
            
            # Test สร้าง strategy
            client.responses["create_strategy"] = {"success": True}
            result = await client.create_strategy(
                "test_strategy", "pure_market_making", "binance", "BTC-USDT"
            )
            assert result["success"] is True
            
            # Test เริ่ม strategy
            client.responses["start_strategy"] = {"success": True}
            result = await client.start_strategy("test_strategy")
            assert result["success"] is True
            
            # Test ดูสถานะ
            client.responses["get_strategy_status"] = {
                "success": True,
                "strategy": {"name": "test_strategy", "status": "running"}
            }
            result = await client.get_strategy_status("test_strategy")
            assert result["success"] is True
            
            # Test หยุด strategy
            client.responses["stop_strategy"] = {"success": True}
            result = await client.stop_strategy("test_strategy")
            assert result["success"] is True
            
            # ปิดการเชื่อมต่อ
            client.disconnect()


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 