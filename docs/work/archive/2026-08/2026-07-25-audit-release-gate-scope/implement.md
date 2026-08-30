# Widen release payload gates — Implementation Plan

## Execution Order

1. **Script: base resolution (P1).** In
   `.github/scripts/check-release-payload.py`:
   - Add `resolve_base(repo: Path, base: str) -> str`: if `base != "auto"`,
     return it unchanged; else return `"origin/main"` when
     `run_git(repo, "rev-parse", "--verify", "origin/main^{commit}")` has
     `returncode == 0`, otherwise `"HEAD"`.
   - In `main()`, after resolving `repo`, compute
     `base = resolve_base(repo, args.base)` and pass it to `run_gate`.
   - Update the `--base` help to mention `auto`.

2. **Script: widen surface (P2).**
   - `PAYLOAD_PREFIXES = ("templates/", "generated/", "installer/")`.
   - Add `PAYLOAD_EXACT = frozenset({MANIFEST_NAME, "install.py"})`.
   - In `run_gate`, change the comprehension guard to
     `if path in PAYLOAD_EXACT or path.startswith(PAYLOAD_PREFIXES)`.
   - Update the module docstring's item 1 to name installer paths.

3. **Makefile (P1 wiring).** `release-check` recipe: change the gate line to
   `"$(RUN_PYTHON)" .github/scripts/check-release-payload.py --base auto`.

4. **CONTRIBUTING (P3 docs).** Release-discipline section: extend the gated
   surface list to `install.py` and `installer/**`. State the carve-out
   correctly: a change that leaves **every shipped payload path byte-identical**
   (no git diff) needs no bump — and note `generated/registry-snapshot.json` is
   itself payload, so registry-metadata edits that alter it DO require a bump
   (mirror `.trellis/spec/backend/quality-guidelines.md:172-173`; do NOT write
   the narrower "manifest.json byte-identical"). Note `make release-check` is
   range-aware against `origin/main` locally, is best-effort (a stale
   `origin/main` can mask a missing bump — `git fetch` first), and that CI
   against the real PR base is the authoritative gate.

4b. **Spec correction (C-6).** Update
   `.trellis/spec/backend/quality-guidelines.md` rows `:157` and `:172-173` so
   the family-metadata bump contract reflects `installer/registry.py` now being
   gated payload (family-description source edit needs a bump; only a change
   touching no shipped payload byte stays bump-free). Same PR as the gate change.

5. **Tests (`tests/test_release_gate.py`).** Add:
   - `test_installer_dir_change_without_bump_fails` — write
     `installer/<file>.py`, commit on a feature branch, `gate(base="main")`
     → returncode 1, "without a version bump".
   - `test_install_py_change_without_bump_fails` — same for a root
     `install.py` edit (exercises the exact-match predicate operand).
   - `test_install_py_change_with_bump_passes` — install.py edit + version bump
     + changelog heading → 0 (positive exact-match branch; C-5).
   - `test_installer_change_with_bump_passes` — installer change + version
     bump + changelog heading → 0.
   - `test_base_auto_falls_back_to_head_without_origin` — repo without an
     `origin/main` ref; `gate(base="auto")` behaves as HEAD (uncommitted-only);
     assert a committed payload-without-bump on a branch is *not* flagged
     (proving fallback), and an uncommitted one *is*.
   - `test_base_auto_uses_origin_main_when_present` — positive `auto` path
     (C-2): synthesize the ref with
     `git update-ref refs/remotes/origin/main <main-sha>` (no network), commit a
     payload change without a bump on a feature branch, `gate(base="auto")` →
     returncode 1, "without a version bump". Proves `auto` resolves to
     `origin/main` and measures the branch range, not just uncommitted work.
   - `test_no_payload_diff_passes_without_bump` — carve-out regression guard
     (C-3): make a non-payload edit (e.g. README) while every shipped payload
     path (manifest.json, generated/**, templates/**, installer/**, install.py)
     stays byte-identical → 0. Guards against anyone replacing the diff-based
     detection with a stat/mtime scheme. (This is the accurate carve-out — a
     "rewrite manifest.json with identical bytes" test would be tautological and
     would not represent the real registry-metadata scenario.)

## Validation Plan

- Focused: `python -m pytest tests/test_release_gate.py -q`.
- Manual gate proof (script): on a scratch branch, add `installer/_probe.py`,
  commit without bump, run
  `python .github/scripts/check-release-payload.py --base auto` → expect
  exit 1; delete probe.
- Makefile integration proof (C-2): from the same scratch state, run
  `make release-check` (which now passes `--base auto`) and confirm it fails on
  the probe and passes once the probe is removed — proves the recipe wiring, not
  just the script.
- Broad: `make check` (runs generate --check, tests, ruff, mypy,
  release-check). Must be green.
- Lint scope already includes `.github/scripts` and `tests` (Makefile:30).

## Documentation And Spec Updates

- CONTRIBUTING.md release-discipline (step 4 above).
- `.trellis/spec/backend/quality-guidelines.md` (C-6): rows at `:157` and
  `:172-173` currently say family-metadata edits pass without a bump when
  payload bytes are unchanged, illustrated by "a family-description edit that
  only re-renders non-payload prose." Once `installer/` is gated,
  `installer/registry.py` (holding `FAMILY_DESCRIPTIONS`) is payload, so that
  example is unreachable. Correct the rows: a family-description *source* edit
  requires a bump; only a metadata/catalog change touching NO shipped payload
  byte (not manifest.json, generated/**, templates/**, install.py, or
  installer/**) stays bump-free. Do this edit in the SAME PR as the gate change
  so the spec never lags the enforced surface.
- No `manifest.json` version bump required for THIS task: it changes only
  gate tooling, tests, Makefile, and docs/spec — none under a payload prefix and
  not `install.py`/`manifest.json` (the spec doc lives under `.trellis/`, not a
  payload path). Confirm the gate passes vacuously for this PR's own diff (no
  payload paths touched). Any carve-out/installer test fixture writes inside the
  test's temp repo (TempDirTestCase), never the real pack tree.

## Review Notes

- Reviewer-sensitive: the `"installer/"` prefix uses a trailing slash so it
  cannot false-match a sibling like `installerX`. Call this out.
- `--base auto` must not change CI behavior — CI passes an explicit SHA. Grep
  `.github/workflows/tests.yml` to confirm no `auto` reliance and that the
  explicit base path is untouched.
- Keep `--base` default at `HEAD` so the documented bare-invocation contract
  and `test_real_pack_gate_passes` (no `--base`) stay valid.

## Rollback Points

- Each of the four edits (script, Makefile, CONTRIBUTING, tests) is
  independent; revert the script + Makefile pair together if `auto` misbehaves,
  leaving prefix-widening intact, or revert the whole commit.
- No data migration, no generated-output regeneration, no manifest bump — clean
  single-commit revert.

## Follow-Ups (outside this PR)

- A-037 (P3): run the payload gate on push-to-main (base = last release tag) as
  an auto-tag-release prerequisite, or document that branch protection forbids
  direct pushes to `main`. File/keep as a separate task.
