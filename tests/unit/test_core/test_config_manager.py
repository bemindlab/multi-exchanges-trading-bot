"""
Tests for config_manager.py
"""

import pytest
import json
import os
import tempfile
from unittest.mock import patch, mock_open, Mock
from pathlib import Path

from config_manager import ConfigManager, ensure_config_exists


class TestConfigManager:
    """Test cases for ConfigManager class"""
    
    def test_init_default_paths(self):
        """Test ConfigManager initialization with default paths"""
        manager = ConfigManager()
        assert manager.config_path == Path("config.json")
        assert manager.template_path == Path("config.template.json")
        assert not manager.env_loaded
    
    def test_init_custom_paths(self):
        """Test ConfigManager initialization with custom paths"""
        manager = ConfigManager("custom_config.json", "custom_template.json")
        assert manager.config_path == Path("custom_config.json")
        assert manager.template_path == Path("custom_template.json")
    
    def test_load_env(self):
        """Test environment variables loading"""
        manager = ConfigManager()
        result = manager.load_env()
        assert result is True
        assert manager.env_loaded is True
    
    def test_template_exists(self, temp_config_file):
        """Test template file existence check"""
        manager = ConfigManager(template_path=temp_config_file)
        assert manager.template_exists() is True
        
        manager = ConfigManager(template_path="nonexistent.json")
        assert manager.template_exists() is False
    
    def test_config_exists(self, temp_config_file):
        """Test config file existence check"""
        manager = ConfigManager(config_path=temp_config_file)
        assert manager.config_exists() is True
        
        manager = ConfigManager(config_path="nonexistent.json")
        assert manager.config_exists() is False
    
    def test_substitute_env_vars_basic(self):
        """Test basic environment variable substitution"""
        manager = ConfigManager()
        
        with patch.dict(os.environ, {'TEST_VAR': 'test_value'}):
            result = manager.substitute_env_vars("${TEST_VAR}")
            assert result == "test_value"
    
    def test_substitute_env_vars_multiple(self):
        """Test multiple environment variable substitution"""
        manager = ConfigManager()
        
        with patch.dict(os.environ, {'VAR1': 'value1', 'VAR2': 'value2'}):
            result = manager.substitute_env_vars("${VAR1} and ${VAR2}")
            assert result == "value1 and value2"
    
    def test_substitute_env_vars_missing(self):
        """Test substitution with missing environment variable"""
        manager = ConfigManager()
        
        result = manager.substitute_env_vars("${MISSING_VAR}")
        assert result == "${MISSING_VAR}"
    
    def test_substitute_env_vars_unsafe_name(self):
        """Test substitution with unsafe variable name"""
        manager = ConfigManager()
        
        result = manager.substitute_env_vars("${unsafe-var}")
        assert result == "${unsafe-var}"
    
    def test_create_config_from_template_success(self, temp_directory):
        """Test successful config creation from template"""
        template_path = os.path.join(temp_directory, "template.json")
        config_path = os.path.join(temp_directory, "config.json")
        
        # Create template file
        template_data = {
            "test_key": "${TEST_VAR}",
            "static_key": "static_value"
        }
        with open(template_path, 'w') as f:
            json.dump(template_data, f)
        
        manager = ConfigManager(config_path, template_path)
        
        with patch.dict(os.environ, {'TEST_VAR': 'test_value'}):
            result = manager.create_config_from_template()
            assert result is True
            assert os.path.exists(config_path)
            
            # Verify config content
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            assert config_data['test_key'] == 'test_value'
            assert config_data['static_key'] == 'static_value'
    
    def test_create_config_from_template_no_template(self):
        """Test config creation when template doesn't exist"""
        manager = ConfigManager("config.json", "nonexistent_template.json")
        result = manager.create_config_from_template()
        assert result is False
    
    def test_create_config_from_template_config_exists(self, temp_config_file):
        """Test config creation when config already exists"""
        manager = ConfigManager(temp_config_file, temp_config_file)
        result = manager.create_config_from_template()
        assert result is False
    
    def test_create_config_from_template_force(self, temp_directory):
        """Test config creation with force flag"""
        template_path = os.path.join(temp_directory, "template.json")
        config_path = os.path.join(temp_directory, "config.json")
        
        # Create template and existing config
        template_data = {"key": "${TEST_VAR}"}
        with open(template_path, 'w') as f:
            json.dump(template_data, f)
        with open(config_path, 'w') as f:
            json.dump({"old": "data"}, f)
        
        manager = ConfigManager(config_path, template_path)
        
        with patch.dict(os.environ, {'TEST_VAR': 'new_value'}):
            result = manager.create_config_from_template(force=True)
            assert result is True
            
            # Verify config was overwritten
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            assert config_data['key'] == 'new_value'
            assert 'old' not in config_data
    
    def test_auto_enable_exchanges_cex(self, temp_directory):
        """Test auto-enabling CEX exchanges"""
        manager = ConfigManager()
        
        config_data = {
            "exchanges": {
                "binance": {
                    "type": "cex",
                    "enabled": False,
                    "api_key": "real_api_key",
                    "secret": "real_secret"
                },
                "gateio": {
                    "type": "cex",
                    "enabled": False,
                    "api_key": "${GATEIO_API_KEY}",
                    "secret": "${GATEIO_SECRET}"
                }
            }
        }
        
        manager.auto_enable_exchanges(config_data)
        
        # Binance should be enabled (has real keys)
        assert config_data["exchanges"]["binance"]["enabled"] is True
        # Gate.io should remain disabled (has placeholders)
        assert config_data["exchanges"]["gateio"]["enabled"] is False
    
    def test_auto_enable_exchanges_dex(self):
        """Test auto-enabling DEX exchanges"""
        manager = ConfigManager()
        
        config_data = {
            "exchanges": {
                "uniswap": {
                    "type": "dex",
                    "enabled": False,
                    "rpc_url": "https://mainnet.infura.io/v3/real_key",
                    "private_key": "real_private_key"
                },
                "pancakeswap": {
                    "type": "dex",
                    "enabled": False,
                    "rpc_url": "${BSC_RPC_URL}",
                    "private_key": "${BSC_PRIVATE_KEY}"
                }
            }
        }
        
        manager.auto_enable_exchanges(config_data)
        
        # Uniswap should be enabled (has real keys)
        assert config_data["exchanges"]["uniswap"]["enabled"] is True
        # PancakeSwap should remain disabled (has placeholders)
        assert config_data["exchanges"]["pancakeswap"]["enabled"] is False
    
    def test_load_config_success(self, temp_config_file):
        """Test successful config loading"""
        manager = ConfigManager(temp_config_file)
        config_data = manager.load_config()
        assert config_data is not None
        assert isinstance(config_data, dict)
    
    def test_load_config_not_exists(self):
        """Test config loading when file doesn't exist"""
        manager = ConfigManager("nonexistent.json")
        config_data = manager.load_config()
        assert config_data is None
    
    def test_load_config_invalid_json(self, temp_directory):
        """Test config loading with invalid JSON"""
        config_path = os.path.join(temp_directory, "invalid.json")
        with open(config_path, 'w') as f:
            f.write("invalid json content")
        
        manager = ConfigManager(config_path)
        config_data = manager.load_config()
        assert config_data is None
    
    def test_sanitize_config_for_display(self):
        """Test config sanitization for display"""
        manager = ConfigManager()
        
        config_data = {
            "exchanges": {
                "binance": {
                    "api_key": "very_long_api_key_here",
                    "secret": "very_long_secret_here",
                    "other": "normal_value"
                }
            },
            "telegram": {
                "bot_token": "${TELEGRAM_BOT_TOKEN}",
                "chat_id": "123456789"
            }
        }
        
        sanitized = manager.sanitize_config_for_display(config_data)
        
        # API keys should be masked
        assert sanitized["exchanges"]["binance"]["api_key"] == "very...here"
        assert sanitized["exchanges"]["binance"]["secret"] == "very...here"
        # Placeholders should remain unchanged
        assert sanitized["telegram"]["bot_token"] == "${TELEGRAM_BOT_TOKEN}"
        # Normal values should remain unchanged
        assert sanitized["exchanges"]["binance"]["other"] == "normal_value"
    
    def test_validate_config_success(self, sample_config, temp_directory):
        """Test successful config validation"""
        config_path = os.path.join(temp_directory, "config.json")
        with open(config_path, 'w') as f:
            json.dump(sample_config, f)
        
        manager = ConfigManager(config_path)
        result = manager.validate_config()
        assert result is True
    
    def test_validate_config_missing_sections(self, temp_directory):
        """Test config validation with missing sections"""
        config_data = {"incomplete": "config"}
        config_path = os.path.join(temp_directory, "config.json")
        with open(config_path, 'w') as f:
            json.dump(config_data, f)
        
        manager = ConfigManager(config_path)
        result = manager.validate_config()
        assert result is False
    
    def test_validate_config_no_enabled_exchanges(self, temp_directory):
        """Test config validation with no enabled exchanges"""
        config_data = {
            "exchanges": {
                "binance": {"enabled": False}
            },
            "trading_strategy": {"timeframe": "1h"},
            "bot_settings": {"log_file": "test.log"}
        }
        config_path = os.path.join(temp_directory, "config.json")
        with open(config_path, 'w') as f:
            json.dump(config_data, f)
        
        manager = ConfigManager(config_path)
        result = manager.validate_config()
        assert result is False
    
    def test_get_enabled_exchanges(self, sample_config, temp_directory):
        """Test getting enabled exchanges"""
        config_path = os.path.join(temp_directory, "config.json")
        with open(config_path, 'w') as f:
            json.dump(sample_config, f)
        
        manager = ConfigManager(config_path)
        enabled = manager.get_enabled_exchanges()
        assert "binance" in enabled
        assert "gateio" not in enabled  # disabled in sample_config
    
    def test_backup_config_success(self, temp_config_file):
        """Test successful config backup"""
        manager = ConfigManager(temp_config_file)
        result = manager.backup_config("test_suffix")
        assert result is True
        
        backup_path = f"{temp_config_file}.backup.test_suffix"
        assert os.path.exists(backup_path)
        
        # Cleanup
        os.unlink(backup_path)
    
    def test_backup_config_not_exists(self):
        """Test config backup when file doesn't exist"""
        manager = ConfigManager("nonexistent.json")
        result = manager.backup_config()
        assert result is False
    
    def test_export_config_template(self, sample_config, temp_directory):
        """Test config template export"""
        config_path = os.path.join(temp_directory, "config.json")
        output_path = os.path.join(temp_directory, "exported_template.json")
        
        # Modify sample config to have real values
        sample_config["exchanges"]["binance"]["api_key"] = "real_api_key"
        sample_config["exchanges"]["binance"]["secret"] = "real_secret"
        
        with open(config_path, 'w') as f:
            json.dump(sample_config, f)
        
        manager = ConfigManager(config_path)
        result = manager.export_config_template(output_path)
        assert result is True
        assert os.path.exists(output_path)
        
        # Verify template has placeholders
        with open(output_path, 'r') as f:
            template_data = json.load(f)
        
        assert template_data["exchanges"]["binance"]["api_key"] == "${BINANCE_API_KEY}"
        assert template_data["exchanges"]["binance"]["secret"] == "${BINANCE_SECRET}"
        assert template_data["exchanges"]["binance"]["enabled"] is False
    
    def test_get_config_summary(self, sample_config, temp_directory):
        """Test config summary generation"""
        config_path = os.path.join(temp_directory, "config.json")
        template_path = os.path.join(temp_directory, "template.json")
        
        with open(config_path, 'w') as f:
            json.dump(sample_config, f)
        with open(template_path, 'w') as f:
            json.dump({}, f)
        
        manager = ConfigManager(config_path, template_path)
        summary = manager.get_config_summary()
        
        assert summary['config_exists'] is True
        assert summary['template_exists'] is True
        assert summary['total_exchanges'] == 2
        assert len(summary['enabled_exchanges']) == 1
        assert 'binance' in summary['enabled_exchanges']
        assert summary['trading_strategy'] == 'market_making'
        assert summary['timeframe'] == '1m'


class TestEnsureConfigExists:
    """Test cases for ensure_config_exists function"""
    
    def test_ensure_config_exists_config_present(self, temp_config_file):
        """Test when config file already exists"""
        result = ensure_config_exists(temp_config_file)
        assert result is True
    
    @patch('config_manager.ConfigManager')
    def test_ensure_config_exists_create_from_template(self, mock_manager_class):
        """Test creating config from template when config doesn't exist"""
        mock_manager = Mock()
        mock_manager.config_exists.return_value = False
        mock_manager.create_config_from_template.return_value = True
        mock_manager_class.return_value = mock_manager
        
        result = ensure_config_exists()
        assert result is True
        mock_manager.create_config_from_template.assert_called_once()
    
    @patch('config_manager.ConfigManager')
    def test_ensure_config_exists_creation_fails(self, mock_manager_class):
        """Test when config creation fails"""
        mock_manager = Mock()
        mock_manager.config_exists.return_value = False
        mock_manager.create_config_from_template.return_value = False
        mock_manager_class.return_value = mock_manager
        
        result = ensure_config_exists()
        assert result is False


class TestConfigManagerCLI:
    """Test cases for ConfigManager CLI functionality"""
    
    def test_cli_integration(self, temp_directory):
        """Test CLI integration with ConfigManager"""
        # This would test the CLI commands, but since they use click
        # and print statements, we'll focus on the core functionality
        pass


# Integration tests
class TestConfigManagerIntegration:
    """Integration tests for ConfigManager"""
    
    def test_full_workflow(self, temp_directory):
        """Test complete workflow from template to config"""
        template_path = os.path.join(temp_directory, "template.json")
        config_path = os.path.join(temp_directory, "config.json")
        
        # Create template
        template_data = {
            "exchanges": {
                "binance": {
                    "enabled": False,
                    "api_key": "${BINANCE_API_KEY}",
                    "secret": "${BINANCE_SECRET}"
                }
            },
            "trading_strategy": {
                "timeframe": "1h"
            },
            "bot_settings": {
                "log_file": "test.log"
            }
        }
        
        with open(template_path, 'w') as f:
            json.dump(template_data, f)
        
        manager = ConfigManager(config_path, template_path)
        
        # Test workflow
        with patch.dict(os.environ, {'BINANCE_API_KEY': 'test_key', 'BINANCE_SECRET': 'test_secret'}):
            # 1. Create config from template
            assert manager.create_config_from_template() is True
            
            # 2. Validate config
            assert manager.validate_config() is True
            
            # 3. Get enabled exchanges
            enabled = manager.get_enabled_exchanges()
            assert 'binance' in enabled
            
            # 4. Backup config
            assert manager.backup_config() is True
            
            # 5. Export template
            export_path = os.path.join(temp_directory, "exported.json")
            assert manager.export_config_template(export_path) is True
            
            # 6. Get summary
            summary = manager.get_config_summary()
            assert summary['config_exists'] is True
            assert summary['enabled_exchanges'] == ['binance'] 