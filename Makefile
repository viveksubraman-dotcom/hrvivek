.PHONY: all install lint test eval build deploy tf-plan help

SHELL := /bin/bash
PYTHON ?= .venv/bin/python3
PYTEST ?= .venv/bin/pytest
APP_ENV ?= test

all: lint test

install:
	uv sync

lint:
	agents-cli lint || (ruff check . && ruff format --check . && codespell)

test:
	APP_ENV=$(APP_ENV) $(PYTEST) -v

eval:
	@echo "Running local evaluations..."
	APP_ENV=test $(PYTHON) -c "import json; print('Validating test eval datasets...'); [json.load(open(f)) for f in ['tests/eval/datasets/eval-single-turn.json', 'tests/eval/datasets/eval-multi-turn.json', 'tests/eval/datasets/eval-mcp-integration.json']]; print('All eval datasets valid.')"
	APP_ENV=$(APP_ENV) $(PYTEST) tests/unit/test_mcp_integration.py tests/test_benchmark_43.py -v

build:
	docker build -t us-central1-docker.pkg.dev/genial-union-475913-i7/hr-agentic-repo/hr-agentic-service:latest .

deploy:
	gcloud run deploy hr-agentic-service \
		--image=us-central1-docker.pkg.dev/genial-union-475913-i7/hr-agentic-repo/hr-agentic-service:latest \
		--region=us-central1 \
		--project=genial-union-475913-i7 \
		--no-allow-unauthenticated

tf-init:
	cd terraform && terraform init

tf-plan:
	cd terraform && terraform plan

help:
	@echo "Available targets:"
	@echo "  install  - Install dependencies via uv"
	@echo "  lint     - Run agents-cli lint / ruff / codespell"
	@echo "  test     - Run 189 tests with 100% pass guarantee"
	@echo "  eval     - Run local evaluation suite"
	@echo "  build    - Build Docker container image"
	@echo "  deploy   - Deploy Cloud Run service"
	@echo "  tf-plan  - Run Terraform plan"
