# ============================================
# CP'S Enterprise POS - Makefile
# ============================================

.PHONY: help install dev test lint format clean docker-up docker-down migrate seed

# Default target
help:
	@echo "CP'S Enterprise POS - Available Commands:"
	@echo ""
	@echo "  make install      - Install Python dependencies"
	@echo "  make dev          - Run development server"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make docker-up    - Start Docker services"
	@echo "  make docker-down  - Stop Docker services"
	@echo "  make migrate      - Run database migrations"
	@echo "  make seed         - Seed database with sample data"
	@echo ""

# ============================================
# Development
# ============================================

install:
	cd backend && pip install -r requirements.txt

dev:
	cd backend && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# ============================================
# Testing
# ============================================

test:
	cd backend && pytest -v

test-coverage:
	cd backend && pytest --cov=src --cov-report=html --cov-report=term

test-watch:
	cd backend && ptw

# ============================================
# Code Quality
# ============================================

lint:
	cd backend && flake8 src tests
	cd backend && mypy src

format:
	cd backend && black src tests
	cd backend && isort src tests

format-check:
	cd backend && black --check src tests
	cd backend && isort --check-only src tests

# ============================================
# Database
# ============================================

migrate:
	cd backend && alembic upgrade head

migrate-create:
	@read -p "Enter migration message: " message; \
	cd backend && alembic revision --autogenerate -m "$$message"

migrate-downgrade:
	cd backend && alembic downgrade -1

seed:
	cd backend && python -m scripts.seed_data

# ============================================
# Docker
# ============================================

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-build:
	docker-compose build

docker-clean:
	docker-compose down -v
	docker system prune -f

# ============================================
# Utilities
# ============================================

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.egg-info" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +

env:
	cp .env.example .env

# ============================================
# Production
# ============================================

prod-build:
	docker-compose -f docker-compose.prod.yml build

prod-up:
	docker-compose -f docker-compose.prod.yml up -d

prod-down:
	docker-compose -f docker-compose.prod.yml down

# ============================================
# Kubernetes
# ============================================

k8s-apply:
	kubectl apply -f infrastructure/kubernetes/

k8s-delete:
	kubectl delete -f infrastructure/kubernetes/

k8s-status:
	kubectl get pods -n cps-enterprise

# ============================================
# Documentation
# ============================================

docs-serve:
	cd docs && mkdocs serve

docs-build:
	cd docs && mkdocs build
