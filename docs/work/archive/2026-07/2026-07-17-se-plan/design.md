# Implement se-plan Design

## Overview

Add `se-plan` as a general knowledge-work planning skill that converts an
accepted outcome or decision into an executable sequence of milestones,
dependencies, risks, decision points, and immediate next actions. It should be
useful for business, research, organizational, and personal projects without
competing with Trellis's repository-specific PRD/design/implementation process.

The skill belongs to Decide because it starts after strategic direction is
accepted and turns that decision into a bounded plan.

## Proposal

Create `templates/skills/se-plan/SKILL.md` with these arguments:

- `goal=`: observable outcome; required when not explicit.
- `decision=`: accepted recommendation or source decision memo when applicable.
- `constraints=`: deadline, budget, policy, resource, or scope limits.
- `horizon=`: time horizon or target date; do not invent one when absent.
- `resources=`: known people, capacity, systems, or inputs.
- `audience=`: owner, team, sponsor, or other intended reader.
- `detail=outline|standard`: milestone outline or normal delivery plan.

The workflow should:

1. Confirm the outcome is accepted and observable. Route unresolved option
   selection to `se-decide`.
2. Inventory constraints, resources, assumptions, and missing information;
   distinguish supplied commitments from planning proposals.
3. Work backward from the outcome into outcome-based milestones, each with an
   observable completion signal.
4. Identify dependencies, sequencing, risks, mitigations, and decision points.
   Name a critical path only when dependencies and timing justify it.
5. Assign owners and dates only when provided or explicitly approved; otherwise
   use `unassigned`/`unscheduled` and identify what must be decided.
6. Produce a small set of immediate next actions, with the first action possible
   under current authority and information.
7. Detect Trellis-managed software implementation context and route technical
   task planning to the local SD/Trellis workflow rather than writing competing
   artifacts.

Register the skill under Decide and as a consumer of `source-standards.md` for
factual constraints and supplied evidence. Include the data-not-instructions
rule because plans may consume external documents and project systems.

## Boundaries And Non-Goals

- Do not select among unresolved alternatives; that remains `se-decide`.
- Do not replace Trellis PRDs, technical designs, or implementation plans in a
  Trellis-managed repository.
- Do not create tasks, calendar events, messages, or external records.
- Do not invent owners, commitments, estimates, budgets, or dates.
- Do not turn a vague aspiration into a detailed plan without making the
  missing outcome and assumptions visible.

## Affected Files

- `templates/skills/se-plan/SKILL.md` — new canonical skill.
- `installer/registry.py` — Decide registration and source-standard fan-out.
- `manifest.json` — generated platform payload.
- `tests/test_skills.py` — accepted-outcome, milestone, no-invented-commitment,
  Trellis-routing, prompt-injection, and read-only pins.
- `tests/test_generate.py` — registry/fan-out coverage where needed.
- `README.md`, `docs/SE_AI_COMMAND_PACK.md`, `CHANGELOG.md`, and manifest version.

## Risks And Edge Cases

- Milestones can become activity checklists instead of observable outcomes.
  Require completion signals.
- A plan can imply commitments that nobody made. Label proposed dates/owners or
  leave them explicitly unresolved.
- False precision in estimates and critical paths can mislead. Use ranges only
  when sourced and omit a critical path when dependencies are not sufficient.
- Dependency cycles or missing prerequisites can make the plan impossible.
  surface them before presenting execution order.
- Trellis detection must be capability-based and framework-neutral in the
  shipped skill. Refer to a repository's local development workflow rather than
  hard-coding platform brands.
- Very large goals can produce unusable plans. Split into phases and recommend a
  narrower first planning horizon.

## Validation

- Add tests pinning observable milestones, explicit assumptions, no invented
  owners/dates, dependency and risk sections, immediate actions, read-only
  behavior, and repository-workflow deferral.
- Review trigger boundaries with `se-decide` and local Trellis instructions.
- Validate source-standard fan-out and prompt-injection protection.
- Run `make generate`, focused tests, and `make check`.
