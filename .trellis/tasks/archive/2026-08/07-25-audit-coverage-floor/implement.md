# Implement — Coverage measurement and floor in gates (A-020)

Base branch: `main`. Feature branch: `audit/coverage-floor`.
Floor: **80%** (conservative introduction; see design.md Decision 4).

## Ordered steps

1. **deps**: add `coverage==7.6.10` to `requirements-dev.txt` (with a short
   comment noting it powers the coverage floor).

2. **coverage config**: add `.coveragerc` at repo root:
   - `[run] source = installer,install,.github/scripts`
   - `[run] parallel = true`
   - `[report] precision = 1` (explicit; makes the round-based `--fail-under`
     semantics deterministic — see design.md Decision 4).

3. **subprocess bootstrap**: add
   `tests/_coverage_subprocess/sitecustomize.py` containing
   `import coverage; coverage.process_startup()`, plus a one-line `__doc__`
   explaining it is auto-imported only when the directory is on `PYTHONPATH`
   during a coverage run. **Do not** add `__init__.py` — the directory must stay
   a non-package so `unittest discover -s tests` never collects it (its name
   starts with `_` and it holds no `test*.py`, so discovery ignores it).

4. **Makefile `test` recipe** — enforce the floor locally (goal prd.md:5), not
   just print. Sequence (using `$(RUN_PYTHON) -m coverage`):
   - `coverage erase` (drop any stale parallel `.coverage.*` from an aborted run)
   - `COVERAGE_PROCESS_START=.coveragerc PYTHONPATH=tests/_coverage_subprocess`
     `coverage run -m unittest discover -s tests`
   - `coverage combine`
   - `coverage report --fail-under=80` (prints report AND fails below floor)
   Keep `make check` → `test lint release-check` unchanged.

5. **CI `unittest` lane** (`.github/workflows/tests.yml`, matrix job): replace
   the single `python -m unittest discover -s tests -v` run step with the same
   erase → run → combine → `coverage report --fail-under=80` sequence, setting
   `COVERAGE_PROCESS_START` and `PYTHONPATH` on the `coverage run` line so child
   processes inherit them. `requirements-dev.txt` install already brings
   coverage. The lane failure propagates to the aggregate job via `needs`.

6. **docs** (`CONTRIBUTING.md` test section): document the 80% floor, the
   measured ~88% (3.13/macOS) baseline, the expected-lower 3.10 total (tomllib
   skips), the in-scope paths, the `precision`/rounding semantics, and the
   ratchet path (raise the floor toward the observed CI minimum once known).

7. **AC1 demo — in CI**: after the gate is green, push one throwaway commit
   that forces the `unittest` lane red (temporarily bump `--fail-under` above
   baseline, or add an uncovered function), confirm the CI lane goes red and
   the aggregate job fails, capture the failing run URL, then **revert** so the
   PR ends green at 80%. Record run URL + revert SHA in the journal. Keep a
   local `coverage report --fail-under=95` → non-zero as a secondary check.

8. **.gitignore**: ensure `.coverage`, `.coverage.*`, and `htmlcov/` are
   ignored (add if absent) so coverage data is never committed.

## Validation commands

- `make test` → prints a coverage report, TOTAL ≥ 80%, exit 0 (AC2 + goal:
  local floor enforcement).
- After a run, `.venv/bin/python -m coverage report --fail-under=95` → exit 2
  (coverage.py's below-floor exit code; non-zero, so `make`/CI go red — secondary
  local proof the gate mechanism trips).
- CI on the PR: all 3 matrix combos green at `--fail-under=80`; the temporary
  red commit demonstrates the failing gate, then revert (AC1, authoritative).
- `make check` → still green (ruff/mypy/generate --check/release-payload).
- `make lint` → ruff accepts `tests/_coverage_subprocess/sitecustomize.py`.
- Release gate: `.coveragerc`, `.gitignore`, `requirements-dev.txt`, Makefile,
  CI workflow, and a test-dir file do **not** touch
  `manifest.json`/`templates/`/`generated/**` → no version bump; confirm
  `check-release-payload.py` stays green.
- PR-body scope: the branch delta will touch `.trellis/tasks/**` at
  finalization → the PR body must carry a `Tooling/generated scope:` section
  (learned from PR #123).

## Review gates

- Deterministic sd-check green at the PR head.
- Copilot review clean.
- CI unittest lane green on all 3 matrix combos at the floor (authoritative
  cross-platform check that cannot be run locally), plus the one demonstrated
  red run for AC1.

## Rollback

Revert the branch; no runtime/consumer surface changes. The gate is additive
(new dev dep + config + CI step); removing them restores prior behavior.
