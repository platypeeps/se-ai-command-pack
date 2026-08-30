# Implement — Argument vocabulary enforcement (A-006, last child)

Ordered checklist. Land after every migration child (done) so `make check` is
green the moment the guard activates.

## 1. Registry: alias constant + pure checker

- [ ] `installer/registry.py`: add `KNOWN_COVERED_AXIS_ALIASES` immediately
      after `RESERVED_ARGUMENT_NAMES`, values `length→(depth,)`, `source→(input,)`,
      `inputs→(input,)`, `detail→(depth, sensitivity)`.
- [ ] Add `argument_vocabulary_errors(label, arguments_section) -> list[str]`:
      - regex `` r"`([^`\n]+)`" `` over the section; keep matches containing `=`.
      - for each, `raw` = match; split once on `=`; take leading
        `re.match(r"[a-z0-9_-]+", left)` as `name`; skip if no name match.
      - if `name in KNOWN_COVERED_AXIS_ALIASES`: append
        `f"{label}: argument `{name}=` is a non-canonical alias for the "
        f"{' / '.join(canon)} axis; use `{canon[0]}=`"` (name both canonicals in text).
      - elif `name in CANONICAL_ARGUMENT_LADDERS`: ladder = set(...); for each
        `v` in `right.split("|")` stripped and truthy and matching a bare value
        token, if `v not in ladder` collect it; if any, append
        `f"{label}: `{name}=` value(s) {sorted(bad)} are not in the "
        f"{name} ladder {ladder_tuple}"`.
- [ ] Keep it pure (no I/O); it only reads the two module constants.

## 2. Generator: call the checker in validate_skill

- [ ] `.github/scripts/generate-skill-surfaces.py`: add
      `argument_vocabulary_errors` to the `from installer.registry import (...)`
      block.
- [ ] In `validate_skill()`, after the `REQUIRED_SECTIONS` order loop, slice the
      Arguments section from `body`:
      `start = body.find("\n## Arguments\n")`; if `start != -1`, `rest = body[start+1:]`;
      `nxt = rest.find("\n## ", len("## Arguments"))`; `section = rest if nxt == -1
      else rest[:nxt]`; then `errors.extend(argument_vocabulary_errors(label, section))`.
- [ ] Confirm errors propagate: `validate_skills()` raises `GenerationError` on
      non-empty errors (existing behavior).

## 3. Negative fixtures — tests/test_generate.py

- [ ] In `SandboxGeneratorTest`, add tests building a bad Arguments section by
      replacing `VALID_SKILL`'s `## Arguments\n\nText.` with declarations:
      - `length=brief|standard` → `assert_validation_error("non-canonical alias")`
        and `"depth"`.
      - `source=` → `assert_validation_error("input")`.
      - `depth=brief|verbose` → `assert_validation_error("not in the depth ladder")`
        (fragment names `verbose`).
      - `sensitivity=secret` → `assert_validation_error("sensitivity ladder")`.
- [ ] Add a positive: Arguments with `` `depth=deep|brief` `` + `` `input=` ``
      passes `gen.validate_skills()` (order-independent subset; canonical name OK).
- [ ] Add a two-span-one-bullet fixture: a bullet with both `` `mode=x` `` and
      `` `length=brief` `` → still rejects `length`.

## 4. Live-corpus conformance — tests/test_skills.py

- [ ] Import `argument_vocabulary_errors` from `installer.registry`.
- [ ] Add `test_argument_vocabulary_conformance`: for `name in SKILL_NAMES`,
      slice the `## Arguments` section from `skill_text(name)` (same slice logic;
      factor a tiny local helper), assert
      `argument_vocabulary_errors(name, section) == []` with `name` in the msg.

## 5. Changelog + manifest

- [ ] Bump `manifest.json` version (next patch, e.g. 0.66.8) **before**
      `make generate`.
- [ ] Add `CHANGELOG.md` top entry `## 0.66.8 - 2026-08-05` documenting the full
      A-006 rename set + the now-active covered-axis guard; cite A-006.

## 6. Generate + validate

- [ ] `make generate` (embeds version into catalog/README).
- [ ] `.venv/bin/python .github/scripts/generate-skill-surfaces.py --check` → 0.
- [ ] `make test` → green (new negative + corpus cases pass).
- [ ] `make check` → green (test + lint + release-check).

## Validation commands (ACs)

```bash
.venv/bin/python .github/scripts/generate-skill-surfaces.py --check   # exit 0
make test
make check
# Prove the guard bites (throwaway, revert after):
#   temporarily add `length=brief` to a skill's Arguments → --check exits nonzero
```

## Review gates

- Convergence-boundary two-lane adversarial review (host + Codex) on prd/design/
  implement before `task.py start` (planning-adversarial-review rule).
- sd-ship Stage 2 sd-review + Copilot after implementation.

## Rollback points

- After step 2: revert registry + generator hunk if the guard misfires on the
  corpus (should not — corpus already migrated).
- Before push: `git restore` the four files; no external state touched.
