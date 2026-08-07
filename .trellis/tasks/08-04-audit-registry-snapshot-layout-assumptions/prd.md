# Evaluate remaining skill_review layout assumptions for snapshot inclusion

## Goal

Decide, with evidence, which of `skill_review.py`'s remaining hardcoded or
layout-derived values are registry data that belong in the versioned snapshot,
and which are correctly layout-derived — then act only where the evidence
supports it.

The default outcome is **no schema change**. This task is a read-only
assessment that is allowed to conclude "leave everything as it is", and that
conclusion is a success, not a failure to deliver.

## Problem

The registry snapshot was introduced to remove one coupling: `skill_review.py`
learning family order, skill order, platforms, and shared references by parsing
another repository's `installer/registry.py`. The snapshot is preferred where it
exists, but the AST fallback is still live at `skill_review.py:421-428` and
still the only path in an SD checkout — removing it is
`08-04-audit-registry-snapshot-ast-removal`, gated on
`08-04-audit-registry-snapshot-sd-twin`. Several values were left behind by the
snapshot regardless, and still come from the tool's own constants or from
directory layout. Those are what this task assesses.

### Candidate 1 — `FIRST_PARTY_REMOTES` (`:39-42`)

```python
FIRST_PARTY_REMOTES = {
    "se-ai-command-pack": "github.com/platypeeps/se-ai-command-pack",
    "sd-ai-command-pack": "github.com/platypeeps/sd-ai-command-pack",
}
```

Hardcoded in the consumer, used at `:433` to classify `owner_kind` and again at
`:703`. Note the self-reference problem: this maps a pack *name* to the remote
that pack is expected to live at. A snapshot shipped **by** a pack cannot
authoritatively assert which remote is first-party — a fork would ship a
snapshot claiming its own remote. Whether that makes it unsuitable for the
snapshot, or merely requires the consumer to keep the check, is precisely what
this task must decide rather than assume.

### Candidate 2 — adapter paths (`:442-446`)

```python
allowed: Path | None = None
if name == "se-ai-command-pack":
    allowed = package_root / "templates" / "skills"
elif name == "sd-ai-command-pack":
    allowed = package_root / "templates"
```

A per-pack layout fact, branching on pack name inside the consumer. This is the
strongest candidate: it is genuinely per-pack data, it is knowable by the pack
that ships the snapshot, and the current form means adding a third pack
requires editing the consumer.

### Candidate 3 — discovery globs and `IGNORED_DIRECTORIES` (`:43+`)

Tool policy about what to scan and skip, not facts about a pack's registry.
Weakest candidate; likely correctly layout-derived and tool-owned.

## The cost side of the ledger

A schema change is not cheap, and the assessment must price it:

- **Two producers must ship it.** `se-ai-command-pack` generates its own
  snapshot today; `sd-ai-command-pack` does not yet, which is exactly what
  `08-04-audit-registry-snapshot-sd-twin` exists to fix. So a `schemaVersion` 2
  would have to be adopted by a producer that does not yet ship version 1.
  `sd-ai-command-pack` is a separate repository, so any bump needs a
  coordinated,
  approval-gated change there as well as here.
- **The consumer must accept both versions during rollout.**
  `SUPPORTED_REGISTRY_SNAPSHOT_SCHEMA_VERSIONS` is currently
  `frozenset({1})` (`:31`), and an unsupported version raises `ReviewError`
  rather than degrading (`:329-337`). A version bump without a coordinated
  rollout hard-fails every checkout still shipping the old snapshot.
- **The snapshot is shipped payload.** Per `quality-guidelines.md:296`, any
  change to it requires a version bump and a dated CHANGELOG heading in both
  packs.

So the bar is: does moving a value into the snapshot remove a *real* coupling —
one that would otherwise force a consumer edit when a pack changes — and is that
worth a coordinated two-repository schema migration?

## Requirements

- Assess each of the three candidates separately and reach a separate verdict
  for each. A single blanket verdict is not an acceptable outcome.
- For each candidate, record: what reads it today (file and line), what change
  would force it to be edited, whether the shipping pack can authoritatively
  state it, and the verdict with its reason.
- Explicitly address the `FIRST_PARTY_REMOTES` self-reference problem — whether
  a pack-supplied value can be trusted to classify that same pack's own
  provenance. Do not move it into the snapshot without answering this.
- Any proposal to extend the schema must specify the rollout: how both packs
  ship `schemaVersion` 2, what `SUPPORTED_REGISTRY_SNAPSHOT_SCHEMA_VERSIONS`
  contains during the transition, and what happens to a checkout still shipping
  version 1.
- The assessment phase changes no code. Split any accepted change into its own
  implementation task rather than growing this one.
- Do not re-open registry resolution, the fallback removal, or snapshot
  validation. Those are the other two tasks in this group.

## Acceptance Criteria

- [ ] Each of the three candidates has a recorded verdict — snapshot, stays
      layout-derived, or deferred — with a stated reason and file/line evidence.
- [ ] The `FIRST_PARTY_REMOTES` self-reference question is answered explicitly,
      not left implicit in the verdict.
- [ ] If any verdict is "snapshot", a rollout plan naming both producers and the
      supported-version transition is recorded, and the implementation is split
      into a separate task rather than done here.
- [ ] If every verdict is "stays layout-derived", that is recorded as the
      outcome with its reasoning, and the task completes without a code change.
- [ ] No file outside `.trellis/` is modified by this task.

## Out of scope

- Implementing any accepted schema change. That is a follow-up task this one
  may create.
- Removing the AST fallback (`08-04-audit-registry-snapshot-ast-removal`) or
  producing the SD snapshot (`08-04-audit-registry-snapshot-sd-twin`).
- Any change to `installer/registry.py`, the generator, or the existing
  `schemaVersion` 1 payload.
- Adding a third first-party pack, which would motivate but not constitute this
  work.

## Notes

- Best *worked* last of the three registry-snapshot tasks: it is not blocked by
  them — the assessment can be done at any time — but its most likely accepted
  change (adapter paths) is cheaper to land once both packs already ship
  snapshots. This is a preference, not an encoded ordering. The task carries no
  `order` in `task.json`, so a ranker sorts it as `0` and it ranks *ahead* of
  `08-04-audit-registry-snapshot-ast-removal` (P3, `order` 30), not behind it.
  That is deliberate: `order` is reserved for the tasks that contend for
  `quality-guidelines.md`, and this one only reads that file. A run picking this
  up early loses nothing but the discount described above.
- Explicitly speculative. The task exists to close the question with evidence,
  and closing it as "no change" is a complete outcome.
- Line references verified against `se-ai-command-pack` 0.67.1.
- Planning depth: PRD-only. The deliverable is a recorded assessment; any accepted change is split into its own task, which carries its own planning depth.
