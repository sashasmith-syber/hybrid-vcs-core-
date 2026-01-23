# Makefile for Hybrid VCS project

.PHONY: help install install-dev test test-cov lint format clean build upload docs serve-docs

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install the package"
	@echo "  install-dev  - Install package with development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run linting (flake8, mypy)"
	@echo "  format       - Format code (black, isort)"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build distribution packages"
	@echo "  upload       - Upload to PyPI (requires credentials)"
	@echo "  docs         - Build documentation"
	@echo "  serve-docs   - Serve documentation locally"
	@echo "  example-basic - Run basic example"
	@echo "  example-advanced - Run advanced example"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev,docs]"

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=hybrid_vcs --cov-report=html --cov-report=term

# Code quality
lint:
	flake8 hybrid_vcs/ tests/
	mypy hybrid_vcs/

format:
	black hybrid_vcs/ tests/ examples/
	isort hybrid_vcs/ tests/ examples/

# Build and distribution
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

upload: build
	python -m twine upload dist/*

# Documentation
docs:
	cd docs && make html

serve-docs:
	cd docs/_build/html && python -m http.server 8000

# Examples
example-basic:
	cd examples && python basic_usage.py

example-advanced:
	cd examples && python advanced_usage.py

# Development workflow
dev-setup: install-dev
	@echo "Development environment set up successfully!"
	@echo "Run 'make test' to run tests"
	@echo "Run 'make example-basic' to try the basic example"

# CI/CD targets
ci-test: install-dev test-cov lint

# Quick development cycle
dev: format lint test
	@echo "Development cycle complete!"
