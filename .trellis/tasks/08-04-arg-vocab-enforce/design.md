# Design — Argument vocabulary enforcement (A-006, last child)

## Status

Implementation-ready. Builds on the parent decision record
`07-25-audit-skill-arg-vocabulary/design.md` (D-1/D-2/D-3, two-lane review). The
four migration children (reference, verbosity, format, locator) have shipped, so
every canonical rename is already in the corpus; this child adds the guard that
keeps it from regressing and records the consumer-visible renames.

## Guarantee (scoped, per parent review)

The guard prevents regression **under a known covered-axis alias or an off-ladder
value**. It does NOT claim "no drift under any conceivable future name" — a
covered concept reintroduced under a brand-new arbitrary name is not inferable
from a `key=values` span alone, and the parent acceptance claim is narrowed to
match. The closed alias set and the two enforced ladders are the whole contract.

## Single source of truth

`installer/registry.py` already owns the canonical vocabulary constants:

- `CANONICAL_ARGUMENT_LADDERS = {"depth": (brief, standard, deep),
  "sensitivity": (minimal, restricted, standard)}` — name + set-membership
  enforced.
- `RESERVED_ARGUMENT_NAMES` — name reserved, values per-skill (not enforced).

This child adds one constant and one pure function to the same module, so the
checker, the negative fixtures, and the live-corpus test all consume one
definition — never a duplicated list.

### New constant — the closed alias set

```python
# Known non-canonical aliases for the enforced covered axes. A skill declaring
# one of these names is a hard error: the axis has a canonical name. Closed set
# by construction — see design guarantee.
KNOWN_COVERED_AXIS_ALIASES: dict[str, tuple[str, ...]] = {
    "length": ("depth",),        # verbosity
    "source": ("input",),        # primary artifact under action
    "inputs": ("input",),        # primary artifact under action
    "detail": ("depth", "sensitivity"),  # historical verbosity + se-red-team redaction stray
}
```

`detail` maps to both canonicals because it was used for both senses pre-A-006;
the error message names both so the fix is unambiguous. `input` is the canonical
target of `source`/`inputs`; it is already in `RESERVED_ARGUMENT_NAMES`, so a
skill that *correctly* uses `input=` is untouched.

### New pure function — the parser + checker

```python
def argument_vocabulary_errors(label: str, arguments_section: str) -> list[str]:
    """Covered-axis violations in one skill's `## Arguments` body text.

    Parses every inline-code `key=values` span (a single bullet may declare two,
    e.g. se-ask-me). Rejects a covered axis under a known alias, and depth=/
    sensitivity= values outside their ladder set (membership, not order)."""
```

- Span regex: `` `([^`\n]+)` `` over the section text; keep spans that contain
  `=`. Split once on `=`: left = candidate name (strip trailing chars, take the
  identifier), right = values.
- Name normalization: a declaration span is `` `name=v1|v2` `` or bare `` `name=` ``.
  Extract `name` as the leading `[a-z0-9_-]+` before `=`. Ignore spans whose left
  side is not a bare argument token (e.g. prose fragments) — the corpus test
  proves the real skills parse cleanly.
- Alias check: `name in KNOWN_COVERED_AXIS_ALIASES` → error naming the
  canonical(s).
- Ladder check: `name in CANONICAL_ARGUMENT_LADDERS` → every `|`-separated value
  token that is a non-empty word must be in the ladder set; report the offending
  value(s). Empty value list (a bare `` `depth=` `` prose reference) is vacuously
  fine.
- Names that are neither alias nor ladder are allowed (reserved or per-skill
  owned) — no error. This is the scoped guarantee in code.

Returned strings are prefixed with `label` so they read like the other
`validate_skill` errors.

## Integration point — `validate_skill()`

`.github/scripts/generate-skill-surfaces.py:208 validate_skill(name)` already
parses frontmatter/body and accumulates `errors`. Add, after the existing
section-order loop:

1. Slice the `## Arguments` section out of `body` (from the `\n## Arguments\n`
   index to the next `\n## ` heading, or end of body). `## Arguments` is in
   `REQUIRED_SECTIONS`, so every skill has it; a skill whose section is missing
   already errors upstream.
2. `errors.extend(registry.argument_vocabulary_errors(label, section))`.

`validate_skill` is called by `validate_skills()`, which raises
`GenerationError` on any error; that surfaces as a nonzero
`.venv/bin/python .github/scripts/generate-skill-surfaces.py --check`,
`make release-check`, and `make check`. Confirmed by parent review: `make
generate --check` does NOT forward `--check` (Make runs write-mode), so the ACs
cite the direct interpreter invocation.

Import: `generate-skill-surfaces.py` already does `from installer.registry
import (...)`; add `argument_vocabulary_errors` (and, if referenced directly,
the constants — but the function encapsulates them, so only the function needs
importing).

## Tests — two places, one parser

- **Negative validator fixtures** — `tests/test_generate.py`
  `SandboxGeneratorTest` (`write_skill()` / `assert_validation_error()`).
  `VALID_SKILL`'s Arguments body is just "Text."; write variants whose Arguments
  section declares:
  - `` `length=brief|standard` `` → error names `depth`;
  - `` `source=` `` → error names `input`;
  - `` `depth=brief|verbose` `` → error names the off-ladder `verbose`;
  - `` `sensitivity=secret` `` → error names the off-ladder value.
  Each asserts the specific fragment. Also one positive: a skill declaring
  `` `depth=deep|brief` `` (subset, reordered) and `` `input=` `` passes
  `validate_skills()` — proves order-independence and that canonical use is not
  flagged.
- **Live-corpus conformance** — `tests/test_skills.py` beside the existing
  section/argument pins (~:145). For every `name in SKILL_NAMES`, extract the
  `## Arguments` section from `skill_text(name)` and assert
  `argument_vocabulary_errors(label, section) == []`. Imports
  `argument_vocabulary_errors` from `installer.registry` (test_skills already
  imports from that module). This proves the shipped corpus conforms and pins it.

The negative fixtures prove *rejection*; the corpus test proves *conformance*;
both call the one registry function — no duplicated alias/ladder list in tests.

## Changelog + manifest

`CHANGELOG.md` gains a new `## <semver> - <date>` entry documenting the full
A-006 rename set (length/detail→depth, source/inputs→input, sources=N→
min_sources=N, se-red-team detail→sensitivity, se-technical-editor depth→
coverage, se-author target_words split) and the newly active guard. `manifest.json`
version bumps to the same semver **before** `make generate` so the embedded
catalog/README match. Release gate `check-release-payload.py --base auto`
requires the manifest bump + a top changelog heading matching the version.

## Compatibility / rollout

- Additive validation only; no skill content changes are required because the
  corpus already conforms (four migration children shipped). If the corpus test
  fails, that is a real residual drift to fix in this task, not a guard bug.
- Rollback: revert the registry function + constant, the `validate_skill` call,
  and the two test additions. No data migration, no consumer-visible runtime
  behavior beyond generation-time validation.

## Risks

- **Over-broad parsing** flags a legitimate prose span containing `=` inside the
  Arguments section. Mitigation: restrict to the Arguments section only, require
  a bare leading argument token, and let the live-corpus test catch any real
  false positive before merge.
- **Under-broad parsing** misses a two-arg bullet. Mitigation: parse every span
  in the section, not one-per-bullet; add a fixture with two spans in one bullet.
- **`detail` dual meaning** — mapping to both canonicals keeps the message
  correct regardless of which sense a regressor intended.
