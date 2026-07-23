# Add installer documentation contract checks

## Goal

Add deterministic tests that keep installer documentation aligned with canonical prior-provenance terminology and preservation-precedence behavior.

## Requirements

- Add deterministic coverage for the user-facing installer documentation that
  describes normal refresh behavior.
- Require the documentation to identify prior `provenance.json` hashes as the
  evidence authorizing a non-force refresh; do not reduce that contract to an
  ambiguous generic install receipt.
- Require the documentation to state that preservation semantics take
  precedence and applicable targets remain `preserved`.
- Keep checks focused on contract-bearing sections and phrases rather than
  pinning entire paragraphs or generated repository-map output.
- Preserve legitimate detailed uses of provenance or receipt terminology
  outside the normal-refresh contract.

## Acceptance Criteria

- [x] A focused test fails if the README normal-refresh section stops naming
  the prior provenance hash or `provenance.json` evidence.
- [x] A focused test fails if that section stops explaining preservation
  precedence and the `preserved` status.
- [x] The detailed installer documentation is covered where it carries the
  same externally visible contract.
- [x] Tests remain resilient to unrelated prose reflow and catalog generation.
- [x] Focused tests and the repository's full validation gate pass.

## Notes

- This is a lightweight, PRD-only task.
- The checks should encode observable installer behavior, not stylistic word
  preference disconnected from the implementation.
