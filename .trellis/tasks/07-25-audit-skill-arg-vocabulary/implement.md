# Implement — Pack-wide skill argument vocabulary (A-006)

This parent owns the vocabulary decision, the shared reference, and the
enforcement contract. Consumer-visible renames are split into ordered child
tasks so no single PR carries a large breaking change and `make check` never
fails mid-migration. Canonical picks and the D-1/D-2/D-3 taxonomy are
operator-confirmed; see `design.md`.

## Ordering rationale

Enforcement cannot land first — it would fail `make check` on every
still-non-canonical skill. So: reference first (adds only a citation), then the
mechanical verbosity rename, then the `format=` density judgment, then the
primary/discrete renames, then hard enforcement last. Within the verbosity
child, `se-technical-editor depth=→coverage=` precedes reserving `depth=`.

## Child tasks (ordered)

1. **`08-04-arg-vocab-reference`** — Ship the 3-axis vocabulary reference +
   reserved-name registry (`depth=`/`sensitivity=` ladders; name-only `input=`,
   `sources=`, `min_sources=`, `coverage=`, `privacy=`, `evidence=`, `format=`).
   Define the canonical-vocabulary constant (single source of truth). Fanned via
   `_shared/references/` + `SHARED_REFERENCES`, so consumer bodies gain the
   required one-line citation (`test_skills.py:389`) — no *argument* changes.
   Version bump + changelog.
2. **`08-04-arg-vocab-verbosity`** — Mechanical verbosity rename to
   `depth=brief|standard|deep` (subset values; `brief|full`→`brief|deep`):
   every `length=` and verbosity-sense `detail=` (23 skills) plus normalize the
   6 existing off-ladder `depth=` declarations (~29 touched). First rename
   `se-technical-editor depth=full|focused`→`coverage=full|focused`; resolve
   `se-author` numeric length via `target_words=`. No `format=` judgment here.
   Regenerate mirrors; version bump + changelog.
3. **`08-04-arg-vocab-format`** — Classify each `format=` declaration; migrate
   pure density ladders (`compact|standard`, `standard|compact`, e.g.
   se-thread-digest, se-meeting-follow-through) to `depth=`; leave structural
   shapes as `format=`. ~4 judgment calls. Regenerate mirrors; version bump +
   changelog.
4. **`08-04-arg-vocab-locator`** — Primary-artifact + discrete renames (D-1/D-2):
   `source=` (se-capture, se-presentation, se-publish) and `inputs=` (se-digest)
   → `input=`; se-research count `sources=N`→`min_sources=N`; se-red-team
   redaction `detail=`→`sensitivity=`. Leave `sources=` (reference lists),
   `privacy=`, `evidence=` untouched. Regenerate mirrors; version bump +
   changelog.
5. **`08-04-arg-vocab-enforce`** — Enforcement. Add covered-axis known-alias name
   checks + `depth=`/`sensitivity=` ladder **set-membership** checks to
   `validate_skill()`, parsing every inline-code span per bullet. Negative
   fixtures in `tests/test_generate.py` (prove rejection) + live-corpus case
   beside `tests/test_skills.py:145` (prove conformance). Consume the child-1
   constant. Version bump + changelog documenting the full A-006 rename set.
   Lands last; `make check` green with the guard active.

Each child is independently planned, implemented, checked, archived, and
reverted. Ordering lives here and in each child `prd.md`, not a dependency
system. (A fifth child, `08-04-arg-vocab-format`, is created for D-3; the parent
`subtasks` list will show five children.)

## Per-child validation gate

```bash
python3 -m pytest tests/test_skills.py tests/test_generate.py -q   # or: make test
make generate                                                       # regenerate mirrors
make release-check                                                  # payload + drift gate
git diff --stat
```

`make release-check` (not `make generate --check`) is the generator check-mode
gate; it also enforces the manifest bump + changelog heading for `templates/**`/
`generated/**`/`installer/**` changes. The enforcement child additionally
requires `make check` green with the rule active and a failing-case proof:
`.venv/bin/python .github/scripts/generate-skill-surfaces.py --check` exits
nonzero on a deliberately off-ladder value.

## Parent acceptance (integration)

After all five children archive:

- Reference shipped + cited; enforcement diagnostic points at it.
- `.venv/bin/python .github/scripts/generate-skill-surfaces.py --check` and
  `make test` reject a **known** non-canonical covered-axis alias or off-ladder
  value (proven by a deliberate violation + negative fixtures). The guarantee is
  regression-prevention under known aliases + ladders, not detection of an
  arbitrary future semantic alias.
- All covered skills conform; `CHANGELOG.md` documents every rename with A-006;
  `sources=` (reference), `privacy=`, `evidence=`, `format=` shapes, `mode=`,
  `scope=` left intact.

## Rollback points

- Each child PR reverts independently.
- Enforcement (child 5) reverts alone to disable the guard.
- The reference (child 1) is additive.

## This planning iteration

No skill bodies or code change in this parent iteration. Deliverables: `prd.md`,
`design.md`, `implement.md`, five child stubs. The planning adversarial review
(host + Codex, two rounds) ran at the convergence boundary; its D-1/D-2/D-3
decisions were operator-resolved. Migration children execute in later work-loop
iterations.
