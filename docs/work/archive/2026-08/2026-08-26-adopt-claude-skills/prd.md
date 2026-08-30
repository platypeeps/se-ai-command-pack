---
title: Adopt the claude-skills library as pack-product inspiration
status: done
created: 2026-08-26
branch: feat/adopt-claude-skills
---
# Adopt the Shearerbeard claude-skills library as pack-product inspiration

## Goal

Enrich the `se-ai-command-pack` product with the durable ideas from
`Shearerbeard/claude-skills` (@ `0e4fb48`) and the `opencode-cfg` agent roster:
re-authored `se-*` skills and agents in `templates/skills/` and
`templates/agents/`, shipped to the whole fleet through the normal registry
and generator pipeline — plus a Vale prose gate and a lightweight upstream
inspiration watch.

## Mode: inspiration, not import

Decided 2026-08-26 after a full conflict review. Upstream content is
**rewritten to match this repository's conventions**, never copied verbatim.
Consequences:

- The `se-` prefix guard (`installer/registry.py:682`) is satisfied, not
  fought: every adopted skill is renamed `se-<upstream-name>`.
- Every file is editable. Routing tables point at this pack's lanes
  (`sd-review`, `trellis-check`, sibling `se-*` skills), never at upstream
  skills that were not adopted.
- No verbatim third-party redistribution: re-authored content under the
  pack's own license posture, with an inspiration credit. The earlier
  licensing constraint dissolves.
- The digest drift checker planned for import mode is unnecessary. Upstream
  tracking shrinks to a pinned SHA and a harvest ritual (see the
  inspiration-watch child).

## Sources

- `Shearerbeard/claude-skills` @ `0e4fb48ed69d665fd1307a51cb126af915c6502b`,
  local checkout under `~/repos/ai/`. 22 skills; active upstream.
- `opencode-cfg` local receipt `b37c6ec` (no license, no remote; its
  `opencode.json` holds private Tailscale hostnames — never public, C4).
  Design source for the rust agent trio only.

Evidence: [`research/upstream-inventory-2026-08-26.md`](research/upstream-inventory-2026-08-26.md).

## Requirements

- R1. Author 13 `se-*` skills in `templates/skills/`, registered in
  `installer/registry.py`, regenerated through
  `generate-skill-surfaces.py`: the five `se-rust-*` skills plus the
  `se-typed-holes` companion discipline, `se-gate-probes`, `se-docs-bustest`,
  `se-rebase-hygiene`, `se-skill-retro`, `se-prose-lint`, `se-humanizer`,
  `se-adr-review`. Child: `08-26-author-se-skills`.
- R2. Author the rust agent trio (`se-rust-write`, `se-rust-fill`,
  `se-rust-reviewer`) in `templates/agents/`, encoding the
  skeleton→fill→review workflow with the deny-by-default posture
  re-expressed per platform. Child: `08-26-author-se-rust-agents`.
- R3. Introduce Vale as the deterministic prose gate for the skill product
  and top-level docs (advisory first, then `make check`). Vale 3.18.0 is
  installed locally. Child: `08-26-introduce-vale-prose-gate`.
- R4. Fold non-skill-shaped content into existing surfaces:
  `plan-discipline` probes into Trellis planning guidance;
  `python-review`/`python-quality` probes (minus the click/pytest mandates
  that contradict this repo's argparse/unittest code) into
  `.prism/rules.json`. Child: `08-26-fold-inspiration-checklists`.
- R5. Record the upstream pin, the inspiration map (which upstream skill
  informed which `se-*` skill), and the non-adoption list with reasons, and
  define the recurring harvest ritual. Child:
  `08-26-upstream-inspiration-watch`.

## Non-adoptions (recorded so refreshes do not re-litigate)

| Upstream | Reason |
| --- | --- |
| `mermaid` | Depends on `mermaid-view` from the author's dotfiles; arrives broken. |
| `git-commit` | Forbids the `Co-authored-by`/`Generated-with` trailers this user's convention mandates; demands per-commit approval the SD standing authority waives. |
| `codex-cli`, `opencode-cli`, `collaborating-with-antigravity` | Route reviews to external CLIs; `sd-review` forbids direct reviewer fallbacks and no review-tooling document binds lanes. Revisit only after such a document exists. |
| `adr-review` as import | Superseded — re-authored as `se-adr-review`, review-process-specific (fleet repos will carry ADRs). |
| `skill-retro`, `process-feedback` as imports | Function survives merged into `se-skill-retro`, routed to this ecosystem's surfaces. |
| `prose-lint`, `python-quality` as imports | Vale-coupled / toolchain-conflicting; both survive re-authored or folded with the conflicts edited out. |
| `plan-discipline` as a skill | Competes with Trellis planning; folded as checklist input (R4). |
| `codebase-design`, `prose-corpus`, `vale-lsp`, `haskell-lsp` | Not skills or not shipped upstream. |
| Agents `frontier-reviewer`, `prose-write`, `python-write`, `python-reviewer` | Deferred; review agents compete with the sd-review lane. Revisit on demonstrated gap. |

The abandoned user-scope install of upstream originals (deleted child) is
superseded: the pack's own install pipeline delivers the re-authored `se-*`
skills to user scope everywhere.

## Constraints

- C1. **Product quality bar.** New skills go through the same pipeline as the
  existing 55: registry row with family, canonical frontmatter, generator
  validation, `make check` green. A new skill family for engineering work
  (recommended: `engineer`) is a deliberate registry change, decided in the
  authoring child's design.
- C2. **Do not disturb PR #273** (receipt pinned to `bb5ea2c`). This work
  stays on `feat/adopt-claude-skills`.
- C3. **Trellis payload untouched** (`.gemini/**`, `.codex/**`, vendored
  `trellis-*` files).
- C4. **`opencode-cfg` stays private** (Tailscale hostnames in its config).
- C5. **Conflict findings from the 2026-08-26 review are binding on the
  rewrites**: `se-gate-probes` must not claim "review this diff" (sd-review's
  turf) and routes only to shipped lanes; `se-prose-lint`/`se-humanizer`
  degrade gracefully where Vale is absent; nothing mandates click/pytest;
  nothing demands per-commit user approval inside SD workflows.

## Acceptance Criteria

- [x] AC1. 13 new `se-*` skills exist in `templates/skills/`, registered, and
      `generate-skill-surfaces.py --check` passes; catalog and manifest
      regenerate cleanly.
- [x] AC2. The rust agent trio ships from `templates/agents/` with no foreign
      model pin and the workflow contract stated in each file.
- [x] AC3. `make prose-lint` runs Vale over `templates/skills/` and top-level
      docs; promotion into `make check`/CI is done, or recorded as a follow-up
      with the blocking finding count (per the vale child's AC4).
- [x] AC4. `.prism/rules.json` carries the folded python probes; the Trellis
      planning guidance carries the plan-discipline checklist; neither
      contradicts repo conventions.
- [x] AC5. A tracked inspiration pin records the upstream SHA, the
      inspiration map, and the non-adoption table above; the harvest ritual
      is documented and produces a reviewable report.
- [x] AC6. No re-authored skill or agent references an upstream skill that
      was not adopted (no dangling routes) — checked by grep over
      `templates/` for the non-adopted names.
- [x] AC7. `make check` green over the whole outcome.

Merge, branch deletion, and default-branch synchronization are the
post-archive handoff, not acceptance criteria.

## Children

- `08-26-author-se-skills` — R1; AC1, AC6.
- `08-26-author-se-rust-agents` — R2; AC2.
- `08-26-introduce-vale-prose-gate` — R3; AC3.
- `08-26-fold-inspiration-checklists` — R4; AC4.
- `08-26-upstream-inspiration-watch` — R5; AC5.

Ordering: vale gate before or with the skill authoring (the prose gate should
see the new skills; the new `se-prose-lint` skill assumes the gate exists).
Authoring before inspiration-watch (the map records what was authored).
Fold child independent. Agents child independent of all but benefits from
`se-rust-*` skills existing first.

## References

Research notes that lived beside this item's Trellis record and were not carried
into docs/work. Recover the bodies from git history under `.trellis/tasks/archive/2026-08/08-26-adopt-claude-skills`:

- research/upstream-inventory-2026-08-26.md
