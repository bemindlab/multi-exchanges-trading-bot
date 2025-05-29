# 🧪 คู่มือการทดสอบ (Testing Guide)

## 📚 ภาพรวม

คู่มือนี้ครอบคลุมการทดสอบ Multi-Exchange Trading Bot แบบครบวงจร ตั้งแต่ unit tests จนถึง security tests โดยปฏิบัติตาม best practices ของ Python testing

## 🏗️ โครงสร้างการทดสอบ

```
tests/
├── conftest.py                 # Shared pytest fixtures
├── unit/                       # Unit tests (fast, isolated)
│   ├── test_core/             # Core components
│   │   ├── test_config_manager.py
│   │   ├── test_exchange_manager.py
│   │   ├── test_market_analyzer.py
│   │   └── test_risk_manager.py
│   ├── test_strategies/       # Trading strategies
│   │   ├── test_macd_bot.py
│   │   └── test_multi_exchange_bot.py
│   └── test_utils/            # Utilities
│       ├── test_crypto_scanner.py
│       └── test_monitor.py
├── integration/               # Integration tests
│   ├── test_hummingbot_manager.py
│   ├── test_hummingbot_simple.py
│   └── test_mqtt_client.py
├── performance/               # Performance tests
│   └── test_order_processing.py
└── security/                  # Security tests
    └── test_api_key_security.py
```

## 🚀 การตั้งค่าสภาพแวดล้อมการทดสอบ

### 1. การติดตั้ง Dependencies

```bash
# ติดตั้ง project ในโหมด development
pip install -e ".[dev]"

# หรือติดตั้ง test dependencies แยก
pip install pytest pytest-cov pytest-mock pytest-asyncio pytest-timeout
pip install pytest-benchmark psutil  # สำหรับ performance tests
```

### 2. การตั้งค่า Pre-commit Hooks

```bash
# ติดตั้ง pre-commit
pip install pre-commit

# ติดตั้ง hooks
pre-commit install

# รัน hooks manually
pre-commit run --all-files
```

## 📋 การรันการทดสอบ

### การทดสอบพื้นฐาน

```bash
# รันทุก test
pytest

# รันพร้อม verbose output
pytest -v

# รันเฉพาะ unit tests
pytest tests/unit/

# รันเฉพาะ integration tests
pytest tests/integration/

# รันเฉพาะ performance tests
pytest tests/performance/ -m performance

# รันเฉพาะ security tests
pytest tests/security/ -m security
```

### การทดสอบเฉพาะส่วน

```bash
# ทดสอบ core components
pytest tests/unit/test_core/

# ทดสอบ strategies
pytest tests/unit/test_strategies/

# ทดสอบ specific file
pytest tests/unit/test_core/test_exchange_manager.py

# ทดสอบ specific test
pytest tests/unit/test_core/test_exchange_manager.py::TestExchangeManager::test_create_order
```

### Coverage Reports

```bash
# รันพร้อม coverage
pytest --cov=src --cov-report=term-missing

# สร้าง HTML coverage report
pytest --cov=src --cov-report=html

# ดู coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## 🧪 ประเภทการทดสอบ

### 1. Unit Tests

**วัตถุประสงค์**: ทดสอบ functions และ methods แบบแยกส่วน

```python
# ตัวอย่าง: tests/unit/test_core/test_risk_manager.py
class TestRiskManager:
    def test_calculate_position_size(self):
        """Test position size calculation."""
        risk_manager = RiskManager(max_position_size=1000)
        size = risk_manager.calculate_position_size(
            balance=10000,
            risk_percent=1.0,
            stop_loss_percent=2.0
        )
        assert size == 500  # 1% risk with 2% stop loss
```

**Best Practices**:
- ใช้ mocks สำหรับ external dependencies
- ทดสอบทั้ง happy path และ edge cases
- แต่ละ test ควรรันเร็ว (< 0.1 วินาที)
- ตั้งชื่อ test ให้อธิบายสิ่งที่ทดสอบ

### 2. Integration Tests

**วัตถุประสงค์**: ทดสอบการทำงานร่วมกันระหว่าง components

```python
# ตัวอย่าง: tests/integration/test_hummingbot_manager.py
@pytest.mark.integration
class TestHummingbotIntegration:
    def test_strategy_lifecycle(self, mqtt_client, hummingbot_manager):
        """Test complete strategy lifecycle."""
        # Create strategy
        strategy_id = hummingbot_manager.create_strategy(config)
        
        # Start strategy
        mqtt_client.publish("strategy/start", {"id": strategy_id})
        
        # Verify strategy is running
        assert hummingbot_manager.is_running(strategy_id)
        
        # Stop strategy
        mqtt_client.publish("strategy/stop", {"id": strategy_id})
        
        # Cleanup
        hummingbot_manager.delete_strategy(strategy_id)
```

**Best Practices**:
- ใช้ fixtures สำหรับ setup/teardown
- ทดสอบ workflows ที่เกิดขึ้นจริง
- อนุญาตให้ใช้เวลานานกว่า unit tests
- ทำ cleanup หลังทดสอบเสมอ

### 3. Performance Tests

**วัตถุประสงค์**: ตรวจสอบประสิทธิภาพและ scalability

```python
# ตัวอย่าง: tests/performance/test_order_processing.py
@pytest.mark.performance
def test_order_throughput(benchmark, exchange_manager):
    """Test order processing throughput."""
    def process_orders():
        for i in range(100):
            exchange_manager.create_order(
                symbol="BTC/USDT",
                type="limit",
                side="buy",
                amount=0.01,
                price=50000 + i
            )
    
    # Benchmark the function
    result = benchmark(process_orders)
    
    # Assert performance requirements
    assert benchmark.stats['mean'] < 2.0  # Should complete in < 2 seconds
```

**Performance Markers**:
- `@pytest.mark.performance` - Performance tests ทั้งหมด
- `@pytest.mark.slow` - Tests ที่ใช้เวลานาน (> 5 วินาที)
- `@pytest.mark.benchmark` - Benchmark tests

### 4. Security Tests

**วัตถุประสงค์**: ตรวจสอบความปลอดภัยของระบบ

```python
# ตัวอย่าง: tests/security/test_api_key_security.py
@pytest.mark.security
def test_api_keys_not_logged(caplog, exchange_manager):
    """Test that API keys are never logged."""
    api_key = "SECRET_API_KEY_12345"
    
    with caplog.at_level(logging.DEBUG):
        exchange_manager.setup_exchange({
            'api_key': api_key,
            'api_secret': 'secret'
        })
    
    # Verify key is not in logs
    assert api_key not in caplog.text
    assert "[REDACTED]" in caplog.text
```

**Security Test Categories**:
- API key handling
- Authentication/Authorization
- Input validation
- SQL injection prevention
- XSS protection
- Rate limiting

## 🔧 Fixtures และ Utilities

### Common Fixtures (conftest.py)

```python
@pytest.fixture
def mock_exchange():
    """Mock exchange for testing."""
    exchange = Mock()
    exchange.fetch_balance.return_value = {
        'USDT': {'free': 10000, 'used': 0, 'total': 10000}
    }
    return exchange

@pytest.fixture
async def async_exchange():
    """Async mock exchange."""
    exchange = AsyncMock()
    exchange.fetch_ticker.return_value = {
        'symbol': 'BTC/USDT',
        'last': 50000
    }
    return exchange

@pytest.fixture
def temp_config_file(tmp_path):
    """Create temporary config file."""
    config_path = tmp_path / "config.json"
    config_data = {"exchanges": {}, "strategies": {}}
    config_path.write_text(json.dumps(config_data))
    return config_path
```

## 📊 Test Markers

```ini
# pytest.ini
[pytest]
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (component interaction)
    performance: Performance tests
    security: Security tests
    slow: Tests that take > 5 seconds
    asyncio: Async tests
    requires_network: Tests requiring network access
```

### การใช้ Markers

```bash
# รันเฉพาะ fast tests
pytest -m "not slow"

# รันเฉพาะ async tests
pytest -m asyncio

# รัน unit และ integration tests
pytest -m "unit or integration"

# ไม่รัน tests ที่ต้องใช้ network
pytest -m "not requires_network"
```

## 🚨 การ Debug Tests

### Debug Techniques

```bash
# รันพร้อม Python debugger
pytest --pdb tests/unit/test_core/test_exchange_manager.py

# แสดง print statements
pytest -s

# แสดง local variables เมื่อ test fail
pytest -l

# Verbose traceback
pytest --tb=long

# Stop after first failure
pytest -x

# Run last failed tests
pytest --lf
```

### VS Code Configuration

```json
// .vscode/settings.json
{
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "--no-cov"  // Disable coverage in VS Code
    ]
}
```

## 📈 Coverage Goals

### Target Coverage

| Component | Target | Priority |
|-----------|--------|----------|
| Core Business Logic | 90%+ | Critical |
| Trading Strategies | 85%+ | High |
| Utilities | 80%+ | Medium |
| Integration Points | 70%+ | Medium |
| UI/CLI | 60%+ | Low |

### Excluding from Coverage

```python
# pragma: no cover - สำหรับ code ที่ไม่ต้อง test
if TYPE_CHECKING:  # pragma: no cover
    from typing import Dict, List

# หรือใน .coveragerc
[run]
omit = 
    */tests/*
    */migrations/*
    */__pycache__/*
```

## 🔄 Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -e ".[dev]"
    
    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## 📝 Best Practices

### 1. Test Organization
- หนึ่ง test file ต่อหนึ่ง module
- จัดกลุ่ม related tests ใน classes
- ใช้ชื่อ test ที่สื่อความหมาย
- เขียน docstrings อธิบาย test

### 2. Test Data
- ใช้ fixtures สำหรับ reusable test data
- สร้าง realistic test data
- หลีกเลี่ยง hardcoded values
- ใช้ factories สำหรับ complex objects

### 3. Mocking
- Mock external dependencies เท่านั้น
- Mock ที่ระดับ boundary
- ใช้ realistic mock responses
- Verify mock calls เมื่อจำเป็น

### 4. Assertions
- ใช้ specific assertions
- ทดสอบทั้ง success และ failure cases
- รวม edge cases
- ทดสอบ error conditions

## 🛠️ Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # ติดตั้ง package ในโหมด editable
   pip install -e .
   ```

2. **Async Test Issues**
   ```python
   # ใช้ pytest-asyncio
   @pytest.mark.asyncio
   async def test_async_function():
       result = await some_async_function()
       assert result is not None
   ```

3. **Flaky Tests**
   - เพิ่ม proper waits/retries
   - ใช้ mock แทน real network calls
   - ทำ proper cleanup

## 📚 Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Python Testing Best Practices](https://realpython.com/python-testing/)
- [Test-Driven Development](https://testdriven.io/)
- [Property-based Testing with Hypothesis](https://hypothesis.works/)

---

**Happy Testing! 🎉** เขียน test ให้ครอบคลุม ทดสอบให้มั่นใจ!