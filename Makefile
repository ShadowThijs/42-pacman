UV := $(shell command -v uv 2>/dev/null)
PYTHON ?= python3
VENV := .venv
MAIN := pac-man.py
CONFIG := config.json
WHL := maze/mazegenerator-2.0.2-py3-none-any.whl

ifeq ($(UV),)
PY := $(VENV)/bin/python
else
PY := uv run python
endif

.DEFAULT_GOAL := help

##@ Development
.PHONY: install lint lint-strict test debug package clean

install: ## Install dependencies (uv when available, otherwise pip)
ifeq ($(UV),)
	@$(PYTHON) -m venv $(VENV)
	@$(VENV)/bin/python -m pip install --upgrade pip
	@$(VENV)/bin/python -m pip install "$(WHL)" \
		"pygame>=2.5" "flake8>=7.0" "mypy>=1.10" \
		"pytest>=8.0" "pyinstaller>=6.0"
else
	@uv sync --all-groups
endif

lint: ## Check linting errors with flake8 and mypy
	@$(PY) -m flake8 .
	@$(PY) -m mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict: ## Stricter linting errors
	@$(PY) -m flake8 .
	@$(PY) -m mypy . --strict

test: ## Run the test suite
	@$(PY) -m pytest tests/ -v

debug: ## Debug the game with Python's built-in debugger
	@$(PY) -m pdb -c continue $(MAIN) $(CONFIG)

clean: ## Clean generated caches and build artifacts
	find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.mypy_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	rm -rf build dist

##@ Running
.PHONY: run

run: ## Run the Pac-Man game
	@$(PY) $(MAIN) $(CONFIG)

package: ## Build a one-file executable with PyInstaller
	@$(PY) -m PyInstaller --clean --noconfirm 42-pacman.spec
	@cp $(CONFIG) dist/
	@cp README.md dist/

##@ help
.PHONY: help

help: ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[.a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
