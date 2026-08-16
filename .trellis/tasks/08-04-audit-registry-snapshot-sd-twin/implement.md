# Implement: SD pack registry-snapshot producer

Ordered steps with gates. Every gate is a command with a stated pass condition,
named before it runs.

## Step 0 — isolate

```bash
cd ~/repos/platypeeps/sd-ai-command-pack   # shared clone; do not work in it
git fetch origin
WT="$(mktemp -d)/sd-snapshot"
git worktree add "$WT" -b feat/registry-snapshot-producer origin/main
cd "$WT"
BASE="$(git rev-parse origin/main)"
```

The shared clone is in use by other sessions: never check out, reset, or branch
in it. Record `BASE` — the falsifiability gate restores from it.

**Commit before any destructive verification.** In the 2026-08-16 late-arrival
run a `git checkout $BASE -- <files>` on a branch with no commits made
`HEAD == BASE` and destroyed the uncommitted implementation. Commit first.

## Step 1 — producer

In `.github/scripts/generate-command-surfaces.py`:

1. Add `REGISTRY_SNAPSHOT_PATH = "generated/registry-snapshot.json"` and
   `REGISTRY_SNAPSHOT_SCHEMA_VERSION = 1`, with the SE comment carried over:
   bump only alongside the consumer's
   `SUPPORTED_REGISTRY_SNAPSHOT_SCHEMA_VERSIONS`.
2. Add `generate_registry_snapshot_text()` mirroring
   `generate-skill-surfaces.py:1115`, deriving from the **imported** objects.
   All four are already imported at `generate-command-surfaces.py:66-87`:
   `COMMAND_FAMILIES`, `COMMAND_REGISTRY`, `PLATFORM_REGISTRY` and
   `SHARED_SKILL_REFERENCES`. An earlier draft of this step claimed only two
   were present and told the implementer to add the other two; that was wrong
   and the import block needs no change. Corrected 2026-08-16 against the file
   rather than left to mislead a later reader.
   - `familyOrder`: `[f.id for f in COMMAND_FAMILIES]` — 5 entries
   - `skills`: `[{"name": c.name, "family": c.family} for c in COMMAND_REGISTRY]`
   - `platforms`: `sorted(PLATFORM_REGISTRY)`
   - `sharedReferences`: `{k: list(v) for k, v in SHARED_SKILL_REFERENCES.items()}`
   - return `json.dumps(payload, indent=2) + "\n"`
   Docstring must record why `familyOrder`/`sharedReferences` come from
   `COMMAND_FAMILIES`/`SHARED_SKILL_REFERENCES` rather than matching the AST's
   empty result: `_parse_registry` reads the SE names and is blind to SD's, and
   this file becomes the only registry source once the AST path is removed.
3. Register it in `generate_surfaces()`:
   `outputs[REGISTRY_SNAPSHOT_PATH] = generate_registry_snapshot_text()`.

Do **not** add a separate write path or `--check` branch. The existing
`write_surfaces` / `run_check` pair covers it.

## Step 2 — payload gate

In `.github/scripts/prepare-release.py`, add
`"generated/registry-snapshot.json"` to `PAYLOAD_SINGLETONS`. Singleton, not a
`generated/` prefix — see `design.md`.

## Step 3 — generate and commit

```bash
python3 .github/scripts/generate-command-surfaces.py
git add -A && git commit -m "feat(registry): ship the generated registry snapshot"
```

**G1 — the snapshot exists and matches the schema.** Pass: five keys,
`schemaVersion == 1`, 20 skills, 18 platforms, 5 `familyOrder` entries, 4
`sharedReferences` entries.

## Step 4 — parity against the real consumer

The decisive gate. Run the actual `skill_review.py` from the SE checkout against
this SD worktree and compare both derivations field by field.

**G2a — the three AST-derivable fields agree exactly.** Pass: `families`,
`skill_order`, and `platforms` equal between the snapshot-derived and
`_parse_registry`-derived `RegistryData`. Any inequality means the producer is
wrong; a snapshot that parses but disagrees is worse than no snapshot, because
it fails closed instead of falling back.

**G2b — the two AST-blind fields match the imported objects.** Pass:
`family_order == tuple(f.id for f in COMMAND_FAMILIES)` (5 entries) and
`shared_references == SHARED_SKILL_REFERENCES` (4 entries). Deliberately *not*
compared against the AST, which yields empty for both because it reads the SE
symbol names. Asserting parity here would accept empty and discard real data —
see `design.md`.

**G3 — the consumer actually resolves the snapshot.** Criterion 3 requires
proving `_parse_registry` is **not called**, which "it still works" does not
show. Import `skill_review` and monkeypatch `_parse_registry` to raise, then run
the inventory against the SD worktree. Pass: the run succeeds, proving the
snapshot path was taken. Then delete the monkeypatch, move the snapshot aside,
and confirm the run still succeeds via the fallback — establishing both arms
rather than only the one being shipped.

Also run `skill_review.py inventory --root "$WT" --scope package --installed
off` unpatched and confirm `status: success` with `selectedSkills: 20`, matching
the pre-change baseline measured on 2026-08-16.

Evidence from a run, not from reading the code.

## Step 5 — drift and determinism

**G4 — `--check` fails on induced drift.** Edit a `CommandInfo.family` in
`installer/registry.py`, run
`python3 .github/scripts/generate-command-surfaces.py --check`, confirm nonzero
exit naming the snapshot path, then restore. Restore via
`git checkout -- installer/registry.py` and confirm `--check` returns 0 again.

**Clear `__pycache__` as part of the restore, and restore every file the
tampered run wrote — not just the tampered source.** Both bit this run:

- A reorder of two `CommandInfo` lines leaves the file *size* unchanged, and the
  restore landed in the same wall-clock second as the tampered compile, so
  `installer/__pycache__/registry.cpython-314.pyc` passed Python's mtime+size
  validation. The generator kept importing the tampered registry from a clean
  tree. `find . -name __pycache__ -type d -exec rm -rf {} +` before re-checking.
- A write-mode generator run under the tampered registry rewrites
  `manifest.json` and the sd-help command catalog too. `git checkout -- .`, not
  `git checkout -- installer/registry.py`.

Without both, `--check` reports drift on a tree that `git status` calls clean,
which reads as generator nondeterminism and is not.

**G5 — byte-identical regeneration.** Run the generator twice on an unchanged
registry; `git status --porcelain` must be empty the second time.

## Step 6 — release-gate proof

**G6 — the payload gate refuses an unbumped snapshot change.** Induce a snapshot
change without a version bump and confirm `prepare-release.py` fails naming the
snapshot path. Then bump `manifest.json`, add the dated CHANGELOG heading, and
confirm it passes. Criterion 7 requires the induced demonstration, not a reading
of the gate.

Remember SD's plugin manifest must match (`_validate_plugin_version`), so bump
`plugins/sd/.claude-plugin/plugin.json` too.

## Step 7 — full gates

**G7 — `make test` and `make check` exit 0.** Regenerate mirrors first if the
repo requires it (`make sync` before `make generate`, in that order — reversing
them fails with `mirror.stale`), and revalidate the fleet candidate ledger after
the version bump.

## Step 7b — boundary check on this repository

**G7b — only `.trellis/` changed here.** Acceptance criterion 8 bounds this
repository's diff, and nothing else in this plan enforces it. In
`se-ai-command-pack`:

```bash
git status --porcelain | grep -v '^.. \.trellis/' || echo "boundary clean"
```

Pass: no output other than `boundary clean`. Any other path means the task
exceeded its stated boundary and must be listed with its reason before
completion — criterion 8 requires the listing, not silent acceptance.

## Step 8 — falsifiability

**G8 — the parity test fails without the producer.** With the branch committed,
`git checkout $BASE -- .github/scripts/generate-command-surfaces.py` and remove
the snapshot; the Step 4 parity assertion must fail, and `skill_review.py` must
fall back to `_parse_registry`. Restore afterwards and re-run G2.

`git checkout <base> -- <file>`, never `git stash` — stash silently no-ops once
the change is committed and the test reports a pass that never ran.

## Step 9 — ship

Open the PR against `platypeeps/sd-ai-command-pack` under the approval recorded
in `prd.md`. The branch diff mixes authored code with generated payload, so let
`--prepare-tooling-body` declare the generated subset; from 0.71.23 it handles a
mixed diff. Request Copilot review, verify each finding against the code before
acting, rebut with evidence rather than complying when wrong.

## Step 10 — close out

Write `disposition.md` following
`08-10-review-scope-late-arrival/disposition.md`: route, PR URL, branch, base
and head SHAs, each acceptance criterion ticked with quoted evidence and the
exact head it was taken at, and what this repository is left holding.

Then unblock `08-04-audit-registry-snapshot-ast-removal` — but only after the SD
PR has **merged**, since its precondition is that SD actually ships the
snapshot, not that a PR proposing it exists.

## Rollback points

- **R0** — before Step 3: nothing committed, delete the worktree.
- **R1** — after Step 3: revert the producer commit; SD has no snapshot and the
  consumer falls back exactly as before.
- **R2** — after merge: delete the snapshot and the `PAYLOAD_SINGLETONS` entry.
  Safe because this task does not remove the AST fallback; that is why the
  removal is a separate, later task.

## Validation summary

| Gate | Command | Pass condition |
| --- | --- | --- |
| G1 | inspect the snapshot | 5 keys, v1, 20 skills, 18 platforms, 5 families, 4 shared refs |
| G2a | parity harness | `families`, `skill_order`, `platforms` equal to AST |
| G2b | parity harness | `family_order` / `shared_references` equal to imported objects |
| G3 | `_parse_registry` patched to raise | inventory still succeeds; 20 skills unpatched |
| G4 | `--check` on induced drift | nonzero, names the snapshot |
| G5 | generate twice | clean tree on the second run |
| G6 | `prepare-release.py` | fails unbumped, passes bumped |
| G7 | `make test` / `make check` | exit 0 |
| G7b | `git status` in this repo | only `.trellis/` paths |
| G8 | restore from `BASE` | parity fails, fallback engages |
