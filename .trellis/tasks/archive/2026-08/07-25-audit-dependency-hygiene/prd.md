# Dependency hygiene for npm and transitive pins

## Goal

Every third-party fetch this repo triggers is deliberate and reviewed. The
Python dev toolchain becomes fully hash-locked and wheel-only; no npm lifecycle
script runs un-reviewed; and the one fetch that stays unlocked — the
`npx --yes repomix` docs refresh — is recorded as an accepted risk rather than
left unexamined.

**The goal is deliberately narrower than the original.** That original text
promised "no unpinned transitives" without qualification. This task does not
deliver that for npm: `scripts/update_repomix` is repo-owned, so its unlocked
transitive tree is squarely in scope, and it is being *accepted*, not solved —
vendoring an npm lockfile plus an `npm ci` step for a docs-only tool that produces a
gitignored artifact is more machinery than the exposure warrants. Two absolutes
therefore become one pip absolute plus one recorded acceptance, which is what
the audit's own fix line permits (`.trellis/audit/report-2026-07-25.md:288`).

## Requirements

- **[A-032 — reclassified, local-only record.](#a-032-disposition-local-only-record)**
  `.opencode/package.json` is **upstream-Trellis vendored**, not repo-owned:
  `.trellis/.template-hashes.json` (Registry A) contains it,
  `.sd-ai-command-pack/manifest.json` (Registry B) does not, and
  `.github/trellis-provenance.json` lists it under `templateReceipted`. Per
  "Vendored-Artifact Ownership And Upstream Route"
  (`.trellis/spec/backend/quality-guidelines.md:786` classifies it; `:843`
  records that a local edit into a vendored file survives only until the next
  pack refresh, observed with commit `bc01bc2`), a code edit here is
  reverted by the next Trellis refresh, so removing `@opencode-ai/plugin`
  locally is out of scope. This task records the four-field local-only record
  (below, and in the spec) and corrects `CONTRIBUTING.md:78`, which today
  asserts the dependency is "slated for removal" as if this repository owned
  that removal.
- Compile a fully pinned, hash-locked dev requirements file with
  `uv pip compile --universal --generate-hashes` and use it in CI and
  `make setup`; transitives float today. Installs must be binary-only so a
  future missing wheel cannot silently execute a source build. [A-033]
- `scripts/update_repomix`: stop `npx` from running package lifecycle scripts,
  matching the script's existing `NPM_CONFIG_*` environment-variable style, and
  record the remaining unlocked-transitive exposure as accepted. The audit's own
  fix line offers exactly this disjunction — "Add --ignore-scripts, or move
  behind a committed package-lock + npm ci; otherwise record the risk as
  accepted" (`.trellis/audit/report-2026-07-25.md:288`) — and this task takes the
  first and third branches, not the second. [A-034]
- Coordinate with 07-25-audit-dependabot-config (bot + audit lane, archived
  `2026-08`) — that task owns update automation; this one owns the pinning
  surface. The lock must not become a second Dependabot-managed manifest, and a
  Dependabot bump of `requirements-dev.txt` must fail loudly rather than
  silently install stale pins.

## Acceptance Criteria

- [x] `.opencode/package.json`'s floating `@opencode-ai/plugin` dependency is
      recorded as an upstream-Trellis defect with all four local-only-record
      fields, in both this PRD and
      `.trellis/spec/backend/quality-guidelines.md`, and no **living** guidance
      document (`CONTRIBUTING.md`, `README.md`, `AGENTS.md`, `docs/`, active
      specs) still claims this repository will remove it. Archived task
      artifacts under `.trellis/tasks/archive/` are historical records and are
      deliberately left unedited.
      - Evidence: the four fields appear here (`## A-032 disposition`) and in
        `quality-guidelines.md` "Scenario: Vendored OpenCode npm Manifest"
        (`:2259`). `CONTRIBUTING.md:87` no longer says "slated for removal"; it
        states the upstream ownership and points at the spec record. The sweep
        `grep -rn "opencode-ai/plugin\|slated for removal\|removal-pending"
        --include="*.md" . | grep -v "^./.trellis/tasks/archive/"` returns only
        this task's artifacts, the two new records, the audit report/ledger
        (historical finding text), and no removal claim in living guidance.
      - The `.trellis/audit/ledger.md` A-032 entry keeps `status: open`: all 44
        ledger entries are `open`, the file is managed by `sd-audit-repo`, and
        the already-fixed A-031 was left open by the archived task that fixed
        it. Flipping one entry by hand would invent a convention.
- [x] CI and `make setup` install from the hash-locked file with
      `--require-hashes --only-binary :all:`; transitive drift cannot change
      lane behavior day to day.
      - Evidence: `Makefile:17` and all three installing jobs in
        `.github/workflows/tests.yml` (`:39`, `:63`, `:83`) install
        `-r requirements-dev.lock` with both flags, and `cache-dependency-path`
        follows the lock. `make setup` rebuilt `.venv` with `--clear` and
        installed exactly the 9 locked entries whose markers admit CPython 3.13
        (`tomli` is excluded by `python_full_version < '3.11'`); the same
        install into a throwaway `mktemp -d` venv reproduced that set.
        `make lock` re-run over the committed lock produced a byte-identical
        file, so the lock is compiler output rather than a hand-edit.
- [x] A deterministic, offline check fails when a **direct** pin in
      `requirements-dev.txt` is missing from the lock, present at a different
      version, or loosened off `==`, and when any lock entry is unpinned or
      unhashed. That is the Dependabot failure mode; the check does not claim to
      prove the lock is a complete regeneration of its input, which is not
      decidable offline.
      - Evidence: `.github/scripts/check-dev-requirements-lock.py` (stdlib-only,
        no network) is wired into `make lock-check`, `make check`,
        `.sd-ai-command-pack/check.json` (`repo.lockcheck`), and the `lint` job
        *before* its install step. `tests/test_dev_requirements_lock.py` covers
        all five finding classes — including a `ruff>=0.16` lock fixture that
        must report `unpinned` rather than skip — plus both exit-2 paths:
        14 tests, `OK`. A disposable-fixture negative run printed
        `pin-mismatch: ruff is 0.0.1 … but 0.16.1 …; run \`make lock\`` and
        exited 1, with the real `requirements-dev.txt` unmodified.
      - The stated limitation is honoured in the docstring and in the spec
        scenario: a transitive silently held back, or an internally consistent
        hand-edited lock, passes this check. Only `make lock` plus an empty
        diff proves regeneration.
- [x] `make repomix` no longer runs package lifecycle scripts, and the residual
      unlocked-transitive exposure is recorded as accepted where the pattern is
      documented.
      - Evidence: `scripts/update_repomix` exports
        `NPM_CONFIG_IGNORE_SCRIPTS=true` before `exec npx`, and
        `tests/test_repomix.py` asserts both the export and that ordering — npm
        reads its configuration at invocation time, so an export after
        `exec npx` would never apply. `make repomix` ran end to end on
        2026-08-10: 134 files, `Security: ✔ No suspicious files detected`,
        `docs/repomix-map.md` regenerated.
      - Residual risk recorded in the `README.md` repomix section ("Accepted
        risk — unlocked npm transitives") and in the spec's repomix scenario
        contracts. The audit's second branch (a committed npm lockfile plus
        `npm ci`) is deliberately not taken.

## A-032 disposition: local-only record

1. **Owning pack**: upstream Trellis (`mindfold-ai/Trellis`), version `0.6.7`
   per `.trellis/.version`.
2. **File**: `.opencode/package.json` — Registry A member
   (`.trellis/.template-hashes.json`), absent from Registry B
   (`.sd-ai-command-pack/manifest.json`), and `templateReceipted` in
   `.github/trellis-provenance.json`.
3. **Behaviour**: it declares `@opencode-ai/plugin: ^1.14.39` while no
   `.opencode` JavaScript imports it — every import in `.opencode/lib/*.js` and
   `.opencode/plugins/*.js` resolves to a node builtin or a sibling module — so
   a caret range is resolved for a package nothing uses. Those installs land in
   the checkout (`.gitignore:70` ignores `.opencode/node_modules/`). The
   upstream fix is to drop the dependency, or pin it exactly and ship a
   lockfile if it is kept for editor types.
4. **No upstream pull request was opened**, and upstream approval was not
   sought. The upstream repository *is* identifiable — `mindfold-ai/Trellis`,
   already cited at `.trellis/spec/backend/quality-guidelines.md:651` — so the
   relay is blocked on explicit per-PR approval, not on missing identity. It is
   recorded as a follow-up in `implement.md`.

## Notes

- Audit findings: A-032, A-033, A-034 (P3/S) —
  `.trellis/audit/report-2026-07-25.md`.
- Evidence: `.opencode/package.json:3`; `.opencode/lib/session-utils.js:2`;
  `requirements-dev.txt:4-7`; `.github/workflows/tests.yml:39`, `:60`, `:80`;
  `scripts/update_repomix:24`; `README.md:290`; `CONTRIBUTING.md:78`.
- **Measured 2026-08-10** (all counts below are that day's measurement, not a
  standing constant):
  - `.opencode` JavaScript imports only node builtins (`fs`, `path`, `os`,
    `child_process`, `crypto`, `process`) and sibling `.opencode/lib/*.js`
    modules — `@opencode-ai/plugin` is imported nowhere, confirming the A-032
    premise.
  - `requirements-dev.txt` declares 4 direct pins (PyYAML, ruff, mypy,
    coverage). A universal resolve floored at Python 3.10 adds **6 unpinned
    transitives, all via mypy**: `ast-serialize`, `librt`, `mypy-extensions`,
    `pathspec`, `typing-extensions`, and `tomli` — 10 locked entries in total.
    The lock's own `# via` comment attributes `tomli` to mypy
    (`mypy` declares `tomli; python_version < "3.11"`); coverage's `tomli`
    dependency sits behind its unrequested `toml` extra. The audit's "5
    unpinned transitives via mypy" (`report-2026-07-25.md:278`) counted a local
    freeze on Python 3.13, where `tomli`'s marker excludes it — 5 and 6 are the
    same set measured at different interpreter versions, not a contradiction.
  - Drift is live, not theoretical: this machine's `.venv` holds
    `ast_serialize==0.6.0` while today's resolve of the same unchanged
    `mypy==2.3.0` pin yields `ast-serialize==0.8.0`.
- `README.md:463` in the original evidence list no longer points at the repomix
  section; the current location is `README.md:290`.
- Planning depth: escalated from PRD-only to `prd.md` + `design.md` +
  `implement.md` (contract at `.trellis/workflow.md:164` requires both
  together). The original PRD named that exact escalation trigger — "if an
  unpinned transitive turns out to need a lockfile strategy" — and A-033 does: a
  new generated artifact, a new CI input, and a Dependabot interaction.
