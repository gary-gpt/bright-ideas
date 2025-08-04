# Bright Ideas Development Makefile

.PHONY: help setup install-backend install-frontend install dev dev-backend dev-frontend build test lint clean docker-up docker-down

help: ## Show this help message
	@echo "Bright Ideas - Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Initial setup - create virtual environment and install dependencies  
	@echo "Setting up Bright Ideas development environment..."
	python -m venv .venv
	@echo "Virtual environment created. Activate with: source .venv/bin/activate"
	@echo "Then run: make install"

install: install-backend install-frontend ## Install all dependencies

install-backend: ## Install backend dependencies
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

dev: ## Start both backend and frontend in development mode
	@echo "Starting development servers..."
	make -j2 dev-backend dev-frontend

dev-backend: ## Start backend development server
	@echo "Starting FastAPI backend..."
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start frontend development server
	@echo "Starting SvelteKit frontend..."
	cd frontend && npm run dev

build: ## Build frontend for production
	@echo "Building frontend..."
	cd frontend && npm run build

test: ## Run tests
	@echo "Running backend tests..."
	cd backend && python -m pytest
	@echo "Running frontend checks..."
	cd frontend && npm run check

lint: ## Run linting
	@echo "Linting backend..."
	cd backend && python -m flake8 . || true
	@echo "Linting frontend..."
	cd frontend && npm run lint || true

format: ## Format code
	@echo "Formatting backend..."
	cd backend && python -m black . || true
	@echo "Formatting frontend..."
	cd frontend && npm run format || true

clean: ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	rm -rf backend/__pycache__
	rm -rf backend/.pytest_cache
	rm -rf frontend/node_modules
	rm -rf frontend/.svelte-kit
	rm -rf frontend/build

docker-up: ## Start services with Docker Compose
	@echo "Starting services with Docker Compose..."
	docker-compose up -d

docker-down: ## Stop Docker Compose services
	@echo "Stopping Docker Compose services..."
	docker-compose down

docker-logs: ## View Docker Compose logs
	docker-compose logs -f

# Database commands
db-migrate: ## Run database migrations
	@echo "Running database migrations..."
	cd backend && alembic upgrade head

db-revision: ## Create new database migration
	@echo "Creating new migration..."
	cd backend && alembic revision --autogenerate -m "$(MSG)"

db-reset: ## Reset database (DANGER: drops all data)
	@echo "WARNING: This will drop all database data!"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ]
	cd backend && alembic downgrade base
	cd backend && alembic upgrade head

# Environment setup
env-setup: ## Copy environment files from examples
	@echo "Setting up environment files..."
	cp backend/.env.example backend/.env
	cp frontend/.env.example frontend/.env
	@echo "Please edit the .env files with your configuration"

# Deployment helpers
deploy-check: ## Check if ready for deployment
	@echo "Checking deployment readiness..."
	@echo "✓ Backend requirements check"
	cd backend && pip check
	@echo "✓ Frontend build check"
	cd frontend && npm run build
	@echo "✓ Environment variables check"
	@test -f backend/.env || (echo "❌ backend/.env missing" && exit 1)
	@echo "✅ Ready for deployment"