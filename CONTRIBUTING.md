# 🤝 Contributing to Multi-Exchange Trading Bot

Thank you for your interest in contributing to the Multi-Exchange Trading Bot! We welcome contributions from the community.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)

## 📜 Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

### Our Standards

- **Be respectful** and inclusive
- **Be collaborative** and helpful
- **Focus on what's best** for the community
- **Show empathy** towards other community members

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Git
- Basic understanding of cryptocurrency trading
- Familiarity with REST APIs and WebSockets

### First Contribution

1. **Fork the repository**
2. **Clone your fork**
3. **Create a feature branch**
4. **Make your changes**
5. **Test your changes**
6. **Submit a pull request**

## 🛠️ How to Contribute

### 🐛 Bug Reports

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title** and description
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Environment details** (OS, Python version, etc.)
- **Log files** (with sensitive data removed)
- **Configuration** (sanitized)

### 💡 Feature Requests

Feature requests are welcome! Please:

- **Check existing issues** first
- **Describe the feature** clearly
- **Explain the use case**
- **Consider implementation** complexity
- **Discuss alternatives**

### 🔧 Code Contributions

We welcome code contributions for:

- **Bug fixes**
- **New features**
- **Performance improvements**
- **Documentation updates**
- **Test coverage**
- **Code refactoring**

## 💻 Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
git clone https://github.com/YOUR_USERNAME/multi-exchanges-trading-bot.git
cd multi-exchanges-trading-bot
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Setup Development Environment

```bash
# Copy environment template
cp env.example .env

# Create config from template
python cli.py setup

# Run tests
python -m pytest tests/
```

### 4. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number
```

## 📝 Coding Standards

### Python Style Guide

- Follow **PEP 8** style guide
- Use **type hints** where possible
- Write **docstrings** for functions and classes
- Keep functions **small and focused**
- Use **meaningful variable names**

### Code Structure

```python
def function_name(param: str) -> bool:
    """
    Brief description of what the function does.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: Description of when this exception is raised
    """
    # Implementation here
    return True
```

### Import Organization

```python
# Standard library imports
import os
import json
from typing import Dict, List, Optional

# Third-party imports
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Local imports
from .config_manager import ConfigManager
from .exchange_manager import ExchangeManager
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=bots

# Run specific test file
python -m pytest tests/test_config_manager.py

# Run with verbose output
python -m pytest -v
```

### Writing Tests

- Write tests for **new features**
- Include **edge cases**
- Test **error conditions**
- Use **meaningful test names**
- Mock **external dependencies**

Example test:

```python
def test_config_manager_creates_config_from_template():
    """Test that ConfigManager can create config from template."""
    manager = ConfigManager()
    result = manager.create_config_from_template()
    assert result is True
    assert manager.config_exists()
```

## 📤 Pull Request Process

### Before Submitting

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Ensure all tests pass**
4. **Update CHANGELOG.md**
5. **Check code style**

### PR Guidelines

- **Clear title** describing the change
- **Detailed description** of what was changed and why
- **Link to related issues**
- **Screenshots** for UI changes
- **Breaking changes** clearly marked

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added new tests
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No sensitive data exposed
```

## 🐛 Issue Guidelines

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Environment:**
- OS: [e.g. Ubuntu 20.04]
- Python version: [e.g. 3.9.0]
- Bot version: [e.g. 2.0.1]

**Additional context**
Add any other context about the problem here.
```

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
```

## 🏷️ Labels and Milestones

### Issue Labels

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Improvements or additions to documentation
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention is needed
- `security` - Security-related issues
- `performance` - Performance improvements

### Priority Labels

- `priority: high` - Critical issues
- `priority: medium` - Important issues
- `priority: low` - Nice to have

## 🔒 Security

- **Never commit** sensitive data
- **Review security implications** of changes
- **Report security issues** privately
- **Follow security best practices**

## 📚 Documentation

### What to Document

- **New features** and how to use them
- **Configuration options**
- **API changes**
- **Breaking changes**
- **Examples and tutorials**

### Documentation Style

- Use **clear, simple language**
- Include **code examples**
- Add **screenshots** where helpful
- Keep **up to date** with code changes

## 🎉 Recognition

Contributors will be recognized in:

- **README.md** contributors section
- **CHANGELOG.md** for significant contributions
- **GitHub releases** notes

## 📞 Getting Help

- **GitHub Discussions** for questions
- **GitHub Issues** for bugs and features
- **Discord/Telegram** for real-time chat (if available)

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to make this project better! 🚀** 