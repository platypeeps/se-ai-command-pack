# Widen release payload gates — Design

## Overview

`make release-check` runs `.github/scripts/check-release-payload.py`, which
enforces: any change under a payload prefix (or to `manifest.json`) requires a
`manifest.json` version bump plus a matching `CHANGELOG.md` heading. Two gaps
(audit A-035, A-040):

1. **Vacuous local pass.** The script's `--base` defaults to `HEAD`, and the
   Makefile invokes it with no `--base`. `run_gate` then computes
   `merge-base(HEAD, HEAD) == HEAD`, so the diff range is empty and only
   *uncommitted* work is measured. A committed payload change with no bump
   passes locally (it is only caught in CI, which passes the real PR base).
2. **Narrow payload surface.** `PAYLOAD_PREFIXES = ("templates/", "generated/")`
   plus the exact `manifest.json`. Consumer-visible installer code —
   `install.py` and `installer/**` — is not gated, so an installer behavior
   change can ship with no bump + changelog.

## Proposal

### P1 — Range-aware Makefile via `--base auto`

Add an `auto` base mode to the script rather than shell logic in the Makefile
(keeps resolution unit-testable and platform-portable):

- New helper `resolve_base(repo, base)`: when `base == "auto"`, return
  `"origin/main"` if `git rev-parse --verify origin/main^{commit}` succeeds,
  else `"HEAD"`. Any other explicit value passes through unchanged.
- `main()` resolves the base through this helper before calling `run_gate`.
- Makefile `release-check` recipe passes `--base auto`.

CI is unaffected: it passes an explicit base SHA, which bypasses `auto`.
Fresh clones with no `origin/main` fall back to `HEAD` (today's behavior — no
regression, no hard failure). `--base` default stays `HEAD` so a bare
`python check-release-payload.py` keeps its documented uncommitted-only meaning.

**Local check is best-effort, CI is authoritative.** `auto` only checks that
`origin/main` *resolves*, not that it is current. If a local `origin/main` ref
is stale (behind the real remote) and mainline has since bumped `manifest.json`,
`merge-base(origin/main, HEAD)` can land on a pre-bump commit; the gate then sees
`version_changed == True` and an already-matching changelog, so a payload change
on the branch that added *no bump of its own* can pass locally. This is a
property of the diff-vs-merge-base gate itself, not new to `auto`. It is
acceptable because CI's `release-payload-gate` lane uses the real PR base SHA
(`github.event.pull_request.base.sha`), which is never stale, and is the
authoritative gate. The local check is a convenience pre-check; do NOT claim it
is a sound branch-only guarantee. CONTRIBUTING documents this and suggests
`git fetch` before relying on the local result.

### P2 — Widen the payload surface

- Add `"installer/"` to `PAYLOAD_PREFIXES`.
- `install.py` is a single file, not a prefix. Introduce
  `PAYLOAD_EXACT = {MANIFEST_NAME, "install.py"}` and change the membership
  test from `path == MANIFEST_NAME or path.startswith(PAYLOAD_PREFIXES)` to
  `path in PAYLOAD_EXACT or path.startswith(PAYLOAD_PREFIXES)`.

**Consequence — family-metadata bump contract shifts (blanket rule, chosen).**
`FAMILY_DESCRIPTIONS` and `FAMILY_LABELS` live in `installer/registry.py:88`.
Once `installer/` is gated, editing a family description is a shipped-payload
byte change and therefore requires a bump — even though it also re-renders
non-payload README prose. The existing spec rows
`.trellis/spec/backend/quality-guidelines.md:157` and `:172-173` illustrate a
"family-description edit that only re-renders non-payload prose" passing without
a bump; that example is no longer reachable once `installer/registry.py` is
payload. We deliberately take the blanket `installer/` rule (it matches this
task's goal — consumer-visible installer changes get release discipline) rather
than carving `registry.py` out, and we correct those spec rows to say a
family-description *source* edit needs a bump; only a metadata/catalog change
that touches no shipped payload byte stays bump-free.

### P3 — Payload carve-out (preserve, do not add code)

The correct carve-out is **"a change that leaves every shipped payload path
byte-identical (no git diff) needs no bump"** — NOT "byte-identical
`manifest.json`". This matches the committed spec in
`.trellis/spec/backend/quality-guidelines.md:172-173` (added in b225583 for PR
#131), which is explicit that `generated/registry-snapshot.json` is shipped
payload under `generated/`: registry-metadata edits that alter the snapshot DO
require a bump; only edits that touch no shipped payload byte pass without one.

The carve-out is automatic: `changed_paths` is derived from `git diff`, and a
byte-identical file never appears in a diff. So a regeneration whose payload
output (manifest.json, registry-snapshot.json, any `templates/**` or
`generated/**` file) is unchanged does not enter `payload_changed` and needs no
bump. Widening the prefixes to installer paths does not touch this: those are
distinct paths. The carve-out is preserved structurally; we add a regression
test asserting it (a non-payload edit alongside an untouched payload tree) and
correct the CONTRIBUTING wording so it names "no shipped payload byte changed"
rather than the too-narrow "manifest.json byte-identical".

## Boundaries And Non-Goals

- Not implementing the optional A-037 stretch (payload gate on push-to-main as
  an auto-tag prerequisite). Recorded as an explicit follow-up.
- No change to the version-bump / changelog-heading rules themselves.
- No change to CI's explicit-base invocation in `.github/workflows/tests.yml`.
- No new manifest kinds, generator changes, or installer behavior changes —
  gate scope only.

## Affected Files

- `.github/scripts/check-release-payload.py` — `resolve_base` helper, `main`
  wiring, `PAYLOAD_PREFIXES` += `installer/`, new `PAYLOAD_EXACT` set.
- `Makefile` — `release-check` recipe passes `--base auto`.
- `CONTRIBUTING.md` — release-discipline section: add `install.py` +
  `installer/**` to the gated surface, state the "no shipped payload byte
  changed" carve-out, and the best-effort range-aware local check.
- `.trellis/spec/backend/quality-guidelines.md` — rows at `:157` and `:172-173`:
  correct the family-metadata bump contract now that `installer/registry.py` is
  gated payload (family-description source edit requires a bump).
- `tests/test_release_gate.py` — new cases (installer file, install.py exact
  positive+negative, `--base auto` positive+fallback, no-payload-diff carve-out
  regression).

## Data And Command Contracts

- CLI: `check-release-payload.py [--repo R] [--base REV|auto]`. `auto` is new;
  default remains `HEAD`; explicit revs unchanged.
- Gated surface (post-change): any changed path where
  `path in {manifest.json, install.py}` or
  `path.startswith(("templates/", "generated/", "installer/"))` requires
  `manifest.json` version != base version, and a matching changelog heading.
- Exit codes unchanged: 0 pass, 1 `GateError`.

## Risks And Edge Cases

- **`origin/main` unresolvable** (fresh clone, renamed remote): `auto` falls
  back to `HEAD` → uncommitted-only, same as today. No crash. Covered by test.
- **`auto` on a branch already merged/behind main**: `merge-base(origin/main,
  HEAD)` gives the common ancestor, correctly scoping the branch's own changes.
- **install.py touched with a bump**: passes — verified by existing bump test
  pattern extended to install.py.
- **Over-capture regression**: adding `installer/` must not accidentally match
  an unrelated top-level path (e.g. a hypothetical `installer-notes.md` at
  root would match the `installer` prefix only if named `installer/...`; a file
  literally `installerX` would false-match `installer` — but `startswith` uses
  the trailing slash `"installer/"`, so `installerX` does not match). Safe.
- **Local dirty tree during `auto`**: uncommitted + committed range both
  measured (merge-base to working tree), matching the script's documented
  "uncommitted and untracked included" behavior.

## Validation

- `make release-check` (with a synthetic committed installer change + no bump
  on a scratch branch) must now fail; passes clean on `main`.
- `python -m pytest tests/test_release_gate.py -q` — all existing + new cases.
- `make check` green (test + lint + release-check).
