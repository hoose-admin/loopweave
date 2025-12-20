.PHONY: help docker-up docker-down docker-build docker-logs
.PHONY: tf-load-env tf-init tf-plan tf-apply tf-destroy tf-output

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

# Docker Commands
docker-up: ## Build and start all containers
	@docker compose up -d --build

docker-down: ## Stop and remove all containers
	@docker compose down

docker-build: ## Build all containers without starting
	@docker compose build

docker-logs: ## View logs from all containers
	@docker compose logs -f

# Terraform Commands
tf-load-env: ## Generate terraform.tfvars from .env file
	@./terraform/load-env.sh

tf-init: tf-load-env ## Initialize Terraform
	@cd terraform && terraform init

tf-plan: tf-init ## Plan Terraform changes
	@cd terraform && terraform plan

tf-apply: tf-init ## Apply Terraform changes
	@cd terraform && terraform apply -auto-approve

tf-destroy: tf-init ## Destroy Terraform infrastructure
	@cd terraform && terraform destroy

tf-output: tf-init ## Show Terraform outputs
	@cd terraform && terraform output
