---
title: Evaluate remaining skill_review layout assumptions for snapshot inclusion
status: done
created: 2026-08-04
branch: task/08-04-audit-registry-snapshot-layout-assumptions
---
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

- [x] Each of the three candidates has a recorded verdict — snapshot, stays
      layout-derived, or deferred — with a stated reason and file/line evidence.
- [x] The `FIRST_PARTY_REMOTES` self-reference question is answered explicitly,
      not left implicit in the verdict.
- [x] If any verdict is "snapshot", a rollout plan naming both producers and the
      supported-version transition is recorded, and the implementation is split
      into a separate task rather than done here.
- [x] If every verdict is "stays layout-derived", that is recorded as the
      outcome with its reasoning, and the task completes without a code change.
- [x] No file outside `.trellis/` is modified by this task.

## Assessment (recorded 2026-08-09)

Verified against the current tree before assessing: every line citation in
this PRD still matches
`templates/skills/se-review-skills/scripts/skill_review.py` —
`SUPPORTED_REGISTRY_SNAPSHOT_SCHEMA_VERSIONS = frozenset({1})` at `:31`,
`FIRST_PARTY_REMOTES` at `:39-42`, `IGNORED_DIRECTORIES` from `:43`, the
unsupported-version `ReviewError` at `:329-337`, the snapshot-then-AST
fallback at `:424-428`, `owner_kind` classification at `:433`, adapter paths
at `:442-446`, and the dual-source trust membership check at `:703`. The
shipped `generated/registry-snapshot.json` carries exactly `schemaVersion`,
`familyOrder`, `skills`, `platforms`, and `sharedReferences` — none of the
three candidates.

### Candidate 1 — `FIRST_PARTY_REMOTES`: **stays consumer-owned**

- Read today, two distinct uses with different semantics:
  - `:433-438` — `:433` looks up the expected remote by pack name; `:434-438`
    compare it to the checkout's normalized `remote.origin.url` and classify
    `owner_kind` (`se-upstream`/`sd-upstream` on match). That classification
    is consumed downstream: `owner_verified` at `:1400-1404` requires an
    upstream or repo-local `owner_kind` before a skill is marked
    `changeable`.
  - `:703` — a **name-membership** gate on a supplied source root
    (`context.name not in FIRST_PARTY_REMOTES`). This gate never consults
    the remote at all: a fork that keeps the first-party pack *name* already
    passes it today, remote notwithstanding. Moving the map into the
    snapshot would not change this gate's behaviour — its exposure and its
    mitigation live in the remote-comparing path above.
- What would force an edit: a new first-party pack, or a remote migration
  (org or repo rename) for an existing one.
- Can the shipping pack authoritatively state it: **No.** This is the
  self-reference question, answered explicitly: the map's discriminating
  power is entirely in the remote comparison at `:434-438`, and that value
  classifies the provenance of the very pack that would ship it. A fork's
  snapshot would assert the fork's own remote as expected, the comparison
  would then succeed, the fork would classify itself
  `se-upstream`/`sd-upstream`, and `owner_verified` at `:1400-1404` would
  treat it as trusted — the check would verify that a pack agrees with
  itself. A provenance trust anchor must be held by the verifier, not
  supplied by the subject being verified.
- Verdict: **stays layout-derived/consumer-owned**, unconditionally — not
  deferred, because the answer does not change with rollout cost or pack
  count. Adding a third first-party pack correctly requires a consumer
  edit here: that edit *is* the trust decision.

### Candidate 2 — adapter paths (`:442-446`): **deferred**

- Read today: assigned at `:442-446` (per-pack allowed skill-template root:
  `templates/skills` for se, `templates` for sd), stored on
  `PackageContext.allowed_template_root` (`:116`, `:457`), and consumed in
  six places: canonical-containment filtering (`:591-593`), `local-override`
  role classification (`:733-735`), the shared-reference allowlist
  (`:1245-1252`), the `changeable` computation (`:1399-1408`), the
  per-skill `taskRouting.allowedTemplateRoot` serialization (`:1470`), and
  the report payload (`:1558-1559`). The **assignment** is the only
  per-pack branch; every consumer reads the stored value pack-agnostically.
  A snapshot move would therefore replace the `:442-446` branch and extend
  the snapshot parser (`_registry_from_snapshot`, `:250+`, plus the
  generator and schema) to carry the new field — small, but not "one edit".
- What would force an edit: a third pack, or either pack relocating its
  skill templates.
- Can the shipping pack authoritatively state it: **yes** — it is a pure
  layout fact about the pack's own tree, exactly the kind of data the
  snapshot exists to carry, and the strongest candidate as the PRD
  anticipated.
- Why not now: the cost ledger is decisive at the current pack count. A
  `schemaVersion` 2 needs both producers, and `sd-ai-command-pack` ships no
  snapshot at all today — its producer task
  (`08-04-audit-registry-snapshot-sd-twin`) is blocked on explicit
  upstream-PR approval. The consumer hard-fails unknown versions
  (`frozenset({1})` at `:31`, `ReviewError` at `:329-337`), so rollout
  requires a coordinated two-repository migration plus version bumps and
  dated CHANGELOG headings in both packs (`quality-guidelines.md`
  shipped-payload rule) — all to delete one `elif` that changes only when a
  pack is added or restructured, neither of which is planned.
- Verdict: **deferred**, with two re-assessment triggers recorded: (1)
  `sd-ai-command-pack` ships a `schemaVersion` 1 snapshot (the sd-twin task
  completes), and (2) a third first-party pack or a template relocation
  actually materializes. If adopted then, the natural shape is an optional
  per-pack skill-root key in a `schemaVersion` 2 payload with the consumer
  accepting `{1, 2}` during transition and keeping the `:442-446` branch as
  the version-1 fallback — recorded as a sketch only; the binding rollout
  plan belongs to the future implementation task per this PRD's own
  acceptance criteria.

### Candidate 3 — discovery globs and `IGNORED_DIRECTORIES` (`:43+`): **split — `IGNORED_DIRECTORIES` stays tool-owned; per-pack discovery roots deferred with candidate 2**

The candidate is not homogeneous, and the two halves earn different
verdicts:

- **`IGNORED_DIRECTORIES` (`:43+`): stays tool-owned.** Read in two
  places: discovery traversal pruning (`:481`) and related-resource
  filtering (`:1222`). Universal build/cache/VCS directory names, identical
  for every pack. Only a change in the tool's own scanning policy edits
  them; no pack change can force it. A snapshot copy would be N identical
  copies of tool policy, inverting ownership.
- **Discovery roots (`_discover`, `:491-510`): per-pack after all —
  deferred.** Discovery branches on pack name with *different roots*: se
  scans `templates/skills/*/SKILL.md` (`:498-504`), sd scans
  `templates/.agents/skills/*/SKILL.md` (`:505-510`). A pack relocating its
  skill templates therefore *does* force a consumer edit here — the
  "universal scan policy" framing holds only for the ignore list and the
  `*/SKILL.md` pattern, not the roots. Note the sd discovery root
  (`templates/.agents/skills`) is not even the same value as the sd adapter
  path (`templates`), so a future schema key must carry both facts, not
  one. Verdict: **deferred**, same triggers and same cost ledger as
  candidate 2 — these are the same kind of per-pack layout fact, and one
  future `schemaVersion` 2 change should carry the adapter path and the
  discovery root together rather than migrating twice.

### Outcome

No candidate moves into the snapshot now, and nothing is implemented by
this task. Verdicts: candidate 1 **stays** (consumer-owned trust anchor);
candidate 2 **deferred**; candidate 3 **split** — ignore list stays,
per-pack discovery roots deferred alongside candidate 2 under one future
schema change. No schema change, no code change, no new implementation
task — the deferral triggers already have their own task
(`08-04-audit-registry-snapshot-sd-twin`) or are explicitly out of scope
(third pack). This "no change now" conclusion is the assessment completing
successfully, per the Goal.

### Completion evidence

- Verdicts recorded in the Assessment section above: candidate 1 stays
  consumer-owned (evidence `:433-438`, `:703`, `:1400-1404`); candidate 2
  deferred (assignment `:442-446`, six consumers, triggers recorded);
  candidate 3 split — `IGNORED_DIRECTORIES` stays (`:481`, `:1222`),
  per-pack discovery roots deferred (`:498-510`).
- Self-reference question answered explicitly in candidate 1: a
  pack-shipped remote map cannot classify its own pack's provenance — the
  trust anchor stays with the verifier.
- No verdict is "snapshot", so no rollout plan is owed and no
  implementation task was split out; the deferral triggers map to the
  existing `08-04-audit-registry-snapshot-sd-twin` task.
- Not every verdict is "stays": candidate 2 and half of candidate 3 are
  deferred with recorded triggers; the Outcome section records the
  no-change-now conclusion with reasoning.
- `git status --porcelain` during implementation showed only
  `.trellis/tasks/08-04-audit-registry-snapshot-layout-assumptions/` paths;
  no file outside `.trellis/` was modified.
- Converged through three Codex adversarial rounds (R1: three factual
  defects fixed; R2: two evidence gaps fixed; R3: pass). `make check`:
  `Ran 640 tests ... OK (skipped=1)`, `All checks passed!` Shipped as
  PR #192; Copilot round 1 found one PR-description overclaim (fixed by
  editing the description), round 2 returned no new comments.

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
