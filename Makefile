.PHONY: help install-frontend install-api install-analytics install-scripts install-all
.PHONY: dev-frontend dev-api dev-analytics dev-all
.PHONY: setup-frontend setup-api setup-analytics setup-scripts setup-all
.PHONY: clean-frontend clean-api clean-analytics clean-scripts clean-all
.PHONY: stop seed-stock
.PHONY: terraform-load-env terraform-init terraform-plan terraform-apply terraform-destroy terraform-output
.PHONY: build-push-api build-push-analytics build-push-frontend build-push-all

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

# Load environment variables from root .env file if it exists
ifneq (,$(wildcard .env))
    include .env
    export
endif

help: ## Show this help message
	@echo "$(BLUE)LoopWeave Development Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Setup Commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

# Installation targets
install-frontend: ## Install frontend dependencies
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	cd frontend && npm install

install-api: ## Install API backend dependencies
	@echo "$(BLUE)Installing API backend dependencies...$(NC)"
	cd backend/api && uv sync

install-analytics: ## Install Analytics backend dependencies
	@echo "$(BLUE)Installing Analytics backend dependencies...$(NC)"
	cd backend/analytics && uv sync

install-scripts: ## Install scripts dependencies
	@echo "$(BLUE)Installing scripts dependencies...$(NC)"
	cd scripts && uv sync

install-all: install-frontend install-api install-analytics install-scripts ## Install all dependencies

# Setup targets (install + env setup)
setup-frontend: install-frontend ## Setup frontend (install + create .env if needed)
	@if [ ! -f frontend/.env ]; then \
		echo "$(YELLOW)Creating frontend/.env from .env.example...$(NC)"; \
		cp frontend/.env.example frontend/.env 2>/dev/null || echo "$(YELLOW)No .env.example found, please create frontend/.env manually$(NC)"; \
	fi

setup-api: install-api ## Setup API backend (install + create .env if needed)
	@if [ ! -f backend/api/.env ]; then \
		echo "$(YELLOW)Creating backend/api/.env from .env.example...$(NC)"; \
		cp backend/api/.env.example backend/api/.env 2>/dev/null || echo "$(YELLOW)No .env.example found, please create backend/api/.env manually$(NC)"; \
	fi

setup-analytics: install-analytics ## Setup Analytics backend (install + create .env if needed)
	@if [ ! -f backend/analytics/.env ]; then \
		echo "$(YELLOW)Creating backend/analytics/.env from .env.example...$(NC)"; \
		cp backend/analytics/.env.example backend/analytics/.env 2>/dev/null || echo "$(YELLOW)No .env.example found, please create backend/analytics/.env manually$(NC)"; \
	fi

setup-scripts: install-scripts ## Setup scripts (install dependencies)
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Warning: Root .env file not found. Please create it with FMP_API_KEY, GCP_PROJECT_ID, etc.$(NC)"; \
	fi

setup-all: setup-frontend setup-api setup-analytics setup-scripts ## Setup all services

# Development server targets
dev-frontend: ## Start frontend development server
	@echo "$(GREEN)Starting frontend on http://localhost:3000$(NC)"
	cd frontend && npm run dev

dev-api: ## Start API backend development server
	@echo "$(GREEN)Starting API backend on http://localhost:8000$(NC)"
	cd backend/api && uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-analytics: ## Start Analytics backend development server
	@echo "$(GREEN)Starting Analytics backend on http://localhost:8001$(NC)"
	cd backend/analytics && uv run uvicorn main:app --reload --host 0.0.0.0 --port 8001

# Run all services in background
dev-all: ## Start all services (frontend + both backends)
	@echo "$(BLUE)Starting all services...$(NC)"
	@echo "$(GREEN)Frontend: http://localhost:3000$(NC)"
	@echo "$(GREEN)API: http://localhost:8000$(NC)"
	@echo "$(GREEN)Analytics: http://localhost:8001$(NC)"
	@echo "$(YELLOW)Press Ctrl+C to stop all services$(NC)"
	@trap 'kill 0' EXIT; \
	$(MAKE) dev-frontend & \
	$(MAKE) dev-api & \
	$(MAKE) dev-analytics & \
	wait

# Clean targets
clean-frontend: ## Clean frontend build artifacts
	@echo "$(BLUE)Cleaning frontend...$(NC)"
	cd frontend && rm -rf .next node_modules

clean-api: ## Clean API backend artifacts
	@echo "$(BLUE)Cleaning API backend...$(NC)"
	cd backend/api && rm -rf .uv __pycache__ *.pyc

clean-analytics: ## Clean Analytics backend artifacts
	@echo "$(BLUE)Cleaning Analytics backend...$(NC)"
	cd backend/analytics && rm -rf .uv __pycache__ *.pyc

clean-scripts: ## Clean scripts artifacts
	@echo "$(BLUE)Cleaning scripts...$(NC)"
	cd scripts && rm -rf .uv __pycache__ *.pyc

clean-all: clean-frontend clean-api clean-analytics clean-scripts ## Clean all build artifacts

# Stop all running services
stop: ## Stop all running development servers
	@echo "$(YELLOW)Stopping all services...$(NC)"
	@pkill -f "next dev" || true
	@pkill -f "uvicorn" || true
	@echo "$(GREEN)All services stopped$(NC)"

# Quick start (setup + run all)
start: setup-all dev-all ## Setup and start all services

# Data seeding
seed-stock: setup-scripts ## Seed BigQuery with historical stock data (usage: make seed-stock SYMBOL=AAPL)
	@if [ -z "$(SYMBOL)" ]; then \
		echo "$(YELLOW)Usage: make seed-stock SYMBOL=AAPL$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Seeding BigQuery with historical data for $(SYMBOL)...$(NC)"
	cd scripts && uv run seed-stock-data.py $(SYMBOL)

# Terraform targets
tf-load-env: ## Generate terraform.tfvars from .env file
	@echo "$(BLUE)Loading environment variables from .env...$(NC)"
	./terraform/load-env.sh

tf-init: terraform-load-env ## Initialize Terraform
	@echo "$(BLUE)Initializing Terraform...$(NC)"
	cd terraform && terraform init

tf-plan: terraform-init ## Plan Terraform changes
	@echo "$(BLUE)Planning Terraform changes...$(NC)"
	cd terraform && terraform plan

tf-apply: terraform-init ## Apply Terraform changes (use AUTO_APPROVE=true to skip confirmation)
	@echo "$(BLUE)Applying Terraform changes...$(NC)"
	cd terraform && terraform apply -auto-approve


tf-destroy: terraform-init ## Destroy Terraform infrastructure
	@echo "$(YELLOW)Destroying Terraform infrastructure...$(NC)"
	cd terraform && terraform destroy

tf-output: terraform-init ## Show Terraform outputs
	@echo "$(BLUE)Terraform outputs:$(NC)"
	cd terraform && terraform output

# Docker build and push targets (for use after Terraform creates infrastructure)
build-push-api: ## Build and push API Docker image
	@echo "$(BLUE)Building and pushing API image...$(NC)"
	@if [ -z "$(GCP_PROJECT_ID)" ]; then \
		echo "$(YELLOW)GCP_PROJECT_ID not set, trying gcloud config...$(NC)"; \
		GCP_PROJECT_ID=$$(gcloud config get-value project 2>/dev/null); \
	fi; \
	if [ -z "$$GCP_PROJECT_ID" ]; then \
		echo "$(YELLOW)Error: GCP_PROJECT_ID not set$(NC)"; \
		exit 1; \
	fi; \
	REGION=$${GCP_REGION:-us-central1}; \
	IMAGE="$$REGION-docker.pkg.dev/$$GCP_PROJECT_ID/loopweave/loopweave-api:latest"; \
	cd backend/api && docker build -t $$IMAGE . && docker push $$IMAGE

build-push-analytics: ## Build and push Analytics Docker image
	@echo "$(BLUE)Building and pushing Analytics image...$(NC)"
	@if [ -z "$(GCP_PROJECT_ID)" ]; then \
		echo "$(YELLOW)GCP_PROJECT_ID not set, trying gcloud config...$(NC)"; \
		GCP_PROJECT_ID=$$(gcloud config get-value project 2>/dev/null); \
	fi; \
	if [ -z "$$GCP_PROJECT_ID" ]; then \
		echo "$(YELLOW)Error: GCP_PROJECT_ID not set$(NC)"; \
		exit 1; \
	fi; \
	REGION=$${GCP_REGION:-us-central1}; \
	IMAGE="$$REGION-docker.pkg.dev/$$GCP_PROJECT_ID/loopweave/loopweave-analytics:latest"; \
	cd backend/analytics && docker build -t $$IMAGE . && docker push $$IMAGE

build-push-frontend: ## Build and push Frontend Docker image
	@echo "$(BLUE)Building and pushing Frontend image...$(NC)"
	@if [ -z "$(GCP_PROJECT_ID)" ]; then \
		echo "$(YELLOW)GCP_PROJECT_ID not set, trying gcloud config...$(NC)"; \
		GCP_PROJECT_ID=$$(gcloud config get-value project 2>/dev/null); \
	fi; \
	if [ -z "$$GCP_PROJECT_ID" ]; then \
		echo "$(YELLOW)Error: GCP_PROJECT_ID not set$(NC)"; \
		exit 1; \
	fi; \
	REGION=$${GCP_REGION:-us-central1}; \
	IMAGE="$$REGION-docker.pkg.dev/$$GCP_PROJECT_ID/loopweave/loopweave-frontend:latest"; \
	cd frontend && docker build -t $$IMAGE . && docker push $$IMAGE

build-push-all: build-push-api build-push-analytics build-push-frontend ## Build and push all Docker images

