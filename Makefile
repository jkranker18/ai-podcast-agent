# AI Podcast Agent Makefile

.PHONY: help install test setup run run-scheduler clean format lint

# Default target
help:
	@echo "AI Podcast Agent - Available commands:"
	@echo ""
	@echo "  install      - Install dependencies"
	@echo "  setup        - Initialize database and test setup"
	@echo "  test         - Run the test suite"
	@echo "  run          - Run the agent once"
	@echo "  run-scheduler - Run the agent with scheduler"
	@echo "  clean        - Clean up generated files"
	@echo "  format       - Format code with black"
	@echo "  lint         - Lint code with flake8"
	@echo ""

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

# Setup and test
setup: install
	@echo "Setting up AI Podcast Agent..."
	python test_setup.py

# Run tests
test:
	@echo "Running tests..."
	python -m pytest tests/ -v

# Run the agent once
run:
	@echo "Running AI Podcast Agent..."
	python -m src.main

# Run with scheduler
run-scheduler:
	@echo "Running AI Podcast Agent with scheduler..."
	python -m src.main --scheduler

# Clean up
clean:
	@echo "Cleaning up..."
	rm -rf data/
	rm -rf logs/
	rm -rf __pycache__/
	rm -rf src/__pycache__/
	rm -rf src/*/__pycache__/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

# Format code
format:
	@echo "Formatting code..."
	black src/ test_setup.py

# Lint code
lint:
	@echo "Linting code..."
	flake8 src/ test_setup.py

# Development setup
dev-setup: install setup format lint
	@echo "Development setup completed!"

# Quick start
quick-start: dev-setup run 