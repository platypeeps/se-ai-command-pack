# Implement — CI workflow hygiene and release-script error contract

Ordered steps. Validation after each code change; full check before ship.

## Step 1 — A-038 pip cache (tests.yml)

Add to each of the three `actions/setup-python@v6` steps (unittest, lint,
release-payload-gate):

```yaml
      - uses: actions/setup-python@v6
        with:
          python-version: <existing>
          cache: pip
          cache-dependency-path: requirements-dev.txt
```

## Step 2 — A-039 concurrency (tests.yml)

Add after the top-level `permissions:` block:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
```

## Step 3 — A-037 push-lane gate (tests.yml)

- `release-payload-gate.if`: change to
  `github.event_name == 'pull_request' || (github.event_name == 'push' && github.ref == 'refs/heads/main')`.
- Its checkout: add `fetch-tags: true` beside `fetch-depth: 0`.
- Replace the single gate run step with a base-computing step + gate run:
  - PR: `BASE="${{ github.event.pull_request.base.sha }}"`.
  - push: `BASE="$(git describe --tags --abbrev=0 2>/dev/null || echo HEAD)"`
    (tagless first release degrades to `HEAD`, which the script documents).
  - then `python .github/scripts/check-release-payload.py --base "$BASE"`.
- `auto-tag-release.needs`: add `release-payload-gate` →
  `needs: [unittest, lint, release-payload-gate]`.

## Step 4 — A-014 error contract (create-release-tag.py)

- Add `class ReleaseTagError(Exception): pass` near the top.
- Wrap `run_git`'s `subprocess.run` in try/except:
  - `except FileNotFoundError: raise ReleaseTagError("git not found") from None`
  - `except subprocess.TimeoutExpired: raise ReleaseTagError(f"git {' '.join(args)} timed out") from None`
- In `main()`, wrap the run_git-calling body in
  `try: ... except ReleaseTagError as error: print(f"error: {error}", file=sys.stderr); return 1`.
  Leave the existing `returncode != 0` branches unchanged.

## Step 5 — Tests (tests/test_release_gate.py)

- A-014: the existing tag-script tests run the script as an EXTERNAL subprocess
  via `run_script([sys.executable, TAG_SCRIPT, ...])`, so patching
  `subprocess.run` in-process cannot reach the child. Instead import the script
  as a module and patch its `subprocess.run` directly:
  - Load it with `importlib.util.spec_from_file_location("create_release_tag", TAG_SCRIPT)`
    + `module_from_spec` + `spec.loader.exec_module`.
  - `test_git_timeout_fails_cleanly`: `patch.object(mod, "subprocess")` (or
    `patch.object(mod.subprocess, "run", side_effect=subprocess.TimeoutExpired(cmd="git", timeout=60))`),
    call `mod.main(["--repo", str(self.repo), "--push"])` under
    `contextlib.redirect_stderr(io.StringIO())`, assert it returns `1` and the
    captured stderr contains `error:` and `timed out`, with no exception
    escaping.
  - `test_git_missing_fails_cleanly`: same shape with
    `side_effect=FileNotFoundError()`; assert `error:` and `git not found`.
  This directly exercises `run_git`'s exception mapping; a `--push` invocation
  reaches `run_git` at the first `ls-remote` call before any early return.
- A-038/039/037 lock-in: add a `WorkflowHygieneTest` class reading
  `.github/workflows/tests.yml` text and asserting:
  - `text.count("cache: pip") == 3`
  - `"concurrency:" in text` and `"cancel-in-progress: ${{ github.event_name == 'pull_request' }}" in text`
  - `"needs: [unittest, lint, release-payload-gate]" in text`
  - the gate `if:` push clause substring is present.

## Step 6 — Validate + mark ACs

- `make check` exit 0 (tests + ruff + mypy + generator --check + release gate).
- Confirm no payload path changed (release gate reports "no payload change; no
  version bump required") — this task must NOT bump the version.
- Mark the three prd ACs:
  - PR cache hits + superseded cancellation → implemented (Steps 1–2; CI
    observes hits/cancellation, WorkflowHygieneTest locks the wiring).
  - Push-lane gating implemented (Step 3), not duplicated (sibling deferred it).
  - Simulated git timeout produces clean `error:` + exit 1 (Step 5 test).

## Validation commands

- `make check`
- `python3 -c "import ast; ast.parse(open('.github/scripts/create-release-tag.py').read())"` (syntax)
- `python3 -m unittest tests.test_release_gate -v 2>&1 | tail -20`

## Rollback

Each step is an isolated edit; revert the tests.yml hunk or the script hunk
independently. No data migration, no generated payload, no installer state.
