# Implement: Shared-reference citation-closure gate

## Execution order

1. **Add the citation pattern** (module scope, near the other constants in
   `.github/scripts/generate-skill-surfaces.py`):
   ```python
   CITATION_PATTERN = re.compile(r"references/([A-Za-z0-9][A-Za-z0-9._-]*\.md)")
   ```
   Confirm `re` is already imported (it is — `BANNED_PHRASE_PATTERN` uses it).

2. **Build the delivered-reference map** inside `validate_skills()`, after the
   existing forward/collision loop over `SHARED_REFERENCES`. Reuse the already
   computed `actual` skill-dir list and `missing_dirs`:
   - fan-out arm: iterate `SHARED_REFERENCES.items()`, add
     `basename(source)` to `delivered[consumer]` for each consumer.
   - own arm: for each registered skill with a present dir, add the basenames of
     files directly under `templates/skills/<skill>/references/`.

3. **Scan and check** each registered skill (skip `missing_dirs`): read its
   `SKILL.md`, run `CITATION_PATTERN.findall(body)`, and for every basename not
   in `delivered[skill]` append the Design's error message to `errors`.

4. **Keep the single raise**: the new errors join the existing `errors` list;
   the function's existing `if errors: raise GenerationError(...)` reports them.
   Do not add a second raise or reorder existing checks.

5. **Add the reverse-direction test** in `tests/test_generate.py` (preferred —
   it exercises `validate_skills` end-to-end) proving:
   - a seeded skill whose `SKILL.md` cites `references/nonexistent.md` with no
     own copy and no registration makes `make generate --check` / the validator
     fail with the closure error fragment; and
   - the same skill passes once the reference is either registered as a fan-out
     consumer or added as an own `references/nonexistent.md`.
   Prefer temp-dir / monkeypatched roots consistent with existing generate
   tests; do not write an ad-hoc script (PRD requirement).

## Validation plan

- Named check (pre-decided): after implementing, run the new gate against the
  **current tree** — `make generate --check` must exit 0 (AC3). Any nonzero exit
  is a real dangling citation to resolve in scope (register or remove) per
  Design R-1, then re-run to 0.
- Focused tests: `python -m unittest discover -s tests -p "test_generate.py"`
  and `-p "test_skills.py"` — new reverse test passes, existing forward and
  collision tests unchanged (0 regressions).
- Broader gate: `make check` (unittest + ruff + release-payload-gate) green.
- Ruff: `python -m ruff check .github/scripts/generate-skill-surfaces.py tests`.

## Doc/spec updates

- If any registry `SHARED_REFERENCES` change is needed for AC3, note it in the
  commit; no spec doc governs the reverse gate specifically. If a durable
  convention emerges ("cite only own or registered references"), capture it via
  the spec/review-learning owner after ship, not inline here.

## Review gate

Before `task.py start`: run the planning adversarial review contract (host +
Codex lanes) over prd.md/design.md/implement.md. Resolve blocking concerns
before requesting implementation approval.

## Rollback

`git revert` / single-commit revert of the `validate_skills()` addition and the
new test. No generated artifacts or data change; rollback is pure code.

## Follow-ups

- Deferred (optional PRD bullet 2): invert the ~50-of-53 opt-in consumer list to
  an opt-out exclusion set. Larger registry refactor; separate task if pursued.
