# Implement se-learn Design

## Overview

Add `se-learn` under Understand as a mastery-oriented path planner and adapter.
It converts a capability goal plus demonstrated baseline into sequenced learning
stages, checkpoints, practice, projects, and review. It does not certify mastery
or replace the narrower explain, study-guide, and Socratic-review workflows.

## Proposal

Accept `goal=`, `baseline=`, `constraints=`, `time=`, `modes=`, `materials=`,
`horizon=`, and `detail=outline|standard`. Define the capability in observable
terms and identify prerequisite skills, target contexts, and evidence that would
demonstrate mastery.

Separate self-reported familiarity from demonstrated ability. Start with a
small diagnostic: representative explanation, application, or transfer task;
allow skip/opt-out and label the resulting baseline weaker. Build a dependency
map and stages with measurable outcome, concepts, worked example, retrieval
practice, exercise, transfer/project task, checkpoint, and spaced review.

Fit the plan to available time without silently lowering the target. When time
is insufficient, reduce scope, extend horizon, or label a foundation-only path.
Use accessible/authorized materials; disclose unavailable prerequisites or
resources and never invent access.

At each checkpoint, classify evidence as secure, partial, misconception,
procedure-without-understanding, or not demonstrated. Adapt by revisiting a
prerequisite, changing representation, adding retrieval/application practice,
or increasing difficulty; preserve the original outcome unless the user
approves a scope change.

Return goal/mastery contract, baseline evidence, dependency map, staged path,
weekly/session rhythm, checkpoints, adaptation rules, resource gaps, and next
session. Route concept clarification to `se-explain`, source-derived practice
material to `se-study-guide`, and adaptive testing to `se-socratic-review`.

Register under Understand; fan in source standards when external materials are used.

## Boundaries And Non-Goals

- Do not promise mastery by a date, issue grades/credentials, or silently lower outcomes.
- Do not infer baseline from title/experience alone or confuse recognition with ability.
- Do not become a teaching dialogue or generate an entire curriculum when a
  bounded path is enough.
- Do not enroll, purchase, schedule, or mutate learning systems.

## Affected Files

- Canonical skill, registry/shared references, manifest, diagnostic/adaptation
  tests, catalog/operator docs, changelog, and version.

## Risks And Edge Cases

- Diagnostics can discourage or misclassify; keep them small, relevant, and nonjudgmental.
- Time constraints can produce fantasy schedules; expose workload assumptions.
- Practice may test recall only; include explanation, application, and transfer.
- Inaccessible materials can break dependencies; offer equivalent capability
  requirements, not fabricated resources.
- Adaptation can become endless remediation; define checkpoint exit criteria.

## Validation

- Pin observable mastery, self-report/demonstration distinction, dependency
  sequencing, checkpoint classes, adaptation rules, time-scope negotiation, and no certification.
- Test beginner, expert with gaps, false confidence, limited time, inaccessible
  material, persistent misconception, and early mastery.
- Run generation, focused tests, full checks, and diff check.
