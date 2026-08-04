# Registry-driven shared-reference tests

## Goal

Replace the ~790-line block of 42 hand-copied per-skill shared-reference test methods in tests/test_generate.py with one registry-driven test, so every new skill is covered automatically instead of by manual copy.

## Requirements

- One expected-shared-sources snapshot dict plus a single subTest-driven test iterating SKILL_NAMES (precedent: test_shared_reference_fanned_into_consumers at tests/test_generate.py:174).
- Retire the per-skill methods (block starting tests/test_generate.py:218).
- Failure output must still name the offending skill and reference.

## Acceptance Criteria

- [x] A seeded registry omission fails the generic test, naming the skill.
- [x] The duplicated per-skill methods are gone; suite stays green with equivalent-or-better coverage.
- [x] Adding a skill requires no new hand-written shared-reference test.

## Notes

- Audit finding: A-043 (P2/M) — .trellis/audit/report-2026-07-25.md, ledger.md.
- Evidence: tests/test_generate.py:218-1010, :174; docs/SE_AI_COMMAND_PACK.md:871.
