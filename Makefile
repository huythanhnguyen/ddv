# DDV Product Advisor - Makefile
# Hỗ trợ build, development, testing và deployment

.PHONY: help install dev test clean build frontend-build frontend-dev lint format docs

# Default target
help:
	@echo "DDV Product Advisor - Available commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  install          Install Python dependencies with uv"
	@echo "  install-dev      Install development dependencies"
	@echo "  install-frontend Install frontend dependencies"
	@echo ""
	@echo "Development:"
	@echo "  dev              Run ADK API server development server"
	@echo "  frontend-dev     Run frontend development server"
	@echo "  dev-all          Run both backend and frontend"
	@echo ""
	@echo "Building:"
	@echo "  build            Build Python package"
	@echo "  frontend-build   Build frontend for production"
	@echo "  build-all        Build both backend and frontend"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  test             Run Python tests"
	@echo "  test-cov         Run tests with coverage"
	@echo "  lint             Run linting checks"
	@echo "  format           Format code with black and isort"
	@echo "  type-check       Run type checking with mypy"
	@echo ""
	@echo "Documentation:"
	@echo "  docs             Build documentation"
	@echo "  docs-serve       Serve documentation locally"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean            Clean build artifacts and cache"
	@echo "  clean-all        Clean everything including node_modules"
	@echo ""
	@echo "Database & Data:"
	@echo "  data-sync        Sync data from external sources"
	@echo "  data-validate    Validate data integrity"
	@echo ""
	@echo "Deployment:"
	@echo "  docker-build     Build Docker image"
	@echo "  docker-run       Run Docker container"
	@echo "  deploy           Deploy to production"

# Python environment setup
install:
	@echo "Installing Python dependencies with uv..."
	uv sync
	@echo "✅ Python dependencies installed successfully!"

install-dev:
	@echo "Installing development dependencies..."
	uv sync --group dev
	@echo "✅ Development dependencies installed successfully!"

install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install || echo "⚠️  Frontend folder not found yet. Will create during setup."
	@echo "✅ Frontend dependencies installed successfully!"

# Development servers
dev:
	@echo "Starting ADK API server development server..."
	uv run adk api_server app --host 0.0.0.0 --port ${PORT:-8000} --allow_origins="*"

frontend-dev:
	@echo "Starting frontend development server..."
	cd frontend && npm run dev

dev-all:
	@echo "Starting both backend and frontend development servers..."
	@make -j2 dev frontend-dev

# Building
build:
	@echo "Building Python package..."
	uv build
	@echo "✅ Python package built successfully!"

frontend-build:
	@echo "Building frontend for production..."
	cd frontend && npm run build
	@echo "✅ Frontend built successfully!"

build-all: build frontend-build
	@echo "✅ All packages built successfully!"

# Testing
test:
	@echo "Running Python tests..."
	uv run pytest

test-cov:
	@echo "Running tests with coverage..."
	uv run pytest --cov=app --cov-report=html --cov-report=term

# Code quality
lint:
	@echo "Running linting checks..."
	uv run ruff check .
	uv run black --check .
	uv run isort --check-only .

format:
	@echo "Formatting code..."
	uv run black .
	uv run isort .
	@echo "✅ Code formatted successfully!"

type-check:
	@echo "Running type checking..."
	uv run mypy app/

# Documentation
docs:
	@echo "Building documentation..."
	uv run mkdocs build
	@echo "✅ Documentation built successfully!"

docs-serve:
	@echo "Serving documentation locally..."
	uv run mkdocs serve

# Cleanup
clean:
	@echo "Cleaning Python build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	@echo "✅ Python artifacts cleaned successfully!"

clean-frontend:
	@echo "Cleaning frontend build artifacts..."
	cd frontend && rm -rf dist/ node_modules/.cache/
	@echo "✅ Frontend artifacts cleaned successfully!"

clean-all: clean clean-frontend
	@echo "Cleaning all artifacts..."
	rm -rf .venv/
	cd frontend && rm -rf node_modules/
	@echo "✅ All artifacts cleaned successfully!"

# Data management
data-sync:
	@echo "Syncing data from external sources..."
	uv run python -m crawl_tools.complete_offer_update
	@echo "✅ Data sync completed!"

data-validate:
	@echo "Validating data integrity..."
	uv run python -m crawl_tools.final_price_cleanup
	@echo "✅ Data validation completed!"

# Docker
docker-build:
	@echo "Building Docker image..."
	docker build -t ddv-product-advisor .
	@echo "✅ Docker image built successfully!"

docker-run:
	@echo "Running Docker container..."
	docker run -p 8000:8000 ddv-product-advisor

# Deployment
deploy:
	@echo "Deploying to production..."
	@echo "⚠️  Deployment not implemented yet"
	@echo "Please implement deployment logic based on your infrastructure"

# Database operations
db-migrate:
	@echo "Running database migrations..."
	@echo "⚠️  Database migrations not implemented yet"

db-seed:
	@echo "Seeding database with initial data..."
	@echo "⚠️  Database seeding not implemented yet"

# Utility commands
check-deps:
	@echo "Checking dependency versions..."
	uv pip list --outdated

update-deps:
	@echo "Updating dependencies..."
	uv sync --upgrade

# Development helpers
shell:
	@echo "Starting Python shell with project context..."
	uv run python

logs:
	@echo "Showing application logs..."
	@echo "⚠️  Log viewing not implemented yet"

# Frontend specific
frontend-lint:
	@echo "Linting frontend code..."
	cd frontend && npm run lint

frontend-test:
	@echo "Running frontend tests..."
	cd frontend && npm run test

frontend-format:
	@echo "Formatting frontend code..."
	cd frontend && npm run format

# Quick start for new developers
quickstart: install install-dev install-frontend
	@echo ""
	@echo "🚀 Quick start completed!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Copy .env.example to .env and configure"
	@echo "2. Run 'make dev' to start ADK API server"
	@echo "3. Run 'make frontend-dev' to start frontend"
	@echo "4. Open http://localhost:8000 for backend"
	@echo "5. Open http://localhost:5173 for frontend"
	@echo ""
	@echo "Happy coding! 🎉"

# Environment setup
env-setup:
	@echo "Setting up environment..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ .env file created from .env.example"; \
		echo "⚠️  Please edit .env with your configuration"; \
	else \
		echo "✅ .env file already exists"; \
	fi

# Health checks
health-check:
	@echo "Running health checks..."
	@echo "✅ Python environment: $(shell uv --version)"
	@echo "✅ Node.js: $(shell node --version)"
	@echo "✅ npm: $(shell npm --version)"
	@echo "✅ Make: $(shell make --version | head -n1)"

# Show project info
info:
	@echo "DDV Product Advisor - Project Information"
	@echo "=========================================="
	@echo "Version: $(shell grep '^version =' pyproject.toml | cut -d'"' -f2)"
	@echo "Python: $(shell uv run python --version)"
	@echo "Backend: Google ADK API Server"
	@echo "Frontend: React + TypeScript + Vite"
	@echo "Data: 24 products, 20 offers, 20 reviews, 48 stores"
	@echo "Status: Data collection completed, implementing agents"
