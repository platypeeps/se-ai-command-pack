# Review the Gemini and Codex Retirements Design

## Overview

The task began as "react to two upstream retirements." The R1/R3 inventory
(`research/inventory-2026-08-26.md`) established that this repository has
almost no exposure: its pack never targeted the gemini CLI, and its codex
surface is the CLI, which is unaffected. The remaining deliverable is
therefore documentary, not mechanical — record the finding where the next
reader will hit it, and route the one genuine decision to the repository that
owns it.

## Proposal

Three changes, all documentation or task records.

1. **Land the inventory** as a task research artifact. It is the written
   inventory acceptance criterion and the evidence base for D1-D5.

2. **Add a short note to `CONTRIBUTING.md`** in the vendored-ownership area,
   stating that `.gemini/**` is Trellis-vendored and that this pack ships no
   gemini platform. Placed next to the existing ownership table at line 45,
   which is where a reader forms the wrong impression today. The note must
   name the two real owners so a future investigator routes correctly instead
   of repeating this inventory.

3. **File one follow-up Trellis task** carrying the genuine gemini decision
   (retarget to `agy` / sunset / drop) to `platypeeps/sd-ai-command-pack`,
   which actually ships gemini adapters. That task inherits the deadline that
   matters: the `gemini-cli` formula is disabled 2026-12-18.

## Boundaries And Non-Goals

- **No `.gemini/**` edits.** Vendored Trellis; a local edit is reverted by the
  next `trellis update` and would fail `release-payload-gate` in the meantime.
- **No registry, manifest, or generated-surface change.** There is no gemini
  row to remove; `make generate` output is unaffected.
- **No workflow edits.** The `sd-review.yml` / `ai-review-router.yml` gemini
  references are the Gemini API as a model provider (D5).
- **No `tests/test_skill_review.py` edits.** Its gemini rows are a synthetic
  fixture (D5).
- **No `.codex/config.toml` edit.** Its desktop-app mention is a deliberate
  compatibility warning (D3).
- **No work inside `sd-ai-command-pack` this iteration.** That is a different
  repository and outside this run's repo-local authority; it is relayed as a
  task, not executed here.

## Affected Files

| File | Change | Ownership |
|---|---|---|
| `.trellis/tasks/08-23-.../research/inventory-2026-08-26.md` | new | repo-own task record |
| `.trellis/tasks/08-23-.../prd.md` | decisions appended | repo-own task record |
| `.trellis/tasks/08-23-.../design.md`, `implement.md` | new | repo-own task record |
| `CONTRIBUTING.md` | short note near the ownership table | repo-own |
| new Trellis task dir | new | repo-own task record |

No generated or vendored path is touched, so `make generate` output and
`.github/trellis-provenance.json` both stay byte-identical.

## Data And Command Contracts

None changed. No CLI surface, config schema, manifest row, or registry entry
is added, removed, or renamed. `install.py`, `installer/**`, and every
platform enumeration are untouched, so existing provenance receipts stay valid
and `install.py --check` behavior is unchanged for current users.

## Risks And Edge Cases

- **Risk: the CONTRIBUTING note drifts if the pack later does add gemini.**
  Mitigated by phrasing the note as a statement about the current registry and
  pointing at `installer/registry.py` as the source of truth rather than
  restating the platform list (the repo's "one fact, one place" convention).
- **Risk: the upstream relay is forgotten and 2026-12-18 passes.** Mitigated by
  filing it as a real Trellis task with the date in its PRD, not as a comment.
- **Edge case: `CONTRIBUTING.md` is repo-own, not vendored.** Confirmed — the
  vendored table at line 45 lists platform payload dirs, and CONTRIBUTING.md
  itself is not among them. Editing it is in bounds.
- **Non-risk, stated explicitly:** dropping gemini would break no test in this
  repo, because no test asserts a real gemini surface. This is recorded so a
  future reader does not mistake test silence for absence of coverage.

## Validation

- `make check` (test + lint + lock-check + release-check + shell-syntax +
  trellis-provenance) must pass unchanged. The provenance gate is the decisive
  one: it proves no vendored payload moved.
- `git diff --stat` must show changes only under
  `.trellis/tasks/**` and `CONTRIBUTING.md`.
- `python3 .github/scripts/check-trellis-provenance.py` must report no
  `uncovered:` or `drifted:` paths.
