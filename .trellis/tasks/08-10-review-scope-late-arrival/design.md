# Design — close the `pack.review-scope` late-arrival gap for mixed diffs

All work lands in **platypeeps/sd-ai-command-pack**. Nothing in this repository
changes except this task directory and the spec section named in acceptance
criterion 2. Upstream head at planning time: `c9405f0d` on `main`.

## Boundaries: what changes and what deliberately does not

| Surface | Change |
| --- | --- |
| `templates/scripts/sd-ai-command-pack-pr-body-scope.py` | Behavior change in `prepare_tooling_body`, plus new section constant and cap |
| `templates/scripts/sd-ai-command-pack-review-scope.sh` | **No change** |
| `templates/scripts/sd-ai-command-pack-review.py` | **No change** |
| `tests/test_pr_body_scope.py` | New cases |
| `templates/.agents/skills/sd-create-pr/SKILL.md` | Exit-contract prose |
| `templates/docs/SD_AI_COMMAND_PACK.md` | Exit-contract prose |
| Generated mirrors, `manifest.json`, `CHANGELOG.md`, fleet ledger | Release bookkeeping |

The gate itself is untouched, and that is the load-bearing decision. Two facts
make it possible:

1. `github_pr_body_mentions_scope`
   (`templates/scripts/sd-ai-command-pack-review-scope.sh:196-200`) tests for
   **heading presence only**. It never checks that declared paths correspond to
   the paths that triggered it. A heading written at PR creation therefore
   satisfies the gate at the Stage 2b finalization head.
2. The caller already routes exit `0` into a body write
   (`templates/.agents/skills/sd-create-pr/SKILL.md:331-344`: `0)` runs
   `gh pr edit --body-file`, `3)` is a documented no-op, anything else is fatal).

So moving the mixed case from `3` to `0` makes the existing, unmodified caller
do exactly the right thing. No new network call, no new stage, no skill logic.

### Why the preparer refuses today

`prepare_tooling_body` is not being lazy. Its section constant asserts
`"Changes are limited to generated or repository-bookkeeping surfaces."`
(`:72-76`). On a mixed diff that sentence is **false**. The refusal at
`:696-706` is a truthfulness guard. Any fix must therefore change *what the
section says*, not merely when it fires — which is why "append the tooling
subset" is a text change first and a control-flow change second.

## Contract

`_tooling_only_unmatched_paths` (`:611-622`) returns **only** the unmatched
list — it does not partition. The design needs both halves, so the
implementation either computes `matched` alongside it or widens the helper to
return the pair. Prefer widening the helper: it is module-private, has one
caller, and computing the two lists in separate passes invites them to drift
apart under a later rule change.

On a non-empty changed set, with `matched` = paths matching a tooling-labeled
rule and `unmatched` = the rest:

| `matched` | `unmatched` | Status | Body |
| --- | --- | --- | --- |
| ∅ | any | `3` | unchanged |
| non-∅ | ∅ | `0` | exhaustive section (**current text, unchanged**) |
| non-∅ | non-∅ | `0` | **new** enumerating section |

Empty changed set stays `3` (`:685-691`, unchanged). Exit `1` and `2` are
untouched. Exit `3` therefore survives with a narrower, still-honest meaning:
*nothing to declare*, rather than *mixed or empty*.

The `matched = ∅` row is what keeps the preparer honest: it never writes a
heading it cannot justify from the diff.

### Why this does not weaken the gate

The obvious objection is that if the preparer now auto-writes a heading whenever
*any* tooling path is present, the gate can never fail through `sd-ship`, so an
unexplained generated change sails through. Three things answer it, and the
third is decisive:

1. **A diff with no tooling path still gets no heading** and still fails — the
   `matched = ∅` row above, covered by test case 2.
2. **The enumeration is strictly more informative than what it replaces.** The
   status quo on a mixed diff is: write nothing, fail at the finalization head,
   and have a human paste a canned sentence that names no paths at all. The new
   section names the exact generated paths in the body, where a reviewer sees
   them.
3. **A human-authored PR body is never auto-prepared.**
   `templates/docs/SD_AI_COMMAND_PACK.md:828`: "User-provided bodies never enter
   this preparation mode and remain byte-for-byte subject to the existing
   validator." Auto-preparation applies only to the no-custom-body path, where
   the alternative was GitHub's untouched auto-fill. The gate keeps full teeth
   on every body a person actually wrote.

### Residual gap, accepted knowingly

A branch whose PR-creation diff contains **zero** tooling paths, but which
acquires journal/index files at Stage 2b, is still not covered: `matched` is
empty at creation, so no heading is written, and the gate fails at the
finalization head exactly as today.

All five observed PRs (#156, #163, #172, #203, #208) carried `.trellis/tasks/**`
in the creation-time diff, which is a tooling path, so all five are covered.
Closing the residual shape would require asserting a future diff — the
"predict the category" option rejected above. This is documented rather than
fixed, and the spec update in acceptance criterion 2 must say so plainly rather
than claiming the gap is closed unconditionally.

### Section text on a mixed diff

```
Tooling/generated scope:

- Generated or repository-bookkeeping paths in this branch include:
  - `.trellis/workspace/sdelmas/index.md`
  - `.trellis/workspace/sdelmas/journal-4.md`
- Remaining changes are authored and reviewed normally.
```

Three properties, each deliberate:

- **"include:" makes no completeness claim.** The branch acquires journal and
  index files *after* this text is written, so any exhaustive phrasing would be
  false by Stage 2b. A non-exhaustive enumeration written at creation time is
  still true at the finalization head. This is the one wording constraint the
  late-arrival sequence actually imposes.
- **Paths are sorted** so the output is deterministic and testable.
- **The list is capped** at `MAX_ENUMERATED_SCOPE_PATHS = 20`, with overflow
  reported explicitly as a final bullet — `- ...and 7 more generated or
  repository-bookkeeping paths.` — never truncated silently. A PR body has a
  65536-character ceiling and a generated-surface refresh can touch hundreds of
  paths.

Paths are rendered inside backticks. They come from the branch diff, so they are
repository-relative and already normalized by `_matches_normalized_pattern`'s
caller; no path is echoed from an untrusted network source.

The heading matches the gate's regex: `Tooling/generated scope:` at line start
satisfies `^[[:space:]>#*\-]*(Tooling/generated scope)(:.*|[[:space:]]*)$`, and
the same heading is what `_body_has_heading` already recognizes, so the existing
idempotency guard at `:714-723` keeps a second run from double-appending.

## Compatibility

Backward compatible for every caller, because the only transition is
`3 → 0` on a case where the body was previously left unchanged. A caller that
treated `3` as a no-op now receives `0` and a modified body file — which is the
intended outcome and the path `sd-create-pr` already implements.

The reverse risk — a caller that treats `0` as "the whole diff was tooling" —
does not exist: `grep -rn -- '--prepare-tooling-body' templates/ docs/` returns
exactly the skill and the doc page, and neither infers diff composition from the
status. Both nonetheless state the old contract in prose and are updated in the
same change, per acceptance criterion 4.

## Failure modes

| Mode | Handling |
| --- | --- |
| Diff has hundreds of tooling paths | Capped at 20 with an explicit remainder count |
| Diff has no tooling path | Exit `3`, body untouched — gate still fails as intended |
| Body already carries a heading | Existing `_body_has_heading` guard returns `0`, no write |
| Body file unreadable / non-UTF-8 / non-regular | Existing `_load_regular_utf8_file` errors, exit `2` |
| Write interrupted | Existing `_atomic_write_body` mkstemp + `os.replace`, mode preserved |
| Section becomes non-exhaustive as branch grows | By design; "include:" wording stays true |

## Rollout and rollback

Ships as one upstream PR against `platypeeps/sd-ai-command-pack`, cut from
`origin/main` in an **isolated `git worktree`** so the shared clone at
`~/repos/platypeeps/sd-ai-command-pack` — which other sessions use — is never
touched. That isolation is precedent from
`08-10-review-check-cache-pr-body/disposition.md`.

Rollback is reverting that PR. No migration, no persisted state, no schema. The
change is confined to text a script writes into a PR body.

This repository consumes the fix through the ordinary fleet-refresh lane, which
existing `sd-fleet-refresh` surfaces already own. Per the same precedent, that
refresh is **not** tracked as a follow-up task here.

## Release bookkeeping this repository does not get to skip

Upstream gates make these mandatory, not optional polish:

- `templates/**` is the authored source; `scripts/`, `plugins/sd/bin/`, and
  `plugins/sd/machine-payload/scripts/` are byte-identical mirrors regenerated
  by `make generate` and `make sync`. `run_pack_source_drift_gates`
  (`scripts/sd-ai-command-pack-full-check.sh:611`) fails on drift, and CI job
  `release-payload-gate` re-runs it against the PR base.
- Editing a file under both `templates/` and `plugins/` always trips the version
  gate (`:755-805`), so `manifest.json` `version` must be bumped and
  `CHANGELOG.md` must gain a matching `## <version> - YYYY-MM-DD` heading.
- A version bump requires an all-pass `docs/fleet/candidate-validation.json`
  matching the exact payload; the `.githooks/pre-push` ledger gate enforces it.
- `check-shipped-script-coverage.sh:47` holds `pr-body-scope.py` to a **78%**
  per-file floor.
