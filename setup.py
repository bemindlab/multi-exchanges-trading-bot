#!/usr/bin/env python3
"""
Setup script for Multi-Exchange Trading Bot

This setup.py is maintained for backward compatibility.
The main configuration is in pyproject.toml.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
def read_requirements(filename):
    """Read requirements from file."""
    requirements_path = this_directory / filename
    if requirements_path.exists():
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

# Main dependencies
install_requires = read_requirements('requirements.txt')

# Optional dependencies
hummingbot_requires = read_requirements('requirements_hummingbot.txt')

# Development dependencies
dev_requires = [
    'pytest>=7.0.0',
    'pytest-cov>=4.0.0',
    'pytest-asyncio>=0.21.0',
    'black>=22.0.0',
    'isort>=5.10.0',
    'flake8>=5.0.0',
    'mypy>=0.991',
    'pre-commit>=2.20.0',
]

# Monitoring dependencies
monitoring_requires = [
    'prometheus-client>=0.14.0',
    'grafana-api>=1.0.0',
]

# Notification dependencies
notifications_requires = [
    'python-telegram-bot>=20.0',
    'discord-webhook>=1.0.0',
]

setup(
    name="multi-exchanges-trading-bot",
    version="2.1.0",
    author="Bemind Technology Co., Ltd.",
    author_email="info@bemind.tech",
    description="A comprehensive trading bot system for managing multiple exchanges",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/multi-exchanges-trading-bot",
    project_urls={
        "Bug Tracker": "https://github.com/your-username/multi-exchanges-trading-bot/issues",
        "Documentation": "https://github.com/your-username/multi-exchanges-trading-bot/docs",
        "Source Code": "https://github.com/your-username/multi-exchanges-trading-bot",
        "Changelog": "https://github.com/your-username/multi-exchanges-trading-bot/blob/main/CHANGELOG.md",
    },
    packages=find_packages(include=['src', 'src.*']),
    package_dir={'': '.'},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require={
        'dev': dev_requires,
        'hummingbot': hummingbot_requires,
        'monitoring': monitoring_requires,
        'notifications': notifications_requires,
        'all': dev_requires + hummingbot_requires + monitoring_requires + notifications_requires,
    },
    entry_points={
        'console_scripts': [
            'trading-bot=src.main:main',
            'trading-bot-cli=cli:main',
        ],
    },
    include_package_data=True,
    package_data={
        'src': ['*.json', '*.yaml', '*.yml', '*.toml'],
        '': ['*.md', '*.txt', '*.cfg', '*.ini'],
    },
    zip_safe=False,
    keywords=[
        'trading', 'bot', 'cryptocurrency', 'exchange', 'hummingbot', 
        'mqtt', 'arbitrage', 'macd', 'risk-management', 'binance', 
        'kucoin', 'gate.io', 'automated-trading'
    ],
    platforms=['any'],
    license='MIT',
) 