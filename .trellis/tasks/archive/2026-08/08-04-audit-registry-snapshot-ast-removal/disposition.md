# Disposition: remove the AST registry fallback

**Shipped.** `platypeeps/se-ai-command-pack#239`, branch
`task/audit-registry-snapshot-ast-removal`, base
`568049fc6465385589176cefded455f768e136c7`, implementation commit `fc606c4`,
planning commit `df9692a`. Release 0.70.0.

## What shipped

`skill_review.py` resolves the registry from `generated/registry-snapshot.json`
alone. `_parse_registry`, `_assignment`, `_string_value`, `_call_value`, the
`if registry is None:` fallback branch and `import ast` are gone. The consumer no
longer opens `installer/registry.py` in any checkout; the *generator* still reads
it, which is the intended split.

The two `None` causes separated:

- **Symlinked path** raises `ReviewError` from inside `_load_registry_snapshot`,
  unconditionally, in every checkout. The check runs before any read, so the
  target is still never opened.
- **Absent file** stays `None`; `_package_context` applies policy — `ReviewError`
  when `name in FIRST_PARTY_REMOTES`, `_empty_registry()` otherwise.

## Acceptance criteria

| Criterion | Evidence |
| --- | --- |
| sd-twin verifiably complete first | PR #483 merged as `232138a8`; that task's `disposition.md` |
| No AST surface remains | Both greps return no matches; all four symbols and `import ast` gone; `_crosses_symlink` retained with 3 call sites |
| Absent → error in a first-party pack; symlink → error everywhere, not opened | exit 2 with each message; paired-arm marker evidence below |
| Non-first-party checkout byte-identical | Baseline captured before the edit; identical after on all four fields |
| Messages distinguishable | The two strings share no substring; each test asserts its own *and* the other's absence |
| Non-first-party behaviour recorded with justification | `design.md`, "The decision the task turns on"; PR body, "absent ≠ error everywhere" |
| No surviving AST-fallback claim in the spec | Whole-file grep, not the diff — see below |
| Suite passes, no net loss of fail-closed coverage | `Ran 53 tests ... OK`; fail-closed 4 → 8 |

All eight satisfied.

## Gate results

| Gate | Result |
| --- | --- |
| G0 baseline (before the edit) | `{"declaredPlatforms": [], "familyOrder": [], "ownerKind": "repo-local", "skillFamilies": {"demo": "Uncategorized"}}` |
| G1 removal surface | both greps empty; `_crosses_symlink` count 4 = definition + 3 callers; syntax ok |
| G1b diff boundary | 7 files, all in the allowed set; nothing under `installer/`; no `+`/`-` line names either protected symbol; `_registry_from_snapshot`'s executable lines byte-identical to base |
| G2 repo-local | before == after, exact |
| G3 first-party absent | exit 2, `first-party pack 'se-ai-command-pack' ships no registry snapshot at ...; the generator must write it` |
| G4 symlink, paired arms | link arm: exit 2, `refusing to follow symlinked registry snapshot path ...`, marker count **0**. Control arm, identical bytes as a regular file: exit 0, marker count **1** |
| G5 messages | no shared substring |
| G6 suite | `Ran 53 tests ... OK` |
| G7 spec | whole-file grep: the only `AST fallback` hit is the new sentence "There is no AST fallback"; every surviving `installer/registry.py` mention is about the producer or source-of-truth layout |
| G8 `make check` | exit 0; `release payload gate: version 0.69.0 -> 0.70.0; changelog heading matches; one version step` |
| G9 falsifiability | consumer restored from base: **4 FAIL**, and the new repo-local test **passes against both** |

## Findings worth keeping

**The obvious removal was wrong, and only measurement showed it.** "Delete the
fallback, so absent becomes an error" would have withdrawn support for every
non-pack checkout. `_parse_registry` never raised: for a repository with no
`installer/registry.py` the "fallback" was not a parse but a silent empty
registry, and `ownerKind: "repo-local"` is a first-class advertised value. The
PRD had anticipated this as a legitimate outcome; the criterion was amended
because its premise measured false, and a *new* criterion was added requiring the
repo-local path to be provably unchanged — a narrowing paired with a new
obligation, since before the amendment nothing protected that path at all.

**The predicate is pack identity, not `owner_kind`.** `owner_kind` resolves to
`se-`/`sd-upstream` only when the remote also matches, so a fork would resolve
`unresolved` and could delete its snapshot to review with an empty registry —
exactly the defect-masking the fail-closed rule exists to prevent. Recorded
limitation: an unreadable `manifest.json` yields `name = None` and degrades to the
empty registry. Already true of `owner_kind`; closing it means deciding what an
unreadable manifest means tool-wide, outside this boundary.

**A test list assembled from names misses the tests that exercise the surface
without naming it.** Planned 3 tests and predicted coverage 6; the real surface
was 11 and the measured coverage 8. `write_se_pack()` declared the pack name and
wrote `installer/registry.py`, so all 38 tests built on it hit the new error until
the fixture moved to snapshots; `test_symlinked_parent_directory_is_not_followed`
was missed because the list enumerated tests naming "fallback"; three tests drove
behaviour by rewriting `installer/registry.py` *after* the fixture ran and had
been passing for a reason that no longer exists. The prediction is left visible in
`implement.md` beside the measurement rather than restated.

**An error message is not evidence about which files were read.** The adversarial
review rejected a planned `st_atime` "was it opened" probe as unreliable under
`relatime`/`noatime`/APFS. The replacement is paired arms over identical bytes
carrying a distinctive `familyOrder` marker: refused through a link with the
marker absent from the output, consumed as a regular file with the marker present.
The control arm is what makes the refusal arm non-vacuous.

**G9's discriminator cuts both ways, and that is the point.** Against the base
consumer the four converted tests fail *and* the new repo-local test passes. A
repo-local test that failed there would have meant the change altered that path;
one that passed only after the change would have meant it was testing the
implementation rather than the invariant.

## Review round: three findings, all valid, and one caught a premise error

Copilot reviewed PR #239 and raised three test-strength findings. All three were
verified against the code before acting, and all three held.

**The repo-local test asserted only the skill family**, while the criterion it
exists for names `ownerKind`, `familyOrder` and `declaredPlatforms` too. Adding
those assertions failed immediately: `'unresolved' != 'repo-local'`. The fixture
was a plain directory, but the G0 baseline was measured on a throwaway **git**
repository, so the test had been pinning a different branch than the one it
claimed. Both reach the same empty-registry code, which is why the weak assertion
passed. Fixed by `git init`-ing the fixture. A criterion cited by name in a test
docstring is not the same as a criterion asserted by the test.

**The paired arms proved non-influence, not non-opening.** The control arm makes
the marker's absence real evidence -- identical bytes as a regular file do surface
it -- but a loader that read the file and then refused would still keep the marker
out of the error. Added a guard on `_read_regular_text`, the single funnel the
loader reads a snapshot through, that fails if it is called with the symlinked
path. Exact, unlike the `st_atime` probe the planning review rejected.

Falsified deliberately: with the symlink check moved *after* the read in
`_load_registry_snapshot`, the guard fires --
`AssertionError: snapshot was read before refusal: .../generated/registry-snapshot.json`
-- while the marker assertion alone still passes. The finding covers a regression
class the paired arms cannot see.

**The parent-directory symlink test stopped at the unit call** while the leaf test
asserted end to end. Real asymmetry, since only the end-to-end path proves
`_package_context` does not treat a symlinked `generated/` more leniently than a
symlinked leaf. Added the `inventory()` assertion.

Round result: `Ran 53 tests ... OK`, `make check` exit 0.

## Not done here

`FIRST_PARTY_REMOTES`, discovery globs and adapter paths remain outside the
snapshot — `08-04-audit-registry-snapshot-layout-assumptions`. The snapshot
`schemaVersion` and contents are unchanged.

## Rollback

Revert `fc606c4`. Both producers are unaffected, so the fallback returns with no
other coordination. No data migration, no persisted state.
