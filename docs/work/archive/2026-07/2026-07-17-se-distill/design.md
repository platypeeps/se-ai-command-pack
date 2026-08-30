# Implement se-distill Design

## Overview

Add `se-distill` under Understand as purpose-bound extreme compression. Unlike
`se-digest`, which reconciles a corpus at a normally useful length, distillation
starts with an explicit information budget and makes loss auditable.

## Proposal

Accept `topic=`, `sources=`, `audience=`, `purpose=executive|study|decision|technical`,
`target=10%|<words>|<tokens>`, `must_keep=`, and `loss_tolerance=`. Inventory
every supplied source and measured size; report unreadable portions and choose
one consistent word/token measure for input and output.

Before drafting, build an importance map with stable IDs for thesis, conclusions,
decisions, constraints, causal structure, strongest evidence, risks, exceptions,
actions, definitions, and user-designated invariants. Rank by consequence to the
stated purpose, not rhetorical prominence or repetition. Preserve source and
locator for each surviving load-bearing item and expose conflicts rather than
compressing them into consensus.

Draft to the target, then run an invariant audit. If thesis, required decision,
constraint, strongest evidence, material risk, or decision-changing exception
cannot fit, return the smallest safe result, its actual ratio, and the exact
reason the requested target is unsafe. Never claim the 80% value target was
measured objectively; report it as the operational prioritization goal.

Return source/input size, output size, ratio, audience/purpose, distilled
artifact, importance-map coverage, loss ledger, contested points, and a
consult-the-source list. The loss ledger groups omitted examples, history,
secondary evidence, nuance, implementation detail, and unresolved material;
each potentially decision-changing omission is individually named.

Register under Understand, fan in source standards, and add external-input safety coverage.

## Boundaries And Non-Goals

- Do not promise lossless retention or a universal 80/10 guarantee.
- Do not add external research unless separately approved; sources define the corpus.
- Do not replace source material, ordinary summaries, or `se-digest` conflict synthesis.
- Do not drop citations, constraints, contradictions, or exceptions silently.

## Affected Files

- Canonical skill, registry/shared-reference rows, manifest, focused skill and
  generator tests, catalog/operator docs, changelog, and version.

## Risks And Edge Cases

- Short sources make 10% meaningless; set a minimum useful artifact and report ratio.
- Technical notation/code may carry high information density; preserve exact
  invariants or request a larger budget.
- Repeated claims can look important; weight decision consequence and evidence strength.
- Citation text consumes budget but remains mandatory for load-bearing claims.
- Conflicting sources require explicit disagreement even when it costs compression.

## Validation

- Pin measured ratios, importance-map IDs, required invariants, smallest-safe
  escape, loss ledger, attribution, and no false 80% guarantee.
- Test short/long corpora, impossible targets, conflicts, code/math, citation
  retention, unreadable sources, and injection.
- Run generation, focused tests, full checks, and diff check.
