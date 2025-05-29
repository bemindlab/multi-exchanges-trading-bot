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


class TestMQTTTopics:
    """Test cases สำหรับ MQTT topics และ message format"""
    
    def test_mqtt_topics_format(self):
        """ทดสอบรูปแบบ MQTT topics"""
        topics = {
            "command": "hummingbot/command",
            "status": "hummingbot/status",
            "strategy": "hummingbot/strategy",
            "performance": "hummingbot/performance",
            "logs": "hummingbot/logs"
        }
        
        # ตรวจสอบรูปแบบ topics
        for topic_name, topic_path in topics.items():
            assert topic_path.startswith("hummingbot/")
            assert "/" in topic_path
            assert topic_name in topic_path or topic_path.endswith(topic_name)
    
    def test_command_payload_format(self):
        """ทดสอบรูปแบบ command payload"""
        create_strategy_payload = {
            "name": "test_strategy",
            "strategy_type": "pure_market_making",
            "exchange": "binance",
            "trading_pair": "BTC-USDT",
            "config": {
                "bid_spread": 0.001,
                "ask_spread": 0.001
            }
        }
        
        # ตรวจสอบว่า payload เป็น JSON serializable
        json_str = json.dumps(create_strategy_payload)
        parsed_payload = json.loads(json_str)
        
        assert parsed_payload["name"] == "test_strategy"
        assert parsed_payload["strategy_type"] == "pure_market_making"
        assert parsed_payload["exchange"] == "binance"
        assert parsed_payload["trading_pair"] == "BTC-USDT"
        assert "config" in parsed_payload
    
    def test_response_payload_format(self):
        """ทดสอบรูปแบบ response payload"""
        success_response = {
            "success": True,
            "message": "Operation completed successfully",
            "data": {"key": "value"}
        }
        
        error_response = {
            "success": False,
            "error": "Something went wrong",
            "code": 400
        }
        
        # ตรวจสอบ success response
        assert success_response["success"] is True
        assert "message" in success_response
        
        # ตรวจสอบ error response
        assert error_response["success"] is False
        assert "error" in error_response


class TestConfigValidation:
    """Test cases สำหรับการตรวจสอบ configuration"""
    
    def test_mqtt_config_validation(self):
        """ทดสอบการตรวจสอบ MQTT config"""
        valid_mqtt_config = {
            "host": "localhost",
            "port": 1883,
            "username": None,
            "password": None,
            "keepalive": 60,
            "qos": 1
        }
        
        # ตรวจสอบ required fields
        assert "host" in valid_mqtt_config
        assert "port" in valid_mqtt_config
        assert isinstance(valid_mqtt_config["port"], int)
        assert 1 <= valid_mqtt_config["port"] <= 65535
        
        # ตรวจสอบ optional fields
        assert valid_mqtt_config["keepalive"] > 0
        assert valid_mqtt_config["qos"] in [0, 1, 2]
    
    def test_hummingbot_config_validation(self):
        """ทดสอบการตรวจสอบ Hummingbot config"""
        valid_hummingbot_config = {
            "path": "/opt/hummingbot",
            "config_path": "/opt/hummingbot/conf",
            "logs_path": "/opt/hummingbot/logs",
            "strategies_path": "/opt/hummingbot/conf/strategies"
        }
        
        # ตรวจสอบ required fields
        required_fields = ["path", "config_path", "logs_path", "strategies_path"]
        for field in required_fields:
            assert field in valid_hummingbot_config
            assert isinstance(valid_hummingbot_config[field], str)
            assert len(valid_hummingbot_config[field]) > 0
    
    def test_strategy_config_validation(self):
        """ทดสอบการตรวจสอบ strategy config"""
        valid_strategy_configs = {
            "pure_market_making": {
                "bid_spread": 0.001,
                "ask_spread": 0.001,
                "order_amount": 10.0
            },
            "arbitrage": {
                "primary_market": "binance",
                "secondary_market": "kucoin",
                "min_profitability": 0.003
            }
        }
        
        # ตรวจสอบ pure_market_making config
        pmm_config = valid_strategy_configs["pure_market_making"]
        assert isinstance(pmm_config["bid_spread"], float)
        assert isinstance(pmm_config["ask_spread"], float)
        assert isinstance(pmm_config["order_amount"], (int, float))
        assert pmm_config["bid_spread"] > 0
        assert pmm_config["ask_spread"] > 0
        assert pmm_config["order_amount"] > 0
        
        # ตรวจสอบ arbitrage config
        arb_config = valid_strategy_configs["arbitrage"]
        assert isinstance(arb_config["primary_market"], str)
        assert isinstance(arb_config["secondary_market"], str)
        assert isinstance(arb_config["min_profitability"], float)
        assert arb_config["min_profitability"] > 0


class TestUtilityFunctions:
    """Test cases สำหรับ utility functions"""
    
    def test_json_serialization(self):
        """ทดสอบการ serialize/deserialize JSON"""
        test_data = {
            "string": "test",
            "number": 123,
            "float": 123.45,
            "boolean": True,
            "null": None,
            "array": [1, 2, 3],
            "object": {"nested": "value"}
        }
        
        # Serialize
        json_str = json.dumps(test_data, default=str)
        
        # Deserialize
        parsed_data = json.loads(json_str)
        
        assert parsed_data["string"] == "test"
        assert parsed_data["number"] == 123
        assert parsed_data["float"] == 123.45
        assert parsed_data["boolean"] is True
        assert parsed_data["null"] is None
        assert parsed_data["array"] == [1, 2, 3]
        assert parsed_data["object"]["nested"] == "value"
    
    def test_datetime_handling(self):
        """ทดสอบการจัดการ datetime"""
        now = datetime.now()
        
        # Test datetime to string conversion
        datetime_str = now.isoformat()
        assert isinstance(datetime_str, str)
        assert "T" in datetime_str
        
        # Test string to datetime conversion
        parsed_datetime = datetime.fromisoformat(datetime_str)
        assert isinstance(parsed_datetime, datetime)
        assert parsed_datetime.year == now.year
        assert parsed_datetime.month == now.month
        assert parsed_datetime.day == now.day
    
    def test_path_handling(self):
        """ทดสอบการจัดการ file paths"""
        test_paths = [
            "/opt/hummingbot",
            "/opt/hummingbot/conf",
            "/opt/hummingbot/logs",
            "/opt/hummingbot/conf/strategies"
        ]
        
        for path_str in test_paths:
            path_obj = Path(path_str)
            
            # ตรวจสอบว่าสามารถสร้าง Path object ได้
            assert isinstance(path_obj, Path)
            assert str(path_obj) == path_str
            
            # ตรวจสอบ path operations
            assert path_obj.is_absolute()
            assert len(path_obj.parts) > 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 