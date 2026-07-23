# Pin SE interaction contracts

## Goal

Protect the verified interaction contracts in `se-meeting-prep`, `se-profile`,
`se-knowledge-capture`, `se-research`, `se-help`, and `se-feedback` from
regression. The tests must distinguish required blocking questions from useful
non-blocking clarification without changing current skill behavior.

## Background

The current skills already implement the intended behavior. Existing tests pin
parts of the safety and interaction contracts, but only
`se-knowledge-capture` directly covers both preview approval and the wait state.
The remaining skills have partial or indirect phrase coverage that could allow
their blocking or nonresponse behavior to disappear unnoticed.

## Requirements

- Add focused contract tests in `tests/test_skills.py`; do not edit canonical
  skill instructions unless a test proves the reviewed behavior is absent.
- Pin these required, blocking interactions:
  - `se-meeting-prep` stops rather than guessing when participant identity
    remains ambiguous.
  - `se-profile` asks one focused question and performs no mutation while its
    operation, destination, source boundary, profile, or target IDs are
    ambiguous.
  - `se-knowledge-capture` waits for destination approval and for approval of
    the exact write preview; `mode=apply` alone is insufficient.
- Pin these useful but non-blocking interactions:
  - `se-research` asks one round of scope questions when the missing answer
    would materially affect research, then may proceed only on disclosed stated
    assumptions.
  - `se-help` asks at most one question and only when its answer changes the
    selected route.
  - `se-feedback` keeps unsupported specificity `unclear`, asks a concrete
    clarification question, and retains the provisional `clarify` disposition
    rather than inventing evidence.
- Keep the tests semantic enough to protect the complete interaction rule, not
  merely the presence of a generic keyword such as `ask` or `confirm`.
- Preserve existing generated targets and installation payloads; this is a
  test-only hardening change unless a genuine source defect is discovered.

## Acceptance Criteria

- [x] Each of the six skills has an assertion covering its classified
      interaction and its blocking or non-blocking behavior.
- [x] Required-interaction assertions prove the workflow stops before guessing,
      mutation, destination selection, or an unapproved write.
- [x] Non-blocking assertions prove the workflow can continue only through its
      stated safe assumption or provisional-disposition behavior.
- [x] Removing any reviewed stop, wait, route-change, stated-assumption, or
      `unclear`/`clarify` contract causes a focused test failure.
- [x] `tests/test_skills.py` passes.
- [x] The repository quality gate passes without generated-template drift.

## Notes

- Scope is intentionally limited to evaluation coverage. The completed
  `07-22-se-review-skills-ask-user-question-review` task owns the reviewer
  capability and does not need reopening.
- This is a lightweight PRD-only task.
- Validation: 238 focused skill-contract tests and the 486-test `make check`
  quality gate pass. No canonical skill or generated payload changed.
