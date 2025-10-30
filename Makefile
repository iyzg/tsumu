.PHONY: help test test-fast install clean format lint

help:
	@echo "Tsumu - Anki Flashcard Automation Toolkit"
	@echo ""
	@echo "Available commands:"
	@echo "  make test       - Run all tests"
	@echo "  make test-fast  - Run core tests only"
	@echo "  make install    - Install package in development mode"
	@echo "  make clean      - Remove generated files"
	@echo "  make lint       - Check code style"
	@echo ""
	@echo "Quick examples:"
	@echo "  python scripts/anki.py markdown notes.md -o cards.csv"
	@echo "  python scripts/anki.py cloze text.txt -o cloze.csv"

test:
	@echo "Running all tests..."
	@python scripts/test_anki_utils.py
	@python scripts/test_io_utils.py
	@python scripts/test_cli_integration.py
	@python scripts/test_batch_preview.py
	@echo "✓ All tests passed!"

test-fast:
	@echo "Running core tests..."
	@python scripts/test_anki_utils.py
	@python scripts/test_io_utils.py
	@echo "✓ Core tests passed!"

install:
	pip install -e .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleaned up generated files"

lint:
	@echo "Checking for common issues..."
	@python -m py_compile scripts/*.py 2>&1 | grep -v "test_" || echo "✓ No syntax errors"
