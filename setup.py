from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gate-trading-bot",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A trading bot for Gate.io with MACD strategy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/gate-trading-bot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "flask>=3.0.2",
        "gate-api>=4.5.0",
        "python-dotenv>=1.0.1",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
    ],
    entry_points={
        "console_scripts": [
            "gate-bot=gate_bot.cli:main",
        ],
    },
) 