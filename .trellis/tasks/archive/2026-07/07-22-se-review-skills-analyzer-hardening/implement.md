# Harden The Skill Review Inventory Analyzer Implementation Plan

1. Start one feature branch and load the task, canonical reviewer, analyzer,
   focused tests, and backend quality guidance.
2. Add failing tests for schema 3 test-text references, Python 3.9 runtime
   compatibility, unresolved-copy changeability, and ignored bytecode.
3. Replace the incompatible registry iteration, centralize ignored related
   paths, tighten changeability, and rename the public field and helper.
4. Update `se-review-skills` to disclose the analyzer floor, fallback,
   reference semantics, ownership boundary, and bytecode exclusions.
5. Bump release metadata, generate twice, run focused tests, `make check`, the
   full review gate, update-spec, and the single PR-through-merge lifecycle.

## Review Notes

- `reviewable` and `changeable` are independent.
- Only verified canonical roots permit task/application mutation.
- Test-text references remain candidate locators until semantic inspection.
- Ignored bytecode must not affect related resources or snapshot IDs.
