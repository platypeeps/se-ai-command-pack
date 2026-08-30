BREW_PYTHON ?= /opt/homebrew/bin/python3.13
PYTHON ?= $(shell if [ -x "$(BREW_PYTHON)" ]; then printf '%s' "$(BREW_PYTHON)"; elif [ -x /usr/local/bin/python3.13 ]; then printf '%s' /usr/local/bin/python3.13; elif [ -x /opt/homebrew/bin/python3 ]; then printf '%s' /opt/homebrew/bin/python3; elif [ -x /usr/local/bin/python3 ]; then printf '%s' /usr/local/bin/python3; else command -v python3; fi)
VENV ?= .venv
VENV_PYTHON = $(VENV)/bin/python
RUN_PYTHON = $(shell if [ -x "$(VENV_PYTHON)" ]; then printf '%s' "$(VENV_PYTHON)"; else printf '%s' "$(PYTHON)"; fi)

LINT_PATHS = install.py installer tests .github/scripts templates/skills/se-review-skills/scripts/skill_review.py
MYPY_PATHS = installer install.py templates/skills/se-review-skills/scripts/skill_review.py

.PHONY: setup lock lock-check relock-pr generate repomix sync test test-hermetic lint prose-lint release-check check shell-syntax gate-test gate-lint

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

# Finish a Dependabot pip PR: `make relock-pr PR=221`.
#
# Dependabot bumps requirements-dev.txt only, and nothing installs from that
# file, so every bot pip PR lands red on lock-check until the lock is
# regenerated. This is that step in one command instead of five. It is
# deliberately a local helper and not CI automation: pushing a lock from a
# workflow needs a writable credential in a job triggered by a bot branch, and
# that standing risk buys back only a few minutes a week. See
# docs/work/archive/2026-08/2026-08-14-dependabot-lock-automation/design.md for
# the full comparison.
#
# Three refusals, all before any checkout:
#
#   - a PR whose author is not Dependabot, so a mistyped number cannot move the
#     branch (this gates on the PR author, not on the branch name);
#   - a dirty tree, so nothing local is swept onto the bot branch;
#   - a PR touching anything but the dev requirements files. That last one is
#     the load-bearing check: this target runs `make lock` from the PR's own
#     checkout, so a PR that modified the Makefile would have its Makefile
#     executed here. The archived design rejects CI automation on exactly this
#     ground — head-controlled content must not run — and the same rule applies
#     to running it on a laptop.
#
# `make -n relock-pr` is NOT a dry run. GNU make executes recipe lines that
# contain `$(MAKE)` even under -n, and this whole recipe is one shell line that
# does — so -n runs the guards, and on a bot PR that passes them it would go on
# to fetch, checkout, lock, commit, and push. To preview, read the recipe.
#
# The stray list prints each path in double quotes, via printf. `grep -vxE`
# anchors the whole line, so `requirements-dev.lock ` (trailing space) is
# correctly refused — but unquoted it renders identically to the legitimate
# path, and the refusal reads as a bug in the guard rather than as the odd
# filename it is. printf rather than echo for the same reason: these paths come
# from the PR, and sh's echo eats backslash escapes, so a legal path like
# `a\nb` would print as `ab` — misreporting the very name being refused.
relock-pr:
	@test -n "$(PR)" || { echo "usage: make relock-pr PR=<number>" >&2; exit 2; }
	@test -z "$$(git status --porcelain)" || { echo "working tree is dirty; commit or stash first" >&2; exit 1; }
	@branch="$$(gh pr view "$(PR)" --json headRefName --jq .headRefName)"; \
	author="$$(gh pr view "$(PR)" --json author --jq .author.login)"; \
	case "$$author" in dependabot|app/dependabot|dependabot\[bot\]) ;; \
	  *) echo "PR #$(PR) is authored by $$author, not Dependabot; relock it by hand" >&2; exit 1;; \
	esac; \
	stray="$$(gh pr view "$(PR)" --json files --jq '.files[].path' | grep -vxE 'requirements-dev\.(txt|lock)' || true)"; \
	if [ -n "$$stray" ]; then \
	  echo "PR #$(PR) touches files beyond the dev requirements:" >&2; \
	  printf '%s\n' "$$stray" | sed 's/^/  "/; s/$$/"/' >&2; \
	  echo "refusing: this target runs make lock from that branch's checkout" >&2; \
	  exit 1; \
	fi; \
	echo "relocking #$(PR) ($$branch)"; \
	git fetch --quiet origin "$$branch" && git checkout --quiet -B "$$branch" FETCH_HEAD && \
	$(MAKE) --no-print-directory lock && \
	if git diff --quiet -- requirements-dev.lock; then \
	  echo "lock already matches requirements-dev.txt; nothing to push"; \
	else \
	  git commit --quiet -m "chore(deps): regenerate requirements-dev.lock" -- requirements-dev.lock && \
	  git push --quiet origin "$$branch" && \
	  echo "pushed regenerated lock to $$branch"; \
	fi

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
	"$(RUN_PYTHON)" -m coverage report --fail-under=88

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

# Enforcing prose gate over the skill corpus and the root docs; part of
# `check` and its own CI lane. Which files get which styles lives in
# .vale.ini's glob sections; this path list only decides what Vale walks, so
# keep the two in step when adding a root doc. CHANGELOG.md is out of scope
# on purpose: historical release text, and rewriting it to satisfy a linter
# would falsify the record.
#
# Vale exits 0 when every alert is below error severity, so the recipe fails
# on any alert itself rather than raising the rules to error severity. That
# is deliberate: the rules stay at suggestion so a human reading Vale's own
# output sees advice, while the gate still refuses to pass with advice
# outstanding. Raising them to error to use --minAlertLevel=error would say
# the same thing twice and lose that distinction.
#
# A missing binary is a hard failure, not a silent pass, so an environment
# without Vale cannot report a clean corpus it never linted. Contributors
# install it once (see CONTRIBUTING.md); CI installs a pinned build.
#
# A present binary is not enough either: a clean corpus is only evidence if
# the rules still fire. The target lints .vale/fixtures/positive-detection.md
# first and fails unless it reports its expected 8 alerts across both styles,
# which catches a broken regex, a renamed style, or an unresolved StylesPath
# before the corpus verdict is believed. The major-version check is advisory:
# the styles are written for Vale 3, and CI pins an exact build.
prose-lint: SHELL := /bin/bash
prose-lint:
	@set -euo pipefail; \
	command -v vale >/dev/null || { \
	  echo "prose-lint: vale not installed (developed against vale 3.18)" >&2; \
	  echo "prose-lint: install with 'brew install vale' or see https://vale.sh" >&2; \
	  exit 1; }; \
	major="$$(vale --version | sed -n 's/.*vale version \([0-9][0-9]*\).*/\1/p')"; \
	if [ -n "$$major" ] && [ "$$major" != "3" ]; then \
	  echo "prose-lint: vale major $$major, styles developed against 3;" \
	    "rule syntax may differ" >&2; \
	fi; \
	fx="$$(vale --output=line .vale/fixtures/positive-detection.md || true)"; \
	fxn="$$(printf '%s' "$$fx" | grep -c . || true)"; \
	if [ "$$fxn" -ne 8 ] \
	  || ! printf '%s\n' "$$fx" | grep -q 'se.Weasel' \
	  || ! printf '%s\n' "$$fx" | grep -q 'se.AiTells'; then \
	  printf '%s\n' "$$fx"; \
	  echo "prose-lint: positive-detection fixture reported $$fxn alert(s)," \
	    "expected 8 across se.Weasel and se.AiTells; the styles are not" \
	    "firing, so a clean corpus proves nothing" >&2; \
	  exit 1; \
	fi; \
	out="$$(vale --output=line README.md CONTRIBUTING.md templates/skills)" || { \
	  printf '%s\n' "$$out"; exit 1; }; \
	if [ -n "$$out" ]; then \
	  printf '%s\n' "$$out"; \
	  echo "prose-lint: $$(printf '%s\n' "$$out" | wc -l | tr -d ' ') alert(s); fix or suppress with justification" >&2; \
	  exit 1; \
	fi; \
	echo "prose-lint: clean"

# Guard-safe variants: no coverage data, no linter caches. They exist so an
# external runner can invoke the suite without writing into the working tree.
gate-test:
	"$(RUN_PYTHON)" -m unittest discover -s tests

gate-lint:
	"$(RUN_PYTHON)" -m ruff check --no-cache $(LINT_PATHS)
	"$(RUN_PYTHON)" -m mypy $(MYPY_PATHS)

shell-syntax:
	# The repository owns exactly one shell script. Everything that lived
	# under scripts/ was framework payload and was deleted with it.
	bash -n .github/scripts/update-repomix

release-check:
	"$(RUN_PYTHON)" .github/scripts/generate-skill-surfaces.py --check
	"$(RUN_PYTHON)" .github/scripts/check-release-payload.py --base auto

check: test lint lock-check release-check shell-syntax prose-lint
