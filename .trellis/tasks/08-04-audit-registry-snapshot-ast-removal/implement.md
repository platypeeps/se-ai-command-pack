# Implement: remove the AST registry fallback

Ordered steps with gates. Every gate is a command with a pass condition named
before it runs.

## Step 0 — baseline, on a branch

```bash
cd ~/repos/platypeeps/se-ai-command-pack
git checkout main && git pull --ff-only
git checkout -b task/audit-registry-snapshot-ast-removal
BASE="$(git rev-parse HEAD)"
```

Record `BASE`; the falsifiability gate restores from it.

**Commit before any destructive verification.** `git checkout $BASE -- <file>`
on a branch with no commits makes `HEAD == BASE` and destroys the work. Commit
first, then restore. Never `git stash` — it silently no-ops once the change is
committed and the test reports a pass that never ran.

**G0 — record the pre-change repo-local baseline.** Build a throwaway git
repository holding one `SKILL.md`, no `manifest.json`, no snapshot, no
`installer/`, and run:

```bash
python3 templates/skills/se-review-skills/scripts/skill_review.py \
  inventory --root "$D" --scope package --installed off
```

Pass: exit 0, `"ownerKind": "repo-local"`, `"familyOrder": []`, the skill present
with `"family": "Uncategorized"`. Keep the output — Step 4 compares four named
fields against it, not the whole document, since absolute paths and content
hashes legitimately differ between fixture builds. Taken **before** the edit, so
it cannot be reconstructed to match the result.

## Step 1 — separate the two `None` causes

In `templates/skills/se-review-skills/scripts/skill_review.py`,
`_load_registry_snapshot`:

```python
if _crosses_symlink(path):
    raise ReviewError(
        f"refusing to follow symlinked registry snapshot path {path}"
    )
if not path.is_file():
    return None
```

Update the docstring: `None` now means *absent only*; a symlinked path and a
present-but-broken snapshot both raise. Keep the existing sentence explaining why
a broken snapshot must never fall through.

The symlink check stays **before** any read of the target, and the target is
still never opened on that branch. That ordering is the security property; do not
reorder it for tidiness.

## Step 2 — apply the policy at the caller

Add near `RegistryData`:

```python
def _empty_registry() -> RegistryData:
    return RegistryData({}, (), (), (), {})
```

A factory, not a module-level constant: `RegistryData` is frozen but `families`
and `shared_references` are plain dicts, so a singleton would be shared across
every checkout in one run. Nothing mutates them today (`:1029`, `:1375`,
`:1524`, `:1583`, `:1740` all read), which is what makes the singleton tempting
and the eventual bug remote and confusing.

Replace the fallback branch in `_package_context` (`:422-429`):

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

Replace the transitional comment above it: resolution is snapshot-only; a
first-party pack owes a snapshot, anything else gets an empty registry.

`name` is already computed at `:417-421`, above this point. No reordering of the
remote lookup or of `owner_kind` is needed — confirm that rather than assume it,
because moving the manifest read would change what `owner_kind` sees.

## Step 3 — delete the AST parser

Delete `_parse_registry` (`:341`), `_assignment` (`:225`), `_string_value`
(`:236`), `_call_value` (`:242`), and `import ast` (`:11`).

Fix the two stale comments that reference the deleted function by name:
`:253` ("`_parse_registry`'s field semantics") and `:302-304` ("mirror
`_parse_registry`'s `tuple(sorted(platforms))`"). The sort stays — it is a
producer-drift defence in its own right — but its stated reason must stop citing
a function that no longer exists.

**G1 — the removal surface is gone and nothing else broke.**

```bash
F=templates/skills/se-review-skills/scripts/skill_review.py
grep -n 'installer/registry.py\|installer" / "registry' $F
grep -n '_parse_registry\|_assignment\|_string_value\|_call_value\|^import ast\|\bast\.' $F
```

Pass: both return **no matches**. `_crosses_symlink` must still be present with
its two other callers (`:1087`, `:1909`) intact — grep for it and expect three
sites, not zero.

**G1b — the diff stays inside the stated boundary.** The PRD forbids touching
`SUPPORTED_REGISTRY_SNAPSHOT_SCHEMA_VERSIONS`, the snapshot schema,
`_registry_from_snapshot`'s validation, and anything under `installer/`, and
nothing else in this plan enforces it.

```bash
git diff --name-only "$BASE" | grep -vE '^(templates/skills/se-review-skills/scripts/skill_review\.py|tests/test_skill_review\.py|\.trellis/|CHANGELOG\.md|manifest\.json)$' \
  || echo "boundary clean"
git diff "$BASE" -- templates/skills/se-review-skills/scripts/skill_review.py \
  | grep -E '^[-+].*(SUPPORTED_REGISTRY_SNAPSHOT_SCHEMA_VERSIONS|_registry_from_snapshot)' \
  || echo "protected symbols untouched"
```

Pass: `boundary clean` and `protected symbols untouched`, plus whatever
`make generate` legitimately restamps for the version bump. Any other path is
listed with its reason before completion, not silently accepted.

## Step 4 — repo-local is unchanged

**G2 — the measured baseline is reproduced exactly.** Re-run the Step 0 command
against the same throwaway repository and diff against the recorded output.

Pass: exit 0, and `ownerKind`, `familyOrder`, `declaredPlatforms` and the skill's
`family` identical to the G0 capture. Compare the JSON fields, not a visual
skim; paths and hashes may legitimately differ if the fixture is rebuilt, so
rebuild it once and reuse it.

Fail here means the change withdrew support for non-pack checkouts, which is the
outcome the PRD said would make the removal not yet shippable.

## Step 5 — the first-party arm fails closed

**G3 — a pack checkout with no snapshot raises.** Write a minimal
`manifest.json` -- `{"name": "se-ai-command-pack", "version": "0.0.0"}` -- into a
throwaway git repository with no `generated/registry-snapshot.json`, and run the
inventory. Minimal, not a copy of this repository's 200KB manifest: only `name`
and `version` are read (`:417-421`), and a copied manifest would leave the gate
depending on fields it does not test.

Pass: nonzero exit, and the message contains `ships no registry snapshot`.

**G4 — a symlinked snapshot path raises and is not followed.** Point
`generated/registry-snapshot.json` at a real, valid snapshot **through a
symlink**, in a *non*-first-party checkout, so the only thing under test is the
symlink refusal.

Pass: nonzero exit and the message contains `refusing to follow symlinked`.

Prove the not-opened half by **paired arms**, not by the error text and not by
`st_atime` — atime is unreliable under `relatime`/`noatime` and on APFS, so a
gate resting on it reports a pass it did not earn. Make the symlink target a
*valid* snapshot carrying a distinctive `familyOrder`, then run twice:

- symlink at `generated/registry-snapshot.json` → nonzero, refusal message, and
  the distinctive `familyOrder` appears nowhere in the output;
- the same bytes as a regular file at the same path → exit 0 and the distinctive
  `familyOrder` present.

The second arm is what makes the first mean something: it shows the content was
readable and consumable, so the refusal came from the symlink and not from the
run failing for an unrelated reason.

**G5 — the two messages are distinguishable.** Assert on the message text of each
of G3 and G4, not on `ReviewError` alone. Two tests that both assert
`assertRaises(ReviewError)` would pass while the messages were identical, which
is the failure the "distinguishable messages" criterion names.

## Step 6 — rework the tests

In `tests/test_skill_review.py`:

- `test_snapshot_preferred_matches_ast_fallback` (`:241`) — delete. Its
  comparand no longer exists.
- `test_absent_snapshot_falls_back_to_ast` (`:250`) — becomes
  absent-snapshot-fails-closed **for a first-party checkout**, asserting the
  message text.
- `test_symlinked_snapshot_is_not_followed_and_falls_back` (`:257`) — becomes
  symlinked-snapshot-fails-closed, asserting the message text **and** that the
  target was not opened. **Deleting this test is not acceptable**; it is the
  regression test for the security property.
- Add a repo-local test: no manifest, no snapshot, inventory succeeds with an
  empty registry. This is new coverage the old suite did not have, and it is what
  makes the amended criterion honest.
- The four existing fail-closed tests (`:290`, `:300`, `:311`, `:317`) must pass
  **unchanged**. If one needs editing, the change reached further than intended.

**G6 — the suite passes with no net loss of fail-closed coverage.**

```bash
.venv/bin/python -m pytest tests/test_skill_review.py -q
```

Pass: green, and the count of tests asserting `ReviewError` on registry
resolution goes from **4 before** (`:290`, `:300`, `:311`, `:317`) to **6 after**
(those four, plus the converted absent- and symlinked-snapshot tests). State both
numbers from a count of the actual tests rather than asserting "no loss"; the
deleted test (`:241`) and the new repo-local test are not fail-closed tests and
do not enter either figure.

## Step 7 — spec

**The PRD's spec line references are stale.** It names `quality-guidelines.md`
`:295`, `:318-319`, `:835-838`, taken at 0.67.1. The live claims are:

- `:1167` — "it does not silently fall back to the AST parser"
- `:1193-1194` — "Consumer tests pin snapshot-preferred resolution matching the
  AST fallback, absent- and symlinked-snapshot fallback"
- `:1737-1745` — the long paragraph describing snapshot-preferred resolution
  "falling back to a static AST parse of `installer/registry.py` only when the
  snapshot is absent or crosses a symlink boundary"

Rewrite all three to describe snapshot-only resolution, the first-party
requirement, the repo-local empty registry, and the symlink refusal as an error.

**G7 — no surviving claim of an AST fallback.**

```bash
grep -n 'AST parse\|AST fallback\|AST parser\|falls back to.*AST' \
  .trellis/spec/backend/quality-guidelines.md
```

Pass: no match describing consumer registry resolution. Grep the whole file, not
the diff — the spec criterion says so explicitly, and the last two runs in this task
family both had a grep scoped from memory miss a live claim.

## Step 8 — full gates

**G8 — `make check` exits 0.** Do not export
`SD_AI_COMMAND_PACK_FULL_CHECK_RELEASE_BASE_REF` into this run: in the sd-twin
task it leaked into tests that build throwaway repositories and produced three
false failures.

Version bump and dated CHANGELOG heading: `templates/**` is shipped payload, so
the release gate requires both.

## Step 9 — falsifiability

**G9 — the new tests fail without the change.**

```bash
git checkout $BASE -- templates/skills/se-review-skills/scripts/skill_review.py
.venv/bin/python -m pytest tests/test_skill_review.py -q   # must FAIL
git checkout HEAD -- templates/skills/se-review-skills/scripts/skill_review.py
```

Pass: the converted fail-closed tests fail against the old consumer. A test that
passes both with and without the change is testing nothing. Only after the branch
is committed.

## Step 10 — ship

PR against `platypeeps/se-ai-command-pack` — same repository, inside the
autonomous run-level authority; no upstream approval is involved. Request Copilot
review, verify each finding against the code before acting, rebut with evidence
rather than complying when wrong.

Then `disposition.md` and archive, following
`08-04-audit-registry-snapshot-sd-twin/disposition.md`.

## Rollback points

- **R0** — before Step 3: only the loader and caller changed; revert the two
  edits and the fallback is back.
- **R1** — after Step 3: revert the commit. Nothing else depends on it; the
  producers on both packs are unaffected.
- **R2** — after merge: revert the merge commit. No migration, no persisted
  state.

## Validation summary

| Gate | Command | Pass condition |
| --- | --- | --- |
| G0 | inventory on a throwaway repo, before the edit | exit 0, `repo-local`, empty `familyOrder`, `Uncategorized` |
| G1 | grep the removal surface | no matches; `_crosses_symlink` still has 3 sites |
| G1b | `git diff --name-only $BASE` + protected-symbol grep | `boundary clean`, `protected symbols untouched` |
| G2 | re-run G0's command after the edit | fields identical to the G0 capture |
| G3 | pack manifest, no snapshot | nonzero, `ships no registry snapshot` |
| G4 | symlinked snapshot path | nonzero, `refusing to follow symlinked`, target not opened; control arm succeeds |
| G5 | message assertions | the two texts differ, asserted individually |
| G6 | `pytest tests/test_skill_review.py` | green; fail-closed count stated before and after |
| G7 | grep `quality-guidelines.md` whole file | no surviving AST-fallback claim |
| G8 | `make check` | exit 0, no base-ref env exported |
| G9 | restore consumer from `BASE` | converted tests fail |
