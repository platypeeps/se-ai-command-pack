BREW_PYTHON ?= /opt/homebrew/bin/python3.13
PYTHON ?= $(shell if [ -x "$(BREW_PYTHON)" ]; then printf '%s' "$(BREW_PYTHON)"; elif [ -x /usr/local/bin/python3.13 ]; then printf '%s' /usr/local/bin/python3.13; elif [ -x /opt/homebrew/bin/python3 ]; then printf '%s' /opt/homebrew/bin/python3; elif [ -x /usr/local/bin/python3 ]; then printf '%s' /usr/local/bin/python3; else command -v python3; fi)
VENV ?= .venv
VENV_PYTHON = $(VENV)/bin/python
RUN_PYTHON = $(shell if [ -x "$(VENV_PYTHON)" ]; then printf '%s' "$(VENV_PYTHON)"; else printf '%s' "$(PYTHON)"; fi)

LINT_PATHS = install.py installer tests .github/scripts templates/skills/se-review-skills/scripts/skill_review.py
MYPY_PATHS = installer install.py templates/skills/se-review-skills/scripts/skill_review.py

.PHONY: setup lock lock-check generate repomix sync test test-hermetic lint release-check check shell-syntax gate-test gate-lint trellis-provenance

# --clear: `python -m venv` reuses an existing directory, so without it a
# package that dropped out of the lock survives and the gate runs against a
# superset of the locked set.
setup:
	"$(PYTHON)" -m venv --clear "$(VENV)"
	"$(VENV_PYTHON)" -m pip install --require-hashes --only-binary :all: -r requirements-dev.lock

# Regenerate the hash-locked dev requirements from requirements-dev.txt.
# Requires uv and network access; contributors run it only when changing a pin.
# --only-binary :all: keeps resolution to wheels, so the compile itself cannot
# build a source distribution and run its build hooks.
lock:
	uv pip compile --universal --python-version 3.10 --generate-hashes \
	  --no-header --only-binary :all: requirements-dev.txt -o requirements-dev.lock

# Guard-safe (read-only): the lock still matches its input's direct pins.
lock-check:
	"$(RUN_PYTHON)" .github/scripts/check-dev-requirements-lock.py

generate:
	"$(RUN_PYTHON)" .github/scripts/generate-skill-surfaces.py

repomix:
	bash .github/scripts/update-repomix

# Dogfood: refresh this machine's user-level install from templates/.
sync:
	"$(RUN_PYTHON)" install.py --user

test:
	"$(RUN_PYTHON)" -m coverage erase
	COVERAGE_PROCESS_START="$(CURDIR)/.coveragerc" PYTHONPATH="$(CURDIR)/tests/_coverage_subprocess$${PYTHONPATH:+:$$PYTHONPATH}" "$(RUN_PYTHON)" -m coverage run -m unittest discover -s tests
	"$(RUN_PYTHON)" -m coverage combine
	"$(RUN_PYTHON)" -m coverage report --fail-under=80

# Runs the suite the way a runner sees the repository: tracked files only, in a
# throwaway git repository, under a git configuration built to break it. Not
# part of `make check` — the inner loop should not pay for two suite runs — but
# it is a required CI lane. `abspath` matters: RUN_PYTHON may be the relative
# .venv path, which would not resolve after cd, and CI has no .venv at all.
#
# The lane's own setup runs through `scrub`, for the same reason the suite does:
# an ambient hostile configuration otherwise breaks the fixture instead of being
# tested by it (a `core.hooksPath` in the caller's environment failed the setup
# commit, so the lane errored before running a single test). The scrub is a
# function rather than an exported block because the hostile run below must not
# inherit it — a `GIT_CONFIG_GLOBAL=/dev/null` in scope there would outrank the
# hostile `HOME` and silently defang the one thing this lane exists to prove.
test-hermetic: SHELL := /bin/bash
test-hermetic:
	@set -euo pipefail; \
	scrub() { env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE \
	    -u GIT_CONFIG_COUNT -u GIT_CONFIG_PARAMETERS \
	    GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null GIT_CONFIG_NOSYSTEM=1 \
	    GIT_AUTHOR_NAME=hermetic GIT_AUTHOR_EMAIL=hermetic@example.com \
	    GIT_COMMITTER_NAME=hermetic GIT_COMMITTER_EMAIL=hermetic@example.com "$$@"; }; \
	python="$(abspath $(RUN_PYTHON))"; \
	tmp="$$(mktemp -d)"; \
	trap 'rm -rf "$$tmp"' EXIT; \
	copy="$$tmp/copy"; mkdir -p "$$copy" "$$tmp/hooks" "$$tmp/home"; \
	scrub git ls-files -z | while IFS= read -r -d "" f; do \
	  mkdir -p "$$copy/$$(dirname "$$f")"; cp "$$f" "$$copy/$$f"; \
	done; \
	scrub bash -c 'cd "$$0" && git init -q . && git add -A && git commit -qm hermetic' "$$copy"; \
	printf '#!/bin/sh\nexit 1\n' > "$$tmp/hooks/pre-commit"; \
	chmod +x "$$tmp/hooks/pre-commit"; \
	printf '[core]\n\thooksPath = %s\n' "$$tmp/hooks" > "$$tmp/home/.gitconfig"; \
	cd "$$copy"; \
	env HOME="$$tmp/home" GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.hooksPath \
	    GIT_CONFIG_VALUE_0="$$tmp/hooks" \
	  "$$python" -m unittest discover -s tests

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
	for f in scripts/*.sh .github/scripts/update-repomix; do bash -n "$$f" || exit 1; done

release-check:
	"$(RUN_PYTHON)" .github/scripts/generate-skill-surfaces.py --check
	"$(RUN_PYTHON)" .github/scripts/check-release-payload.py --base auto

# Guard-safe (read-only): coverage + integrity of unreceipted platform files.
trellis-provenance:
	"$(RUN_PYTHON)" .github/scripts/check-trellis-provenance.py

check: test lint lock-check release-check shell-syntax trellis-provenance
