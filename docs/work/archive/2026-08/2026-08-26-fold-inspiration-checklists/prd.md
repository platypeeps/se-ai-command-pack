---
title: Fold upstream checklists into existing surfaces
status: done
created: 2026-08-26
branch: feat/adopt-claude-skills
---
# Fold upstream checklists into existing surfaces

Parent: [`../08-26-adopt-claude-skills/`](../08-26-adopt-claude-skills/) — R4; parent AC4.

## Goal

Two upstream skills carry value but must not become skills here — their
delivery surface already exists in this repo. Fold the content in, adjusted
to repo conventions.

## Fold 1: plan-discipline → Trellis planning guidance

Upstream `plan-discipline` fires on multi-file changes and interviews scope,
blast radius, and delegation before work. As a skill it competes with the
Trellis planning workflow (both would claim the same planning moment). Its
durable content is checklist material for planning that already happens.

- Target surface: the repo-owned Trellis planning guidance
  (`.trellis/spec/guides/` — exact file chosen in-task from the existing
  index), not the vendored Trellis payload (parent C3).
- Content to fold: scope-interview prompts (what is in/out, blast radius
  enumeration before editing), the plan-quality probes (steps independently
  verifiable, rollback points named, delegation inventory), adjusted to
  Trellis vocabulary (prd/design/implement, not upstream's Gate ladder).
- Explicitly not folded: upstream's gate-severity ladder and its
  fire-on-3-files trigger — Trellis owns when planning starts.

## Fold 2: python probes → `.prism/rules.json`

Upstream `python-review`/`python-quality` mix durable probes with mandates
that contradict this repo (click over argparse, pytest over unittest, uv-run
assumptions). The durable half becomes deterministic local-review checks.

- Target surface: `.prism/rules.json` `required` checks array (the local
  prism provider the sd-review lane already runs).
- Probes to fold (repo-convention-adjusted): fail-loud (no silent excepts, no
  defaulted error swallowing), one-walker-many-projections (single traversal
  feeding multiple outputs instead of repeated walks), comment discipline
  (comments say why, not what), and any others from the upstream checklists
  that survive the argparse/unittest filter.
- Explicitly not folded: click, pytest, uv mandates; anything duplicating
  ruff/mypy rules already enforced by `make lint`.

## Requirements

- R1. Both folds are additive edits to existing surfaces; no new skill, no
  new tool, no new CI job.
- R2. Every folded item is phrased in this repo's vocabulary with no
  reference to the upstream skill names (parent AC6 applies to these
  surfaces too).
- R3. `.prism/rules.json` stays valid for the prism provider (schema check:
  the sd-review local lane still runs green after the edit).

## Acceptance Criteria

- [x] AC1. The chosen Trellis guide file carries the folded planning
      checklist; `task.py validate` and the guide index stay consistent.
- [x] AC2. `.prism/rules.json` parses and the added checks appear in a local
      sd-review run's prism receipt.
- [x] AC3. Grep over both edited surfaces for `plan-discipline`,
      `python-review`, `python-quality` returns nothing.
- [x] AC4. No folded item contradicts `make lint`/repo conventions (argparse,
      unittest, ruff config) — reviewed against the conflict findings.

Lightweight task: PRD-only.
