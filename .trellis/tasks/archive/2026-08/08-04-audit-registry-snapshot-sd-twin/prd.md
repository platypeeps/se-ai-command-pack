# SD pack twin: registry snapshot producer parity

## Goal

Make the `sd-ai-command-pack` repository ship a `generated/registry-snapshot.json`
with the same schema the SE pack already ships, so `skill_review.py` resolves a
snapshot in an SD checkout instead of falling back to AST-parsing
`installer/registry.py`.

## Route: upstream pull request (approved)

Explicit per-PR approval was granted 2026-08-16 for **one** pull request against
`platypeeps/sd-ai-command-pack`. Per-PR only; it creates no standing authority
and does not extend to a second PR. The autonomous run-level authority excludes
upstream PRs, and this section records the approval rather than presuming it.

That approval is now **spent**: `platypeeps/sd-ai-command-pack#483` was opened,
reviewed and squash-merged as `232138a8` on 2026-08-16. Any further upstream pull
request needs its own explicit approval.

Work happens in an isolated `git worktree`. The shared clone at
`~/repos/platypeeps/sd-ai-command-pack` is in use by other sessions and must not
be checked out, reset, or branched.

## Problem

`skill_review.py` prefers the snapshot and falls back only when there is none
(`templates/skills/se-review-skills/scripts/skill_review.py:421-428`):

```python
registry = _load_registry_snapshot(
    package_root / "generated" / "registry-snapshot.json"
)
if registry is None:
    registry = _parse_registry(package_root / "installer" / "registry.py")
```

The comment marks the fallback as transitional, "until every pack ships a
snapshot". Today only this pack does. `se-review-skills` is installed into SD
checkouts too, so in an SD checkout the fallback is not a fallback — it is the
only path, every run.

That leaves the AST parser load-bearing fleet-wide, which is what blocks
`08-04-audit-registry-snapshot-ast-removal`.

## Constraint: this is a different repository

`sd-ai-command-pack` is a separate repository
(`github.com/platypeeps/sd-ai-command-pack`, per `FIRST_PARTY_REMOTES` at
`skill_review.py:39-42`), checked out locally as a sibling at
`../sd-ai-command-pack`. The work lands there, not here. A pull request against
another repository is outside the autonomous run-level authority and needs
explicit approval for that PR.

No shipped file in this repository changes — no source, no template, no
generated payload. This task's deliverable here is the specification and the
verification that the SD-side result actually satisfies the consumer, both of
which are recorded in this task's own `.trellis/` artifacts; the producer change
itself is external work.

Because the external pull request cannot be opened under this repository's
autonomous authority, `task.json` carries `blocked: true` and a `blockedOn`
naming that approval, so a ranking helper skips the task instead of selecting it
and stalling at the first acceptance criterion.

## Target schema

The consumer's validator (`_registry_from_snapshot`, `skill_review.py:248-309`)
is the contract. Required top-level keys:

| Key | Type | Consumer requirement |
| --- | --- | --- |
| `schemaVersion` | `int` | Exactly `1`. `type(version) is not int` rejects `bool` and `1.0` (`:329-337`). |
| `familyOrder` | list of strings | Family ordering. |
| `skills` | list of `{name, family}` objects | Skill ordering and family assignment. |
| `platforms` | list of strings | Validated as a list of strings, then re-sorted by the consumer. |
| `sharedReferences` | object mapping string to list of strings | Each value becomes a tuple. |

Two consumer behaviours matter for the producer:

- **Sorting is defensive, not forgiving of drift.** The consumer applies
  `tuple(sorted(platforms))` and says why: "Sort to mirror `_parse_registry`'s
  `tuple(sorted(platforms))` exactly ... even if a producer emits unsorted
  platforms" (`:301-307`). An unsorted producer still *works* — but its
  committed bytes would be unstable across runs, and the drift check compares
  bytes. Emitting sorted output is a producer-determinism requirement, not a
  consumer-correctness one.
- **A broken snapshot fails closed; an absent one falls back.** Any malformed,
  mistyped, or unsupported-version snapshot raises `ReviewError` rather than
  falling back (`:311-338`, and `quality-guidelines.md:295`). Shipping a wrong
  snapshot is therefore strictly worse than shipping none: it turns a working
  SD checkout into a hard failure.

## Requirements

- The SD pack's surface generator produces `generated/registry-snapshot.json`
  from its own `installer/registry.py`, matching the schema table above at
  `schemaVersion` 1. Do not introduce an SD-specific variant of the schema.
- The producer is the sole writer of the snapshot, and its `--check` mode fails
  when the committed snapshot drifts from `installer/registry.py` — the same
  contract this pack documents at `quality-guidelines.md:294` and `:844-845`.
- Emit deterministic bytes: sorted `platforms`, and a stable ordering for every
  other collection, so re-running the generator on an unchanged registry
  produces an identical file.
- Treat the snapshot as shipped payload in the SD pack's release gate, matching
  `quality-guidelines.md:296` — a change to it requires a version bump and a
  dated CHANGELOG heading.
- Verify against the real consumer, not against the schema description. Run
  `skill_review.py` in an SD checkout and confirm the snapshot is consumed. A
  snapshot that parses but disagrees with `_parse_registry` is the failure this
  task exists to prevent, so the two must be compared directly on the same
  checkout.
- Do not modify `skill_review.py`, `_load_registry_snapshot`, the fallback
  branch, or `SUPPORTED_REGISTRY_SNAPSHOT_SCHEMA_VERSIONS` as part of this task.
  Removing the fallback is `08-04-audit-registry-snapshot-ast-removal`.

## Acceptance Criteria

- [x] Explicit approval for a pull request against `sd-ai-command-pack` is
      obtained and recorded before any change is proposed there. Granted
      2026-08-16, recorded under "Route" above, before any SD change was
      written.
- [x] `sd-ai-command-pack` ships `generated/registry-snapshot.json` at
      `schemaVersion` 1 with all five keys, produced by its surface generator.
- [x] In an SD checkout, `skill_review.py` resolves the snapshot and does not
      call `_parse_registry`. Demonstrated by evidence from a run, not by
      reading the code.
- [x] On the same SD checkout, the snapshot-derived registry and the
      `_parse_registry`-derived registry agree **exactly** on the three fields
      the AST can derive: `families`, `skill_order`, and `platforms`.
- [x] `family_order` and `shared_references` — which the AST cannot derive for
      SD, because it reads `FAMILY_LABELS`/`SHARED_REFERENCES` while SD names
      them `COMMAND_FAMILIES`/`SHARED_SKILL_REFERENCES` — are asserted against
      the **imported registry objects**: `family_order` equals
      `[f.id for f in COMMAND_FAMILIES]` (5 entries) and `shared_references`
      equals `SHARED_SKILL_REFERENCES` (4 entries). Asserting these against the
      AST instead would accept empty and silently discard real data.
- [x] The generator's `--check` mode fails on an induced drift between
      `installer/registry.py` and the committed snapshot.
- [x] Re-running the generator on an unchanged registry produces byte-identical
      output.
- [x] The SD pack's release gate treats the snapshot as shipped payload: a
      change to it fails the gate without a version bump and a dated CHANGELOG
      heading. Demonstrated by an induced change, not by reading the gate.
- [x] Only `.trellis/` task artifacts change in this repository. Any other
      changed file here means the task exceeded its stated boundary and must be
      listed with its reason before completion.

## Out of scope

- Removing the AST fallback from `skill_review.py`. That is
  `08-04-audit-registry-snapshot-ast-removal`, which this task unblocks.
- Extending the snapshot schema beyond `schemaVersion` 1. That is
  `08-04-audit-registry-snapshot-layout-assumptions`.
- Any change to `installer/registry.py` content in either pack. This task
  serializes the registry; it does not edit it.
- Third-party or `repo-local` packs, which ship no snapshot and are not
  addressed by pack parity.

## Notes

- Direct precondition for `08-04-audit-registry-snapshot-ast-removal`, which
  carries `blocked: true` / `blockedOn` naming this task.
- Cross-repository: the deliverable lands in `../sd-ai-command-pack`, so
  completion depends on an approval this repository cannot grant itself.
- Consumer contract verified against `skill_review.py` at `se-ai-command-pack`
  0.67.1.
- Planning depth: PRD-only here, since no shipped file in this repository changes. The SD generator's shape *does* differ materially (see the verification below), which by the original note would push `design.md` and `implement.md` into that repository's task. They are kept here instead, following the `08-10-review-scope-late-arrival` precedent from 2026-08-16: that relay planned in this repository and shipped the fix upstream without creating an upstream Trellis task, and its `disposition.md` is the accepted record shape. Deviation recorded rather than silent.

## Verification of this PRD's premise, 2026-08-16

The PRD was written against `se-ai-command-pack` 0.67.1; the repository is now
at 0.71.23. Every load-bearing claim was re-checked before starting, because the
premise is the kind that quietly expires.

**The premise holds.** Measured by importing `skill_review.py` and calling
`_parse_registry` directly on both checkouts:

| | families | familyOrder | skills | platforms | sharedReferences |
| --- | --- | --- | --- | --- | --- |
| SE via AST | 54 | 6 | 54 | 3 | — |
| **SD via AST** | **20** | **0** | **20** | **18** | **0** |

So `_parse_registry` is genuinely load-bearing on SD — it supplies 20 family
assignments, 20 skill orderings and 18 platforms. An earlier guess that the
fallback might be near-empty on SD, and therefore replaceable with an empty
`RegistryData`, was **wrong and was discarded on this measurement**. There is no
shortcut around shipping the snapshot.

Confirmed alongside it:

- `SUPPORTED_REGISTRY_SNAPSHOT_SCHEMA_VERSIONS = frozenset({1})` — unchanged.
- The fallback at `skill_review.py:425-429` is intact, still comment-marked
  transitional.
- `FIRST_PARTY_REMOTES` still lists `sd-ai-command-pack`, and
  `package_root = git_root`, so running the reviewer inside an SD checkout does
  resolve SD's own `installer/registry.py`.
- `skill_review.py inventory --root <SD> --scope package` returns
  `status: success` with `selectedSkills: 20` today, so this is a live path, not
  a hypothetical one.
- SD ships **zero** tracked `registry-snapshot.json`.

## What SD's registry actually contains

SD is a command pack, and its shape differs from SE's in ways that decide the
producer:

- `_parse_registry` reads skills from `SKILLS`/`SkillInfo` **or**
  `COMMAND_REGISTRY`/`CommandInfo` (`skill_review.py:359-361`). SD has only the
  latter: `CommandInfo(name, short, family, ...)`, with `family` at positional
  index 2 — which is exactly the `family_position` the parser expects. 20
  entries.
- The AST derives `family_order = ()` and `shared_references = {}` for SD. **Not
  because SD lacks them.** The parser reads `FAMILY_LABELS` and
  `SHARED_REFERENCES`; SD names the same concepts `COMMAND_FAMILIES` (5
  `CommandFamily(id, label, summary)` entries, ids exactly the 5 families its 20
  commands use) and `SHARED_SKILL_REFERENCES` (4 entries, same
  `dict[str, tuple[str, ...]]` shape as SE's). The parser simply cannot see
  them.

This corrects an earlier draft of this section, which read those empties as real
absences and concluded the snapshot must ship `"familyOrder": []` and
`"sharedReferences": {}` for strict parity with the AST. That would have
encoded a parser blind spot into the file that becomes the *only* registry
source once `08-04-audit-registry-snapshot-ast-removal` deletes the AST path —
discarding real data permanently to satisfy a transitional comparison. It would
also have made SD inconsistent with SE, whose snapshot ships the real
`list(FAMILY_LABELS.keys())`.

**The snapshot ships the real values.** Acceptance criterion 4 is corrected
accordingly below: strict AST agreement is required on the three fields the AST
can derive, and the two blind fields are asserted against the imported registry
objects instead. That is stricter than the original criterion, not weaker —
strict parity would have accepted empty for both.
