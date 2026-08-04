# Shared-reference citation-closure gate

## Goal

A skill whose body cites `references/<file>.md` that will not ship to it (neither own resource nor registered SHARED_REFERENCES fan-out) fails the generate gate instead of installing fleet-wide with a dangling citation.

## Requirements

- Extend validate_skills (generate-skill-surfaces.py) to scan skill bodies for references/ citations and verify closure against own resources + registered fan-out.
- Alternatively (planning decision): invert the near-universal 50-of-53 opt-in consumer list to an opt-out exclusion set.
- Keep the existing forward-direction test; add the reverse direction as a real test, not an ad-hoc script.

## Acceptance Criteria

- [x] A seeded violation (citation without registration) fails `make generate --check`. The reverse closure check in `validate_skills()` raises `GenerationError`, which `--check` surfaces as a nonzero exit. (test: `test_generate.SandboxGeneratorTest.test_dangling_citation_fails`)
- [x] A test in tests/test_generate.py (or test_skills.py) proves the failure mode. (tests: `test_dangling_citation_fails`, plus positive closure via own resource `test_citation_satisfied_by_own_reference`, via fan-out `test_citation_satisfied_by_registered_fanout`, and placeholder-ignored `test_placeholder_citation_is_ignored`)
- [x] Current tree passes the new gate. `generate-skill-surfaces.py --check` exits 0; empirical probe found 0 dangling citations across all registered skills. (verified in `make check`)

## Notes

- Audit finding: A-007 (P2/S) — .trellis/audit/report-2026-07-25.md.
- Evidence: installer/registry.py:292-344, .github/scripts/generate-skill-surfaces.py:326, tests/test_skills.py:365.

## Cross-program coordination (2026-07-25 review)

- Same-file coordination: `07-25-agent-artifact-kind` refactors the generator's
  build/validate paths (renderer hook). Land this gate before that refactor, or rebase it
  on top afterward — not concurrently.
