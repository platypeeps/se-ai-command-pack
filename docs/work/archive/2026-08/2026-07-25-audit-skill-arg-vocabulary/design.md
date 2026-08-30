# Design — Pack-wide skill argument vocabulary (A-006)

## Status

Implementation-ready. Reached after two full two-lane adversarial review rounds
(host + Codex) surfaced 14 verified concerns and three irreducible taxonomy
decisions (D-1/D-2/D-3), which the operator resolved. Those decisions are
recorded as authoritative below and in the review-outcome section.

## Scope decision

Inventory of the **53** canonical `templates/skills/*/SKILL.md` argument sections
(the `_shared` dir is not a skill), hardened by adversarial review, settles the
covered axes:

| Axis / name | Verdict | Action |
| --- | --- | --- |
| Verbosity (`length=`/`detail=`/`depth=`, plus density-only `format=` values) | **Drift** | Canonical `depth=`; enforce name + ladder membership |
| Primary artifact under action (`input=`/`source=`/`inputs=`) | **Drift** | Canonical `input=` |
| Redaction level (`sensitivity=`, plus se-red-team's stray `detail=`) | **Drift** | Canonical `sensitivity=`; enforce name + ladder membership |
| Reference material to consult (`sources=`) | Already consistent (21 skills) | Reserve name; no rename |
| `privacy=` (distribution/audience ceiling) | Distinct concept, 1 skill | Reserve name only |
| `evidence=` (authorized supporting material) | Distinct from `sources=` | Reserve name only |
| `coverage=` (editorial coverage), `format=` shapes, `mode=`, `scope=`, `audience=`, owned names | Per-skill | Reserve name to concept; no value enforcement |

## Canonical vocabulary — three covered axes

### 1. Verbosity → `depth=`

- **Name:** `depth=`. **Ladder:** `brief|standard|deep`. Enforcement checks that
  declared values are a **subset** of the ladder set (not declaration order —
  skills legitimately list values default-first). Each skill defaults explicitly.
- Migrates onto `depth=`: every `length=`; every verbosity-sense `detail=`; and
  `format=` declarations whose values are a *pure density ladder*
  (`compact|standard`, `standard|compact`) — classified in the format child.
  Structural `format=` shapes (`ledger|memo`, `full|quick-reference`, …) stay.
- Value map: `short`/`compact`/`quick`/`outline`→`brief`; `long`/`full`→`deep`;
  `standard` unchanged. `brief|full`→`brief|deep` (subset, no invented middle).
- **`depth=` name collision:** `se-technical-editor depth=full|focused` is
  editorial **coverage** (`focused` requires `passes=`, `se-technical-editor:42`)
  → rename `coverage=full|focused` first. `se-author length=` also takes an exact
  word count (`se-author:45`) — the enforced `depth=` ladder has no numeric slot,
  so preserve the count via a separate `target_words=` argument (not a numeric
  `depth=<n>`, which the ladder rule would reject); the tier form migrates to
  `depth=`.

### 2. Primary artifact under action → `input=`

The evidence (D-1): se-capture "normalize one logical intake unit"
(`se-capture:8`), se-digest "material already exists, job is synthesis"
(`se-digest:8`), se-presentation/se-publish "turn an approved source artifact
into …" (`:8`) all *transform a supplied primary artifact*. That is the same
concept as se-fact-check/se-feedback/se-technical-editor `input=` — the thing
being acted on — not reference material.

- **Name:** `input=` — the primary artifact/subject under action.
- Migrates onto `input=`: `se-capture source=`, `se-presentation source=`,
  `se-publish source=`, `se-digest inputs=`.
- `sources=` (21 skills) is a *separate, already-consistent* axis — a list of
  reference material to consult. No rename; name reserved.
- **Count collision:** `se-research sources=N` (a numeric minimum,
  `se-research:37`) → `min_sources=N`; update its downstream prose.

### 3. Redaction level → `sensitivity=`

The disclosure family is three distinct concepts (D-2), kept separate:

- **`sensitivity=` — content redaction level.** Ladder `minimal|restricted|
  standard` (enforced as set membership). 5 skills already use it
  (`standard|restricted` subset). `se-red-team detail=minimal|restricted|
  standard` (`se-red-team:40`) is this concept mislabeled → rename
  `sensitivity=` (values already in-ladder; also ends se-red-team's
  `detail=`/`depth=` double-use — its `depth=` verbosity stays).
- **`privacy=` — distribution / audience ceiling.** `se-weekly-review
  privacy=private-only|internal|outward-safe` (`:52`). Different concept
  (who may receive), distinct value set; 1 skill, no drift. Name reserved,
  values not enforced.
- **`evidence=` — authorized supporting material** (~8 skills). A claim-support
  list, distinct from general reference `sources=`. Name reserved, not enforced.

## Reserved-name registry & enforcement

Two tiers:

- **Name + ladder-membership enforced:** `depth=`, `sensitivity=`.
- **Name-only reserved (values per-skill):** `input=`, `sources=`,
  `min_sources=`, `coverage=`, `target_words=`, `privacy=`, `evidence=`,
  `format=`, `mode=`, `scope=`, `audience=`, owned names.

Enforcement scope, corrected by review:

- Chokepoint `validate_skill()` in
  `.github/scripts/generate-skill-surfaces.py:208`; errors propagate to nonzero
  `.venv/bin/python .github/scripts/generate-skill-surfaces.py --check` /
  `make release-check` / `make check`. **Not** `make generate --check` — Make
  eats `--check` and runs write-mode (verified).
- Parse **every** inline-code `` `key=values` `` span per Arguments bullet (some
  bullets declare two args, `se-ask-me:46`).
- Checks: a verbosity/primary-artifact/redaction axis under a **known
  non-canonical alias** is rejected; `depth=`/`sensitivity=` values must be a
  subset of their ladder. Enforcement **cannot** infer a covered concept under
  an arbitrary *future* name from `key=values` alone — the guarantee is "no
  regression under a known covered-axis alias or off-ladder value," not "no
  drift under any conceivable name." The parent acceptance claim is narrowed
  accordingly.
- Tests, two places: **negative validator fixtures** in `tests/test_generate.py`
  (`write_skill()`/`assert_validation_error()`) prove `validate_skill()` rejects
  malformed skills; a **live-corpus conformance** case beside
  `tests/test_skills.py:145` proves the real skills conform. One canonical
  constant, imported by both — never duplicated.

## Shared reference delivery

`test_shared_reference_consumers_cite_registered_reference`
(`tests/test_skills.py:390`) requires every `SHARED_REFERENCES` consumer's body
to cite the doc. So delivery is **not** body-neutral: if the vocabulary ships as
a `_shared/references/` doc fanned to consumers, those bodies gain a one-line
citation (a `templates/**` change). The reference child owns that citation edit;
"no argument-name change" is the accurate no-change claim, not "no body edit."

## Release payload / versioning

`make release-check` → `check-release-payload.py` requires a `manifest.json`
version bump + matching top `CHANGELOG.md` heading for any `templates/**`,
`generated/**`, or `installer/**` change (`check-release-payload.py:6,172`).
Every child that touches those paths ships its own bump + changelog entry citing
A-006 — the pack's normal per-PR hygiene. Independent-child-PR model preserved.

## Migration split (D-3)

Verbosity alone is ~29 mechanical renames — kept as one low-risk mechanical
child (fully gated by `make check` + the new enforcement); the ~4 judgment
`format=` density-vs-shape calls are isolated in a separate small child. Five
ordered children (see `implement.md`): reference → verbosity-mechanical →
format-density → primary/discrete-renames → enforce-last, so `make check` never
fails mid-migration.

## Compatibility, rollback, risk

- Consumer-visible breaking renames, each in `CHANGELOG.md` (`## <semver> -
  <date>` citing A-006). No deprecation aliases (no external name-stability
  contract; an alias table would itself become drift).
- Each child reverts independently; enforcement (last) reverts alone to disable
  the guard without reverting renames.
- Behavior-change risks (not just names): value renames, 2-tier↔ladder shifts,
  `se-author` numeric length, `format=` density-vs-shape — each a per-declaration
  decision in its owning child, never a silent sweep.

## Two-lane adversarial review outcome (host + Codex, 2 rounds)

Round 1: 7 defects; reshaped 2→3 axes. Round 2: 7 more (5 P1). Mechanical fixes
folded in: set-membership (not order) enforcement (R2-#1); narrowed enforcement
guarantee (R2-#4); shared-ref citation reality (R2-#5); single true `depth=`
collision (R2-#7); 53-skill count. Three irreducible product decisions escalated
and **operator-resolved**:

- **D-1 → `input=` for primary artifact, `sources=` for reference.** Rename
  `source=`/`inputs=`→`input=` (se-capture/presentation/publish/digest);
  `sources=` unchanged; `sources=N`→`min_sources=`.
- **D-2 → three separate disclosure concepts.** `sensitivity=` (redaction,
  enforced; +se-red-team), `privacy=` (distribution, name-only), `evidence=`
  (support, name-only).
- **D-3 → mechanical verbosity child + separate format-density child.**

## Remaining open items (child-level, non-blocking)

1. `se-author` exact-count captured by `target_words=` (the `depth=` ladder is
   value-enforced, so a numeric `depth=<n>` is not an option).
2. `format=` density-vs-shape split for borderline `full|compact` (se-sop),
   `full|quick-reference` (se-runbook) — default "keep as shape unless the value
   pair is a pure density ladder."
