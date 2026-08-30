# Design — Repomix map policy decision (A-025)

## Decision (planning gate)

**Option (a): gitignore `docs/repomix-map.md` and generate it on demand via
`make repomix`.** Audit-preferred, and confirmed by the operator on
2026-08-04. Option (b) (keep committing + add a `--check` drift mode) is
rejected: it leaves the 1.1 MB artifact accumulating in history, which is the
root A-025 concern.

Rationale: once the map is never committed, a committed-but-stale state is
structurally impossible — there is no tracked copy to drift. That satisfies the
"no silent-drift state remains possible" acceptance criterion without adding a
new drift gate. History rewrite of the already-committed 1.1 MB is explicitly
out of scope and left as a separate, later decision (per PRD).

## Current state (evidence)

- `docs/repomix-map.md`: tracked, 1.1 MB, 118 commits of history. Not gitignored.
- Generation already exists: `make repomix` → `scripts/update_repomix` runs
  pinned `repomix@1.16.1` via `npx`, writing `docs/repomix-map.md` from
  `repomix.config.json` (`output.filePath = docs/repomix-map.md`).
- Consumers:
  - `scripts/sd-ai-command-pack-install-audit.py:266` — already **excludes**
    `repomix-map.md` from the reference scan. No change.
  - `scripts/sd-ai-command-pack-check.py:103` — path is in `GUARDED_PATHS`,
    hashed **by path** into the check-state fingerprint via `_hash_path`, which
    is present-or-absent safe. No change; keeps a content signal even when
    untracked.
  - `sd-update-spec` reads the map **"when present"** — already tolerates
    absence (fresh clones will not have it). No change.
  - `scripts/sd-ai-command-pack-review-preflight.mjs`,
    `scripts/sd-ai-command-pack-review-scope.sh:146`,
    `scripts/sd-ai-command-pack-pr-body-scope.py:196` classify the path as
    "tooling/generated scope" **when it appears in a diff**. Once gitignored it
    stops appearing in diffs, so these entries become inert but remain a
    correct, defensive classification if the file is ever force-added. Left in
    place (removing them expands scope without benefit).
  - `tests/test_repomix.py:89` — `test_checked_in_map_matches_scope_contract`
    reads `MAP_PATH` **unconditionally**. Under gitignore the map is absent on
    fresh clones and CI, so this test would fail. **Must change.**

## Changes

1. **`.gitignore`** — add `docs/repomix-map.md`.
2. **Untrack** — `git rm --cached docs/repomix-map.md` (keep the working-tree
   copy; the commit records only the tracking removal).
3. **`tests/test_repomix.py`** — the config-contract test is unchanged. Rename
   `test_checked_in_map_matches_scope_contract` to reflect the new policy and
   guard it with `unittest.skipUnless(MAP_PATH.exists(), ...)` so it validates
   the map's scope headers **when present** (local dev after `make repomix`) and
   skips cleanly when absent (CI / fresh clone). No network generation is added
   to the test — the suite stays hermetic.
4. **`.trellis/spec/backend/quality-guidelines.md`** (§3 Contracts, §4
   Validation matrix, §5 Good case) — replace "regenerate and commit … in the
   same change" and "replaces the tracked map" with the on-demand,
   gitignored-never-committed policy. Add one line stating the map is gitignored
   and generated on demand.
5. **`README.md:467`** — reword the Repomix section so it describes an
   on-demand, gitignored artifact rather than a committed file, and keep the
   `make repomix` instruction. Remove the implication that the linked file is
   checked in.

## Non-changes (verified, with reason)

- `repomix.config.json` — `output.filePath` stays `docs/repomix-map.md`; the
  config test is unaffected.
- `scripts/update_repomix`, `make repomix` — generation path unchanged.
- install-audit, check.py, sd-update-spec, review-scope consumers — tolerate
  absence as shown above.

## Compatibility / rollout / rollback

- **Diff shape:** the PR removes 1.1 MB of tracked content (`git rm --cached`),
  which the tooling/generated-scope classifiers flag. The PR body must carry the
  "Tooling/generated scope:" section (sd-create-pr / pack.review-scope gate).
- **Fresh clone / CI:** map absent → dependent reads are "when present" or
  skip-guarded, so nothing breaks. Anyone wanting the map runs `make repomix`.
- **Rollback:** revert the commit; the file returns to tracked state. No data
  loss (generation is deterministic from source).

## Planning adversarial review — concern ledger

Host lane: complete. Codex lane: complete (task `blq6cxdxf`, exit 0).

- **C-1** (blocking) Unguarded map read `tests/test_repomix.py:90` breaks on
  fresh clone/CI → **addressed**: renamed to
  `test_generated_map_matches_scope_contract_when_present` with
  `skipUnless(MAP_PATH.exists())`.
- **C-2** (blocking-if-true) Map is a release/manifest payload target →
  **rebutted**: `manifest.json` and `.sd-ai-command-pack/manifest.json` have 0
  references; install-audit `REFERENCE_SCAN_EXCLUDED_NAMES` excludes it.
- **C-3** (medium) README/doc reference breaks doc-path check once untracked →
  **rebutted**: `review-preflight.mjs checkDocumentationPathReferences()`
  special-cases `docs/repomix-map.md`; README link replaced with a code-form
  path (no dead Markdown link on fresh clones).
- **C-4** (Codex, high) Spec update incomplete — contradictory "checked-in"
  language and a nonexistent stale-map gate at quality-guidelines.md §"PR Full
  Check" → **addressed**: removed the `| The Repomix map is stale | make check
  exits nonzero ... |` row (that gate never existed in `make check` and is
  meaningless once nothing is committed) and reworded §1/§3/§4/§5/§6 of the
  Repomix scenario.
- **C-5** (Codex, medium) On-demand workflow never exercised → **addressed**:
  `make repomix` added to the validation gate and run (exit 0, security-clean)
  to prove generation after untracking.
- **C-6** (Codex, medium) Consumer audit omits `sd-update-spec` →
  **rebutted**: the sd-update-spec repository-map extension *generates* via the
  detected `make repomix` target and follows the documented output path; it
  never reads a pre-committed map, so it is presence-safe.
- **C-7** (Codex, low) Manifest verification command used uppercase `MANIFEST*`
  → **addressed**: implement.md now greps the real lowercase `manifest.json`;
  the underlying "not a payload target" fact was already verified.

No unresolved blockers.

## Risks

- A consumer reads the map without a presence guard and fails on a fresh clone.
  Mitigation: the implement plan greps every `repomix-map` reference and
  confirms each is either excluded, present-or-absent safe, or skip-guarded
  before ship.
- The shipped release payload references the map as an installed target.
  Mitigation: implement step verifies it is not a manifest/payload target
  (install-audit already excludes it; confirm no MANIFEST entry).
