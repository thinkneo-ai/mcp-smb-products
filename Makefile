# ThinkNEO MCP Products — Build & Deploy

.PHONY: build up down logs status clean

# Build all product images
build:
	docker compose build

# Start all products
up:
	docker compose up -d

# Stop all products
down:
	docker compose down

# View logs for a specific product (e.g., make logs PRODUCT=mcp-guardrails)
logs:
	docker compose logs -f $(PRODUCT)

# Status of all containers
status:
	docker compose ps

# Rebuild a single product (e.g., make rebuild PRODUCT=mcp-guardrails)
rebuild:
	docker compose build $(PRODUCT)
	docker compose up -d $(PRODUCT)

# Clean everything
clean:
	docker compose down -v --rmi local

# Run database migrations
migrate:
	psql "host=$${MCP_DB_HOST:-172.17.0.1} port=5432 dbname=thinkneo_mcp user=mcp_user password=$${MCP_DB_PASSWORD}" -f shared/migrations/001_tnc_tables.sql

# Test a single product locally (e.g., make test-local PRODUCT=mcp-guardrails PORT=8101)
test-local:
	cd $(PRODUCT) && python3 -m uvicorn src.server:app --host 0.0.0.0 --port $(PORT) --reload
