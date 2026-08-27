# Author the se- rust agent trio

Parent: [`../08-26-adopt-claude-skills/`](../08-26-adopt-claude-skills/) — R2; parent AC2.

## Goal

Ship three pack-owned agents in `templates/agents/` that encode the
type-driven Rust workflow the `opencode-cfg` roster demonstrated:
skeleton-first writing, hole-filling, and review — re-authored for this pack,
not copied.

## Roster

| Agent | Role | Contract |
| --- | --- | --- |
| `se-rust-write` | Skeleton author | Designs types and signatures first; emits compiling skeletons with `todo!()` bodies; never fills logic in the same pass. |
| `se-rust-fill` | Hole filler | Fills named `todo!()` bodies only; never changes signatures, types, or public API; refuses when the requested hole does not exist. |
| `se-rust-reviewer` | Reviewer | Reviews Rust diffs against the `se-rust-*` skill bar; findings with file:line and one verdict line; read-only. |

The trio pairs with `se-typed-holes` from the sibling skill task: the skill
teaches the workflow, the agents execute stages of it.

## Requirements

- R1. Three flat Markdown files in `templates/agents/`, matching the existing
  `se-claim-verifier.md` / `se-source-reader.md` conventions (frontmatter
  shape, tone, bounded-worker contract style).
- R2. No foreign model pin: agents inherit the session model. (Upstream pinned
  models via a local gateway; that never ships.)
- R3. The deny-by-default permission posture is re-expressed in each agent's
  own terms: `se-rust-write` and `se-rust-fill` edit only files named in
  their brief; `se-rust-reviewer` is read-only. No upstream permission JSON
  is copied — the posture lives in the agent instructions and tool grants.
- R4. Each agent states its refusal boundary (what it must not do) and its
  return contract (what the parent receives).
- R5. No reference to opencode-cfg internals, private hostnames, or upstream
  file paths (parent C4).

## Constraints

- C1. Agents ship through the same generator/install pipeline as the existing
  `templates/agents/` files; whatever surfaces derive from that directory
  regenerate cleanly.
- C2. `se-rust-reviewer` is a local lens; the sd-review lane remains the
  review authority (parent C5).
- C3. `make check` green.

## Acceptance Criteria

- [x] AC1. `templates/agents/se-rust-write.md`, `se-rust-fill.md`,
      `se-rust-reviewer.md` exist and follow the existing agent conventions.
- [x] AC2. `grep -riE 'model:|tail8432e9|nobara|fedora-cube' templates/agents/se-rust-*.md`
      shows no model pin and no private hostname.
- [x] AC3. Each file contains its workflow-stage contract, refusal boundary,
      and return contract.
- [x] AC4. Install/generate pipeline runs clean with the new files;
      `make check` green.

Lightweight-leaning task: PRD plus a short `design.md` capturing the
conversion decisions (what of the upstream posture was kept, dropped, or
re-expressed); no separate `implement.md` needed unless design reveals
pipeline work.
