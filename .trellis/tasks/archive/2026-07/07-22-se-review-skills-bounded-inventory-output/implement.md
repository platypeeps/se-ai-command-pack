# Implementation plan: bounded se-review-skills inventory output

## Ordered checklist

- [x] Add destination validation, existing-artifact provenance validation,
      destination fingerprinting, atomic JSON writing, and bounded envelope
      helpers to `skill_review.py`.
- [x] Add `--output` and `--output-root` arguments while preserving legacy and
      pretty stdout behavior.
- [x] Ensure bounded failures return nonzero, preserve existing content, clean
      temporary files, and never claim an artifact was written.
- [x] Add focused CLI tests for large-output preservation, snapshot/count
      equivalence, opt-in persistence, safe replacement, path/symlink/root
      rejection, and interrupted writes.
- [x] Update `se-review-skills/SKILL.md` with bounded-mode invocation,
      destination authority, artifact verification, and recovery guidance.
- [x] Update the installed-inventory code-spec with the new CLI, envelope,
      validation, and test contracts.
- [x] Bump the pack version and changelog, then run `make generate` and
      `make repomix` for shipped/generated parity.

## Validation

```text
.venv/bin/python -m unittest discover -s tests -p 'test_skill_review.py'
.venv/bin/python -m unittest discover -s tests -p 'test_skills.py'
make generate
make check
git diff --check
```

Also exercise the analyzer directly in a temporary output root and verify the
stdout envelope, complete artifact JSON, snapshot equality, and no temporary
file residue.

## Risk And Rollback Points

- Destination validation and replacement provenance are the primary data-loss
  boundary; do not relax them to make tests convenient.
- Keep `build_inventory()` and its payload untouched so legacy and bounded
  modes cannot drift semantically.
- Stop before generation if focused filesystem tests fail.
- Stop before publication if release payload/version or generated-target parity
  fails.
