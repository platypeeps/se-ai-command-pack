# Implementation plan: `scope=session` for se-review-skills

Ordered checklist. Validation commands inline; rollback is `git checkout --`
per file before commit, or reverting the single feature commit after.

## 1. Pre-edit pin verification (prove the pins can fail)

For every phrase to be pinned in step 4, verify absence from **both** unedited
target files:

```bash
for f in templates/skills/se-review-skills/SKILL.md \
         templates/skills/se-review-skills/references/report-schema.md; do
  echo "== $f"
  git show HEAD:"$f" | python3 -c "import sys; t=sys.stdin.read().lower()
for p in [p.lower() for p in (
    'post-inventory filter',
    'identity-unresolved',
    'name narrows, provenance decides',
    'resolved review scope',
    'analyzer inventory boundary',
    'selection digest',
    'never a fallback to repository-plus-installed discovery',
    'scope=session\` with \`sessions=off',
)]:
    print(('PRESENT ' if p in t else 'absent  ') + p)"
done
```

Expected: every line `absent` in both files. A `PRESENT` phrase must be
re-worded before it may be pinned. Record the output in the PRD completion
evidence.

## 2. SKILL.md edits

- [ ] `scope=` argument line (`:60`): add `session` to the value list with a
      one-clause description ("derive the reviewed set from confirmed
      invocations in the inspected sessions").
- [ ] Arguments section: add the `scope=session sessions=off` argument-error
      rule and the `scope=session` + `skill=`/`family` rejection rule (name
      both arguments in the error).
- [ ] New workflow step after the observed-use pass (step 6, `:156`): the
      session-selection procedure — analyzer invoked with `--scope` omitted
      and no `--skill` selectors; dedup first, then join by normalized name;
      the three outcomes of design Decision 1; report block contents; empty
      result naming the session stage; the `:1606-1607` inventory failure
      attributed to the inventory stage.
- [ ] Report header rule: resolved review scope vs analyzer inventory
      boundary (design Decision 3), preserved JSON untouched.
- [ ] Session-selection report block: selected entries recorded under the
      analyzer's deduplication key verbatim (owned: canonical root +
      resolved canonical path; unowned: name + sha256), each with its
      confirming retained record(s), plus the selection digest computed per
      the design's deterministic serialization (sorted no-whitespace JSON of
      key arrays + record identities as locator/turns string pairs, sha256
      hex). No new request argument — the digest is report content.
- [ ] Steps 10 and 12 (`:190`, `:207`): acting on a session-scoped report
      requires the snapshot ID match **and** a recomputed-from-the-report
      digest equal to the stamped digest (missing/corrupt/non-matching block
      fails closed); the unchanged mutation-revalidation contracts run
      exactly as in existing scopes; the reviewed set is never re-derived by
      fresh session inspection — new session evidence means a new review
      run.

## 3. report-schema.md edit

- [ ] Additive session-selection section: confirmed set under deduplication
      keys with confirming records, the selection digest and its
      verification rule, identity-unresolved list with candidate entries,
      absent-from-inventory coverage notes, resolved-scope/inventory-boundary
      pair. No existing line reworded.

## 4. Tests (`tests/test_skills.py`)

- [ ] New test class following `ReviewSkillsGotchaMandateTest`
      (`tests/test_skills.py:4077`): section-scoped pins via
      `skill_section("se-review-skills", ...)` for the behaviors listed in
      the design test plan, plus a `normalized_resource` pin for the
      report-schema session section.
- [ ] Prove the pins per `quality-guidelines.md:129-152`, restoring **every**
      tested source from HEAD for the failing run:

```bash
TEST=<SessionScopeTestClass>
T1="$(mktemp)"; T2="$(mktemp)"
F1=templates/skills/se-review-skills/SKILL.md
F2=templates/skills/se-review-skills/references/report-schema.md
cp "$F1" "$T1"; cp "$F2" "$T2"
git checkout HEAD -- "$F1" "$F2"
.venv/bin/python -m unittest discover -s tests -p test_skills.py -k "$TEST"  # expect FAILED
cp "$T1" "$F1"; cp "$T2" "$F2"; rm -f "$T1" "$T2"
.venv/bin/python -m unittest discover -s tests -p test_skills.py -k "$TEST"  # expect OK
```

## 5. Release surface

- [ ] Locate the version source that generates `manifest.json` `version`
      (`0.68.0`) and bump to `0.68.1`.
- [ ] `CHANGELOG.md`: new dated `## 0.68.1 - 2026-08-09` heading describing
      the `scope=session` capability addition.
- [ ] `make generate` — regenerate the committed Claude entrypoint and
      catalog surfaces from the canonical SKILL.md; stage the regenerated
      files with the commit (`make check` only detects drift via
      `generate-skill-surfaces.py --check`, it does not regenerate).
- [ ] `make check` — full suite, lint, release payload gate, provenance all
      green: `Ran <N> tests ... OK`, `All checks passed!` (test count rises
      with the new class).

## 6. Ship

- [ ] Commit (feature + tests + changelog + version in one intended commit).
- [ ] Nested `sd-ship until=merge` under the work-loop trusted context.
