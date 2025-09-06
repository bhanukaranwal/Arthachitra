# Arthachitra Trading Platform Makefile

.PHONY: help install dev build test clean deploy backup monitor

# Default target
help:
	@echo "Arthachitra (अर्थचित्र) Trading Platform"
	@echo "========================================"
	@echo ""
	@echo "Available commands:"
	@echo "  install     - Install all dependencies"
	@echo "  dev         - Start development environment"
	@echo "  build       - Build all services"
	@echo "  test        - Run all tests"
	@echo "  clean       - Clean build artifacts"
	@echo "  deploy      - Deploy to production"
	@echo "  backup      - Create system backup"
	@echo "  monitor     - Start monitoring stack"
	@echo "  help        - Show this help message"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing ML dependencies..."
	cd ml && pip install -r requirements.txt
	@echo "Building C++ tick engine..."
	cd tick_engine && mkdir -p build && cd build && cmake .. && make
	@echo "✅ All dependencies installed!"

# Development environment
dev:
	@echo "🚀 Starting development environment..."
	docker-compose -f docker-compose.dev.yml up -d
	@echo "✅ Development environment started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

# Build all services
build:
	@echo "🔨 Building all services..."
	docker-compose build
	@echo "✅ Build completed!"

# Run tests
test:
	@echo "🧪 Running tests..."
	@echo "Running frontend tests..."
	cd frontend && npm test
	@echo "Running backend tests..."
	cd backend && python -m pytest
	@echo "Running ML tests..."
	cd ml && python -m pytest
	@echo "Running C++ tests..."
	cd tick_engine/build && make test && ctest
	@echo "✅ All tests passed!"

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	docker system prune -f
	cd frontend && rm -rf .next node_modules/.cache
	cd backend && find . -type d -name __pycache__ -delete
	cd tick_engine && rm -rf build
	@echo "✅ Cleanup completed!"

# Deploy to production
deploy:
	@echo "🚀 Deploying to production..."
	@read -p "Are you sure you want to deploy to production? (y/N): " confirm && [ "$$confirm" = "y" ]
	docker-compose -f docker-compose.prod.yml build
	docker-compose -f docker-compose.prod.yml up -d
	@echo "✅ Deployment completed!"

# Create backup
backup:
	@echo "💾 Creating system backup..."
	./scripts/backup.sh
	@echo "✅ Backup completed!"

# Start monitoring
monitor:
	@echo "📊 Starting monitoring stack..."
	docker-compose -f deploy/monitoring/docker-compose.yml up -d
	@echo "✅ Monitoring started!"
	@echo "Prometheus: http://localhost:9090"
	@echo "Grafana: http://localhost:3001"

# Development shortcuts
frontend:
	cd frontend && npm run dev

backend:
	cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

ml-service:
	cd ml && python inference/api_server.py

tick-engine:
	cd tick_engine/build && ./tick_engine

# Database operations
db-migrate:
	cd backend && python -m alembic upgrade head

db-seed:
	cd backend && python database/seed_data.py

db-reset:
	cd backend && python -m alembic downgrade base && python -m alembic upgrade head && python database/seed_data.py

# Linting and formatting
lint:
	cd frontend && npm run lint
	cd backend && black . && isort . && flake8 .

# Security checks
security:
	cd frontend && npm audit
	cd backend && safety check
	cd backend && bandit -r .

# Performance tests
perf:
	cd tests && locust -f load/test_api.py --host=http://localhost:8000

# Documentation
docs:
	cd docs && make html

# Quick setup for new developers
setup-dev:
	@echo "🎯 Setting up development environment..."
	./scripts/setup.sh
	make install
	make db-migrate
	make db-seed
	@echo "✅ Development setup completed!"
	@echo "Run 'make dev' to start the development environment"

# Version management
version:
	@echo "Current version: $(shell grep version package.json | head -1 | awk -F: '{ print $$2 }' | sed 's/[", ]//g')"

# Health check
health:
	@echo "🔍 Checking system health..."
	./scripts/monitor.sh
	@echo "Health check completed!"
