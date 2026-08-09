BREW_PYTHON ?= /opt/homebrew/bin/python3.13
PYTHON ?= $(shell if [ -x "$(BREW_PYTHON)" ]; then printf '%s' "$(BREW_PYTHON)"; elif [ -x /usr/local/bin/python3.13 ]; then printf '%s' /usr/local/bin/python3.13; elif [ -x /opt/homebrew/bin/python3 ]; then printf '%s' /opt/homebrew/bin/python3; elif [ -x /usr/local/bin/python3 ]; then printf '%s' /usr/local/bin/python3; else command -v python3; fi)
VENV ?= .venv
VENV_PYTHON = $(VENV)/bin/python
RUN_PYTHON = $(shell if [ -x "$(VENV_PYTHON)" ]; then printf '%s' "$(VENV_PYTHON)"; else printf '%s' "$(PYTHON)"; fi)

LINT_PATHS = install.py installer tests .github/scripts templates/skills/se-review-skills/scripts/skill_review.py
MYPY_PATHS = installer install.py templates/skills/se-review-skills/scripts/skill_review.py

.PHONY: setup generate repomix sync test lint release-check check shell-syntax gate-test gate-lint trellis-provenance

setup:
	"$(PYTHON)" -m venv "$(VENV)"
	"$(VENV_PYTHON)" -m pip install -r requirements-dev.txt

generate:
	"$(RUN_PYTHON)" .github/scripts/generate-skill-surfaces.py

repomix:
	bash scripts/update_repomix

# Dogfood: refresh this machine's user-level install from templates/.
sync:
	"$(RUN_PYTHON)" install.py --user

test:
	"$(RUN_PYTHON)" -m coverage erase
	COVERAGE_PROCESS_START="$(CURDIR)/.coveragerc" PYTHONPATH="$(CURDIR)/tests/_coverage_subprocess$${PYTHONPATH:+:$$PYTHONPATH}" "$(RUN_PYTHON)" -m coverage run -m unittest discover -s tests
	"$(RUN_PYTHON)" -m coverage combine
	"$(RUN_PYTHON)" -m coverage report --fail-under=80

lint:
	"$(RUN_PYTHON)" -m ruff check $(LINT_PATHS)
	"$(RUN_PYTHON)" -m mypy $(MYPY_PATHS)

# Guard-safe variants for sd-check registration (.sd-ai-command-pack/check.json):
# no coverage data, no linter caches — nothing under sd-check's GUARDED_PATHS.
gate-test:
	"$(RUN_PYTHON)" -m unittest discover -s tests

gate-lint:
	"$(RUN_PYTHON)" -m ruff check --no-cache $(LINT_PATHS)
	"$(RUN_PYTHON)" -m mypy $(MYPY_PATHS)

shell-syntax:
	for f in scripts/*.sh; do bash -n "$$f" || exit 1; done

release-check:
	"$(RUN_PYTHON)" .github/scripts/generate-skill-surfaces.py --check
	"$(RUN_PYTHON)" .github/scripts/check-release-payload.py --base auto

# Guard-safe (read-only): coverage + integrity of unreceipted platform files.
trellis-provenance:
	"$(RUN_PYTHON)" .github/scripts/check-trellis-provenance.py

check: test lint release-check shell-syntax trellis-provenance
