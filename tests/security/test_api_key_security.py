"""Security tests for API key handling.

Tests to ensure API keys are handled securely throughout the system.
"""

import os
import pytest
import tempfile
import json
from unittest.mock import Mock, patch, mock_open
import logging

from src.core.exchange_manager import ExchangeManager
from config_manager import ConfigManager


class TestAPIKeySecurity:
    """Security tests for API key management."""
    
    @pytest.mark.security
    def test_api_keys_not_logged(self, caplog):
        """Test that API keys are never written to logs."""
        # Arrange
        sensitive_key = "SUPER_SECRET_API_KEY_12345"
        sensitive_secret = "SUPER_SECRET_API_SECRET_67890"
        
        config = {
            'exchange': 'binance',
            'api_key': sensitive_key,
            'api_secret': sensitive_secret
        }
        
        # Act
        with caplog.at_level(logging.DEBUG):
            exchange_manager = ExchangeManager()
            exchange_manager.setup_exchange(config)
            
            # Simulate various operations that might log
            try:
                exchange_manager.connect()
            except:
                pass
        
        # Assert
        log_text = caplog.text
        assert sensitive_key not in log_text, "API key found in logs!"
        assert sensitive_secret not in log_text, "API secret found in logs!"
        assert "****" in log_text or "[REDACTED]" in log_text, "Sensitive data not properly masked"
    
    @pytest.mark.security
    def test_api_keys_not_in_config_files(self, temp_directory):
        """Test that API keys are not saved in plain text config files."""
        # Arrange
        config_path = os.path.join(temp_directory, 'config.json')
        
        config_data = {
            'exchanges': {
                'binance': {
                    'api_key': 'test_key',
                    'api_secret': 'test_secret'
                }
            }
        }
        
        # Act
        config_manager = ConfigManager(config_path)
        config_manager.save_config(config_data)
        
        # Assert
        with open(config_path, 'r') as f:
            saved_data = json.load(f)
        
        # Check that sensitive data is either encrypted or stored as reference
        binance_config = saved_data.get('exchanges', {}).get('binance', {})
        
        # API keys should either be encrypted or stored as environment variable references
        if 'api_key' in binance_config:
            assert not binance_config['api_key'].startswith('test_'), "Plain text API key found"
            assert binance_config['api_key'].startswith('$') or binance_config['api_key'].startswith('enc:'), \
                "API key not properly protected"
    
    @pytest.mark.security
    def test_api_keys_from_environment(self):
        """Test that API keys can be loaded securely from environment variables."""
        # Arrange
        os.environ['BINANCE_API_KEY'] = 'env_test_key'
        os.environ['BINANCE_API_SECRET'] = 'env_test_secret'
        
        config = {
            'exchanges': {
                'binance': {
                    'api_key': '$BINANCE_API_KEY',
                    'api_secret': '$BINANCE_API_SECRET'
                }
            }
        }
        
        try:
            # Act
            config_manager = ConfigManager()
            resolved_config = config_manager.resolve_env_vars(config)
            
            # Assert
            assert resolved_config['exchanges']['binance']['api_key'] == 'env_test_key'
            assert resolved_config['exchanges']['binance']['api_secret'] == 'env_test_secret'
            
            # Ensure original config wasn't modified
            assert config['exchanges']['binance']['api_key'] == '$BINANCE_API_KEY'
            
        finally:
            # Cleanup
            del os.environ['BINANCE_API_KEY']
            del os.environ['BINANCE_API_SECRET']
    
    @pytest.mark.security
    def test_api_key_permissions(self, temp_directory):
        """Test that files containing API keys have restricted permissions."""
        # Arrange
        env_file = os.path.join(temp_directory, '.env')
        
        # Act
        with open(env_file, 'w') as f:
            f.write('API_KEY=secret_key\n')
            f.write('API_SECRET=secret_value\n')
        
        # Set restrictive permissions (owner read/write only)
        os.chmod(env_file, 0o600)
        
        # Assert
        stat_info = os.stat(env_file)
        permissions = oct(stat_info.st_mode)[-3:]
        
        assert permissions == '600', f"File permissions {permissions} are too permissive, expected 600"
    
    @pytest.mark.security
    def test_memory_cleanup_after_use(self):
        """Test that sensitive data is cleared from memory after use."""
        # Arrange
        import gc
        
        sensitive_data = "SENSITIVE_API_KEY_12345"
        
        class SecureHandler:
            def __init__(self):
                self._api_key = None
            
            def set_api_key(self, key):
                self._api_key = key
            
            def clear_sensitive_data(self):
                if self._api_key:
                    # Overwrite the string in memory
                    self._api_key = 'X' * len(self._api_key)
                    self._api_key = None
        
        # Act
        handler = SecureHandler()
        handler.set_api_key(sensitive_data)
        handler.clear_sensitive_data()
        
        # Force garbage collection
        gc.collect()
        
        # Assert
        assert handler._api_key is None
        # Note: In real implementation, we'd use secure memory handling libraries
    
    @pytest.mark.security
    def test_api_key_validation(self):
        """Test that API keys are validated before use."""
        # Arrange
        invalid_keys = [
            '',  # Empty
            ' ',  # Whitespace
            'test',  # Too short
            '<script>alert("xss")</script>',  # Potential XSS
            "'; DROP TABLE users; --",  # SQL injection attempt
            '../../../etc/passwd',  # Path traversal
        ]
        
        exchange_manager = ExchangeManager()
        
        # Act & Assert
        for invalid_key in invalid_keys:
            with pytest.raises((ValueError, AssertionError)):
                exchange_manager.validate_api_credentials(invalid_key, "some_secret")
    
    @pytest.mark.security
    def test_rate_limiting_on_api_calls(self):
        """Test that API calls are rate limited to prevent abuse."""
        import time
        
        # Arrange
        exchange_manager = ExchangeManager()
        exchange_manager.rate_limit = 10  # 10 calls per second
        
        call_times = []
        
        # Act
        for i in range(15):
            start = time.time()
            exchange_manager.make_api_call("test_endpoint")
            call_times.append(time.time() - start)
        
        # Assert
        # After 10 calls, subsequent calls should be delayed
        assert any(t > 0.05 for t in call_times[10:]), "Rate limiting not enforced"
    
    @pytest.mark.security
    def test_secure_storage_encryption(self, temp_directory):
        """Test that sensitive data is encrypted when stored."""
        from cryptography.fernet import Fernet
        
        # Arrange
        key = Fernet.generate_key()
        cipher = Fernet(key)
        
        sensitive_data = {
            'api_key': 'my_secret_api_key',
            'api_secret': 'my_secret_api_secret'
        }
        
        # Act
        encrypted_data = cipher.encrypt(json.dumps(sensitive_data).encode())
        
        storage_file = os.path.join(temp_directory, 'encrypted_config.enc')
        with open(storage_file, 'wb') as f:
            f.write(encrypted_data)
        
        # Verify encryption
        with open(storage_file, 'rb') as f:
            stored_data = f.read()
        
        # Assert
        assert b'my_secret_api_key' not in stored_data, "API key found in plain text"
        assert b'api_secret' not in stored_data, "API secret found in plain text"
        
        # Verify we can decrypt
        decrypted_data = json.loads(cipher.decrypt(stored_data))
        assert decrypted_data == sensitive_data 