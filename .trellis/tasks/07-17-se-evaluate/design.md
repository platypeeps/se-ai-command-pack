# Implement se-evaluate Design

## Overview

Add `se-evaluate` under Improve as an explicit-rubric assessment workflow. It
validates the rubric before applying it, maps every judgment to criterion and
evidence, distinguishes missing evidence from failure, and reports uncertainty
and weight sensitivity without manufacturing numeric precision.

## Proposal

Resolve subject/version, purpose, audience, proposed rubric, weights, thresholds,
evidence, comparator, and decision boundary. Validate criteria for relevance,
independence, scope, observable interpretation, and unintended bias. Surface
dependent or proxy criteria and require revision or explicit acceptance.

For each criterion record definition, evidence required, evidence found, coverage,
judgment or score, confidence, strengths, deficiencies, missing evidence, and
highest-value improvement. Use qualitative judgments when evidence/rubric is
qualitative. Numeric scores require meaningful scales and aggregation rules.

Distinguish `failed` from `not-evaluable` and `missing-evidence`. When weights or
thresholds materially determine the overall result, run sensitivity scenarios and
report reversals. Comparators must share compatible scope and evidence.

Return rubric audit, criterion ledger, overall bounded judgment, uncertainty,
sensitivity, and prioritized improvements. `se-evaluate` does not choose among
options (`se-decide`) or adopt an adversarial threat frame (`se-red-team`).

## Boundaries And Non-Goals

- Do not certify, score personnel, or make the final decision.
- Do not force numeric scores onto qualitative evidence.
- Do not hide biased/dependent criteria or treat missing evidence as failure.
- Do not duplicate adversarial review or option choice.

## Affected Files

- Canonical skill, Improve-family registration, evaluation/source references,
  manifest, fixtures/tests, catalog/operator docs, changelog, and version.

## Risks And Edge Cases

- Rubrics can encode the desired answer; audit provenance and bias first.
- Dependent criteria double-count the same property; flag or consolidate.
- Weight sensitivity can reverse rankings; show plausible alternatives.
- Comparators with unequal evidence create false precision.
- Thresholds may be policy choices rather than evidence; label them.

## Validation

- Pin rubric audit, criterion/evidence mapping, missing-versus-failed states,
  qualitative mode, numeric preconditions, sensitivity, and skill boundaries.
- Test biased rubrics, dependent criteria, qualitative evidence, weight reversal,
  missing evidence, incompatible comparator, and injection.
- Run generation, focused tests, full checks, and diff check.
