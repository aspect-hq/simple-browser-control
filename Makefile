.PHONY: help install setup run test lint format clean

help:
	@echo "Available commands:"
	@echo "  setup    - Install dependencies and setup project"
	@echo "  install  - Install dependencies only"
	@echo "  run      - Run the browser control application"
	@echo "  test     - Run tests"
	@echo "  lint     - Run linting checks"
	@echo "  format   - Format code with black and isort"
	@echo "  clean    - Clean up generated files"

setup: install
	@echo "Setting up simple-browser-control..."
	@if [ ! -f .env ]; then cp env.example .env; echo "Created .env file from env.example"; fi
	@echo "Setup complete! Edit .env with your ASPECT_API_KEY and run 'make run'"

install:
	@echo "Installing dependencies..."
	uv sync --dev

run:
	@echo "Starting browser control application..."
	uv run main.py

test:
	@echo "Running tests..."
	uv run pytest

lint:
	@echo "Running linting checks..."
	uv run flake8 src/ main.py
	uv run mypy src/ main.py

format:
	@echo "Formatting code..."
	uv run black src/ main.py
	uv run isort src/ main.py

clean:
	@echo "Cleaning up..."
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
