---
title: Author wave-1 SE worker agents
status: done
created: 2026-07-25
branch: task/07-25-worker-agents
---
# Author wave-1 SE worker agents

Parent: `.trellis/tasks/07-25-agent-artifacts` (Tier 2 content). Settled inputs: parent
`design.md` section 1 and `research/cross-platform-agent-support.md`.

## Goal

Ship the first named SE worker agents — se-source-reader (bounded read-only source
consumption returning a structured extract) and se-claim-verifier (adversarial refuter for
a single claim) — and wire skills to them through the RuntimeProfile delegation schema.

## Requirements

- R1: Canonical agents authored as neutral MD + frontmatter under the format established
  by 07-25-agent-artifact-kind; bodies pass the neutrality lint.
- R2: se-source-reader: input = one source + extraction brief; output = structured extract
  with provenance; no writes, no recursive spawning, no scope expansion.
- R3: se-claim-verifier: input = one claim + evidence set; output = verdict
  (supported/refuted/uncertain) with cited reasons; prompted to REFUTE by default.
- R4: RuntimeProfile layer extended with the delegation mapping from runtime-routing.md
  (`delegation: none|optional|required`, role references) for the pilot skills; dispatch
  sections reference roles as an OPTIONAL enhancement over host built-in agents.
- R5: Dispatch prompts open with an explicit context line (class-2 platforms get no hook
  injection); document in the agent bodies.
- R6: Governance invariants encoded in agent bodies: bounded authority, concurrency cap
  set by parent, parent owns the final report.

## Acceptance Criteria

- [x] Both agents render to Claude MD and Codex TOML and install/remove cleanly.
- [x] Pilot skills (se-research, se-fact-check) reference the roles without requiring
      them; inline platforms unaffected.
- [x] Registry/profile validation covers the delegation mapping; tests extended.
- [x] Version bump + changelog; operator docs list the new agents.

## Dependencies / order

- BLOCKED by 07-25-agent-artifact-kind (plumbing must exist).
- Coordinates with 07-25-dispatch-pilot (role references land where dispatch sections
  already exist).

## Notes

- Complex task: needs `design.md` + `implement.md` before start.

## References

Research notes that lived beside this item's Trellis record and were not carried
into docs/work. Recover the bodies from git history under `.trellis/tasks/archive/2026-08/07-25-worker-agents`:

- research/agent-artifact-format.md
- research/agent-rendering.md
- research/install-remove-and-tests.md
- research/registry-delegation.md
- research/skill-role-references.md
