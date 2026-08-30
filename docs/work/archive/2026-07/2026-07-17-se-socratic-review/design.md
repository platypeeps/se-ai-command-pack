# Implement se-socratic-review Design

## Overview

Add `se-socratic-review` under Understand as an adaptive, one-question-at-a-time
dialogue that diagnoses and deepens demonstrated understanding. It is formative
practice, not formal grading, adversarial interrogation, or personality assessment.

## Proposal

Accept `topic=`, `target_level=`, `purpose=`, `curriculum=`, `bounds=questions|time`,
`starting_difficulty=`, and `feedback=deferred|brief`. Define the target
capabilities and source curriculum before questioning; disclose gaps/unavailable material.

Ask exactly one question per turn. Use a balanced progression across recall,
explanation, mechanism, application, comparison, debugging, and transfer. Require
the learner to commit to an answer/reasoning before explanation unless they ask
to stop, skip, or reveal. Avoid leading cues that contain the answer.

Evaluate each response on correctness, reasoning quality, confidence calibration,
misconception evidence, and transfer—not fluent wording. Distinguish correct
guess, correct reasoning, partial model, procedural success without mechanism,
and misconception. Adapt the next question by narrowing, changing representation,
probing a prerequisite, or increasing transfer difficulty.

Use non-humiliating language and never diagnose personal ability. If a
misconception persists, pause escalation, explain the minimal correction with
source attribution, ask a new non-identical check, and record whether repair transferred.

Stop on user request, bound reached, inaccessible prerequisite, or diminishing
diagnostic value. Return session scope, demonstrated capabilities, evidence by
question, misconceptions/repaired items, confidence calibration, unknown/not
tested areas, and next-practice recommendations. Do not assign a credential or grade.

Register under Understand, fan in source standards when curriculum material is
used, and add external-input safety coverage.

## Boundaries And Non-Goals

- Do not ask multiple questions per turn, leak answers by default, or force continuation.
- Do not infer intelligence/personality, humiliate, rank people, or issue grades/credentials.
- Do not lower the target silently after errors or count a lucky guess as mastery.
- Do not replace a full learning path or source-derived study guide.

## Affected Files

- Canonical skill, registry/shared references, manifest, dialogue/adaptation
  tests, catalog/operator docs, changelog, and version.

## Risks And Edge Cases

- “One question” can hide several subquestions; keep one assessable demand.
- Leading hints contaminate evidence; record when help was given.
- Persistent error may reflect ambiguous wording; validate the question/source first.
- Session bounds can end before coverage; report not-tested areas explicitly.
- Confidence self-report can be performative; use it as one signal, not truth.

## Validation

- Pin one-question turns, commitment-before-reveal, help contamination labels,
  response classes, adaptive difficulty, misconception repair/transfer, stopping,
  and non-grading final report.
- Test correct guess, partial reasoning, persistent misconception, ambiguity,
  skip/reveal/stop, bound exhaustion, and injection.
- Run generation, focused tests, full checks, and diff check.
