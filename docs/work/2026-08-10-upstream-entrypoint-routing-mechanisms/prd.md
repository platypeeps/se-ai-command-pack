---
title: Upstream canonical-entry-point mechanisms (pack installer + Trellis injected routing) — both deliverables relayed
status: planning
created: 2026-08-10
---
# Upstream canonical-entry-point mechanisms

**FULLY RELAYED 2026-08-20.** Deliverable 1 is filed upstream as
`platypeeps/sd-ai-command-pack#486` (2026-08-16), including the consumer-guard
question it must answer and the rejected shadowing alternative. **Deliverable 2
is filed as a pull request against the fork the fleet consumes:
sdelmas/Trellis#6** (`feat/declared-entry-point-seam-fork` → `sdelmas:main`,
2026-08-20, rebased over the fork's divergence; full CLI suite 1874 passed).
It was first opened upstream as mindfold-ai/Trellis#566 with explicit per-PR
approval (interactive maintainer selection "Draft full PR" against this
task), then withdrawn the same day when the maintainer retargeted the relays
at the fork. The PR implements the declared-entry-point seam:
an installed pack may write `.trellis/entry-points.json` [absent: written by an installed pack at runtime; not present in this repository] (schemaVersion 1,
keys `start`/`continue`/`finish-work`/`update-spec`, strictly validated
all-or-nothing), consulted both at init/update write chokepoints (riding the
`replacePythonCommandLiterals` transform points, so template hash tracking
stays consistent) and at runtime by the dynamic emitters enumerated below;
every path falls back to today's literals when nothing is declared.

Still not actionable from `se-ai-command-pack`: both deliverables edit vendored
files that a refresh reverts.

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
- Deliverable 1 is relayed as an upstream issue (`platypeeps/sd-ai-command-pack#486`),
  not a pull request.
  Deliverable 2 is relayed as sdelmas/Trellis#6 (originally
  mindfold-ai/Trellis#566, withdrawn on retarget), opened with the explicit
  per-PR approval recorded above.
- Behavior in a repository with no SD pack installed must not change.

## Acceptance Criteria

- [ ] A `sd-ai-command-pack` PR adds the `AGENTS.md` managed-block row and its
      generated content, with the consumer-guard decision recorded.
- [x] A Trellis PR adds the declared-entry-point seam, with the emitters above
      consulting it and falling back when undeclared.
      (sdelmas/Trellis#6, merged 2026-08-20 as fork release 0.6.16-sd.8;
      upstream mindfold-ai/Trellis#566 withdrawn on retarget. Delivered here
      at the 0.6.16-sd.8 vendored-runtime refresh: the runtime loaders —
      `.trellis/scripts/common/entry_points.py`, the shared session-start and
      inject-workflow-state hooks, `.opencode/lib/session-utils.js` — now
      consult `.trellis/entry-points.json` [absent: written by an installed pack at runtime; not present in this repository] with all-or-nothing validation and
      fall back when undeclared.)
- [ ] After both land and this repository refreshes, its hand-written
      `AGENTS.md` section is replaced by the installed block and
      `tests/test_agent_routing.py` still passes against it.

## Notes

- Audit finding: A-005 (P3/S) — `.trellis/audit/report-2026-07-25.md:46`.
- Predecessor: `07-25-audit-workflow-entrypoint-routing`, whose PRD carries the
  measured divergence and the ownership reasoning.
- `blockedOn`: Deliverable 2 is done — sdelmas/Trellis#6 merged 2026-08-20
  (fork release 0.6.16-sd.8) and this repository refreshed to sd.8 the same
  day, so the seam's runtime loaders are installed here. Deliverable 1 still
  waits on triage of `platypeeps/sd-ai-command-pack#486` (relayed
  2026-08-16): the `AGENTS.md` managed-block row, its generated content, and
  the consumer-guard decision. The final acceptance criterion (hand-written
  `AGENTS.md` section replaced by the installed block,
  `tests/test_agent_routing.py` still green) closes only after that pack
  change ships and this repository refreshes to it. Nothing is actionable
  here until then; the autonomous work loop must not select this task.
