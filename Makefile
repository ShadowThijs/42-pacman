PM = uv
MAIN = pac-man.py
SOURCES = src/
DEBUG = --with ipdb -m pdb -c continue
MODULE = $(PM) run python -m

install:
	@$(PM) sync

run:
	@$(PM) run $(MAIN)

debug:
	@$(PM) run $(DEBUG) $(MAIN)

clean:
	find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.mypy_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true

lint:
	@$(MOD_CMD) flake8 $(SOURCES) $(MAIN)
	@$(MOD_CMD) mypy $(SOURCES) $(MAIN) --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@$(MOD_CMD) flake8 $(SOURCES) $(MAIN)
	@$(MOD_CMD) mypy $(SOURCES) $(MAIN) --strict

test:
	@$(MOD_CMD) pytest tests/ -v

.PHONY: install run debug ling lint-strict test
