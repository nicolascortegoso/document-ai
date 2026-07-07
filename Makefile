.PHONY: help test lint build shell clean profile

help:
	@echo "Available targets:"
	@echo "  make test              - lint + full test suite with coverage (in Docker)"
	@echo "  make lint              - ruff only (in Docker)"
	@echo "  make build             - build the production (runtime) image"
	@echo "  make shell             - open a shell in the test image, for debugging"
	@echo "  make clean             - remove local __pycache__/.pytest_cache/.ruff_cache"
	@echo "  make profile FILE=path - profile a real document through the ingestion pipeline"

test:
	docker compose run --rm test

lint:
	docker compose run --rm test ruff check .

build:
	docker build --target runtime -t document-ai .

shell:
	docker compose run --rm test sh

clean:
	find . -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache

profile:
	docker compose run --rm test python scripts/profile_document.py $(FILE)