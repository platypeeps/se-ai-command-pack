# Implement se-decide Design

## Overview

Add `se-decide` as a canonical user-level skill that turns a bounded choice and
already-available evidence into a decision memo. It fills the gap after
`se-scan`, `se-research`, or `se-digest` without becoming another discovery or
synthesis workflow.

The implementation should follow the existing one-directory-per-skill model,
reuse the shared source standards, fan out through the generated manifest, and
leave installed skill paths flat.

## Proposal

Create `templates/skills/se-decide/SKILL.md` with the standard five sections and
framework-neutral wording. Give it a narrow argument surface:

- `question=`: the decision to make; required when not unambiguous from context.
- `options=`: the known alternatives; require at least two, including the status
  quo when it is a real option.
- `criteria=`: comparison axes; derive a provisional set from stated goals only
  when absent and label that derivation.
- `constraints=`: hard limits that can disqualify an option.
- `evidence=`: supplied paths, links, prior results, or connected-source context.
- `format=brief|memo`: concise decision read or forwardable decision memo.

The workflow should:

1. Confirm the decision, options, constraints, and success criteria.
2. Stop for a material ambiguity; otherwise expose provisional assumptions.
3. Route missing candidate discovery to `se-scan`, open evidence questions to
   `se-research`, and supplied-document synthesis to `se-digest`.
4. Build an option-by-criterion evidence matrix using consistent criteria.
5. Separate facts, assumptions, and judgment; do not invent weights, scores, or
   precision the user did not supply.
6. Test the leading option against the strongest counterargument and identify
   conditions that would change the recommendation.
7. Deliver the decision, tradeoffs, confidence, reversibility, missing evidence,
   and smallest next action.

Register the skill in the Decide family when the taxonomy task has landed. If
this task lands first, add it to the current `SKILL_NAMES` tuple in an order
that can be migrated mechanically to the family registry later. Fan
`source-standards.md` into the skill because the decision matrix can contain
external or time-sensitive evidence.

## Boundaries And Non-Goals

- Do not enumerate a market or discover candidates; that remains `se-scan`.
- Do not perform an open-ended evidence sweep; that remains `se-research`.
- Do not re-read and reconcile a supplied corpus as its primary job; that
  remains `se-digest`.
- Do not build the execution plan; hand an accepted decision to `se-plan`.
- Do not execute, purchase, message, schedule, or otherwise act on the choice.
- Do not create a separate `se-compare` skill until real use shows a distinct
  trigger that cannot be expressed inside `se-decide`.

## Affected Files

- `templates/skills/se-decide/SKILL.md` — new canonical skill.
- `installer/registry.py` — skill/family registration and shared-reference
  consumer entry.
- `manifest.json` — regenerated per-platform skill and reference rows.
- `tests/test_skills.py` — decision-specific safety and output pins.
- `tests/test_generate.py` — existing fan-out coverage should include the new
  registry entry; add focused coverage only if taxonomy changes its fixtures.
- `README.md` and `docs/SE_AI_COMMAND_PACK.md` — catalog and maintenance docs.
- `CHANGELOG.md` and the manifest version — release metadata.

## Risks And Edge Cases

- A recommendation can look objective while relying on unstated criteria or
  invented weights. Require visible assumptions and avoid numeric scoring by
  default.
- Options may be incomparable because evidence quality differs. Surface unknown
  cells and confidence rather than normalizing weak evidence upward.
- A hard constraint may make the nominally highest-scoring option invalid.
  Evaluate constraints before preference criteria.
- The user may expect autonomous execution after asking what to choose. Keep the
  skill explicitly read-only and require a separate action request.
- Trigger overlap is reviewer-sensitive. The description and `When to use`
  section must distinguish decision-making from discovery, research, digesting,
  and planning.

## Validation

- Run the generator's skill validation and confirm the shared reference fans
  out to every supported platform.
- Add tests pinning the unknown-argument stop rule, data-not-instructions rule,
  read-only boundary, counterargument step, and required final-report fields.
- Run `make generate` and inspect the new manifest targets without hand-editing
  generated rows.
- Run focused skill/generator tests, then `make check` for unittest, Ruff, mypy,
  generation parity, and the payload/version release gate.
