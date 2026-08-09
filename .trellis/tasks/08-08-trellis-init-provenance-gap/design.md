# Design: local Trellis provenance manifest + checker

Required by the PRD Notes rule: the local-manifest route was chosen and grows
a generator, so this design precedes `task.py start`. Revised after
adversarial review round 1 (blocking findings: CI cannot read the untracked
`.trellis/.template-hashes.json`; `git check-ignore` without `--no-index` is
vacuous on tracked paths).

## Components

Two repo-own artifacts, both under `.github/` (the repo-own CI area, next to
the existing release-gate scripts):

- `.github/trellis-provenance.json` — the manifest (data).
- `.github/scripts/check-trellis-provenance.py` — generator + checker (one
  script, two modes). Python 3, stdlib only, ruff-clean (CI lints
  `.github/scripts`).

Neither file may live under `scripts/` (pack-installed territory per
`installed-targets.txt`) or any Trellis-owned path.

## Manifest schema

```json
{
  "__version": 1,
  "files": { "<repo-relative path>": "<sha256 hex, lowercase, 64 chars>" },
  "repoOwn": ["<repo-relative path>", "..."],
  "templateReceipted": ["<repo-relative path>", "..."]
}
```

- `files`: the 54 covered paths — 46 `.agents`, 7 `.codex`, `.gitignore`.
  Hashes are sha256 of blob content in the working tree at `--write` time.
- `repoOwn`: curated exclusion list — paths classified repo-own whose
  integrity record is git history: the 6 CI/release `.github` files,
  `PULL_REQUEST_TEMPLATE.md` (force-preserved by the pack, user-tunable),
  and the script and manifest themselves (they sit inside an enumerated
  dot-dir and would otherwise self-report as uncovered).
- `templateReceipted`: snapshot of the tracked platform paths covered by
  `.trellis/.template-hashes.json` (v2 schema, keys of the nested `hashes`
  object). Needed because that registry is gitignored and untracked
  (`.gitignore` Trellis-state block), so a CI checkout never has it; the
  manifest must be self-contained for coverage. Paths only, no hashes —
  integrity of those 116 files stays with Trellis's own machinery (PRD out
  of scope), this list settles coverage only.
- No timestamps or git SHAs: content-addressed only, so regeneration on an
  unchanged tree is byte-stable.

Strict validation on load (both modes): exactly the four schema keys;
`__version == 1`; hash values match `^[0-9a-f]{64}$`; all paths canonical
repo-relative (no `..`, no leading `/`, no duplicates); the three path sets
pairwise disjoint. Any violation exits 2 (malformed manifest, not a
finding).

## Enumeration (runtime, not a frozen list)

Covered universe = `git ls-files` under the six platform dot-dirs
(`.agents .claude .codex .gemini .github .opencode`) plus `.gitignore`.
Coverage sets consulted at check time:

- `.sd-ai-command-pack/provenance.json` `files` keys (tracked, always
  available).
- The manifest's `files`, `repoOwn`, and `templateReceipted`.
- When `.trellis/.template-hashes.json` exists locally, validate it before
  any use (check or `--write` refresh): `__version == 2`, a `hashes` object
  whose keys are canonical repo-relative paths and whose values match
  `^[0-9a-f]{64}$`. An invalid registry exits 2 and leaves the manifest
  untouched — a corrupt registry must never bless coverage membership into
  the CI snapshot. When valid, **check mode only** cross-checks: its
  tracked-platform key set must equal `templateReceipted`, else fail as
  `template-snapshot-stale` (rerun `--write` deliberately). Write mode does
  not enforce that equality — it is the repair path: it validates the live
  registry, builds the candidate snapshot from it, and atomically replaces
  the manifest. When absent (CI), the snapshot stands alone — no failure.

## Check mode (default, read-only)

Exit 0 = pass, 1 = findings, 2 = usage/environment/malformed-manifest error.
Every finding prints one line with the path and the failure class.

1. **Coverage:** every tracked platform file must appear in at least one
   coverage set. Any remainder fails as `uncovered` — a newly added
   unreceipted file forces a deliberate classification, never silent
   absorption.
2. **Integrity:** every `files` entry must exist, be tracked, be a regular
   non-symlink file, and hash to the recorded value. Content mismatch fails
   as `drifted`; missing/untracked fails as `missing`; symlink fails as
   `not-regular-file`.
3. **Gitignore durability:** for every tracked path under `.claude/`, run
   `git check-ignore --no-index -q -- <path>` and map its exit status
   exactly: `0` = the path is ignored, finding `ignored-tracked-path`;
   `1` = not ignored, pass; **any other status (e.g. 128 fatal) = exit 2**,
   never a pass — treating all nonzero as "not ignored" would let a broken
   Git invocation fail open. `--no-index` is load-bearing: without it Git
   suppresses ignore evaluation for tracked paths and the assertion can
   never fire. A wholesale `.claude/` ignore (the CONTRIBUTING.md:99-104
   re-init failure mode) then fails as `ignored-tracked-path` (and
   `.gitignore` itself as `drifted`).

The script writes nothing in check mode (guard-safe for sd-check's
GUARDED_PATHS rule, same constraint the gate-test/gate-lint variants honor).

## Write mode (`--write`)

Membership-conservative refresh:

- Re-hashes only paths already in `files` (dropping ones no longer tracked,
  with each removal printed).
- Refreshes `templateReceipted` from the live registry when present; keeps
  the existing snapshot (with a notice) when absent.
- Never touches `repoOwn` — that list is only ever edited by hand.
- Bootstrap (no manifest on disk yet): `--write` starts from an empty
  manifest, so the hand-curated `repoOwn` skeleton is written first and
  every initial `files` member enters through an explicit `--accept` — the
  same named-decision path as later additions, no special mode.
- A tracked platform file outside every coverage set is **not** absorbed:
  `--write` exits 1 listing each such path unless it is explicitly named via
  repeatable `--accept <path>`. Each accepted addition is printed. This
  keeps the PRD's inventory-first boundary: new paths enter the receipt only
  by named human decision, and existing drift is never silently reblessed
  (`--write` also prints every hash that changed).
- **Atomicity:** `--write` builds and validates the complete candidate
  manifest in memory first, then writes to a temporary file in the same
  directory and renames it over the target. On every exit 1 or 2 the
  on-disk manifest is byte-identical to before the invocation — a refused
  or failed write never partially rewrites or reblesses the receipt.

## Gate wiring

`make check` alone reaches neither sd-check nor CI (sd-check runs only the
`check.json` entries; CI jobs invoke individual commands), so three wires:

- Makefile: new `trellis-provenance` target running the script via
  `"$(RUN_PYTHON)"`, appended to the `check:` dependency list and `.PHONY`.
- sd-check: new entry in `.sd-ai-command-pack/check.json` — a
  repo-customizable registration file (tracked; absent from both
  `installed-targets.txt` and `provenance.json`, and the Makefile's
  guard-safe comment documents repo-side registration):
  `{ "id": "repo.trellis-provenance", "argv": ["make", "trellis-provenance"], "cwd": ".", "timeoutSeconds": 60 }`.
  Guard-safe: check mode writes nothing.
- CI: explicit step in the `release-payload-gate` job of `tests.yml`
  (already a prerequisite of `auto-tag-release` and `ci-result` via
  `needs`), mirroring the release-check pattern:
  `python .github/scripts/check-trellis-provenance.py`.

## Validation plan (maps to the PRD ACs)

Sequencing: the demonstrations run **after** the implementation (script,
manifest, wiring, tests) is committed on the feature branch, so the
disposable worktree materializes them from that commit — never from a dirty
tree with untracked new files. All mutation-based demonstrations run in a
disposable `git worktree` of the feature-branch HEAD (removed afterward),
never against the primary working tree —
no tamper, `.gitignore` edit, registry move, or scratch index change touches
live state. The one exception is the trivially reversible
`.trellis/.template-hashes.json` aside-move for CI parity, which is
untracked; it is moved back under a shell trap.

Check mode:

- Clean tree: exits 0.
- Tamper demo (AC2): append a byte to one covered `.agents` file, rerun,
  expect exit 1 with `drifted`; restore via `git checkout --`.
- Ignore demo (AC3): append a wholesale `.claude/` ignore to `.gitignore`,
  rerun, expect exit 1 with `ignored-tracked-path` for tracked adapter
  paths (plus `drifted` for `.gitignore`); restore.
- CI parity: move `.trellis/.template-hashes.json` aside, rerun, expect
  exit 0 (self-contained coverage); restore, corrupt one snapshot entry in
  a scratch copy to see `template-snapshot-stale`.

Write mode (regenerability, PRD requirement):

- `--write` twice on a clean tree: second run leaves the manifest
  byte-identical.
- New-path refusal: add a scratch tracked file under `.codex/`, expect
  `--write` exit 1 naming it; with `--accept`, expect absorption printed;
  clean up.
- `repoOwn` preservation: byte-compare the `repoOwn` array across `--write`.
- Failed-write atomicity: trigger the new-path refusal, byte-compare the
  manifest before/after the failed `--write`.

Coverage metrics (AC4): report both numbers at completion — original
two-registry-union uncovered = 62 (explicitly accepted, fully classified in
the PRD), checker four-set uncovered = 0.

## Durable regression tests

Manual demonstrations satisfy the ACs once; a unittest module
(`tests/test_trellis_provenance.py`) locks the contracts — unittest, not
pytest, because the repo's suite runs via `make test` / `unittest discover`
and pytest is not installed. It runs the script against disposable fixture
git repos (`tempfile.TemporaryDirectory`, no live-tree mutation):

- strict manifest parsing (bad key set, bad hash format, overlapping path
  sets, bad version, noncanonical path forms (`..`, leading `/`),
  duplicate array entries, and duplicate JSON object members → exit 2;
  duplicate-member detection requires decoding with a duplicate-aware
  `object_pairs_hook`, since plain `json.load` silently keeps the last
  member);
- live-registry validation (malformed v2 registry → exit 2, manifest
  untouched);
- check-mode findings: `uncovered`, `drifted`, `missing`,
  `not-regular-file`, `ignored-tracked-path`, `template-snapshot-stale`;
- `git check-ignore` exit-status mapping, including the fatal-status path
  (nonzero-non-one → exit 2, not a pass);
- `--write` byte-stability, `--accept` gating, `repoOwn` preservation, and
  failed-write atomicity;
- wiring text assertions: the `release-payload-gate` job in
  `.github/workflows/tests.yml` invokes the checker, `check.json` contains
  the `repo.trellis-provenance` entry, and the Makefile `check:` chain
  includes `trellis-provenance` (same pattern as the existing release-gate
  workflow-text tests in `tests/test_release_gate.py`).

## Risks / tradeoffs

- **Manifest staleness on intended upstream updates:** a legitimate Trellis
  re-init or pack update that changes covered files fails the gate until
  `--write` is rerun. Intended — the gate's whole point is making that
  change visible and deliberate.
- **`.gitignore` hand-edits above the generated block** also require
  `--write`; acceptable for a rarely-edited file, and the failure message
  names the path.
- **Self-reference:** the script/manifest are in `repoOwn`, so the checker
  never gates its own content; git history covers them like the other
  repo-own files.
- **`templateReceipted` drift window:** if Trellis init adds new templated
  paths, local runs catch the stale snapshot (`template-snapshot-stale`)
  but a CI-only environment cannot; the new paths would instead surface as
  `uncovered` once tracked, which is the acceptable backstop.
