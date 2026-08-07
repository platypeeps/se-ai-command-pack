# Remove skill_review AST registry fallback once both packs ship snapshots

> **Blocked on `08-04-audit-registry-snapshot-sd-twin`.** Do not start until the
> SD twin producer has shipped. The machine-readable markers are `blocked: true`
> and `blockedOn` in `task.json`; this line is for human readers.

## Goal

Make `_load_registry_snapshot` the sole registry source in `skill_review.py`,
so the tool no longer opens `installer/registry.py` in any checkout, and delete
the AST parser that exists only to support the transitional fallback.

## Problem

`_package_context` currently resolves the registry two ways
(`templates/skills/se-review-skills/scripts/skill_review.py:421-428`):

```python
# Prefer the versioned generated snapshot; fall back to AST-parsing the
# checkout's registry.py when no usable snapshot is present (transitional,
# until every pack ships a snapshot). A present-but-broken snapshot raises.
registry = _load_registry_snapshot(
    package_root / "generated" / "registry-snapshot.json"
)
if registry is None:
    registry = _parse_registry(package_root / "installer" / "registry.py")
```

The fallback is explicitly transitional. It keeps an AST parser of another
repository's source code load-bearing, which is exactly what the snapshot was
introduced to eliminate: `quality-guidelines.md:842-844` states the point is to
establish "snapshot identity without importing or executing reviewed repository
code".

## Removal surface

| Symbol | Line | Role |
| --- | --- | --- |
| `_parse_registry` | `:340` | AST-parses `installer/registry.py` into `RegistryData`. |
| `_assignment` | `:224` | Locates a module-level assignment by name. |
| `_string_value` | `:235` | Extracts a string literal. |
| `_call_value` | `:241` | Extracts a positional or keyword argument from a call. |
| fallback branch | `:427-428` | The `if registry is None:` arm. |
| `None` return | `:317-318` | `_load_registry_snapshot`'s absent/symlink return, which exists solely to trigger the fallback. |

The three helpers are used only by `_parse_registry`; confirm that before
deleting rather than assuming it, since `_string_value` is the kind of helper
that acquires unrelated callers over time.

## The two decisions this task must not get wrong

### 1. `None` must become a hard failure, not a permissive path

`_load_registry_snapshot` returns `None` for two distinct reasons
(`:309-318`):

```python
if _crosses_symlink(path) or not path.is_file():
    return None
```

Absent snapshot, and a snapshot path that crosses a symlink boundary the tool
deliberately refuses to follow. Today both mean "fall back". With the fallback
gone they must both mean "fail closed" — a `ReviewError`, consistent with how
the function already treats a malformed or unsupported-version snapshot.

**The symlink refusal is a security property and must survive the refactor
unchanged.** Removing the fallback must not turn "refuse to follow the symlink"
into "follow it". The two `None` causes should also produce distinguishable
messages: an absent snapshot is a packaging problem, a symlinked one is a
rejected input.

### 2. Pack parity is not fleet coverage

The Goal's precondition — both SE and SD packs ship snapshots — covers the two
first-party packs in `FIRST_PARTY_REMOTES` (`:39-42`). But `_package_context`
also resolves `owner_kind = "repo-local"` for any other Git checkout (`:439-440`),
and `skill_review.py` runs against those. They ship no snapshot and no
`installer/registry.py` either.

So this task must establish what a non-first-party checkout does after the
change, and confirm that turning its current behaviour into a hard error is
intended rather than incidental. If it is not acceptable, the fallback removal
is not yet unblocked even after the SD twin ships, and that finding is a
legitimate outcome of this task.

## Requirements

- Delete `_parse_registry`, `_assignment`, `_string_value`, `_call_value`, and
  the `if registry is None:` fallback branch, after confirming no other caller
  exists for each.
- Convert both `None` causes in `_load_registry_snapshot` into `ReviewError`
  with distinguishable messages, preserving the `_crosses_symlink` refusal
  exactly. The tool must never follow a symlinked snapshot path.
- Determine and record the post-change behaviour for `repo-local` and any other
  non-first-party checkout, and confirm it is intended. Do not ship the removal
  while that behaviour is unexamined.
- Update `quality-guidelines.md` where it documents the fallback as current
  behaviour — at minimum `:295`, `:318-319`, and `:835-838`, each of which
  describes snapshot-preferred resolution *with* an AST fallback.
- Rework the fallback tests rather than deleting them wholesale
  (`tests/test_skill_review.py`):
  - `test_snapshot_preferred_matches_ast_fallback` (`:241`) loses its
    comparand and goes.
  - `test_absent_snapshot_falls_back_to_ast` (`:250`) becomes an
    absent-snapshot fail-closed test.
  - `test_symlinked_snapshot_is_not_followed_and_falls_back` (`:257`) becomes a
    symlinked-snapshot fail-closed test. **Deleting this one is not
    acceptable** — it is the regression test for the security property.
  - The existing fail-closed tests (`:290`, `:300`, `:311`, `:317`) should
    continue to pass unchanged.
- Keep the change bounded to registry resolution. Do not alter
  `SUPPORTED_REGISTRY_SNAPSHOT_SCHEMA_VERSIONS`, the snapshot schema,
  `_registry_from_snapshot`'s validation, or anything under `installer/`.

## Acceptance Criteria

- [ ] `08-04-audit-registry-snapshot-sd-twin` is verifiably complete — an SD
      checkout resolves a snapshot — before this task starts.
- [ ] `grep -n 'installer/registry.py\|installer" / "registry'` over
      `skill_review.py` returns no matches, and none of the four removed
      symbols remains.
- [ ] An absent snapshot raises `ReviewError`; a symlinked snapshot path raises
      `ReviewError` and is not opened. Both are covered by tests, and the
      symlink test asserts the path was not followed.
- [ ] The two `ReviewError` messages are distinguishable — a test asserts on the
      message text of each, so an absent snapshot cannot be mistaken for a
      rejected one. Asserting only the exception type does not satisfy this.
- [ ] The behaviour for non-first-party checkouts is recorded with its
      justification.
- [ ] `quality-guidelines.md` contains no remaining claim that the consumer
      falls back to an AST parse. Verified by grepping for `fallback` and `AST`
      in that file, not by reviewing the diff.
- [ ] The full `tests/test_skill_review.py` suite passes, with no net loss of
      fail-closed coverage.

## Out of scope

- Producing the SD snapshot. That is `08-04-audit-registry-snapshot-sd-twin`.
- Moving `FIRST_PARTY_REMOTES`, discovery globs, or adapter paths into the
  snapshot. That is `08-04-audit-registry-snapshot-layout-assumptions`.
- Bumping the snapshot `schemaVersion`, or changing what the snapshot contains.
- Any change to `installer/registry.py`, which remains the source of truth the
  generator reads.

## Notes

- Blocked on `08-04-audit-registry-snapshot-sd-twin`; markers are `blocked: true`
  and `blockedOn` in `task.json`. Before this task, the blocker existed only as
  prose in this file's Goal, which no ranking helper can read — an autonomous
  run could have selected it.
- Line references verified against `se-ai-command-pack` 0.67.1.
- Complex enough to warrant `design.md` and `implement.md` if the
  non-first-party-checkout question turns out to have a non-trivial answer;
  PRD-only otherwise. The repository contract requires both together for a
  complex task (`.trellis/workflow.md:164`), so the escalation is not partial.
