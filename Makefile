PM = uv
MAIN = pac-man.py
SOURCES = src/
DEBUG = --with ipdb -m pdb -c continue
MODULE = $(PM) run python -m

##@ Development
.PHONY: install lint lint-strict test debug

install: ## Install dependencies
	@$(PM) sync

clean: ## Clean python artifacts
	find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.mypy_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true

lint: ## Check linting errors
	@$(MOD_CMD) flake8 $(SOURCES) $(MAIN)
	@$(MOD_CMD) mypy $(SOURCES) $(MAIN) --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict: ## Stricter linting errors
	@$(MOD_CMD) flake8 $(SOURCES) $(MAIN)
	@$(MOD_CMD) mypy $(SOURCES) $(MAIN) --strict

test: ## Run tests
	@$(MOD_CMD) pytest tests/ -v

debug: ## Debug the pacman game with the python debugger
	@$(PM) run $(DEBUG) $(MAIN)

##@ Running
.PHONY: run

run: ## Run pacman game
	@$(PM) run $(MAIN)

##@ help
.PHONY: help

help:  ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[.a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
