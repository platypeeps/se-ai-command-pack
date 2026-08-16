# Design: remove the AST registry fallback

## Premise re-verification, 2026-08-16

The PRD's line references were taken at 0.67.1; this repository's `manifest.json`
now reads 0.69.0. Everything load-bearing was re-checked before designing.

| PRD claim | Status at HEAD |
| --- | --- |
| `_parse_registry` at `:340` | `:341` |
| `_assignment` `:224`, `_string_value` `:235`, `_call_value` `:241` | `:225`, `:236`, `:242` |
| fallback branch `:427-428` | `:428-429` |
| `None` return `:317-318` | `:318-319` |
| `_package_context` `:421-428` | `:413`, resolution at `:422-429` |
| test line numbers `:241 :250 :257 :290 :300 :311 :317` | all exact |
| spec claims at `:295`, `:318-319`, `:835-838` | **stale.** The live claims are `quality-guidelines.md:1167`, `:1193-1194`, and `:1737-1745` |

The three helpers are used **only** by `_parse_registry` — confirmed by grep, as
the PRD required rather than assumed. `_string_value` is called at `:245`,
`:247`, `:355`, `:387`, `:395`, `:401`; `_assignment` at `:350`, `:364`, `:382`,
`:391`; `_call_value` at `:374`, `:375`. Every one of those sites is inside
`_parse_registry` or inside another of the three.

`_crosses_symlink` has two callers outside this surface (`:1087`, `:1909`) and
**stays**.

`import ast` (`:11`) becomes unused: every `ast.` reference in the file
(`:225-242`, `:345-396`) is inside the deleted region. It goes with them.

Only one copy of the file is tracked: `templates/skills/se-review-skills/scripts/skill_review.py`.
`se-review-skills` is not mirrored into `.agents/` or `.claude/`, so there is no
second copy to keep in step — enumerated with `git ls-files | grep 'skill_review.py$'`,
not assumed.

## The decision the task turns on: what a non-first-party checkout does

The PRD said this must be established and not left incidental. It was measured,
not reasoned about.

`_parse_registry` **never raises**. Absent file, symlinked file, or a
`SyntaxError` all return `RegistryData({}, (), (), (), {})` (`:342-347`). So for
a checkout with no `installer/registry.py` — which is every non-pack repository —
today's "fallback" is not a parse at all. It is a silent empty registry.

Measured on a throwaway git repository holding one `SKILL.md`, no
`manifest.json`, no snapshot and no `installer/`:

```
"ownerKind": "repo-local", "familyOrder": [], "declaredPlatforms": []
"skills": [{"name": "demo", "family": "Uncategorized", ...}]
exit=0
```

`skill_review.py` works there today and emits `ownerKind: "repo-local"` as a
first-class value. Turning that into a `ReviewError` would not be removing a
transitional fallback; it would be withdrawing support for every non-pack
checkout the tool advertises support for.

**So an absent snapshot fails closed only where a snapshot is owed.** The
predicate is first-party pack identity.

### Predicate: `name in FIRST_PARTY_REMOTES`, not `owner_kind`

Two candidates, and the weaker one is the tempting one.

`owner_kind` is `"se-upstream"`/`"sd-upstream"` only when the *remote* also
matches (`:434-441`). A fork, a mirror, or a clone added under a different
remote name resolves to `"unresolved"` — so keying the requirement on
`owner_kind` would let a fork of the pack delete its snapshot and silently
review with an empty registry. That is the defect-masking the snapshot fail-closed
rule exists to prevent.

`name` comes from the checkout's own `manifest.json` (`:417-421`) and is already
computed before registry resolution, so no reordering is needed. A checkout that
*claims* to be `se-ai-command-pack` or `sd-ai-command-pack` owes a snapshot
regardless of where it was cloned from.

Known limitation, recorded rather than hidden: a pack checkout whose
`manifest.json` is missing or unreadable resolves `name = None` and therefore
degrades to the empty registry instead of failing closed. That is already true of
`owner_kind` today and is not made worse here. Closing it would mean deciding
what an unreadable manifest means for the whole tool, which is outside this
task's boundary.

## The two `None` causes separate, and only one stays `None`

Today (`:318-319`):

```python
if _crosses_symlink(path) or not path.is_file():
    return None
```

Two unrelated conditions collapsed into one signal because both meant the same
thing — fall back. They stop meaning the same thing.

- **Symlinked path — a rejected input.** Raises `ReviewError` from inside
  `_load_registry_snapshot`, unconditionally, for every checkout including
  repo-local. The refusal is a security property: the check runs *before* any
  filesystem read of the target and the path is still never opened. Raising is
  strictly stronger than today's silent fallback, and it must not become
  conditional on pack identity — a symlinked path is not a packaging gap that
  some checkouts are allowed to have.
- **Absent file — a packaging question.** Stays `None`, and the *caller* decides:
  `ReviewError` for a first-party pack, an empty `RegistryData` for anything
  else.

Keeping the absent case as `None` is deliberate. The alternative — passing a flag
into `_load_registry_snapshot` so it can raise both — puts pack-identity policy
inside a function whose job is to load and validate a file. The loader reports
what it found; the caller applies policy.

## Shape after the change

```python
def _empty_registry() -> RegistryData:
    """A fresh empty registry per call.

    RegistryData is frozen but `families` and `shared_references` are plain
    dicts, so a module-level singleton would be shared across every checkout
    resolved in one run. Nothing mutates them today -- every consumer site uses
    `.get()` or `.items()`, checked at `:1029`, `:1375`, `:1524`, `:1583`,
    `:1740` -- but a singleton makes the first future mutation a
    cross-checkout contamination bug instead of a local one. A factory costs a
    line."""
    return RegistryData({}, (), (), (), {})
```

In `_load_registry_snapshot`:

```python
if _crosses_symlink(path):
    raise ReviewError(
        f"refusing to follow symlinked registry snapshot path {path}"
    )
if not path.is_file():
    return None
```

In `_package_context`, replacing the fallback branch:

```python
snapshot_path = package_root / "generated" / "registry-snapshot.json"
registry = _load_registry_snapshot(snapshot_path)
if registry is None:
    if name in FIRST_PARTY_REMOTES:
        raise ReviewError(
            f"first-party pack {name!r} ships no registry snapshot at "
            f"{snapshot_path}; the generator must write it"
        )
    registry = _empty_registry()
```

The two messages are lexically distinguishable — `refusing to follow symlinked`
versus `ships no registry snapshot` — which the "two `ReviewError` messages are distinguishable" criterion requires a
test to assert on, not merely the exception type.

## Behaviour matrix

| Checkout | Snapshot | Today | After |
| --- | --- | --- | --- |
| SE pack | present, valid | snapshot | snapshot, unchanged |
| SD pack | present, valid (since `232138a8`) | snapshot | snapshot, unchanged |
| First-party pack | absent | AST parse of its own `registry.py` | **`ReviewError`** |
| First-party pack | malformed / bad version | `ReviewError` | `ReviewError`, unchanged |
| repo-local / unresolved | absent (always) | empty `RegistryData`, exit 0 | **empty `RegistryData`, exit 0 — unchanged** |
| any | symlinked path | silent fallback, not followed | **`ReviewError`, still not followed** |

Two rows change. The first-party-absent row is the point of the task. The
symlinked row is a deliberate narrowing that applies to every checkout, including
repo-local: an unusual input that was tolerated becomes an error. No path that
was refused becomes followed — the narrowing is in the direction of refusing
more, never of following more.

Every other row is unchanged, and the repo-local row being unchanged is an
obligation this design takes on, not an incidental outcome.

## Consequence for the absent-snapshot criterion

That criterion read "An absent snapshot raises `ReviewError`" without
qualification. As written it would mandate the repo-local break that the
"behaviour for non-first-party checkouts is recorded with its justification"
criterion asks the task to examine — the two criteria are in tension, which is exactly what
the PRD anticipated when it said a non-trivial answer here is a legitimate
outcome.

It is amended to scope the hard failure to first-party checkouts, and a
new criterion is added requiring repo-local behaviour to be *unchanged* and
proven so by a test. That is a narrowing of one criterion paired with a new
obligation, not a relaxation: before the amendment nothing in the criteria
protected the repo-local path at all.

## What is not changed

`SUPPORTED_REGISTRY_SNAPSHOT_SCHEMA_VERSIONS`, the snapshot schema,
`_registry_from_snapshot`'s validation, `_crosses_symlink` itself, and anything
under `installer/`. `installer/registry.py` remains the source of truth the
*generator* reads; what ends is the *consumer* reading it.

## Rollback

Revert the commit. The snapshot producers on both packs are unaffected by this
change, so reverting restores the fallback with no other coordination. There is
no data migration and no persisted state.
