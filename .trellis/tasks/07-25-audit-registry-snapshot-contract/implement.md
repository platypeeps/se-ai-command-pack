# Versioned registry snapshot for skill_review — Implementation Plan

## Execution Order

1. **Producer first (generator).** In `.github/scripts/generate-skill-surfaces.py`:
   - Add `regenerated_registry_snapshot_text()` that reads the already-imported
     `FAMILY_LABELS`, `SKILLS`, `PLATFORM_REGISTRY`, `SHARED_REFERENCES` and
     serializes the schema from `design.md` (`schemaVersion: 1`) from the real
     objects (authoritative — more reliable than AST). Ordering: `skills` in
     `SKILLS` order, `familyOrder` in `FAMILY_LABELS` order, `platforms`
     `sorted()` (matches `_parse_registry` line 312), `sharedReferences` in
     `SHARED_REFERENCES` key order. Reuse the generator's `manifest.json` JSON
     dump convention (2-space indent, trailing newline).
   - In `main`: register `generated/registry-snapshot.json` as an atomic surface
     in BOTH the write branch and the `--check` diff branch, using the existing
     regenerate-to-memory → byte-compare → drift-error pattern and the atomic
     validate-all-before-write / roll-back-on-failure contract
     (quality-guidelines.md:153). Add a single-file present/drift guard.
2. **Bump release metadata BEFORE generating (C-4).** The help-catalog embeds
   the manifest version and `release-check` only runs `--check`, so bump first:
   - `manifest.json` `version` 0.66.2 → 0.66.3.
   - `CHANGELOG.md`: add `## 0.66.3 - <today>` describing the new generated
     registry snapshot + the snapshot-preferred skill_review consumer.
3. **Generate the artifacts.** Run `python .github/scripts/generate-skill-surfaces.py`
   → writes `generated/registry-snapshot.json` and refreshes any surface that
   embeds the new version. Confirm `--check` is then clean.
4. **Consumer — snapshot-preferred + fallback (C-1).** In
   `templates/skills/se-review-skills/scripts/skill_review.py`:
   - Add `SUPPORTED_REGISTRY_SNAPSHOT_SCHEMA_VERSIONS = frozenset({1})`.
   - Add `_load_registry_snapshot(path) -> RegistryData | None` implementing the
     design state table: absent/symlink → `None`; `schemaVersion` wrong type
     (require `type(v) is int` first — `True`/`1.0` must fail, per manifest.py:59)
     or int-not-in-`frozenset({1})` → `ReviewError`; malformed/missing-key/bad
     field type → `ReviewError`; valid → `RegistryData` (exact ordering: skills
     order → `families`+`skill_order`; `familyOrder`; `platforms` as given;
     `sharedReferences` → tuples).
   - At `_package_context` (line ~326): prefer the snapshot, else fall back to
     `_parse_registry(package_root / "installer" / "registry.py")`.
   - **Retain** `_parse_registry` + `_assignment` / `_string_value` /
     `_call_value` as the legacy fallback (do NOT delete). Keep `import ast`.
   - `skill_review.py` scripts are not mirrored into `generated/skills/claude/`
     (only `SKILL.md` bodies are), so this edit produces no overlay drift.
5. **Update the code-spec (C-3).** In `.trellis/spec/backend/quality-guidelines.md`
   reconcile EVERY place the old contract is asserted (search, don't assume 3
   lines):
   - `SHARED_REFERENCES` line (:669) → derive from the versioned JSON snapshot
     when present, else parse statically from the registry AST — in both cases
     without importing or executing reviewed repository code.
   - Generated-surfaces enumeration (:153) → include the registry snapshot as a
     fourth atomic surface; reconcile the "family-only metadata … no release
     bump" note (:157).
   - Validation & Error matrix row (:170, "Family metadata changes but payload
     does not / release gate passes without a bump") → note that registry
     family/order changes now alter the `generated/**` snapshot and therefore
     ARE release-gated (`check-release-payload.py:27`).
   - Tests-Required "version identity"/required-checks language (~:187) → include
     the snapshot surface in generator drift + rollback + patched-output checks.
6. **Tests.** Parity is preserved by the fallback, so existing AST fixtures stay
   (they write `registry.py`, no snapshot → fallback → identical output). ADD:
   - `tests/test_skill_review.py`: snapshot-present consumption yields the same
     inventory/order as the AST path for the same registry; `snapshotId`
     unchanged (parity proof); version int not-in-set (both `0`/`2`) →
     `ReviewError`; version wrong-type (`True`, `1.0`) → `ReviewError`;
     malformed/missing-key → `ReviewError`; symlinked snapshot → AST fallback;
     absent snapshot → AST fallback (no raise). Reuse `write_se_pack` /
     `write_sd_pack` and add a snapshot-writing helper.
   - `tests/test_generate.py`: the new snapshot path must be sandboxed like the
     other outputs (test_generate.py:503 patches output locations away from the
     real checkout) so `gen.main()` never touches the real
     `generated/registry-snapshot.json`. Add snapshot drift/`--check` coverage
     and write-rollback coverage mirroring test_generate.py:905/944.

## Validation Plan

- Focused: `python .github/scripts/generate-skill-surfaces.py --check` clean
  after commit; repo pytest runner on `tests/test_skill_review.py` and
  `tests/test_generate.py` (existing + new all pass).
- Broad: `make check` (test + lint + release-check). `make release-check` proves
  the drift gate + release-payload gate (version bump + CHANGELOG) green.
- Acceptance greps: snapshot is preferred (call site reads
  `generated/registry-snapshot.json`); `registry.py` is opened only in the
  retained fallback; `SUPPORTED_REGISTRY_SNAPSHOT_SCHEMA_VERSIONS` present.
- `node scripts/sd-ai-command-pack-review-preflight.mjs` before publishing.

## Documentation And Spec Updates

- `CHANGELOG.md` + `manifest.json` version (step 2).
- `.trellis/spec/backend/quality-guidelines.md` (step 5, C-3).
- If `docs/SE_AI_COMMAND_PACK.md` enumerates generated surfaces, add the
  snapshot row (verify during implementation; skip if no such catalog).

## Review Notes

- Reviewer-sensitive: the **snapshot-preferred + AST fallback** contract. State
  in the PR body that a present-but-broken snapshot fails closed (never silently
  falls through), absent/symlink falls back to preserve both-pack parity, and
  the strict "no longer opens registry.py" end state is a tracked follow-up.
- PR body must carry the **Tooling/generated scope** section: `generated/**` +
  `manifest.json` + `CHANGELOG.md` changed → release-payload gate applies.
- Parity crux: the `snapshotId`-unchanged test and the untouched existing AST
  fixtures are the parity proof.

## Rollback Points

- Producer (steps 1-3), consumer (step 4), and spec (step 5) are separable
  commits. A consumer regression reverts step 4 alone; the shipped snapshot is
  inert (fallback still governs) until consumed.
- Full revert restores AST-only parsing with no data migration (`registry.py`
  remains the source of truth; the snapshot is derived).

## Follow-Ups (outside this PR)

1. **SD pack twin**: mirror the producer in sd-ai-command-pack so SD checkouts
   ship the same-schema snapshot. File/track as an sd-ai-command-pack task.
2. **AST-fallback removal**: once both packs ship producers, a bounded PR
   removes `_parse_registry` + helpers and the fallback branch, meeting the
   strict "`skill_review.py` no longer opens `installer/registry.py`" criterion
   fleet-wide. File as a follow-up task in this repo.
3. **Remaining layout assumptions**: `FIRST_PARTY_REMOTES`, discovery globs, and
   adapter paths are not registry data; a later task can decide whether any
   belong in the snapshot.
