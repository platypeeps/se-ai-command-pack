# Test hermeticity and update e2e coverage

## Goal

`make test` passes on any contributor machine regardless of global git configuration, and the `install.py update` lifecycle — the one command that mutates the user's checkout — has a real end-to-end test.

## Requirements

- Scrub git environment in every subprocess-git test helper: GIT_CONFIG_GLOBAL=/dev/null and GIT_CONFIG_SYSTEM=/dev/null (or HOME pointed at a temp dir) — covers `tests/test_release_gate.py`'s `git()` helper and the raw `git init` calls in `tests/test_skill_review.py`'s `initialize_verified_se_repo` and `test_first_party_identity_with_wrong_remote_is_unresolved`. [A-021]
  (Anchored by symbol: the audit's line numbers — `test_release_gate.py:17`, `test_skill_review.py:904`/`:1238` — had already drifted by ~20 and ~150 lines respectively when this task was implemented.)
- Add one update e2e in the ReleaseTagTest style: temp clone with a local bare origin one commit ahead → run install.py update → assert the pull happened and installed files refreshed. [A-022]
- Cover a second hermeticity axis the audit findings do not name: a test that reads an untracked or gitignored file. Global git configuration is state a runner *has* and a contributor's machine differs on; this is the mirror case — state a working checkout has and a runner does not. It fails in the more dangerous direction, because the local run is the green one. Demonstrated below, so this requirement is drawn from an incident rather than from speculation.

## Acceptance Criteria

- [x] Suite passes with a hostile global config (e.g. commit.gpgsign=true, core.hooksPath set) simulated in CI or a dedicated test.
      **Evidence:** `make test-hermetic` — the whole suite under a hostile
      `core.hooksPath` at both file and command scope — reports
      `Ran 722 tests ... OK (skipped=2)`. Before the migration the same
      condition failed 61 tests (`test_release_gate` 33,
      `test_trellis_provenance` 26, `test_management` 2). The knob is
      `core.hooksPath`, not `commit.gpgsign`, because a missing signing key is
      not universal and `gpgsign` would pass vacuously where one exists.
      `tests/test_test_hermeticity.py`'s matched pair pins the two scrubs that
      can be pinned; removing either fails it.
- [x] The update e2e runs in CI and fails when the pull/refresh handshake breaks.
      **Evidence:** `tests/test_update_e2e.py` runs in the `unittest` lane and
      in `test-hermetic`. Its probe — deleting the applying `_run_installer`
      call in `update_pack` — fails only the sentinel assertion
      (`the pull landed but the installed tree was never refreshed`) while the
      fast-forward assertion still passes, which is exactly the half-broken
      handshake the criterion names.
- [x] No test reads a repository path that may exist in a working checkout but not in a fresh clone or on CI, unless it explicitly tolerates that path's absence. The criterion covers repo-relative paths the test treats as pre-existing content, judged tracked-vs-ignored as of test start; fixtures the test creates itself — temporary directories, files it writes and then reads — are out of scope, since a fresh checkout reproduces them. Where the choice exists, prefer a check that enumerates from the tracked tree over one that reads a machine-local artifact.
      **Evidence:** the `make test-hermetic` run above executes against a
      tracked-files-only copy, so every untracked and gitignored path is
      absent; it reports exactly two skips, and both are the declared,
      absence-tolerant reads (`.trellis/.template-hashes.json`,
      `docs/repomix-map.md`). `tests/test_test_hermeticity.py` additionally
      fails any new undeclared untracked read statically, and rejects a
      tracked path added to the declaration.

## Evidence: the 2026-08-10 incident (task 07-25-audit-repo-tooling-ownership, PR #206)

A new `tests/test_repo_tooling_ownership.py` read `.trellis/.template-hashes.json` unconditionally. That file is gitignored at `.gitignore:94`, so a working checkout has one and a runner never does. `make check` was green locally and every CI lane failed at `564d252` with `FAILED (errors=8, skipped=1)`.

Three properties of that failure are worth designing against:

1. **The local gate could not catch it.** `make check` ran against a file the runner cannot see, so the pre-push signal was green for exactly the reason it should have been red. Any mitigation that lives only in `make check` reproduces the same blind spot.
2. **Crashing was the lesser failure mode.** Making the read merely optional would have been worse: that file is the sole source for 32 paths, so an absent-file fallback silently reclassified vendored `.trellis/scripts/**` as repo-own on CI alone — green, and wrong. A hermeticity fix that degrades a verdict instead of failing is a regression wearing a fix's clothing.
3. **The repository already documented the property.** `.trellis/spec/backend/quality-guidelines.md:798` branches on `if [ -f .trellis/.template-hashes.json ]` and `:2366` calls it "the machine-local Trellis hash file". The test contradicted a written contract, which suggests the gap is discoverability, not knowledge.

The fix landed with the task (merged in `9d8f37f`): the coverage guard now enumerates from `git ls-files` so it runs everywhere, and the one assertion that genuinely needs the machine-local receipt skips explicitly when it is absent rather than passing vacuously. That shape — enumerate from the tracked tree, skip loudly when you cannot — is a candidate convention for this task to generalize.

A cheap detection idea for design to weigh: run the suite once with untracked and ignored files stashed away, which is close to what a runner sees. Cost and false-positive rate are unmeasured; treat it as a starting point, not a settled decision.

## Notes

- Audit findings: A-021 (P3/S), A-022 (P3/M) — .trellis/audit/report-2026-07-25.md.
- Evidence, anchored by symbol rather than by line: `tests/test_release_gate.py`'s `git()` and `run_script()` helpers; `tests/test_skill_review.py`'s `initialize_verified_se_repo`; the scrubbed environment formerly duplicated as `GIT_ENV` in `tests/test_management.py`, now `git_env()` in `tests/install_test_support.py`; and `installer/management.py`'s `_run_git`/`update_pack`.
- Planning depth: **Complex — needs `design.md` and `implement.md` before `task.py start`.** A real end-to-end test for `install.py update` means designing a hermetic harness for the one command that mutates a user's checkout: fixture checkout, isolation from global git configuration, and rollback assertions. That harness is a design decision, not an implementation detail.

## Planning adversarial review ledger

Three automatic rounds — the contract's limit — each with a host lane and a
Codex lane (`codex exec --sandbox read-only`), reconciled here. `C-R1-*` is
round 1 against the first `design.md`/`implement.md`, `C-R2-*` round 2 against
the rewrite, `C-R3-*` round 3 against the remediated set.

Every concern was addressed in the planning artifacts; none was rejected. One
correction is **scheduled rather than applied**: this PRD's own drifted evidence
lines (the `Requirements` and `Notes` citations to
`tests/test_release_gate.py:17`, `tests/test_skill_review.py:904`/`:1238`,
`tests/test_management.py:108`, `installer/management.py:146`) are corrected by
implementation step 8, which anchors them by symbol, not here — editing them now
would put the fix in a different commit from the evidence that verifies it.

### Round 1 — Codex (11)

| ID | Concern | Disposition |
| --- | --- | --- |
| C-R1-1 | D6's rule flags 26 paths against today's suite, so it cannot pass as specified | Rule narrowed to maximal ∧ exists-as-file ∧ untracked → exactly 2 |
| C-R1-2 | D6 cannot prove the universal third criterion; runtime paths are out of a static rule's reach | Limit stated in D6; D7 added as the run that proves it |
| C-R1-3 | D3 misses the `ast.IfExp` argv at `tests/test_repo_tooling_ownership.py:67` (12 sites, not 13) | Both branches examined; floor raised to the measured 13 |
| C-R1-4 | Four ambient git callers reach git without an `env=` keyword to add | Second D2 table + `hermetic_git_environment()` contextmanager |
| C-R1-5 | `git_env` leaves `GIT_CONFIG_COUNT`/`_PARAMETERS` live at command scope | Helper builds from a `GIT_*`-stripped environ |
| C-R1-6 | D4's positive half proves nothing — the hostile file was injected only into the negative half | Pair rewritten to inject ambiently (superseded again by C-R2-2) |
| C-R1-7 | D5's install may select no payload | `make_home` + `--all` (rationale corrected by C-R2-6) |
| C-R1-8 | D5's probe edits a working-tree file a `HEAD` clone never executes | Origin built from the tracked working tree |
| C-R1-9 | Step 5's verification command cannot discover a class added to `test_management.py` | Dedicated `tests/test_update_e2e.py` |
| C-R1-10 | Git 2.32 was being made a silent new minimum | Asserted in D4, documented in `CONTRIBUTING.md` |
| C-R1-11 | Step 7's "refreshed" line references were themselves wrong | Re-measured; step 8 now carries the verified numbers |

### Round 1 — host (5)

| ID | Concern | Disposition |
| --- | --- | --- |
| H-R1-1 | AST walk found 12 sites, not the drafted count | Independently confirmed C-R1-3 |
| H-R1-2 | Naive untracked rule produces 26 flagged paths | Independently confirmed C-R1-1 |
| H-R1-3 | Vacuity floors were guessed, not measured | All floors restated from measurements |
| H-R1-4 | `GIT_CONFIG_PARAMETERS` is a second command-scope channel | Covered by the wholesale strip |
| H-R1-5 | `--confirm-source` in D5 would mask a `source_root == ROOT` regression | Dropped, with the reason recorded |

### Round 2 — Codex (8, three blocking)

| ID | Concern | Disposition |
| --- | --- | --- |
| C-R2-1 | **Blocking.** D7's copy is not runnable: `git ls-files` never copies `.git`, and several tests enumerate or diff their own repository | D7 gains `git init`/`add`/`commit` under a clean environment, plus absolute interpreter resolution; measured before/after recorded |
| C-R2-2 | **Blocking.** D4 still cannot pin `GIT_CONFIG_GLOBAL`: the `GIT_*` strip removes the hostile value whether or not the assignment survives | Hostility now injected through `HOME`, which survives the strip; D1 gains a per-scrub table naming what is and is not pinned |
| C-R2-3 | **Blocking.** Step 6 omits the lane fixture in `tests/test_aggregate_ci_result.py` | Step 6 now lists four edits; `:159` is the test that catches a partial one |
| C-R2-4 | "25 maximal chains, measured 28" mixes units — 28 is distinct paths, occurrences are 54 | Floor restated as distinct literal paths, with the full count table |
| C-R2-5 | The 553 manifest rows are not all `templates/**` | Corrected to 492 `templates/**` + 61 `generated/**`; D5 now requires a `templates/**` mutation target |
| C-R2-6 | `make_home`'s stated rationale is void — `--all` bypasses the anchor gate | Rationale replaced with suite parity, citing `installer/fileops.py:155` and `tests/test_install.py:119-122` |
| C-R2-7 | `run_script` is at `tests/test_release_gate.py:42`, cited as `:41` | Corrected in both documents |
| C-R2-8 | The 39.4 s suite figure is not exactly reproducible | Restated as ~40 s with both measured runs |

### Round 2 — host (7)

| ID | Concern | Disposition |
| --- | --- | --- |
| H-R2-1 | Tracked-only copy fails 13 tests, all `not a git repository` | Same as C-R2-1, found independently and measured both ways |
| H-R2-2 | `Makefile:4` `VENV_PYTHON` is relative and `.venv` is untracked, so the lane would silently use a PyYAML-less system python | Absolute resolution required in step 6 |
| H-R2-3 | CI wiring is four places; `ci-result`'s `needs:` list was unlisted | Both documents now enumerate all four |
| H-R2-4 | Floor unit mismatch | Same as C-R2-4 |
| H-R2-5 | Manifest source split misstated | Same as C-R2-5 |
| H-R2-6 | `installer/management.py` citations off: the final `_run_installer` is `:510-521`, the confirmation branch begins `:327` | Corrected, and `:464`'s dirty-checkout refusal added to D5 |
| H-R2-7 | Under a hostile ambient configuration today's suite fails 61 tests in exactly `test_release_gate` (33), `test_trellis_provenance` (26), `test_management` (2) | Recorded as D2's runtime corroboration and as step 2's real acceptance number |

### Round 3 — Codex (7, one blocking)

| ID | Concern | Disposition |
| --- | --- | --- |
| C-R3-1 | **Blocking.** `$(CURDIR)/$(VENV_PYTHON)` cannot work on CI: `.venv` is gitignored (`.gitignore:12`) and the runner installs the lockfile into the `setup-python` interpreter (`.github/workflows/tests.yml:34-39`) | Replaced with `$(abspath $(RUN_PYTHON))`, measured to yield the local venv path and to leave an absolute runner path unchanged |
| C-R3-2 | The `OK (skipped=2)` figure was produced without hostility, but is cited as the lane's result | Both documents now label it benign, state the pre-migration hostile result beside it, and split which criterion each closes |
| C-R3-3 | D4's `patch.dict` lacks `clear=True`, so an inherited `GIT_DIR`/`GIT_INDEX_FILE` could pass the negative half for the wrong reason | `clear=True` over an explicitly built environment, with the reason recorded |
| C-R3-4 | D1 wrongly claims the identity variables are pinned — git synthesizes an identity and commits succeed without them | Reclassified as defense, with the measurement recorded |
| C-R3-5 | D6's `is_file` predicate and its "21 existing" figure disagree; the file count is 20 (`templates` is a directory), and 28 is a lexical dedup (27 normalized) | Count table split into exists/exists-as-file, and lexical deduplication made explicit |
| C-R3-6 | D5's target predicate admits three `templates/**` rows whose source is `skill_review.py`, where a Markdown-body sentinel is meaningless | Predicate tightened to a `.md` source |
| C-R3-7 | The ledger claimed every disposition applied while this PRD still carries the stale citations step 8 defers | Stated explicitly above as scheduled rather than applied |

### Round 3 — host (2)

| ID | Concern | Disposition |
| --- | --- | --- |
| H-R3-1 | D4's two claimed bites were asserted, not measured | Both measured: hostile `HOME` alone fails the commit and `GIT_CONFIG_GLOBAL=/dev/null` rescues it; the command-scope triple fails it with both file scopes scrubbed |
| H-R3-2 | The lane condition was measured with an ambient `GIT_CONFIG_GLOBAL` rather than D4's `HOME` injection | Re-measured with the `HOME`-based recipe: identical 61 failures, same three-module distribution |

**Convergence.** Three automatic rounds is the contract's limit, so no fourth
was started. Round 3's single blocking concern was resolved deterministically
rather than by another review lane: `$(abspath $(RUN_PYTHON))` was measured in
both configurations, and the six non-blocking concerns are corrections to
figures and predicates whose replacements are each backed by a reproduced
measurement. No unresolved blocking concern remains and the two lanes are not in
conflict, so implementation is unblocked.
