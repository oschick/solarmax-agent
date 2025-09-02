.PHONY: help install test clean build run docker-build docker-run lint format addon-build

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install dependencies"
	@echo "  test         - Run unit tests"
	@echo "  lint         - Run code linting"
	@echo "  format       - Format code with black"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build Docker image"
	@echo "  run          - Run the agent locally"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run with Docker Compose"
	@echo "  docker-stop  - Stop Docker Compose services"
	@echo "  addon-build  - Build Home Assistant addon"
	@echo "  addon-test   - Test Home Assistant addon locally"

# Development setup
install:
	python -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	@echo "Development environment ready!"
	@echo "Activate with: source .venv/bin/activate"

# Testing
test:
	.venv/bin/python test_agent.py

# Code quality
lint:
	.venv/bin/python -m flake8 src/python/agent.py --max-line-length=100
	.venv/bin/python -m pylint src/python/agent.py

format:
	.venv/bin/python -m black src/python/agent.py test_agent.py

# Clean up
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/

# Local execution
run:
	@echo "Make sure to set environment variables first!"
	@echo "Copy .env.example to .env and configure it."
	.venv/bin/python src/python/agent.py

# Docker commands
docker-build:
	docker build -t solarmax-agent .

docker-run:
	@echo "Make sure you have a .env file configured!"
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f solarmax-agent

# Development with Docker
dev-up:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

dev-down:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down

# Home Assistant addon targets
addon-build:
	@echo "Building Home Assistant addon..."
	docker build -f Dockerfile.hassio -t local/solarmax-addon .

addon-test:
	@echo "Testing Home Assistant addon locally..."
	@echo "Make sure to create a config.json with your settings first!"
	docker run --rm -v $(PWD)/config.example.json:/data/options.json local/solarmax-addon

addon-validate:
	@echo "Validating addon configuration..."
	@which jq > /dev/null || (echo "jq is required for validation" && exit 1)
	@jq . config.json > /dev/null && echo "config.json is valid JSON"
	@jq . config.example.json > /dev/null && echo "config.example.json is valid JSON"

# GitHub Actions validation
validate-workflows:
	@echo "Validating GitHub Actions workflows..."
	@which actionlint > /dev/null || (echo "actionlint is required. Install with: go install github.com/rhymond/actionlint/cmd/actionlint@latest" && exit 1)
	actionlint .github/workflows/*.yml

# Documentation checks
docs-check:
	@echo "Checking documentation..."
	@which markdownlint > /dev/null || npm install -g markdownlint-cli
	markdownlint *.md || echo "⚠️ Markdown issues found"

# Security checks
security-check:
	@echo "Running security checks..."
	.venv/bin/pip install bandit safety
	.venv/bin/bandit -r src/python/
	.venv/bin/safety check

# Complete validation suite
validate-all: test addon-validate validate-workflows docs-check security-check
	@echo "✅ All validations passed!"
