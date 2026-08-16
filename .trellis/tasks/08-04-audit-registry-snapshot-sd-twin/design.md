# Design: SD pack registry-snapshot producer

## Boundaries

| Repository | Changes |
| --- | --- |
| `se-ai-command-pack` (here) | `.trellis/` task artifacts only. No source, template, or generated payload. |
| `sd-ai-command-pack` (upstream) | The producer, the payload-gate entry, the committed snapshot, tests, and release bookkeeping. |

`skill_review.py` is **not touched**. Removing the AST fallback is
`08-04-audit-registry-snapshot-ast-removal`, which this task unblocks. Editing
the consumer here would collapse two tasks into one and remove the only
independent check that the snapshot actually satisfies the real consumer.

## What the snapshot must contain

The consumer's validator `_registry_from_snapshot`
(`skill_review.py:251`) is the contract, and the acceptance criteria require the
snapshot-derived registry to *agree* with the AST-derived one on the same
checkout. That fixes every value:

| Key | SD value | Derivation |
| --- | --- | --- |
| `schemaVersion` | `1` | Literal. Must stay inside `SUPPORTED_REGISTRY_SNAPSHOT_SCHEMA_VERSIONS`. |
| `familyOrder` | 5 ids | `[f.id for f in COMMAND_FAMILIES]`. |
| `skills` | 20 × `{name, family}` | `COMMAND_REGISTRY` order, from `CommandInfo.name` / `.family`. |
| `platforms` | 18 sorted strings | `sorted(PLATFORM_REGISTRY)`. |
| `sharedReferences` | 4 entries | `SHARED_SKILL_REFERENCES`. |

### The AST is blind on two fields, and the snapshot must not copy that blindness

This is the design decision the task turns on, and the first draft got it wrong.

`_parse_registry` reads `FAMILY_LABELS` and `SHARED_REFERENCES`. SD names those
concepts `COMMAND_FAMILIES` and `SHARED_SKILL_REFERENCES`, so the parser finds
neither and derives `family_order = ()` and `shared_references = {}`. The first
draft of this design read that as SD genuinely lacking both and specified
`"familyOrder": []` / `"sharedReferences": {}` for strict parity with the AST.

That was wrong on the facts. SD has both:

- `COMMAND_FAMILIES` — 5 `CommandFamily(id, label, summary)` entries whose ids
  are exactly the 5 families the 20 commands use.
- `SHARED_SKILL_REFERENCES` — 4 entries, `dict[str, tuple[str, ...]]`, the same
  shape as SE's `SHARED_REFERENCES`.

So the empties were **parser blind spots, not absences**. Shipping them would
have permanently encoded a parser limitation into the file that is destined to
become the *only* registry source once
`08-04-audit-registry-snapshot-ast-removal` deletes the AST path — losing real
data that SD has, forever, to satisfy a transitional comparison.

The producer therefore serializes the real objects. The consequence for the
parity criterion is handled honestly in `prd.md`: agreement is required on every
field the AST can actually derive, and the two blind fields are checked against
the **imported objects** instead. The criterion was corrected because its
premise was false, not to make an implementation pass — and it was made
stricter, not weaker: the blind fields now have an assertion where strict-parity
would have accepted empty.

This is also what keeps SD consistent with SE, whose snapshot ships
`list(FAMILY_LABELS.keys())` — real data, not an empty list.

Renaming SD's symbols to `FAMILY_LABELS`/`SHARED_REFERENCES`, or teaching
`_parse_registry` the SD names, would close the gap differently. Both are
rejected: the first churns SD's public registry surface for a parser that is
being deleted, and the second edits the consumer, which this task must not
touch.

## Producer: derive from imported objects, not from the AST

The SE producer (`regenerated_registry_snapshot_text`,
`generate-skill-surfaces.py:1115`) serializes the **imported** registry objects
and says why: the imported objects are authoritative, and field ordering is
load-bearing so the snapshot-derived `RegistryData` is byte-identical to the
AST-derived one.

SD mirrors that. It must not re-parse its own `registry.py` with `ast` — that
would make the producer agree with the parser by construction while both drift
from the real objects, which is the failure the parity criterion exists to
catch.

The one shape difference: SE reads `SKILLS`/`SkillInfo`; SD has
`COMMAND_REGISTRY`/`CommandInfo`. The parser already accepts either
(`skill_review.py:359-361`), with `family` at positional index 2 for
`CommandInfo` — which is where SD's dataclass puts it.

## Seam: one entry in the existing outputs dict

`generate-command-surfaces.py` is already shaped for this.
`generate_surfaces()` returns `dict[relative_path, content]`; `write_surfaces`
writes changed entries and `run_check` regenerates into a temp dir and
byte-compares (`:1151`, `:1188-1193`).

So the producer adds **one entry** to that dict. Consequences, and they are the
reason this seam was chosen over a standalone script:

- `--check` drift detection comes for free. No new gate, no second code path
  that could disagree with the first.
- Determinism is enforced by the existing byte-compare rather than asserted.
- `write_surfaces` already does `destination.parent.mkdir(parents=True)`, so the
  absent `generated/` directory needs no special handling.

Serialization matches SE exactly: `json.dumps(payload, indent=2) + "\n"`.

## The payload gate does not cover `generated/` — it must be extended

Verified rather than assumed, and it is the one place this task changes
behaviour beyond adding a file. `prepare-release.py:221`:

```python
def _is_payload_path(path: str) -> bool:
    return path in PAYLOAD_SINGLETONS or path.startswith(PAYLOAD_PREFIXES)
```

with `PAYLOAD_PREFIXES = ("templates/", "plugins/")` and a fixed
`PAYLOAD_SINGLETONS` set. **`generated/` matches neither.** Left alone, the
snapshot would change without requiring a version bump or a CHANGELOG heading,
and acceptance criterion 7 would fail.

Fix: add `generated/registry-snapshot.json` to `PAYLOAD_SINGLETONS`. A singleton
rather than a `generated/` prefix, because the prefix would silently enrol every
future file placed under `generated/` into the release gate — a decision that
belongs to whoever adds such a file, not to this task.

## Failure modes

- **A wrong snapshot is worse than no snapshot.** Absent falls back
  (`_load_registry_snapshot` returns `None`); malformed, mistyped, or
  unsupported-version raises `ReviewError` (`:324-338`). So shipping a snapshot
  that parses but disagrees turns a working SD checkout into a hard failure.
  This is why parity is verified against the real consumer on a real checkout,
  not against this table.
- **Producer/parser divergence.** Guarded by the parity test comparing
  `_load_registry_snapshot` output against `_parse_registry` output on the same
  SD checkout, field by field.
- **Silent drift.** Guarded by `--check`, proven by inducing a drift rather than
  by reading the code.
- **Schema-version skew.** SD hardcodes `1`. If SE ever bumps
  `SUPPORTED_REGISTRY_SNAPSHOT_SCHEMA_VERSIONS`, SD's snapshot must move in the
  same release or SD checkouts fail closed. Recorded as a known coupling; not
  addressed here because no bump is planned.

## Compatibility

Additive for every consumer. Before: no snapshot, consumer falls back to AST.
After: snapshot present, consumer prefers it and produces the same
`RegistryData`. A pack running the *old* reviewer ignores the file entirely, so
there is no ordering requirement between shipping this and any consumer change.

## Rollout and rollback

Rollback is deleting the snapshot and the payload-gate entry: the consumer
returns to the AST fallback, which is still present because this task does not
remove it. That is the reason the fallback removal is deliberately a separate,
later task — until it lands, this change is fully reversible.

## Release bookkeeping

The snapshot is shipped payload once the gate entry exists, so the SD PR needs a
manifest version bump and a dated CHANGELOG heading, matching the gate SD
already enforces for `templates/` and `plugins/`.
