# Upstream canonical-entry-point mechanisms

**PARKED — blocked on upstream PR approval in two repositories.** Nothing here
is actionable from `se-ai-command-pack`; both deliverables edit vendored files
that a refresh reverts.

## Goal

Close the two halves of audit finding A-005 that `07-25-audit-workflow-entrypoint-routing`
could not: make the canonical-entry-point rule travel to every consumer of the
SD pack, and stop Trellis itself from routing agents to the wrapped path.

## Background

`07-25-audit-workflow-entrypoint-routing` (merged) added a repo-own routing
section to this repository's `AGENTS.md` plus `tests/test_agent_routing.py`,
which derives the wrapped-workflow set from `.agents/skills/` and fails when
the section drifts. That fixes one document in one repository. It does not
reach other consumers, and it does not silence the routing Trellis emits on its
own.

## Deliverable 1 — `sd-ai-command-pack` installer (blocked on upstream PR)

Ship the routing section as an installed managed block instead of a per-repo
hand edit, mirroring the pack's only existing `kind: "managed-block"` row
(`.github/copilot-instructions.md`): a manifest row targeting `AGENTS.md` with
an `SD-AI-COMMAND-PACK:ROUTING:START/END` marker pair, written below the
Trellis block. The alternative the audit named — suppressing or shadowing the
duplicated `trellis:*` command surface at install time — is the same
deliverable's rejected option: it deletes files `trellis update` rewrites, so
it fights the other installer rather than composing with it.

The consumer-side guard is the open question this task must answer: the
derivation in `tests/test_agent_routing.py` reads `.agents/skills/`, which
exists in a consumer, but consumers have no obligation to run this repository's
test suite. Decide whether the block ships with a pack-owned checker or stays
documentation-only.

## Deliverable 2 — Trellis injected routing (blocked on upstream PR)

Trellis routes agents to the wrapped path from files no consumer can edit.
Enumerated at `e0a3afd`, all classifying `vendored-trellis`:

- `.trellis/workflow.md:227`, `:238` — `Flow: ... -> /trellis:finish-work`;
  `:260` — the completed-state next action; `:581` — Phase 3.3 routes to
  `trellis-update-spec`.
- `.gemini/hooks/session-start.py:368` and `.opencode/lib/session-utils.js:68`
  — `Next-Action: Run /trellis:finish-work`.
- `.github/copilot/hooks/inject-workflow-state.py:69`,
  `.codex/hooks/inject-workflow-state.py:69`,
  `.gemini/hooks/inject-workflow-state.py:69` — bootstrap notice pointing at
  the `trellis-start` skill.
- `.trellis/scripts/common/task_store.py:422` — the CLI prints
  "Use /trellis:continue or phase context to decide the next step".
- `.agents/skills/trellis-start/SKILL.md:62` and
  `.agents/skills/trellis-session-insight/SKILL.md:45` — route to
  `trellis-update-spec` by skill name, which a `/trellis:` literal search
  misses.

The ask upstream is a seam, not a rewrite: a way for an installed pack to
declare a preferred entry point per workflow that these emitters consult,
falling back to today's literals when nothing is declared.

## Requirements

- Decide Deliverable 1's consumer-guard question before opening the PR.
- One PR per upstream repository; neither may be opened without explicit
  per-PR approval.
- Behavior in a repository with no SD pack installed must not change.

## Acceptance Criteria

- [ ] A `sd-ai-command-pack` PR adds the `AGENTS.md` managed-block row and its
      generated content, with the consumer-guard decision recorded.
- [ ] A Trellis PR adds the declared-entry-point seam, with the emitters above
      consulting it and falling back when undeclared.
- [ ] After both land and this repository refreshes, its hand-written
      `AGENTS.md` section is replaced by the installed block and
      `tests/test_agent_routing.py` still passes against it.

## Notes

- Audit finding: A-005 (P3/S) — `.trellis/audit/report-2026-07-25.md:46`.
- Predecessor: `07-25-audit-workflow-entrypoint-routing`, whose PRD carries the
  measured divergence and the ownership reasoning.
- `blockedOn`: upstream PR approval in `platypeeps/sd-ai-command-pack` and
  `mindfold-ai/Trellis`. The autonomous work loop must not select this task.
