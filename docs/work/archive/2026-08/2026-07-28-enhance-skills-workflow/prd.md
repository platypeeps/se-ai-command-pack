---
title: "Extend se-review-skills: mandate a Gotchas section in tasks it creates"
status: done
created: 2026-07-28
branch: task/07-28-enhance-skills-workflow
---
# Extend se-review-skills: mandate a Gotchas section in tasks it creates

## Goal

`se-review-skills` already reports gotchas from observed session use. It does
not require the task it creates to carry that gotcha into the target skill, so
the durable lesson depends on whoever picks the task up. Close that gap, and fix
one inaccurate boundary paragraph while in the file.

## Scope history

This task originally proposed a separate `se-enhance-skills` skill. Reading the
current source showed `se-review-skills` already performs almost the whole
proposed workflow — session mining, evidence-backed findings, canonical source
boundaries, cross-repo routing, consent-gated task creation, and gotcha
reporting — capability that landed in `093809c` on 2026-07-22, six days before
this PRD was written. The task became an extension of `se-review-skills`.

It was then scoped to two capabilities: a session-first `scope=session` selector
and this Gotchas mandate. Four rounds of adversarial planning review found
blocking defects in the selector every round — it turned out to reach into the
report schema, the bundled analyzer's payload contract, the session privacy
boundary, snapshot replay, and `mode=apply`. **`scope=session` was split into
its own task** with that ledger as its starting evidence. This task is the half
that was stable: two authored files, no open concerns.

## Requirements

- Every task `mode=task` creates from a **gotcha-qualifying** observed-use
  finding states, as an acceptance requirement, that the touched SKILL.md gains
  or extends a `## Gotchas` section carrying the trigger, failure, prevention,
  recovery, and regression method already defined in
  `references/session-evidence.md`, *Gotchas and regression records*. Create the
  section when absent, placed last in the skill body.
- "Gotcha-qualifying" is that reference's existing gate — a recurring or
  high-consequence edge case whose evidence can state all five parts. The
  mandate must not force a gotcha for evidence the reference says does not
  qualify, and must not broaden the gate to make more findings qualify. A task
  built from non-qualifying observed-use evidence is created without the
  requirement and says so.
- The rule is written into `references/session-evidence.md` as well as
  `SKILL.md`. That reference is the required reading for the observed-use pass,
  so a rule stated only in the skill body does not reach the reader who follows
  the citation.
- The mandate follows the evidence class, not the skill: a task created from a
  source-only finding with no session evidence is unchanged.
- Keep the neighbor boundary accurate in the skill text: `sd-retro` owns
  incident and debugging retrospectives, `sd-review-learnings` owns PR-review
  feedback patterns, and `se-review-skills` owns skill-instruction defects from
  source and observed use. This is the paragraph whose omission allowed the
  duplicate-skill proposal above, so it is part of the deliverable.
- No new skill, no new argument, no new family entry, no new runtime-profile
  assignment, and no new shared-reference consumer. No change to the bundled
  analyzer `templates/skills/se-review-skills/scripts/skill_review.py`, to
  `references/report-schema.md`, to the session budgets,
  the confirmation standard, the privacy boundary, or the causal-classification
  table.

## Acceptance Criteria

- [x] `se-review-skills` states the `## Gotchas` acceptance requirement for
      every task it creates from a gotcha-qualifying observed-use finding,
      referencing the five-part record in `references/session-evidence.md` and
      leaving that reference's qualification gate unchanged.
- [x] The skill states the negative case: a task from non-qualifying
      observed-use evidence is created without the requirement and says so.
- [x] `references/session-evidence.md` carries the same rule in its
      *Gotchas and regression records* section.
- [x] The neighbor-boundary paragraph names `sd-retro` and
      `sd-review-learnings` and what each owns.
- [x] `docs/SE_AI_COMMAND_PACK.md`, `### Skill-review workflow boundary`,
      describes the Gotchas mandate, and the documentation path guard still
      reports zero failures.
- [x] `make check` passes: generation parity, Ruff, mypy, the unittest suite,
      and the release payload gate. New pins cover both the `SKILL.md` mandate
      and the reference edit, and each pinned token is verified absent from the
      unedited file so the assertion can fail.
- [x] `make generate` is idempotent; the release payload gate passes with a
      patch bump to `0.67.1` and a dated CHANGELOG heading, because
      `templates/**` and `generated/**` change.

## Out of scope

- The `scope=session` session-first selector — split to its own task.
- A separate `se-enhance-skills` skill.
- Editing skill sources directly from the reviewing session beyond the existing
  `mode=apply` contract.
- `trellis-*` skill improvements.
- Automated or scheduled invocation.
