---
title: Remove skill_review AST registry fallback once both packs ship snapshots
status: done
created: 2026-08-04
---
# Remove skill_review AST registry fallback once both packs ship snapshots

> **Unblocked 2026-08-16.** The SD twin producer shipped:
> `platypeeps/sd-ai-command-pack#483`, squash-merged as `232138a8`, and
> `generated/registry-snapshot.json` is present on that pack's `main`.
> `task.json` now carries `blocked: false` and a null `blockedOn`; this line is
> for human readers.

## Goal

Make `_load_registry_snapshot` the sole registry source in `skill_review.py`,
so the tool no longer opens `installer/registry.py` in any checkout, and delete
the AST parser that exists only to support the transitional fallback.

## Problem

`_package_context` currently resolves the registry two ways
(`templates/skills/se-review-skills/scripts/skill_review.py:422-429`; the
references in this section and the table below were taken at 0.67.1 and
re-verified at 0.69.0 on 2026-08-16 — see the drift table in `design.md`):

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
| `_parse_registry` | `:341` | AST-parses `installer/registry.py` into `RegistryData`. |
| `_assignment` | `:225` | Locates a module-level assignment by name. |
| `_string_value` | `:236` | Extracts a string literal. |
| `_call_value` | `:242` | Extracts a positional or keyword argument from a call. |
| `import ast` | `:11` | Unused once the three helpers and the parser go; every `ast.` reference in the file is inside them. |
| fallback branch | `:428-429` | The `if registry is None:` arm. |
| `None` return | `:318-319` | `_load_registry_snapshot`'s absent/symlink return. Only the *symlink* half exists solely to trigger the fallback; the *absent* half survives as the signal the caller applies policy to. |

The three helpers are used only by `_parse_registry`; confirmed by grep on
2026-08-16 rather than assumed, since `_string_value` is the kind of helper that
acquires unrelated callers over time. `_crosses_symlink` is **not** in the
removal surface: it has two callers outside it (`:1087`, `:1909`) and stays.

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

**Established 2026-08-16 by measurement, and the answer is not the obvious one.**
`_parse_registry` never raises: absent file, symlinked file, or `SyntaxError` all
return `RegistryData({}, (), (), (), {})` (`:342-347`). For a checkout with no
`installer/registry.py` — every non-pack repository — today's "fallback" performs
no parse at all. It is a silent empty registry.

Run against a throwaway git repository holding one `SKILL.md`, no
`manifest.json`, no snapshot and no `installer/`:

```
"ownerKind": "repo-local", "familyOrder": [], "declaredPlatforms": []
"skills": [{"name": "demo", "family": "Uncategorized", ...}]
exit=0
```

So a hard error for absent snapshots is **not** acceptable across the board: it
would withdraw support for every non-pack checkout, which the tool advertises via
a first-class `ownerKind: "repo-local"`. The removal is still shippable, but the
fail-closed rule is scoped to checkouts that owe a snapshot — `name in
FIRST_PARTY_REMOTES`, not `owner_kind`, so a fork cannot silently degrade. The
symlink refusal is *not* scoped: it raises everywhere. See `design.md`.

The absent-snapshot criterion is amended accordingly and a new criterion added
requiring the repo-local path to be provably unchanged. Amended because its premise was
measured false, not to make an implementation pass — and before the amendment
nothing in the criteria protected the repo-local path at all.

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
  behaviour. The line references above were taken at 0.67.1 and are **stale**;
  re-located 2026-08-16, the live claims are `:1167`, `:1193-1194` and
  `:1737-1745`. Grep the whole file rather than trusting either list.
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

- [x] `08-04-audit-registry-snapshot-sd-twin` is verifiably complete — an SD
      checkout resolves a snapshot — before this task starts. Satisfied
      2026-08-16: PR #483 merged as `232138a8`, and on that branch the real
      consumer was shown to take the snapshot path with `_parse_registry`
      monkeypatched to raise. See that task's `disposition.md`.
- [ ] `grep -n 'installer/registry.py\|installer" / "registry'` over
      `skill_review.py` returns no matches, and none of the four removed
      symbols remains.
- [ ] An absent snapshot raises `ReviewError` **in a first-party pack checkout**
      (`name in FIRST_PARTY_REMOTES`); a symlinked snapshot path raises
      `ReviewError` and is not opened, in **every** checkout. Both are covered by
      tests, and the symlink test asserts the path was not followed.
- [ ] A non-first-party checkout resolves an empty `RegistryData` and still
      succeeds — byte-identical on `ownerKind`, `familyOrder`,
      `declaredPlatforms` and per-skill `family` to a baseline captured **before**
      the change. Covered by a test the suite did not previously have.
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

- Was blocked on `08-04-audit-registry-snapshot-sd-twin`; cleared 2026-08-16 when
  that task's upstream PR merged. Between 2026-08-06 and then, the markers were
  `blocked: true` and `blockedOn` in `task.json`; they are now `false` and null.
  Before 2026-08-06 the blocker existed only as prose in this file's Goal, which
  no ranking helper can read — an autonomous run could have selected it.
- Line references verified against `se-ai-command-pack` 0.67.1, and re-verified
  2026-08-16 at 0.69.0. The `skill_review.py` and test references had drifted by
  one line or not at all; the `quality-guidelines.md` references were wrong and
  are corrected above. The drift table is in `design.md`.
- Complex enough to warrant `design.md` and `implement.md` if the
  non-first-party-checkout question turns out to have a non-trivial answer;
  PRD-only otherwise. The repository contract requires both together for a
  complex task (`.trellis/workflow.md:164`), so the escalation is not partial.
  **The escalation fired**: the answer is non-trivial (see above), so both
  artifacts were written.

## References

Research notes that lived beside this item's Trellis record and were not carried
into docs/work. Recover the bodies from git history under `.trellis/tasks/archive/2026-08/08-04-audit-registry-snapshot-ast-removal`:

- disposition.md
