---
title: Ship SE capabilities as cross-platform sub-agents
status: done
created: 2026-07-25
---
# Ship SE capabilities as cross-platform sub-agents

Status: ACCEPTED as parent task (user, 2026-07-25). Requirements R1-R7 are binding.
Delivery is decomposed into child tasks (see Task map); the parent owns the source
requirement set, cross-child acceptance criteria, and final integration review. The parent
has no direct implementation work and must not be started; start children instead.
That constraint was prose, which a candidate list cannot read, so `task.json` carried
the canonical `PARKED:` title prefix — the one machine-visible marker the backlog selector
and the status board both honor — while the last acceptance criterion stayed open. The
prefix was removed 2026-08-09 when that criterion was met (see the two-platform run
evidence below); the task then proceeds directly to archive, so no selector can pick it
up in the unparked window.

## Goal

Let SE skills delegate bounded units of work (per source, per claim, per document, per
attack lens) to sub-agents on platforms that support them, and ship the agent definitions
through the existing SE installer - without breaking platform neutrality or degrading
behavior on platforms without sub-agent support.

## Requirements

- R1 (cross-platform, settled): The design MUST incorporate the findings and recommendation
  in `research/cross-platform-agent-support.md`: canonical agents authored once as neutral
  MD + frontmatter; per-platform renderers (Claude MD, Codex TOML); NO agent artifacts for
  the Amp/`agents` anchor, which stays skills-only.
- R2 (no new layer): Agent shipping extends the existing registry -> generator -> manifest ->
  installer chain (new manifest kind `agent`); no separate install mechanism.
- R3 (graceful degradation): Every skill that gains a dispatch step MUST keep a
  capability-first inline fallback so behavior on non-dispatch platforms is unchanged in
  outcome (sequential single-context execution).
- R4 (neutrality preserved): Canonical skill bodies and canonical agent sources pass the
  existing neutrality lint; host names appear only in generated overlays/renderers.
- R5 (governance): Dispatch instructions follow the existing runtime-routing doctrine
  (bounded inputs, explicit exclusions, concurrency cap, no recursive spawning, parent
  verifies and owns the final report).
- R6 (fresh-session gap): The `fresh-session` runtime context (se-red-team) gets an explicit,
  documented encoding instead of silently degrading at generation time.
- R7 (pilot scope): First wave limits dispatch protocols to a small pilot set (proposed:
  se-research, se-fact-check) before broader rollout.

## Acceptance Criteria

- [x] `installer/manifest.py` accepts kind `agent`; installer round-trip (install, status,
      remove) works for agent rows on claude and codex anchors; `agents` anchor receives none.
      (07-25-agent-artifact-kind; manifest carries 4 agent rows, claude+codex only.)
- [x] Generator renders canonical agent sources to Claude MD and Codex TOML; `--check`
      drift gate covers them; release-payload version gate passes.
- [x] Pilot skills contain a dispatch section with inline fallback; canonical bodies still
      pass the neutrality lint. (07-25-dispatch-pilot + 07-25-dispatch-rollout.)
- [x] `fresh-session` encoding decision implemented and documented (docs/SE_AI_COMMAND_PACK.md).
      (07-25-runtime-profile-gaps.)
- [x] Runtime-profile/overlay system documented in docs/SE_AI_COMMAND_PACK.md (existing gap).
- [x] Tests updated: generator, install, skills suites cover the new kind and overlays.

## Task map (parent-owned)

Recommended order below; dependencies are restated inside each child's `prd.md` (tree
position is not a dependency system).

1. `07-25-runtime-profile-gaps` (Tier 3) - fresh-session encoding + runtime-profile docs.
   No dependencies; do first.
2. `07-25-dispatch-pilot` (Tier 1) - dispatch sections in se-research and se-fact-check.
   No dependencies.
3. `07-25-dispatch-rollout` (Tier 1) - se-digest, se-feedback, se-scan, se-video-notes,
   se-red-team. Blocked by 2; composes with 1 for se-red-team.
4. `07-25-agent-artifact-kind` (Tier 2) - manifest kind `agent`, renderer hook, Claude MD
   + Codex TOML renderers, Amp exclusion. Blocks 5.
5. `07-25-worker-agents` (Tier 2) - se-source-reader, se-claim-verifier, delegation
   mapping. Blocked by 4; coordinates with 2.

Cross-child acceptance (parent integration review, run when all children archive):

- [x] Full `make check` green with all child changes merged. (Verified on merged main:
      coverage 88.3%, ruff + mypy clean, generator `--check` matches, release gate clean.)
- [x] One se-research run on a sub-agent-dispatch platform and one on an inline platform
      produce contract-identical final reports (execution strategy differs, outcome does not).
      SATISFIED 2026-08-09: live two-platform run executed with the 0.67.1 skill rendering —
      Claude Code (dispatch: 3 parallel se-source-reader lane workers, then 3 parallel
      se-claim-verifier workers, orchestrator-owned synthesis) and Codex CLI (inline,
      sequential single context), same question and arguments (`depth=brief min_sources=3
      format=brief`). Both reports carry all four contract sections, the exact confidence
      vocabulary, graded and dated sources, a recorded disconfirmation pass, and identical
      substantive verdicts; the differences observed are execution-strategy differences, one
      of them a documented deviation (disconfirmation queries ran inside the
      refutation-default verification workers rather than as a separate fan-out wave, with
      phase ordering preserved). Full evidence, both verbatim reports, and the
      section-by-section comparison: `research/dispatch-inline-contract-check.md`.
- [x] Operator docs match shipped behavior (profiles, agents, dispatch). (docs/SE_AI_COMMAND_PACK.md
      carries the Shipped agents inventory, runtime-profile/overlay explanation, and delegation.)

## Open questions (delegated)

- Worker-role granularity -> `07-25-worker-agents`.
- User- vs project-scope installs and the Codex trust-gate verification ->
  `07-25-agent-artifact-kind`.
- Pilot skill set -> RESOLVED (2026-07-25): se-research + se-fact-check.

## Notes

- Keep `prd.md` focused on requirements, constraints, and acceptance criteria.
- Complex program. This parent is not an implementation target and should not be
  started: it owns the requirement set, the task map, and cross-child acceptance
  criteria, and `design.md` is the artifact that carries them. Each
  implementation child must meet the complex-task requirement in full —
  `prd.md`, `design.md`, and `implement.md` before its own `task.py start`
  (`.trellis/workflow.md:164`).

## Cross-program coordination (2026-07-25 review; additive — does not alter R1-R7)

- Audit-backlog interlock: land the cheap audit gate tasks first —
  `07-25-audit-release-gate-scope` (A-035/A-040), `07-25-audit-lint-shipped-payload`
  (A-036), `07-25-audit-coverage-floor` (A-020), `07-25-audit-shared-reference-closure`
  (A-007) — they directly protect this program's payload waves.
- Registry consumer: `07-25-audit-registry-snapshot-contract` (A-002) must precede or ship
  with `07-25-agent-artifact-kind` (see that child's coordination note).
- Twin-pack consistency: before the parent integration review closes, compare with
  sd-ai-command-pack `.trellis/tasks/07-25-agent-artifacts/` for drift in the shared
  settled design.
- Clarification for cross-child acceptance: "contract-identical final reports" means
  identical section structure, field vocabulary, and evidence rules — not identical
  content.
- Planning depth: Parent task: owns the requirement set and cross-child acceptance criteria, with no direct implementation work, so `design.md` (present) is the correct depth here. `implement.md` belongs to each child, not to the parent.

## References

Research notes that lived beside this item's Trellis record and were not carried
into docs/work. Recover the bodies from git history under `.trellis/tasks/archive/2026-08/07-25-agent-artifacts`:

- research/cross-platform-agent-support.md
- research/dispatch-inline-contract-check.md
