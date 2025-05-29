# 🧪 Testing Guide

## 📋 Overview

This directory contains comprehensive test suites for the Multi-Exchange Trading Bot project. The tests are organized following best practices to ensure code quality, reliability, and maintainability.

## 🏗️ Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Shared pytest fixtures
├── unit/                       # Unit tests
│   ├── __init__.py
│   ├── test_core/             # Core components
│   │   ├── __init__.py
│   │   ├── test_config_manager.py
│   │   ├── test_exchange_manager.py
│   │   ├── test_market_analyzer.py
│   │   └── test_risk_manager.py
│   ├── test_strategies/       # Trading strategies
│   │   ├── __init__.py
│   │   ├── test_macd_bot.py
│   │   └── test_multi_exchange_bot.py
│   └── test_utils/            # Utilities
│       ├── __init__.py
│       ├── test_crypto_scanner.py
│       └── test_monitor.py
├── integration/               # Integration tests
│   ├── __init__.py
│   ├── test_hummingbot_manager.py
│   ├── test_hummingbot_simple.py
│   └── test_mqtt_client.py
├── performance/               # Performance tests
│   └── __init__.py
├── security/                  # Security tests
│   └── __init__.py
└── README.md                  # This file
```

## 🚀 Running Tests

### Prerequisites

Install testing dependencies:

```bash
pip install -r requirements.txt
```

### Basic Test Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test category
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/

# Run specific test module
pytest tests/unit/test_core/test_config_manager.py

# Run specific test class
pytest tests/unit/test_core/test_config_manager.py::TestConfigManager

# Run specific test method
pytest tests/unit/test_core/test_config_manager.py::TestConfigManager::test_init_default_paths
```

### Coverage Reports

```bash
# Run tests with coverage
pytest --cov=bots --cov=config_manager

# Generate HTML coverage report
pytest --cov=bots --cov=config_manager --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Test Categories

```bash
# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run core component tests
pytest tests/unit/test_core/

# Run strategy tests
pytest tests/unit/test_strategies/

# Run utility tests
pytest tests/unit/test_utils/

# Skip slow tests
pytest -m "not slow"

# Run only async tests
pytest -m asyncio
```

## 🧪 Test Types

### Unit Tests (`unit/`)
- Test individual functions and methods in isolation
- Mock all external dependencies
- Fast execution (< 0.1s per test)
- High code coverage target (> 90%)
- Organized by module:
  - `test_core/`: Core business logic components
  - `test_strategies/`: Trading strategy implementations
  - `test_utils/`: Utility functions and helpers

### Integration Tests (`integration/`)
- Test component interactions and workflows
- Use real or realistic mock data
- May interact with external services (mocked)
- Slower execution acceptable (< 5s per test)
- Focus on:
  - API integrations
  - Database operations
  - Message queue interactions
  - End-to-end workflows

### Performance Tests (`performance/`)
- Measure execution time and resource usage
- Test system under load
- Identify bottlenecks
- Benchmark critical operations
- Examples:
  - Order processing throughput
  - Market data analysis speed
  - Memory usage patterns

### Security Tests (`security/`)
- Verify security controls
- Test authentication/authorization
- Check for vulnerabilities
- Validate input sanitization
- Examples:
  - API key handling
  - Permission checks
  - SQL injection prevention
  - XSS protection

## 📊 Test Fixtures

### Shared Fixtures (conftest.py)

- `sample_config`: Sample configuration data
- `temp_config_file`: Temporary config file
- `temp_env_file`: Temporary environment file
- `sample_ohlcv_data`: Sample OHLCV market data
- `sample_balance_data`: Sample balance data
- `mock_exchange`: Mock exchange object
- `mock_ccxt_exchange`: Mock CCXT exchange with responses
- `temp_directory`: Temporary directory for tests

### Usage Example

```python
def test_example(sample_config, temp_directory):
    """Test using shared fixtures"""
    assert 'exchanges' in sample_config
    assert os.path.exists(temp_directory)
```

## 🎯 Writing Tests

### Test Naming Convention

```python
class TestClassName:
    """Test cases for ClassName"""
    
    def test_method_name_success(self):
        """Test successful method execution"""
        pass
    
    def test_method_name_failure(self):
        """Test method failure scenarios"""
        pass
    
    def test_method_name_edge_case(self):
        """Test edge cases"""
        pass
```

### Async Test Example

```python
@pytest.mark.asyncio
async def test_async_function():
    """Test async function"""
    result = await some_async_function()
    assert result is not None
```

### Mock Example

```python
@patch('module.external_dependency')
def test_with_mock(mock_dependency):
    """Test with mocked dependency"""
    mock_dependency.return_value = 'mocked_result'
    result = function_using_dependency()
    assert result == 'expected_result'
```

### Parametrized Test Example

```python
@pytest.mark.parametrize("input_value,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_multiply_by_two(input_value, expected):
    """Test multiply by two function"""
    assert multiply_by_two(input_value) == expected
```

## 🔧 Test Configuration

### pytest.ini

The project uses `pytest.ini` for configuration:

- Coverage settings
- Test discovery patterns
- Markers for test categorization
- Warning filters

### Environment Variables

Tests use environment variables for configuration:

```bash
# Set test environment
export TESTING=true
export LOG_LEVEL=DEBUG
```

## 📈 Coverage Goals

- **Overall Coverage**: 80%+
- **Critical Components**: 90%+
- **New Code**: 100%

### Coverage Reports

```bash
# Terminal report
pytest --cov-report=term-missing

# HTML report
pytest --cov-report=html

# XML report (for CI/CD)
pytest --cov-report=xml
```

## 🚨 Common Issues

### Import Errors

```bash
# Add project root to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or use pytest with path
python -m pytest
```

### Async Test Issues

```bash
# Install pytest-asyncio
pip install pytest-asyncio

# Use asyncio marker
@pytest.mark.asyncio
async def test_async():
    pass
```

### Mock Issues

```bash
# Use proper import paths
from unittest.mock import Mock, patch

# Mock at the right level
@patch('module.where.used.function')
```

## 🔄 Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=bots --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

## 📝 Best Practices

### Test Organization
- One test file per module
- Group related tests in classes
- Use descriptive test names
- Include docstrings

### Test Data
- Use fixtures for reusable data
- Create realistic test data
- Avoid hardcoded values
- Use factories for complex objects

### Mocking
- Mock external dependencies
- Mock at the boundary
- Use realistic mock responses
- Verify mock calls when needed

### Assertions
- Use specific assertions
- Test both success and failure cases
- Include edge cases
- Test error conditions

## 🛠️ Debugging Tests

### Running Single Test with Debug

```bash
# Run with pdb
pytest --pdb tests/test_file.py::test_function

# Run with verbose output
pytest -vvv tests/test_file.py

# Run with print statements
pytest -s tests/test_file.py
```

### IDE Integration

Most IDEs support pytest integration:
- PyCharm: Built-in pytest support
- VSCode: Python Test Explorer
- Vim: vim-test plugin

## 📚 Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Python Testing Best Practices](https://realpython.com/python-testing/)

---

**Happy Testing! 🎉** 