# Design — test hermeticity and update e2e coverage

## Problem

Three separate leaks of ambient state into the suite, one per PRD requirement.

1. **Global/system git configuration.** Every test that reaches `git` inherits
   the developer's configuration. `tests/test_management.py:33` already defines a
   scrubbed `GIT_ENV` and uses it at exactly one call site (`:870`). Measured:
   **13 direct `git` subprocess call sites across 19 tracked test modules, one of
   which passes `env=`.**
2. **No end-to-end coverage of `install.py update`.** The one command that
   mutates a user's checkout is exercised only through mocks, or through
   `SourcePinningTest.test_update_execs_installer_inside_pinned_directory`, whose
   source checkout contains a *stub* `install.py` that appends to a sentinel
   file. That test proves process pinning; nothing proves the pull advanced the
   checkout or that installed files changed.
3. **Reads of paths a fresh clone does not have.** The PR #206 incident
   (`.trellis/.template-hashes.json`, gitignored at `.gitignore:94`) is the
   demonstrated case.

## Non-goals

- No production-code change. `installer/management.py` is correct as written;
  what is missing is a test that runs it for real.
- No manifest version bump. Nothing under `tests/` is shipped payload —
  `manifest.json` lists 553 rows and every `source` is under `templates/**`
  (492) or `generated/**` (61), so the release gate's diff-based carve-out
  attaches no version obligation. If the implementation ends up touching
  `templates/**` or `installer/**`, it returns.

One earlier non-goal was **withdrawn during review**: "no CI workflow change".
D7 explains why — the third acceptance criterion cannot be closed by any static
check, and the run that closes it is worth nothing if nobody runs it.

## D1 — One canonical hermetic git environment

Add to `tests/install_test_support.py`:

```python
def git_env(**overrides: str) -> dict[str, str]:
    """Environment for a git that must not see machine state."""
```

**It builds from a `GIT_*`-stripped copy of `os.environ`, not from `os.environ`
itself.** This is the review's sharpest finding and it is not theoretical —
measured on this machine, at git 2.50.1, with all three file-level scrubs set:

```
$ GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null GIT_CONFIG_NOSYSTEM=1 \
  GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.hooksPath \
  GIT_CONFIG_VALUE_0=/hostile/from-env git config --show-origin core.hooksPath
command line:	/hostile/from-env

$ GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null \
  GIT_CONFIG_PARAMETERS="'core.hooksPath=/hostile/params'" \
  git config --show-origin core.hooksPath
command line:	/hostile/params
```

`GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_n`/`GIT_CONFIG_VALUE_n` and
`GIT_CONFIG_PARAMETERS` enter at **command-line scope**, which outranks every
configuration file, so pointing the file scopes at `os.devnull` does not touch
them. Enumerating the dangerous names is the wrong shape — the list grows with
git — so the helper drops every inherited `GIT_*` variable and puts back only
what it explicitly wants. A test has no legitimate need for an inherited `GIT_*`.

| Variable | Value | Reason |
| --- | --- | --- |
| every inherited `GIT_*` | *removed* | Closes command-scope injection, `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, and every future sibling in one rule. |
| `GIT_CONFIG_GLOBAL` | `os.devnull` | Neutralizes `~/.gitconfig` and the XDG global. Git ≥ 2.32. |
| `GIT_CONFIG_SYSTEM` | `os.devnull` | Neutralizes `/etc/gitconfig`. Git ≥ 2.32. |
| `GIT_CONFIG_NOSYSTEM` | `"1"` | Same effect as the row above on git < 2.32. |
| `GIT_AUTHOR_NAME` / `_EMAIL` | `test` / `test@example.com` | A scrubbed config removes the identity `git commit` requires. |
| `GIT_COMMITTER_NAME` / `_EMAIL` | same | git needs both. |
| `GIT_TERMINAL_PROMPT` | `"0"` | Fail rather than block on a credential prompt. |

`**overrides` has no caller. The earlier draft said D4 would build its hostile
environment as `git_env(GIT_CONFIG_GLOBAL=str(hostile))`; D4 as corrected below
injects hostility *ambiently* and calls plain `git_env()`, so the parameter is
kept only as a documented extension point and no test uses it.

**What each scrub is actually pinned by.** The `GIT_*`-stripping rule has a
consequence review caught: a scrub whose only hostile input arrives through a
`GIT_*` variable cannot be bitten, because the strip removes that input whether
or not the explicit assignment survives. Honest accounting:

| Scrub | Hostile input that bites it |
| --- | --- |
| `GIT_CONFIG_GLOBAL` | A hostile `$HOME/.gitconfig`. `HOME` is not a `GIT_*` name, so it survives the strip and only this assignment neutralizes it. Measured: commit exits 1 with the hostile `HOME` alone, and 0 with `GIT_CONFIG_GLOBAL=/dev/null` added. |
| the `GIT_*` strip itself | The ambient `GIT_CONFIG_COUNT`/`KEY_0`/`VALUE_0` triple, which the file scrubs cannot reach. |
| `GIT_AUTHOR_*` / `GIT_COMMITTER_*` | **Nothing.** Review measured it: with `env -i`, an empty `HOME`, and both configuration files disabled, `user.name` and `user.email` are unset (`exit 1` each) and `git commit` still exits 0 — git synthesizes an identity from the account and host. They stay because that synthesis is not guaranteed on every runner, but they are defense, not a pin. |
| `GIT_CONFIG_SYSTEM`, `GIT_CONFIG_NOSYSTEM` | **Nothing, in-suite.** Injecting system scope means writing `/etc/gitconfig`, which a test must not do. They are kept as defense and are explicitly not claimed to be pinned. |
| `GIT_TERMINAL_PROMPT` | Nothing local — no test authenticates. Kept so a future remote-touching test fails instead of hanging. |

**Git 2.32 becomes a documented contributor requirement.** There is no pre-2.32
equivalent of `GIT_CONFIG_GLOBAL` short of relocating `HOME`, which the PRD
allows but which also moves credential and cache state. The decision is to
require 2.32 (June 2021; both CI runner images exceed it, and this machine runs
2.50.1), state it in `CONTRIBUTING.md`, and assert it in D4 so an older git fails
loudly instead of running unscrubbed. Review flagged that the previous draft made
this change silently; it is now explicit and carries a doc change.

**Two consumption modes.**

- *Direct*: the test calls `subprocess.run(["git", ...])` and passes
  `env=git_env()`. D2 enumerates these; D3 enforces them.
- *Ambient*: the test reaches git through something it does not pass an
  environment to. `install_test_support` also exports

  ```python
  @contextlib.contextmanager
  def hermetic_git_environment() -> Iterator[None]:  # patch.dict(os.environ, git_env(), clear=True)
  ```

  applied in `setUp`. D2's second table enumerates these; no static guard covers
  them, and D7 is what catches a missed one.

## D2 — Migrate every call site

Enumerated by AST over `git ls-files -z -- 'tests/*.py'`, not from the PRD's
citations, which have drifted.

**Direct (13 sites, 1 already compliant):**

| File | Lines |
| --- | --- |
| `tests/test_frontmatter_conformance.py` | 148 |
| `tests/test_management.py` | 870 *(already passes `env=`)* |
| `tests/test_release_gate.py` | 34, 151, 349, 359, 369 |
| `tests/test_repo_tooling_ownership.py` | 67 |
| `tests/test_skill_review.py` | 1059, 1060, 1393, 1394 |
| `tests/test_trellis_provenance.py` | 44 |

`ls-files` is not exempt: `core.quotePath` changes how non-ASCII paths are
emitted and `core.excludesFile` changes what `--others` returns, and this suite
treats those enumerations as ground truth.

**Ambient (4 sites, none visible to a static guard):**

| Site | How git is reached |
| --- | --- |
| `tests/test_release_gate.py:42` `run_script()` | Launches `check-release-payload.py`, which runs git at `.github/scripts/check-release-payload.py:63` with no `env=`. |
| `tests/test_trellis_provenance.py:84` `run_checker()` | Calls `checker.main()` in-process; its git runs at `.github/scripts/check-trellis-provenance.py:51` with no `env=`. |
| `tests/test_management.py:972`, `:991` | Unmocked `_run_git`; `installer/management.py:388` passes no `env=` and inherits. |
| D5's e2e | Runs `install.py update` as a subprocess — covered by `env=git_env()` on that call, since the whole chain inherits. |

**Runtime corroboration of this table.** Running today's suite under a hostile
ambient `core.hooksPath` (D7's lane condition, before any migration) fails
`61` tests, distributed over exactly the three modules named above and no
others:

```
FAILED (failures=2, errors=59, skipped=2)     # Ran 710 tests
test_release_gate 33 · test_trellis_provenance 26 · test_management 2
```

The direct-call modules that do not appear — `test_skill_review`,
`test_repo_tooling_ownership`, `test_frontmatter_conformance` — are ones a
`core.hooksPath` hook never reaches, since they read rather than commit. They
are still migrated: the hostile knob chosen for the pair is not the only knob a
contributor's configuration carries.

## D3 — A guard so the direct migration cannot rot

New `tests/test_test_hermeticity.py` parses every tracked module under `tests/`
and requires an `env=` keyword on each call to `subprocess.run`/`Popen`/
`check_output`/`check_call`/`call` whose argv begins with the string `git`.

- **The argv expression may be an `ast.IfExp`, and both branches must be
  examined.** `tests/test_repo_tooling_ownership.py:67` is written
  `["git", "ls-files", "--", *paths] if paths else ["git", "ls-files"]`; a
  list-literal-only rule finds 12 sites and silently skips it. Measured both
  ways: 12 without the `IfExp` arm, 13 with.
- Enumeration comes from `git ls-files`, so a newly tracked test module is
  covered the moment it lands.
- Vacuity guard: **at least 13 call sites**, the measured count. A floor set
  well below the true number (the earlier draft said 6) would let a half-broken
  walk pass.
- The guard does not inspect the `env=` *value*. Any expression satisfies it;
  chasing the value would reject legitimate `git_env(...)` variants and invite an
  allowlist. The failure it prevents — a new call site with no environment at
  all — is the one that actually happened.

## D4 — Prove the scrub survives a hostile configuration

Same module, as a matched pair. Two drafts of this pair have been wrong, in
opposite directions, and both were caught by review.

The first injected the hostile file **only** into the negative half, so deleting
`GIT_CONFIG_GLOBAL` from `git_env` left the positive half reading the
contributor's real configuration and still passing.

The second injected it ambiently as `GIT_CONFIG_GLOBAL` — which does not bite
either, and for a subtler reason: `git_env` strips every ambient `GIT_*` name
*before* setting its own, so deleting the explicit `GIT_CONFIG_GLOBAL=os.devnull`
assignment still removes the hostile value and the positive half still passes.
An ambient `GIT_*` variable can only ever pin the strip, never the assignment.

The corrected pair therefore injects hostility through **two different channels**,
one per property:

1. Build a hostile home: a temp directory holding `.gitconfig` with
   `core.hooksPath` pointing at a directory whose executable `pre-commit`
   exits 1.
2. Wrap both halves in `patch.dict(os.environ, {...}, clear=True)` — an
   explicitly constructed environment (`PATH`, `HOME` → the hostile home, and
   the `GIT_CONFIG_COUNT`/`KEY_0`/`VALUE_0` triple), installed with
   `clear=True`. Without `clear=True` the negative half inherits whatever
   `GIT_DIR`, `GIT_INDEX_FILE`, or `GIT_CONFIG_PARAMETERS` the developer has,
   any of which could fail the commit even with a broken hook fixture, making
   the negative half pass for the wrong reason. `HOME` survives `git_env`'s
   strip and pins `GIT_CONFIG_GLOBAL=os.devnull`; the triple pins the strip.
3. **Negative half**: `init`/`add`/`commit` inheriting that environment
   (`env=None`) must fail.
4. **Positive half**: the identical sequence with plain `git_env()` must
   succeed.

Measured directly, with `env -i` so nothing else leaks:

```
$ HOME=<hostile>                          git add f.txt && git commit -qm x   # exit 1
$ HOME=<hostile> GIT_CONFIG_GLOBAL=/dev/null git add f.txt && git commit -qm x   # exit 0
```

The claim this pair supports is now the narrow true one — removing the
`GIT_CONFIG_GLOBAL` assignment or the `GIT_*` strip fails the positive half —
not the earlier "removing any single scrub fails". D1's table states which
scrubs remain unpinned and why.

`core.hooksPath` is chosen over the PRD's `commit.gpgsign=true` deliberately:
`gpgsign` fails only where no usable signing key exists, so it would pass
vacuously — or hang — on a maintainer's machine that has one. A `pre-commit`
hook that exits 1 fails identically everywhere.

The same test asserts `git --version` ≥ 2.32.

## D5 — The `install.py update` end-to-end test

1. **Build the origin from the tracked working tree, not from `HEAD`.**
   Materialize `git ls-files -z` into a scratch directory, `git init`, commit,
   and `git clone --bare` that into `origin.git`. Review found the earlier
   `git clone --local PACK_ROOT` plan self-defeating: its probe (step 5 of
   `implement.md`) edits `installer/management.py` in the working tree, while a
   clone of `HEAD` would execute the unmodified committed file, so the probe
   would "pass" against code it never ran. Sourcing from the working tree also
   means the e2e tests the change under review rather than the last commit; on
   CI the two are identical.
2. `git clone origin.git src` — the recorded source checkout.
3. `make_home(base)` first, for parity with the rest of the suite. The earlier
   draft justified this by the anchor gate — all 553 rows are
   `if-anchor-exists`, so a bare directory would select nothing — and review
   showed that reason is void once `--all` is passed:
   `installer/fileops.py:155` takes the `install_all or platform_filter`
   branch, and `tests/test_install.py:119-122` installs the complete target set
   into `make_home(self.base, anchors=())`. The call stays, the rationale does
   not. Then `python src/install.py --root <home> --all`, a real install, so the
   provenance the update path reads is the one the installer wrote rather than a
   hand-built fixture. (`UpdateFixtureMixin._point_provenance` writes provenance
   by hand, which is right for the trust-boundary tests and wrong here.)
4. Pick the mutation target from `manifest.json` at the root of `src`: a
   **`templates/**` row** whose `target` exists under the temp home after the
   install, **with a `.md` source**. A `generated/**` row (61 of the 553) is
   the wrong choice — it also has to satisfy generator parity, so editing it
   makes the commit that pushes it fail `make generate --check` for reasons
   unrelated to this test. Neither is a `templates/**` row enough on its own:
   three of the 492 point at `templates/skills/se-review-skills/scripts/skill_review.py`,
   and "append a sentinel to the Markdown body" is meaningless for a Python
   file. Mutate
   that row's **`source`**
   file — appending a sentinel line to the Markdown **body**, never the
   frontmatter, so the assertion survives any per-platform rendering — commit it
   in a scratch clone, and push to `origin.git`.
5. `python src/install.py update --root <home>`, with `env=git_env()`. No
   `--confirm-source`: `installer/registry.py:11` defines `ROOT` as the running
   checkout, so running `src/install.py` makes `source_root == ROOT` and the
   confirmation branch at `installer/management.py:327` is not reached. Passing
   the flag would mask a regression in that equality. Note also
   `installer/management.py:464`: `update_pack` refuses a source checkout with
   uncommitted changes, so the mutation must be committed in a separate scratch
   clone and pushed, never applied inside `src`.
6. Assertions, both required:
   - `git -C src rev-parse HEAD` equals `git -C origin.git rev-parse HEAD`;
   - the installed copy under the temp home contains the sentinel.

The refresh is expected to happen without `--force` because the installed file
still matches its provenance digest — `installer/fileops.py:352` takes the
vouched-update branch. The second assertion is the one with teeth: a pull that
lands without a refresh satisfies the first and leaves the user's tree stale.

## D6 — The untracked-read guard

Also in `tests/test_test_hermeticity.py`. Walk each tracked test module for
`PACK_ROOT / ...` chains and flag a path only when **all three** hold:

1. it is a **maximal** chain — a `BinOp` that is not itself the left operand of
   another `/`, so `PACK_ROOT / "docs"` inside `PACK_ROOT / "docs" / "x.md"` is
   not reported as a bare directory;
2. it **exists as a file** in the working tree; and
3. it is **not tracked**.

The earlier draft required only "resolves and is not in `git ls-files`", which
review showed produces **26 flagged paths** (distinct, counting the non-maximal
chains that rule also matches) — directory prefixes (`git ls-files` lists
files, not directories) and negative-case fixture targets like
`docs/stray-surface.md` and `templates/skills/_shared/generated.json`, which
`tests/test_generate.py:512-545` asserts are *never created*. The PRD explicitly
scopes self-created fixtures out. The three-part rule reproduces the incident's
exact shape — a file that exists here and does not exist in a clone — and
measured over today's suite it flags **exactly two**:

| Path | Reader | Already tolerant? |
| --- | --- | --- |
| `.trellis/.template-hashes.json` | `tests/test_repo_tooling_ownership.py:21` | Yes — `TRELLIS_HASHES.exists()` |
| `docs/repomix-map.md` | `tests/test_repomix.py:11` | Yes — `skipUnless(MAP_PATH.exists())` |

Both must therefore be declared in a module-level
`HERMETICITY_UNTRACKED_PATHS` tuple in the module that reads them. The guard
also asserts every declared path is genuinely untracked, so the tuple cannot
accumulate tracked paths and become a bypass. The earlier draft said "exactly one
entry"; that was wrong, and the second one is evidence the enumerate-and-skip
convention already exists in two places rather than one.

Vacuity guard: at least **25 distinct literal paths** must resolve. The unit
matters and the earlier draft got it wrong — "25 maximal chains" reads as a
floor on occurrences, and there are far more of those, so the floor would have
passed at under half the true coverage. Measured today:

| Quantity | Count |
| --- | --- |
| maximal `PACK_ROOT / ...` chains | 59 |
| of those, entirely literal (the ones a static rule can resolve) | 54 |
| **distinct paths among them** | **28** |
| distinct paths that exist at all | 21 |
| distinct paths that exist **as a file** | 20 |
| distinct paths that exist as a file and are untracked | 2 |

The floor is on the bolded row. The 21/20 gap is `templates`, a directory: the
predicate is `is_file`, so the directory is excluded, and the two rows must not
be conflated. The 28 is a **lexical** deduplication; normalizing `..` first
gives 27, and the guard should dedupe lexically so its count matches the floor
it is compared against.

**Stated limit.** This is a shape check. A path assembled at runtime — such as
`PACK_ROOT / manifest_source(...)` followed by `read_bytes()` in
`tests/test_install.py:134` — is out of reach of any static rule, so D6 alone
cannot prove the PRD's third criterion, which is universal. D7 is what proves it.

## D7 — One hermetic lane that actually runs the suite

Review's decisive point, on two criteria at once: neither "the suite passes under
a hostile global configuration" (criterion 1) nor "no test reads a path a fresh
clone lacks" (criterion 3) can be closed by a check that never runs the suite in
that condition.

Add `make test-hermetic`, which:

1. materializes `git ls-files -z` from the working tree into a temp directory —
   tracked files only, so every untracked and gitignored path is absent exactly
   as in a fresh clone;
2. **makes that directory a git repository**: `git init`, `git add -A`,
   `git commit`, run under a clean environment *before* any hostility is
   injected;
3. runs the full suite there with the *interpreter* from `.venv` but the
   *sources* from the copy (`install_test_support.PACK_ROOT` resolves from its
   own file, so it becomes the copy); and
4. injects the same hostile ambient git configuration D4 uses — hostile `HOME`
   plus the command-scope triple — for the whole run.

**Steps 1 and 2 run through a `scrub` shell function** — the same `GIT_*` strip
plus `/dev/null` file scopes the Python `git_env` applies, with a committer
identity. Review caught the omission empirically: with an ambient
`GIT_CONFIG_COUNT` triple pointing `core.hooksPath` at a failing hook, the
lane's *own setup commit* failed and `make test-hermetic` exited 1 before
running a single test — the fixture was broken by the condition it exists to
test. It has to be a function, not an exported block: a `GIT_CONFIG_GLOBAL`
in scope during step 4 would outrank the hostile `HOME` and silently defang the
lane. Measured after the fix, with the same ambient triple set: exit 0,
`Ran 722 tests`, `OK (skipped=2)`.

**Step 2 is not optional, and the earlier draft omitted it.** "Tracked files
only, exactly like a fresh clone" was wrong in one respect: a fresh clone also
has `.git`. Several tests enumerate or diff the repository they live in —
`tests/test_frontmatter_conformance.py:148`,
`tests/test_repo_tooling_ownership.py:67`, and the real release gate that
`tests/test_release_gate.py:328` runs against `PACK_ROOT`, which needs `HEAD`
and `git diff` at `.github/scripts/check-release-payload.py:98`. Measured on a
copy without `.git`:

```
FAILED (failures=1, errors=12, skipped=2)     # Ran 710 tests
SystemExit: error: recorded source checkout is not a git repository: <copy>
subprocess.CalledProcessError: ['git', 'ls-files', ...] returned non-zero exit status 128
```

With `git init && git add -A && git commit` added, the same copy runs clean —
**in a benign environment**:

```
OK (skipped=2)     # Ran 710 tests in 36.797s, no hostile configuration
```

Those two skips are the two D6 entries — `.trellis/.template-hashes.json` and
`docs/repomix-map.md` — which is the positive evidence for the PRD's third
criterion: the whole suite runs against a tree with no untracked files, and
exactly the two already-guarded reads skip.

That run says nothing about criterion 1, and the distinction matters. The same
copy under the full hostile recipe still fails today, exactly as D2 predicts:

```
FAILED (failures=2, errors=59, skipped=2)     # 61 failures, pre-migration
```

Criterion 3 is closed by the benign copy run; criterion 1 is closed only once
D2's migration turns that 61 into 0 under the hostile run. The lane executes the
hostile form, so one green lane covers both — but only after D1–D6 land.

The interpreter needs its own care, and the naive fix is wrong. `Makefile:4`
defines `VENV_PYTHON` relative to `$(VENV)`, so a lane that changes directory
into the copy would resolve it against the copy, where `.venv` does not exist
(`.gitignore:12`). But hardcoding `$(CURDIR)/$(VENV_PYTHON)` is also wrong: CI
never creates a venv — `.github/workflows/tests.yml:34-39` uses `setup-python`
and installs the lockfile into that interpreter — so on a runner the file is
absent. The lane must absolutize whatever `RUN_PYTHON` already selected:
`$(abspath $(RUN_PYTHON))`, which yields
`<checkout>/.venv/bin/python` locally and leaves an already-absolute
`setup-python` path untouched (measured both ways).

One lane, both properties, and it catches the ambient callers of D2 that no
static guard can see. Wiring it in touches **four** places, not two, because
the lane set is cross-checked in three of them:

| File | Change |
| --- | --- |
| `.github/workflows/tests.yml` | the new job |
| `.github/workflows/tests.yml:136` | add it to `ci-result`'s `needs:` list |
| `.github/scripts/aggregate-ci-result.py:20` | add it to `REQUIRED_LANES` |
| `tests/test_aggregate_ci_result.py:42-45` | add it to the all-success fixture, or every lane-set test fails with a missing-lane error |

`tests/test_aggregate_ci_result.py:159` asserts the workflow's `needs:` list
equals the script's declared lanes, so a partial edit fails the suite rather
than CI — which is the right direction, and is why the obligation the spec at
`.trellis/spec/backend/quality-guidelines.md` states is enforced rather than
remembered.

Cost: the suite runs in **about 40 s** (41.1 s in the checkout, 36.8 s in the
copy, measured), so this roughly doubles total CI test work while running in
parallel with the existing lanes. It is deliberately **not** added to
`make check`: a developer's inner loop should not pay 40 s twice.

## What bites, and what does not

| Group | Proof that it bites |
| --- | --- |
| D3 | Drop `env=` from a migrated call site → fails, naming file and line. |
| D4 | Remove `GIT_CONFIG_GLOBAL=os.devnull` → the positive half fails on the hostile `HOME`. Remove the `GIT_*` strip → it fails on the command-scope triple. The other scrubs are not pinned; D1's table says so. |
| D5 | Skip the applying installer run → the sentinel assertion fails while the HEAD assertion still passes. |
| D6 | Add an unguarded read of `.trellis/.template-hashes.json` in another module → fails. Add a tracked path to the allowlist → fails the genuinely-untracked assertion. |
| D7 | Reintroduce PR #206's unconditional read → the lane fails where `make check` stays green, which is the exact blind spot the PRD names. |
| D2 | Does **not** bite on its own: today's suite passes before and after. D3 and D7 are what keep it in place. |

## Risks

- **Two suite runs per CI cycle.** ~40 s each, parallel. If the lane proves
  flaky on a runner, the mitigation is to keep the lane and fix the leak it
  found — a flaky hermetic lane is usually a real ambient dependency.
- **`make test-hermetic` copies tracked files on every invocation.** Bounded by
  the tracked tree, not by `.git` (19 MB); no clone, no network.
- **AST guards are structural.** Their value is that the two shapes they check
  are exactly the two that produced real failures; their limit is stated in D6
  and covered by D7.
