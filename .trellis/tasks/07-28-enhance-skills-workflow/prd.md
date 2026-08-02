# Create se-enhance-skills: session-driven skill improvement workflow

## Goal

Add a pack skill (working name `se-enhance-skills`) that closes the loop from
live skill usage back to skill source quality. Invoked on demand (typically
near session end), it inventories the `sd-*` and `se-*` skills actually used in
the current conversation, mines the conversation for friction attributable to
each skill's instructions, and files consent-gated Trellis improvement tasks in
each skill's upstream source repository. Every improvement task must require
that the touched SKILL.md gain or extend a **Gotchas** section capturing the
mistake pattern so future sessions avoid it.

## Requirements

- Skill source at `templates/skills/se-enhance-skills/SKILL.md` (this repo's
  skill source tree) plus the pack's standard per-platform command wrappers,
  passing existing generator/manifest validation.
- Workflow the skill encodes:
  1. Inventory skills used in the current conversation only (no transcript
     archaeology beyond the session). Scope: `sd-*` and `se-*` skills;
     `trellis-*` explicitly out of scope for v1.
  2. For each used skill, extract evidence-backed friction: errors hit,
     retries, gates that fired late, ambiguous instructions, workarounds the
     agent had to invent. Evidence must cite the concrete failure (command,
     error line, or misstep), not vibes.
  3. Map each skill to its upstream source repo — `sd-*` →
     sd-ai-command-pack (`templates/.agents/skills/...`), `se-*` →
     se-ai-command-pack (`templates/skills/...`) — and target the source
     tree, never a consumer's installed copy.
  4. With per-repo Trellis task-creation consent, create one improvement task
     per affected skill (dedupe against existing open tasks first). Each task
     carries: evidence, proposed instruction change, and the mandatory
     Gotchas-section requirement.
  5. Report a per-skill summary: task created, deduped against existing task,
     or no actionable friction.
- Gotchas contract: an improvement task is only complete when the target
  SKILL.md has a `## Gotchas` section containing the new entry; create the
  section when absent.
- The enhancer itself is planning-only: it creates tasks and reports; it never
  edits skill sources directly in the invoking session.
- Cross-repo behavior: resolve sibling checkouts; when an upstream repo is
  missing or has no Trellis, report the routing gap instead of failing or
  silently dropping the finding.
- Dry-run mode listing proposed tasks without creating anything.
- Boundary with neighbors, to be kept explicit in the SKILL.md: `sd-retro`
  owns incident/debugging retrospectives and journal capture;
  `sd-review-learnings` owns PR-review feedback patterns; `se-review-skills`
  owns on-demand review of a bounded skill collection (defects, overlap,
  metadata) independent of any session. `se-enhance-skills` owns
  skill-instruction defects observed in live usage of the current
  conversation. Reuse their consent-gating and task-creation conventions; do
  not duplicate their workflows.

## Acceptance Criteria

- [ ] Skill source + platform wrappers generated and passing pack validation
      and tests.
- [ ] Dry-run produces the per-skill friction report without side effects.
- [ ] Live run creates correctly-routed upstream tasks only after per-repo
      consent, with dedupe against existing open tasks.
- [ ] Every created task embeds the Gotchas-section requirement.
- [ ] `se-enhance-skills` SKILL.md itself contains a `## Gotchas` section
      (dogfood).
- [ ] Skill text documents the sd-retro / sd-review-learnings /
      se-review-skills boundary.

## Worked example (seed evidence, 2026-07-28 session in se-ai-command-pack)

Findings the enhancer would have filed from that session:

- `sd-create-pr`: publish preflight failed on a task committed earlier in the
  same session — empty `task.json` description plus generated `_example`
  scaffold rows in `implement.jsonl`/`check.jsonl`. `task.py create` only
  warns; the failure surfaced at PR time. Gotcha candidate: when a new task
  directory is in the intended diff, validate/fix task metadata and scaffold
  rows at commit time, not first at publish preflight.
- `sd-audit-repo`: Workflow-tool `args` can arrive as a JSON string; the
  orchestration script must parse defensively
  (`typeof args === 'string' ? JSON.parse(args) : args`) or `pipeline()`
  throws. Gotcha candidate for the skill's workflow-authoring instructions.
- `sd-finish-work` (work-loop tooling): `work-loop.py stop` validates via
  `lock.json`, which paused loops release — stopping a paused loop errors.
  Gotcha candidate: document the paused-loop stop path.
- `sd-create-pr` × `sd-finish-work` interaction: sd-create-pr bundles the
  sd-update-spec map refresh (`docs/repomix-map.md`) into the same commit as
  task metadata; the later finish-work `final-bundle --mode planning`
  journal-only-recovery gate then fails with
  `planning_recovery_commit_scope_invalid` because a journal-referenced work
  commit touches paths outside the task directory. Gotcha candidate: keep
  task-directory changes and generated-map refreshes in separate commits when
  a planning-mode finish-work will follow.

## Out of scope

- Editing skill sources directly from the enhancer session.
- `trellis-*` skill improvements (v1).
- Automated/scheduled invocation; v1 is on-demand only.
