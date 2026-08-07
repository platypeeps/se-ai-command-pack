# SD pack twin: registry snapshot producer parity

## Goal

Make the `sd-ai-command-pack` repository ship a `generated/registry-snapshot.json`
with the same schema the SE pack already ships, so `skill_review.py` resolves a
snapshot in an SD checkout instead of falling back to AST-parsing
`installer/registry.py`.

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

- [ ] Explicit approval for a pull request against `sd-ai-command-pack` is
      obtained and recorded before any change is proposed there.
- [ ] `sd-ai-command-pack` ships `generated/registry-snapshot.json` at
      `schemaVersion` 1 with all five keys, produced by its surface generator.
- [ ] In an SD checkout, `skill_review.py` resolves the snapshot and does not
      call `_parse_registry`. Demonstrated by evidence from a run, not by
      reading the code.
- [ ] The snapshot-derived registry and the `_parse_registry`-derived registry
      agree on the same SD checkout — same family order, skill order, sorted
      platforms, and shared references.
- [ ] The generator's `--check` mode fails on an induced drift between
      `installer/registry.py` and the committed snapshot.
- [ ] Re-running the generator on an unchanged registry produces byte-identical
      output.
- [ ] The SD pack's release gate treats the snapshot as shipped payload: a
      change to it fails the gate without a version bump and a dated CHANGELOG
      heading. Demonstrated by an induced change, not by reading the gate.
- [ ] Only `.trellis/` task artifacts change in this repository. Any other
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
- Planning depth: PRD-only here, since no shipped file in this repository changes. If the SD generator's shape differs materially from this pack's, the `design.md` and `implement.md` belong to that repository's task, not this one.
