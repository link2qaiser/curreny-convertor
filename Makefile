# Currrenty Convertor Makefile
# Development environment commands

# Load environment variables from .env
include .env
export

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Docker Compose settings
COMPOSE_FILE = -f docker-compose.local.yml
SERVICE_NAME = web

.PHONY: help
help: ## Show this help message
	@echo "$(BLUE)Currrenty Convertor Development Commands$(RESET)"
	@echo ""
	@echo "$(GREEN)Environment: $(ENV_STATE)$(RESET)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "$(BLUE)Available commands:$(RESET)\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(RESET)\n", substr($$0, 5) }' $(MAKEFILE_LIST)

##@ 🐳 Server Management
.PHONY: server-up
server-up: ## Start the development server
	@echo "$(BLUE)Starting development server...$(RESET)"
	docker compose $(COMPOSE_FILE) up --build
	@echo "$(GREEN)✅ Server started at http://localhost:8000$(RESET)"

.PHONY: server-down
server-down: ## Stop the development server
	@echo "$(BLUE)Stopping development server...$(RESET)"
	docker compose $(COMPOSE_FILE) down
	@echo "$(GREEN)✅ Server stopped$(RESET)"

.PHONY: server-restart
server-restart: server-down server-up ## Restart the development server

.PHONY: server-logs
server-logs: ## Show server logs
	@echo "$(BLUE)Showing server logs...$(RESET)"
	docker compose $(COMPOSE_FILE) logs -f $(SERVICE_NAME)

.PHONY: server-clean
server-clean: ## Stop server and clean up containers
	@echo "$(BLUE)Cleaning up server and containers...$(RESET)"
	docker compose $(COMPOSE_FILE) down --remove-orphans
	docker system prune -f
	@echo "$(GREEN)✅ Server cleaned$(RESET)"

##@ 🗄️ Database Migrations
.PHONY: migrate-up
migrate-up: ## Upgrade one revision (+1)
	@echo "$(BLUE)Upgrading one revision...$(RESET)"
	docker compose $(COMPOSE_FILE) exec $(SERVICE_NAME) alembic upgrade +1
	@echo "$(GREEN)✅ Upgraded one revision$(RESET)"

.PHONY: migrate-up-all
migrate-up-all: ## Upgrade all migrations to head
	@echo "$(BLUE)Upgrading all revisions to head...$(RESET)"
	docker compose $(COMPOSE_FILE) exec $(SERVICE_NAME) alembic upgrade head
	@echo "$(GREEN)✅ All migrations applied$(RESET)"

.PHONY: migrate-down
migrate-down: ## Downgrade one revision (-1)
	@echo "$(YELLOW)Downgrading one revision...$(RESET)"
	docker compose $(COMPOSE_FILE) exec $(SERVICE_NAME) alembic downgrade -1
	@echo "$(GREEN)✅ Downgraded one revision$(RESET)"

.PHONY: migrate-down-all
migrate-down-all: ## Downgrade all the way to base
	@echo "$(YELLOW)Downgrading all revisions to base...$(RESET)"
	docker compose $(COMPOSE_FILE) exec $(SERVICE_NAME) alembic downgrade base
	@echo "$(GREEN)✅ Downgraded to base$(RESET)"


##@ 🧪 Testing
.PHONY: test
test: ## Run all tests
	@echo "$(BLUE)Running tests...$(RESET)"
	docker compose $(COMPOSE_FILE) exec $(SERVICE_NAME) pytest
	@echo "$(GREEN)✅ Tests completed$(RESET)"

.PHONY: test-cov
test-cov: ## Run tests with coverage
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	docker compose $(COMPOSE_FILE) exec $(SERVICE_NAME) pytest --cov=app --cov-report=html --cov-report=term
	@echo "$(GREEN)✅ Tests with coverage completed$(RESET)"

##@ 📦 Requirements Management
.PHONY: requirements
requirements: ## Generate requirements.txt from Poetry (based on ENV_STATE)
	@echo "$(BLUE)Generating requirements from Poetry...$(RESET)"
	@if [ "$(ENV_STATE)" = "dev" ]; then \
		echo "$(YELLOW)Environment: Development - generating both files$(RESET)"; \
		poetry export -f requirements.txt --output requirements.txt --without-hashes; \
		echo "$(GREEN)✅ requirements.txt generated$(RESET)"; \
		poetry export -f requirements.txt --output requirements-dev.txt --with dev --without-hashes; \
		echo "$(GREEN)✅ requirements-dev.txt generated$(RESET)"; \
	else \
		echo "$(YELLOW)Environment: Production - generating requirements.txt only$(RESET)"; \
		poetry export -f requirements.txt --output requirements.txt --without-hashes; \
		echo "$(GREEN)✅ requirements.txt generated$(RESET)"; \
	fi

.PHONY: requirements-dev
requirements-dev: ## Generate requirements-dev.txt from Poetry (includes dev dependencies)
	@echo "$(BLUE)Generating requirements-dev.txt from Poetry...$(RESET)"
	poetry export -f requirements.txt --output requirements-dev.txt --with dev --without-hashes
	@echo "$(GREEN)✅ requirements-dev.txt generated$(RESET)"

.PHONY: requirements-prod
requirements-prod: ## Generate requirements.txt for production (no dev dependencies)
	@echo "$(BLUE)Generating requirements.txt for production...$(RESET)"
	poetry export -f requirements.txt --output requirements.txt --without-hashes
	@echo "$(GREEN)✅ requirements.txt generated$(RESET)"