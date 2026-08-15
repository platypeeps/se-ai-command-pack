# Ledger drift: verification sample at HEAD 564d4a2

Method: for each finding, re-run its own recorded evidence against the working
tree. A finding counts as resolved only when the cited construct is gone or
inverted, not merely when a task with a similar name sits in `archive/`.

All 44 findings currently read `status: open`.

## Verified resolved (evidence inverted at HEAD)

| ID | Ledger claim | Observed at HEAD |
|----|--------------|------------------|
| A-001 | `git ls-files .claude` -> 0 | 107 tracked files |
| A-003 | `HELP_CATALOG_PATH` under `templates/` | `generate-skill-surfaces.py:73` points at `GENERATED_REFERENCES_DIR` |
| A-009 | `_is_relative_to` and `_is_within` both defined | only `_is_relative_to` at `skill_review.py:217` |
| A-011 | `os.umask(0)` per installed file | `installer/fileops.py:67-77` captures `_PROCESS_UMASK` once at import |
| A-013 | `_run_git` unbounded | `installer/management.py:397` passes `timeout=GIT_TIMEOUT_SECONDS` |
| A-014 | raw traceback on git failure | `create-release-tag.py:34,36` catch `FileNotFoundError` and `TimeoutExpired` |
| A-019 | `shutil.copyfile` follows symlinks | `fileops.py:406` `_open_exclusive_backup` + `copyfileobj` at `:461` |
| A-020 | no coverage floor | `Makefile:106` `coverage report --fail-under=80` |
| A-021 | tests inherit global git config | `tests/test_release_gate.py` passes `env=git_env()` at 5 call sites |
| A-023 | docs omit `generated/` | 3 references in `CONTRIBUTING.md`, 2 in `README.md` |
| A-024 | `make setup` undocumented | present in `README.md` and `CONTRIBUTING.md` |
| A-025 | 1 MB map committed | `git ls-files docs/repomix-map.md` -> 0; `.gitignore` cites policy A-025 |
| A-026 | dead wrapper present | the repo-root skill-review wrapper under `scripts/` is deleted |
| A-031 | no dependency-update path | `.github/dependabot.yml` present |
| A-035 | `release-check` vacuous | `Makefile:163` passes `--base auto` |
| A-036 | payload Python outside lint | `Makefile:7-8` `LINT_PATHS`/`MYPY_PATHS` both list `skill_review.py` |
| A-038 | no pip caching | `tests.yml:37,62,77` `cache: pip` |
| A-039 | no concurrency group | `tests.yml:13` `concurrency:` |
| A-040 | payload prefixes omit installer | `check-release-payload.py:42,48` include `installer/` and `install.py` |
| A-044 | README promises `$CODEX_HOME` | `README.md:164` states `~/.codex` is read regardless of `$CODEX_HOME` |

## Verified still present

| ID | Observed at HEAD |
|----|------------------|
| A-002 | `_parse_registry` still live in `skill_review.py` (5 occurrences); tracked by blocked task `08-04-audit-registry-snapshot-ast-removal` |
| A-008 | `installer/fileops.py:145` still `continue`s on `ALWAYS_INSTALL`/`IF_NOT_EXISTS` before the platform check at `:152` |
| A-032 | `.opencode/package.json` still declares floating `@opencode-ai/plugin`; local disposition merged, upstream relay parked |

## Needs judgment, not a mechanical check

| ID | Why |
|----|-----|
| A-015 | `hasNextPage` no longer appears in `housekeeping.sh`; the loop was restructured, so "is the cap adequate" is a read, not a grep |
| A-016 | `work-loop.py:717` still calls `os.close(descriptor)` in the failure path after `os.fdopen` at `:705` owned it. An `except OSError` now wraps it, which suppresses `EBADF` but does not prevent closing a reused descriptor |
| A-018 | the `/tmp` cache variables moved out of `toolchain.sh` into `sd_ai_command_pack_lib.py:119`; whether they are UID-qualified there is unverified |
| A-022 | `tests/test_management.py` shows no subprocess/e2e markers for `update`; absence of a grep hit is not proof the coverage is missing |

## Reading

20 of the 27 findings sampled are demonstrably fixed while still marked
open. The status field was never written back when the fixing PR merged. The
archived task list contains a near one-to-one counterpart for most findings
(`07-25-audit-coverage-floor`, `08-08-installer-dead-code-trim`,
`07-25-audit-ci-workflow-hygiene`, ...), which is corroboration but not
evidence: a task can be archived as won't-do.

---

# Completed sweep: remaining 17 + the 4 judgment cases

## Newly verified fixed

| ID | Ledger claim | Observed at HEAD |
|----|--------------|------------------|
| A-004 | no editable-source vs vendored distinction | `CONTRIBUTING.md:17` "Repo-own source vs vendored installs"; the "all 26 files" count matches `ls scripts/` |
| A-006 | conflicting argument vocabularies | `sources=` renamed to `min_sources=`; `tests/test_skills.py:190` `test_argument_vocabulary_conformance` enforces it |
| A-007 | no citation-closure validation | `generate-skill-surfaces.py:454-456` implements reverse citation-closure |
| A-010 | two unbound frontmatter grammars | still two parsers, but `skill_review.py:522` binds them via `tests/test_frontmatter_conformance.py` |
| A-012 | stale-lock unlink without identity re-check | `work-loop.py:1071` deletes "verifying identity" |
| A-017 | update trusts unverified receipt path | `installer/management.py:294` source-trust gate, labelled "audit A-017, hardened by A-017/1" |
| A-027 | fleet collected serially | `status.py:19,3284` `ThreadPoolExecutor` in `collect_fleet` |
| A-028 | one GraphQL spawn per PR | `review-learnings.py:1951` aliased-batch query, batches of 20 (`:71`) |
| A-033 | transitives float unpinned | `requirements-dev.lock` committed, "fully pinned, hashed, wheel-only", `make lock-check` guards drift |
| A-037 | release gate PR-only | `tests.yml:89` `if:` covers `pull_request` **and** push to `refs/heads/main` |
| A-042 | no documented bump policy | `docs/SE_AI_COMMAND_PACK.md:1088` points at the `CONTRIBUTING.md` patch-versus-minor policy |
| A-043 | 42 hand-copied per-skill tests | `tests/test_generate.py:445,630` iterate `gen.SHARED_REFERENCES`; one copy remains |

## Judgment cases settled

| ID | Verdict | Reasoning |
|----|---------|-----------|
| A-015 | fixed | the shell `while hasNextPage` loop is gone from `housekeeping.sh` entirely. Pagination moved to `review.py`, which delegates paging to `gh --paginate` and caps accumulation at `:1322` (`> 1_000` rows raises `ReviewError`). The repeating-cursor loop the finding described no longer exists in pack code |
| A-016 | **open** | `work-loop.py:717` still calls `os.close(descriptor)` in the failure path after `os.fdopen` at `:705` took ownership. The wrapping `except OSError` swallows `EBADF` but does not stop the process from closing a descriptor another thread has since been assigned. Masking is not fixing |
| A-018 | fixed | the variables moved to `sd_ai_command_pack_lib.py:118-124`, and the cache root is UID-qualified at `:333` (`uid = str(os.getuid())`). Relocation *and* the defect gone |
| A-022 | fixed | `tests/test_update_e2e.py` exists |

## Newly verified still present

| ID | Observed at HEAD |
|----|------------------|
| A-005 | `AGENTS.md:13` still names only `/trellis:*`. A canonical `/sd:*` block was added at `:30-36`, so the local half improved, but the two upstream halves remain — owned by blocked task `08-10-upstream-entrypoint-routing-mechanisms` |
| A-029 | no memoization of changed-path or base-ref discovery in `review-preflight.mjs`; only `readTextCache` at `:21`, which is a different cache. The file was heavily restructured, so the original line numbers no longer resolve, but the memo the finding asked for is absent |
| A-030 | `review-scope.sh:127` still runs `grep -Fxq` per path, called per changed file from `:373` |
| A-034 | half addressed, and the half that closed is not the one a file-absence check would catch. The script moved to `.github/scripts/update-repomix`, which sets `NPM_CONFIG_IGNORE_SCRIPTS=true` at `:26` — the lifecycle-script half is closed — but `npx --yes repomix@1.16.1` at `:27` still resolves transitives fresh with no lockfile |
| A-041 | 89 tags against 90 changelog headings; `git tag | grep 0.53.0` returns nothing. Still untagged |

## C-6 settled: the A-032 contradiction

Task `08-10-upstream-relay-opencode-plugin-dep` states A-032's "local
disposition is complete and merged in PR #197". `git log -- .opencode/package.json`
shows one commit, `0863757`, the original add. The dependency was never removed.

The task's claim is about the *audit* disposition — deciding the local answer is
"relay it upstream" — not about editing the package file. Both records are
consistent under that reading, and A-032 stays `open`: the declared floating
dependency is still there.

## Final tally

35 fixed, 9 open (A-002, A-005, A-008, A-016, A-029, A-030, A-032, A-034,
A-041), 0 regressed. Of the 9, three are upstream-blocked (A-002, A-005,
A-032) and six are locally actionable (A-008, A-016, A-029, A-030, A-034,
A-041).

A-034 was initially and wrongly marked fixed on a `not exists("scripts/update_repomix")`
assertion — the exact "it moved" fallacy `design.md` warns about, caught only
because `make check`'s shell-syntax lane named the file at its new path. The
lesson is recorded rather than quietly corrected: a file-absence assertion is
only valid when deletion *is* the fix, as for A-026's dead wrapper.
