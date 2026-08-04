# Versioned registry snapshot for skill_review — Design

## Overview

Today the shipped `templates/skills/se-review-skills/scripts/skill_review.py`
reconstructs a subset of `installer/registry.py` by AST-parsing the reviewed
checkout's copy (`_parse_registry`, the single reader at
`_package_context` line 326). A registry/layout refactor in an installed copy
can silently misparse and degrade review output fleet-wide, with no version
signal. This design replaces the AST parse with a **versioned, generated JSON
snapshot** that `make generate` emits and drift-gates, and that `skill_review.py`
consumes and version-checks.

## Proposal

Two seams, both mirroring existing repo patterns.

### Producer — `generated/registry-snapshot.json`

Add a snapshot producer to `.github/scripts/generate-skill-surfaces.py` that
serializes exactly the registry facts the consumer needs (the five
`RegistryData` fields), from the same `installer/registry.py` names the
generator already imports (`FAMILY_LABELS`, `SKILLS`, `PLATFORM_REGISTRY`,
`SHARED_REFERENCES`). Output a single JSON file `generated/registry-snapshot.json`
carrying its own `schemaVersion`. Wire it into `main`'s regenerate → `--check`
diff → write flow like the other generated surfaces, including a missing/drift
guard (single-file variant).

Because the file lives under `generated/`, the existing release-payload gate
(`check-release-payload.py`, `PAYLOAD_PREFIXES = ("templates/", "generated/")`)
already forces the `manifest.json` version bump + dated `CHANGELOG.md` heading
with **zero new gate code**.

Snapshot schema (`schemaVersion: 1`):

```json
{
  "schemaVersion": 1,
  "familyOrder": ["improve", "..."],
  "skills": [{"name": "se-...", "family": "improve"}, ...],
  "platforms": ["agents", "claude", "codex"],
  "sharedReferences": {"_shared/references/foo.md": ["se-a", "se-b"], ...}
}
```

Field ordering is authoritative and preserved: `skills` follows canonical
`SKILLS` order (so `skill_order`), `familyOrder` follows `FAMILY_LABELS` order,
`platforms` is sorted (matching the current `_parse_registry` sort at line 312),
`sharedReferences` preserves `SHARED_REFERENCES` key order. This byte-for-byte
determinism is what keeps review output — and the emitted `snapshotId`
(payload built from `familyOrder`/`declaredPlatforms`, lines 1453-1454, 1542) —
unchanged.

### Consumer — snapshot-preferred loader in `skill_review.py` (C-1)

Add `_load_registry_snapshot(path) -> RegistryData | None` returning the
identical frozen `RegistryData` dataclass when a valid snapshot is present, and
`None` when there is no usable snapshot to consume. At the single call site
(`_package_context` line 326), **prefer** the snapshot and **fall back** to the
existing `_parse_registry` AST path:

```python
snapshot = _load_registry_snapshot(package_root / "generated" / "registry-snapshot.json")
registry = snapshot if snapshot is not None else _parse_registry(package_root / "installer" / "registry.py")
```

`_parse_registry` and its AST helpers (`_assignment`, `_string_value`,
`_call_value`) are **retained** as the legacy fallback so neither the SE pack
nor an SD-pack checkout regresses before the SD repo ships its own producer.
This is the transitional state; the fallback's removal is a bounded follow-up.
Every downstream consumer already depends only on the five `RegistryData`
fields, so nothing else changes.

Version + integrity contract (mirrors `installer/manifest.py`
`SUPPORTED_MANIFEST_SCHEMA_VERSION` fail-closed load, lines 32/59-67). Only a
**present, well-formed, version-compatible** snapshot short-circuits the
fallback; a present-but-broken snapshot fails closed (it must not silently
fall through to the AST path and mask a shipped-snapshot defect):

| Snapshot state | Behavior | Rationale |
|---|---|---|
| **Absent** (no file) | return `None` → AST fallback (`_parse_registry`) | Preserves today's behavior for both packs; covers foreign / pre-migration checkouts |
| **Symlink** at the snapshot path | return `None` → AST fallback | Trust boundary: never follow a symlinked snapshot into an external file (mirrors `_parse_registry`'s `path.is_symlink()` guard, line 245) |
| **Present, `schemaVersion` wrong type** (bool, float, str, …) | `ReviewError` | `True`/`1.0` are `== 1` so `in frozenset({1})` is a trap; require `type(v) is int` first, mirroring `installer/manifest.py:59` |
| **Present, `schemaVersion` an int not in supported set** | `ReviewError` | Core goal: installed copies **detect incompatibility instead of misparsing**; covers a future/newer schema and an undefined `0`/missing version |
| **Present, malformed / not JSON / missing required key / wrong field types** | `ReviewError` | Do not silently degrade — or silently fall through — for a shipped-but-corrupt snapshot |
| **Present, valid, `schemaVersion` in supported set** | parse → `RegistryData` | Normal path |

`SUPPORTED_REGISTRY_SNAPSHOT_SCHEMA_VERSIONS = frozenset({1})` in
`skill_review.py`. Acceptance uses an explicit supported **set** (not a `>`
comparison): a version not in the set fails closed regardless of direction, so
an undefined `0` or a newer additive `2` both raise until deliberately added to
the set. Keep `import ast` — used by both `_parse_registry` and `_frontmatter`
`ast.literal_eval` (line 445).

The consumer stays pack-neutral: the same JSON schema serves both the SE pack
(from `SKILLS`) and the SD pack (from `COMMAND_REGISTRY`) — each pack's own
generator produces its own snapshot. This PR ships only the SE producer; the SD
checkout uses the AST fallback until its repo ships the twin producer.

## Boundaries And Non-Goals

- **SD pack twin**: the sd-ai-command-pack repo's `skill_review.py` also parses
  its `COMMAND_REGISTRY`/`CommandInfo` and needs its own generator to emit the
  same-schema snapshot. That is a separate task in that repo — a follow-up here,
  not in this PR. Until the SD twin ships, an SD checkout has no snapshot and
  uses the retained **AST fallback** (`_parse_registry`), so its review output
  is byte-identical to today (no regression).
- **AST-fallback removal** is a bounded follow-up (after SD ships its producer),
  not this PR. That later PR meets the strict "no longer opens registry.py" end
  state fleet-wide.
- No change to review output schema (`SCHEMA_VERSION` stays 3): behavior parity
  is an acceptance criterion, verified by `snapshotId`-stability tests. Because
  the fallback is retained, every existing AST-fixture test keeps passing
  unchanged — parity for both packs is preserved by construction.
- Not removing the other hard-coded layout assumptions beyond the registry read
  (`FIRST_PARTY_REMOTES`, discovery globs, adapter paths) — the PRD scopes this
  to "where the snapshot can carry them", and those layout facts are not
  registry data. Called out as a follow-up.

## Affected Files

Canonical / source:
- `.github/scripts/generate-skill-surfaces.py` — add snapshot producer + wire
  into regenerate/`--check`/write/orphan flow.
- `templates/skills/se-review-skills/scripts/skill_review.py` — ADD
  `_load_registry_snapshot`; add the supported-version set; repoint the call
  site to prefer the snapshot and fall back to `_parse_registry`. **Retain**
  `_parse_registry` and its AST helpers as the legacy fallback (do not delete).

Generated / payload (via `make generate`, never hand-edited):
- `generated/registry-snapshot.json` — new.
- Any regenerated overlay if the generator's own output text shifts (expected
  none beyond the new file).

Release metadata:
- `manifest.json` — `version` 0.66.2 → 0.66.3.
- `CHANGELOG.md` — new `## 0.66.3 - <date>` heading.

Tests / docs / spec:
- `tests/test_skill_review.py` — keep the existing AST fixtures (fallback covers
  them); ADD snapshot-consumption + version-not-in-set (both directions) +
  malformed + symlink→fallback + absent→fallback tests, plus a `snapshotId`
  parity assertion.
- `tests/test_generate.py` — sandbox the snapshot output path and add
  snapshot drift/`--check` + write-rollback coverage (C-2).
- `.trellis/spec/backend/quality-guidelines.md` — update `SHARED_REFERENCES`
  source (:669) and generated-surfaces/release notes (:153, :157) (C-3).
- `docs/SE_AI_COMMAND_PACK.md` — document the generated snapshot surface if the
  generated-surfaces catalog enumerates surfaces (verify during implementation).

## Data And Command Contracts

- Producer: `python .github/scripts/generate-skill-surfaces.py` writes the file;
  `--check` regenerates to memory and byte-compares committed vs regenerated,
  failing with the standard "run make generate and commit the result" on drift.
  (Single-file: detects drift and a missing expected file; orphan-after-producer-
  removal is out of scope per Risks C-7.)
- Consumer: `_load_registry_snapshot(package_root / "generated" / "registry-snapshot.json")`
  → `RegistryData` on a valid snapshot, `None` on absent/symlink (caller then
  uses the `_parse_registry` AST fallback), `ReviewError` on version-incompat /
  malformed / wrong-type.
- Canonicalization for the snapshot file uses the generator's existing JSON
  serialization convention (2-space indent + trailing newline, matching
  `manifest.json` formatting) so drift compares stably.

## Risks And Edge Cases

1. **Parity drift**: snapshot-derived `RegistryData` must be byte-identical to
   the old AST-derived one, or `snapshotId` changes and "output unchanged" fails.
   Prevention: preserve exact field ordering + platform sort; a test asserts
   `snapshotId` for a fixed registry is unchanged from the pre-change value.
2. **Missing-snapshot behavior**: absent → AST fallback preserves parity, but a
   *migrated* SE checkout that somehow lost its generated file would silently
   review via the fallback. Mitigation: the generated file ships in
   the payload and is drift-gated; its absence in an SE checkout is an install
   defect, not an expected state. Reviewer note flags this seam.
3. **Version gate** (C-5): supported is an explicit `frozenset({1})`; the loader
   first requires `type(schemaVersion) is int` (so `True`/`1.0`, which are `== 1`,
   fail closed — the `installer/manifest.py:59` trap), then requires set
   membership. Any version not in the set fails closed (undefined `0`, missing,
   newer `2`). Adding a future version is a deliberate set edit, not an implicit
   `>=`/`>`. Tests cover under-version `0`, over-version `2`, and wrong-type
   `True`/`1.0`.
4. **Symlinked snapshot** (C-6): the snapshot path is checked with
   `is_symlink()` before reading and treated as absent (→ AST fallback), never
   followed — same trust-boundary stance as `_parse_registry` line 245.
5. **Orphan/stale file** (C-7): a single-file `--check` detects drift and a
   missing expected file only while the producer still expects the path; it
   cannot, by itself, flag the committed file as orphaned if the producer is
   later deleted (unlike the existing whole-subtree walks at
   generate-skill-surfaces.py:466/760). That is acceptable — deleting the
   producer is itself a reviewed change that must delete the file — and is not
   overclaimed here. A persistent root-level generated-file allowlist is a
   possible future hardening, out of scope.
6. **Spec drift** (C-3): the active `quality-guidelines.md` mandates AST parsing
   of `SHARED_REFERENCES` (:669) and states "three atomic generated surfaces"
   with "family-only metadata … no release bump" (:153, :157). This change adds
   a fourth generated surface and a snapshot source for that data, so the spec
   is updated in the same PR (see implement.md).

## Validation

- `python .github/scripts/generate-skill-surfaces.py` then `--check` → clean
  (no drift) after committing the generated file.
- `make release-check` → generate `--check` + release-payload gate green
  (version bump + CHANGELOG present).
- `python -m pytest tests/test_skill_review.py tests/test_generate.py` (or the
  repo's runner) → all existing tests pass unchanged (fallback preserves
  parity), plus new tests:
  - snapshot consumption produces the same inventory/order as the AST path;
  - `snapshotId` for a fixed registry unchanged (parity);
  - `schemaVersion` not in supported set (both `0` and `2`) → `ReviewError`;
  - malformed/missing-key snapshot → `ReviewError`;
  - symlinked snapshot → AST fallback (no follow);
  - absent snapshot → AST fallback (no raise);
  - generator: snapshot drift fails `--check`; snapshot write rolls back.
- `make check` (test + lint + release-check) green.
- Grep proof for acceptance: `skill_review.py` prefers
  `generated/registry-snapshot.json` and opens `installer/registry.py` only in
  the retained fallback branch.
