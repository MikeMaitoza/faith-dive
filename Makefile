# Faith Dive Makefile
# Convenience commands for development and testing

.PHONY: help install test test-unit test-api test-integration test-performance test-quick test-all test-parallel coverage benchmark lint format clean build run

# Default target
help:
	@echo "Faith Dive - Available Commands:"
	@echo ""
	@echo "Setup:"
	@echo "  install     - Install dependencies with Poetry"
	@echo "  clean       - Clean build artifacts and cache files"
	@echo ""
	@echo "Development:"
	@echo "  run         - Run the development server"
	@echo "  build       - Build the frontend"
	@echo ""
	@echo "Testing:"
	@echo "  test        - Run all tests with coverage"
	@echo "  test-quick  - Run quick tests (excludes slow/performance)"
	@echo "  test-unit   - Run unit tests only"
	@echo "  test-api    - Run API tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-performance - Run performance tests only"
	@echo "  test-parallel    - Run tests in parallel"
	@echo "  benchmark   - Run benchmark tests"
	@echo ""
	@echo "Quality:"
	@echo "  coverage    - Generate coverage report"
	@echo "  lint        - Run linting and type checking"
	@echo "  format      - Format code (if formatter available)"
	@echo ""
	@echo "Examples:"
	@echo "  make install && make test-quick"
	@echo "  make coverage"
	@echo "  make test-api"

# Installation
install:
	@echo "📦 Installing dependencies..."
	poetry install --with dev

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf .pytest_cache/
	rm -rf backend/__pycache__/
	rm -rf tests/__pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	rm -rf frontend/build/
	rm -f *.db *.db-journal

# Development
run:
	@echo "🚀 Starting Faith Dive server..."
	poetry run python run.py

build:
	@echo "🔨 Building frontend..."
	python build_frontend.py

# Testing
test: test-all

test-all:
	@echo "🧪 Running all tests with coverage..."
	python scripts/run_tests.py --all

test-quick:
	@echo "⚡ Running quick tests..."
	python scripts/run_tests.py --quick

test-unit:
	@echo "🔍 Running unit tests..."
	python scripts/run_tests.py --unit

test-api:
	@echo "🌐 Running API tests..."
	python scripts/run_tests.py --api

test-integration:
	@echo "🔗 Running integration tests..."
	python scripts/run_tests.py --integration

test-performance:
	@echo "⚡ Running performance tests..."
	python scripts/run_tests.py --performance

test-parallel:
	@echo "🚀 Running tests in parallel..."
	python scripts/run_tests.py --parallel

benchmark:
	@echo "📊 Running benchmark tests..."
	python scripts/run_tests.py --benchmark

# Quality
coverage:
	@echo "📈 Generating coverage report..."
	python scripts/run_tests.py --coverage

lint:
	@echo "🔍 Running linting and type checking..."
	python scripts/run_tests.py --lint

format:
	@echo "✨ Formatting code..."
	@echo "Note: Add your preferred formatter here (black, autopep8, etc.)"

# CI/CD helpers
ci-test:
	@echo "🤖 Running CI test suite..."
	make install
	make test-quick
	make coverage

ci-full:
	@echo "🤖 Running full CI suite..."
	make install
	make lint
	make test-all

# Docker helpers (if using Docker)
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t faith-dive .

docker-test:
	@echo "🐳 Running tests in Docker..."
	docker run --rm faith-dive make test-quick

# Database helpers
db-reset:
	@echo "🗃️  Resetting database..."
	rm -f faith_dive.db faith_dive.db-journal
	poetry run alembic upgrade head

# Development shortcuts
dev: install build run

full-test: clean install test-all

quick-check: test-quick lint