# Makefile for Multi-Exchange Trading Bot
# =====================================

.PHONY: help install install-dev test test-unit test-integration test-performance test-security
.PHONY: lint format type-check security-check clean build docs
.PHONY: run-manual run-macd run-webhook setup-env
.PHONY: docker-build docker-run docker-compose-dev docker-compose-prod docker-compose-test
.PHONY: compose-up compose-down compose-restart compose-logs compose-ps compose-clean

# Default target
help: ## Show this help message
	@echo "Multi-Exchange Trading Bot - Available Commands:"
	@echo "================================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation
install: ## Install production dependencies
	pip install -r requirements.txt
	pip install -r requirements_hummingbot.txt
	pip install -e .

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install -r requirements_hummingbot.txt
	pip install -e ".[dev]"
	pre-commit install

# Testing
test: ## Run all tests
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

test-unit: ## Run unit tests only
	pytest tests/unit/ -v -m "unit"

test-integration: ## Run integration tests only
	pytest tests/integration/ -v -m "integration"

test-performance: ## Run performance tests only
	pytest tests/performance/ -v -m "performance"

test-security: ## Run security tests only
	pytest tests/security/ -v -m "security"

test-fast: ## Run fast tests only (exclude slow tests)
	pytest tests/ -v -m "not slow"

test-coverage: ## Generate test coverage report
	pytest tests/ --cov=src --cov-report=html --cov-report=term --cov-report=xml
	@echo "Coverage report generated in htmlcov/index.html"

# Code Quality
lint: ## Run linting checks
	flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503
	pylint src/ --rcfile=.pylintrc || true

format: ## Format code with black and isort
	black src/ tests/ --line-length=88
	isort src/ tests/ --profile=black

format-check: ## Check code formatting
	black src/ tests/ --check --line-length=88
	isort src/ tests/ --check-only --profile=black

type-check: ## Run type checking with mypy
	mypy src/ --ignore-missing-imports

security-check: ## Run security checks
	bandit -r src/ -f json -o security-report.json || true
	safety check --json --output safety-report.json || true

pre-commit: ## Run pre-commit hooks on all files
	pre-commit run --all-files

# Development
clean: ## Clean up build artifacts and cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: ## Build the package
	python -m build

docs: ## Generate documentation
	@echo "Generating documentation..."
	@echo "API documentation available in docs/"

# Environment Setup
setup-env: ## Setup development environment
	python -m venv venv
	@echo "Virtual environment created. Activate with:"
	@echo "source venv/bin/activate  # Linux/Mac"
	@echo "venv\\Scripts\\activate     # Windows"

create-config: ## Create configuration file from template
	python main.py --create-config

# Application Commands
run-manual: ## Run manual trading mode (requires additional args)
	@echo "Usage: make run-manual ARGS='--action buy --pair BTC_USDT --amount 100'"
	@echo "Example: make run-manual ARGS='--action buy --pair BTC_USDT --amount 100 --max-daily-loss 200'"
	python main.py --mode manual $(ARGS)

run-macd: ## Run MACD strategy mode (requires additional args)
	@echo "Usage: make run-macd ARGS='--pairs BTC_USDT ETH_USDT --interval 60 --trade-amount 50'"
	python main.py --mode macd $(ARGS)

run-webhook: ## Run webhook server mode
	python main.py --mode webhook

run-cli: ## Run CLI interface
	python cli.py $(ARGS)

# Docker Commands
docker-build: ## Build Docker image
	docker build -t multi-exchange-trading-bot .

docker-run: ## Run Docker container
	docker run -it --rm -v $(PWD)/config:/app/config multi-exchange-trading-bot

# =============================================================================
# Docker Compose Environment Management
# =============================================================================

# Environment Variables
ENV ?= dev
COMPOSE_FILE_DEV = docker-compose.yml
COMPOSE_FILE_PROD = docker-compose.prod.yml
COMPOSE_FILE_TEST = docker-compose.test.yml
COMPOSE_PROJECT_NAME = trading-bot

# Docker Compose - Development Environment
compose-dev-up: ## 🚀 Start development environment
	@echo "🚀 Starting development environment..."
	docker-compose -f docker-compose.yml -p trading-bot-dev up -d
	@echo "✅ Development environment started"
	@echo "📊 Dashboard: http://localhost:8080"
	@echo "📡 MQTT Broker: localhost:1883"
	@echo "🗄️  Database: localhost:5432"
	@echo "🔄 n8n Workflows: http://localhost:5678"

compose-dev-down: ## 🛑 Stop development environment
	@echo "🛑 Stopping development environment..."
	docker-compose -f docker-compose.yml -p trading-bot-dev down
	@echo "✅ Development environment stopped"

compose-dev-logs: ## 📋 Show development environment logs
	docker-compose -f docker-compose.yml -p trading-bot-dev logs -f

compose-dev-restart: compose-dev-down compose-dev-up ## 🔄 Restart development environment

# Docker Compose - Production Environment
compose-prod-up: ## 🚀 Start production environment
	@echo "🚀 Starting production environment..."
	docker-compose -f docker-compose.prod.yml -p trading-bot-prod up -d
	@echo "✅ Production environment started"

compose-prod-down: ## 🛑 Stop production environment
	@echo "🛑 Stopping production environment..."
	docker-compose -f docker-compose.prod.yml -p trading-bot-prod down
	@echo "✅ Production environment stopped"

compose-prod-logs: ## 📋 Show production environment logs
	docker-compose -f docker-compose.prod.yml -p trading-bot-prod logs -f

compose-prod-restart: compose-prod-down compose-prod-up ## 🔄 Restart production environment

# Docker Compose - Test Environment
compose-test-up: ## 🧪 Start test environment
	@echo "🧪 Starting test environment..."
	docker-compose -f docker-compose.test.yml -p trading-bot-test up -d postgres-test redis-test mqtt-test
	@echo "✅ Test environment started"

compose-test-down: ## 🛑 Stop test environment
	@echo "🛑 Stopping test environment..."
	docker-compose -f docker-compose.test.yml -p trading-bot-test down
	@echo "✅ Test environment stopped"

compose-test-run: ## 🧪 Run all tests
	@echo "🧪 Running all tests..."
	docker-compose -f docker-compose.test.yml -p trading-bot-test run --rm test-runner

compose-test-unit: ## 🧪 Run unit tests only
	@echo "🧪 Running unit tests..."
	docker-compose -f docker-compose.test.yml -p trading-bot-test run --rm unit-tests

compose-test-integration: ## 🧪 Run integration tests only
	@echo "🧪 Running integration tests..."
	docker-compose -f docker-compose.test.yml -p trading-bot-test run --rm integration-tests

compose-test-n8n: ## 🔄 Run n8n workflow tests
	@echo "🔄 Running n8n workflow tests..."
	docker-compose -f docker-compose.test.yml -p trading-bot-test --profile n8n --profile workflow up -d
	docker-compose -f docker-compose.test.yml -p trading-bot-test run --rm n8n-workflow-tests

# Generic Commands (accepts ENV parameter: dev, prod, test)
compose-up: ## 🚀 Start environment (ENV=dev|prod|test)
	@if [ "$(ENV)" = "prod" ]; then \
		$(MAKE) compose-prod-up; \
	elif [ "$(ENV)" = "test" ]; then \
		$(MAKE) compose-test-up; \
	else \
		$(MAKE) compose-dev-up; \
	fi

compose-down: ## 🛑 Stop environment (ENV=dev|prod|test)
	@if [ "$(ENV)" = "prod" ]; then \
		$(MAKE) compose-prod-down; \
	elif [ "$(ENV)" = "test" ]; then \
		$(MAKE) compose-test-down; \
	else \
		$(MAKE) compose-dev-down; \
	fi

compose-logs: ## 📋 Show environment logs (ENV=dev|prod|test)
	@if [ "$(ENV)" = "prod" ]; then \
		$(MAKE) compose-prod-logs; \
	elif [ "$(ENV)" = "test" ]; then \
		docker-compose -f docker-compose.test.yml -p trading-bot-test logs -f; \
	else \
		$(MAKE) compose-dev-logs; \
	fi

compose-restart: ## 🔄 Restart environment (ENV=dev|prod|test)
	@if [ "$(ENV)" = "prod" ]; then \
		$(MAKE) compose-prod-restart; \
	elif [ "$(ENV)" = "test" ]; then \
		$(MAKE) compose-test-down compose-test-up; \
	else \
		$(MAKE) compose-dev-restart; \
	fi

# Maintenance Commands
compose-clean: ## 🧹 Clean up Docker resources
	@echo "🧹 Cleaning up Docker resources..."
	docker system prune -f
	docker volume prune -f
	@echo "✅ Cleanup completed"

compose-rebuild: ## 🔨 Rebuild and restart environment (ENV=dev|prod|test)
	@echo "🔨 Rebuilding environment..."
	@if [ "$(ENV)" = "prod" ]; then \
		docker-compose -f docker-compose.prod.yml -p trading-bot-prod down; \
		docker-compose -f docker-compose.prod.yml -p trading-bot-prod build --no-cache; \
		docker-compose -f docker-compose.prod.yml -p trading-bot-prod up -d; \
	elif [ "$(ENV)" = "test" ]; then \
		docker-compose -f docker-compose.test.yml -p trading-bot-test down; \
		docker-compose -f docker-compose.test.yml -p trading-bot-test build --no-cache; \
		docker-compose -f docker-compose.test.yml -p trading-bot-test up -d postgres-test redis-test mqtt-test; \
	else \
		docker-compose -f docker-compose.yml -p trading-bot-dev down; \
		docker-compose -f docker-compose.yml -p trading-bot-dev build --no-cache; \
		docker-compose -f docker-compose.yml -p trading-bot-dev up -d; \
	fi
	@echo "✅ Rebuild completed"

compose-backup: ## 💾 Backup database and volumes
	@echo "💾 Creating backup..."
	mkdir -p ./backups/$(shell date +%Y%m%d_%H%M%S)
	docker-compose -f docker-compose.prod.yml -p trading-bot-prod --profile backup run --rm backup
	@echo "✅ Backup completed"

compose-shell: ## 🐚 Access container shell (SERVICE=service_name ENV=dev|prod|test)
	@if [ -z "$(SERVICE)" ]; then \
		echo "❌ Please specify SERVICE=service_name"; \
		exit 1; \
	fi
	@if [ "$(ENV)" = "prod" ]; then \
		docker-compose -f docker-compose.prod.yml -p trading-bot-prod exec $(SERVICE) sh; \
	elif [ "$(ENV)" = "test" ]; then \
		docker-compose -f docker-compose.test.yml -p trading-bot-test exec $(SERVICE) sh; \
	else \
		docker-compose -f docker-compose.yml -p trading-bot-dev exec $(SERVICE) sh; \
	fi

compose-health: ## 🏥 Check health status of all services
	@echo "🏥 Checking service health..."
	@if [ "$(ENV)" = "prod" ]; then \
		docker-compose -f docker-compose.prod.yml -p trading-bot-prod ps; \
	elif [ "$(ENV)" = "test" ]; then \
		docker-compose -f docker-compose.test.yml -p trading-bot-test ps; \
	else \
		docker-compose -f docker-compose.yml -p trading-bot-dev ps; \
	fi

compose-stats: ## 📊 Show resource usage statistics
	@echo "📊 Resource usage statistics:"
	docker stats --no-stream

# n8n Specific Commands
n8n-dev: ## 🔄 Access n8n development interface
	@echo "🔄 Opening n8n development interface..."
	@echo "URL: http://localhost:5678"
	@echo "Username: admin"
	@echo "Password: n8n_pass"

n8n-prod: ## 🔄 Access n8n production interface
	@echo "🔄 n8n production interface info:"
	@echo "URL: https://your-domain.com/n8n"
	@echo "Check secrets for credentials"

n8n-backup: ## 💾 Backup n8n workflows and data
	@echo "💾 Backing up n8n data..."
	mkdir -p ./backups/n8n/$(shell date +%Y%m%d_%H%M%S)
	@if [ "$(ENV)" = "prod" ]; then \
		docker-compose -f docker-compose.prod.yml -p trading-bot-prod exec n8n n8n export:workflow --backup --output=/home/node/.n8n/backups/; \
	else \
		docker-compose -f docker-compose.yml -p trading-bot-dev exec n8n n8n export:workflow --backup --output=/home/node/.n8n/backups/; \
	fi
	@echo "✅ n8n backup completed"

n8n-restore: ## 🔄 Restore n8n workflows from backup
	@echo "🔄 Restoring n8n workflows..."
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "❌ Please specify BACKUP_FILE=path/to/backup.json"; \
		exit 1; \
	fi
	@if [ "$(ENV)" = "prod" ]; then \
		docker-compose -f docker-compose.prod.yml -p trading-bot-prod exec n8n n8n import:workflow --input=$(BACKUP_FILE); \
	else \
		docker-compose -f docker-compose.yml -p trading-bot-dev exec n8n n8n import:workflow --input=$(BACKUP_FILE); \
	fi
	@echo "✅ n8n restore completed"

# Help
compose-help: ## 📚 Show Docker Compose commands help
	@echo ""
	@echo "🐳 Docker Compose Environment Management"
	@echo "========================================"
	@echo ""
	@echo "📋 Available Environments:"
	@echo "  • dev  - Development environment (default)"
	@echo "  • prod - Production environment"
	@echo "  • test - Testing environment"
	@echo ""
	@echo "🚀 Quick Start Commands:"
	@echo "  make compose-dev-up     - Start development environment"
	@echo "  make compose-prod-up    - Start production environment"
	@echo "  make compose-test-run   - Run all tests"
	@echo ""
	@echo "🔄 n8n Workflow Automation:"
	@echo "  make n8n-dev           - Access n8n development interface"
	@echo "  make n8n-backup        - Backup n8n workflows"
	@echo "  make compose-test-n8n  - Test n8n workflows"
	@echo ""
	@echo "📊 Services Included:"
	@echo "  • Trading Bot (ports 8000, 8080)"
	@echo "  • PostgreSQL Database (port 5432)"
	@echo "  • Redis Cache (port 6379)"
	@echo "  • MQTT Broker (ports 1883, 9001)"
	@echo "  • n8n Workflows (port 5678)"
	@echo "  • Hummingbot instance"
	@echo "  • Grafana Dashboard (port 3000)"
	@echo "  • Prometheus Monitoring (port 9090)"
	@echo "  • Nginx Reverse Proxy (ports 80, 443)"
	@echo ""
	@echo "🛠️  Generic Commands (use ENV=dev|prod|test):"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "(compose-|n8n-)"
	@echo ""
	@echo "💡 Examples:"
	@echo "  make compose-up ENV=prod              - Start production environment"
	@echo "  make compose-shell SERVICE=trading-bot - Access trading bot shell"
	@echo "  make compose-logs ENV=test            - Show test environment logs"
	@echo "  make n8n-backup ENV=prod              - Backup production n8n workflows"
	@echo ""

# Variables for customization
PYTHON := python
PIP := pip
PYTEST := pytest
BLACK := black
ISORT := isort
FLAKE8 := flake8
MYPY := mypy
BANDIT := bandit 