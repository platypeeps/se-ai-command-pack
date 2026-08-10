# Implementation — test hermeticity and update e2e coverage

Every command runs through the toolchain wrapper: a bare `python3` on this
machine has no PyYAML, and `.venv/bin/python` is what the Makefile uses. Single
test modules run through `unittest discover`, because `-m unittest tests.<mod>`
cannot import `install_test_support`.

## Step 1 — `git_env` and `hermetic_git_environment`

In `tests/install_test_support.py`, add both primitives from design D1.

`git_env` must build from a **`GIT_*`-stripped** copy of `os.environ` — dropping
every inherited `GIT_*` key before setting the explicit ones — not from
`os.environ` directly. Pointing only the file scopes at `os.devnull` leaves
`GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_n`/`GIT_CONFIG_VALUE_n` and
`GIT_CONFIG_PARAMETERS` live at command-line scope, which outranks every file.

Delete `GIT_ENV` from `tests/test_management.py` and route its one consumer
(`SourcePinningTest._git`, `:870`) through the import.

Confirm the stripping works before moving on:

```bash
GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.hooksPath \
GIT_CONFIG_VALUE_0=/hostile/from-env \
bash scripts/sd-ai-command-pack-toolchain.sh run-python -- -c \
  "import subprocess,sys; sys.path.insert(0,'tests'); from install_test_support import git_env; \
   print(subprocess.run(['git','config','--show-origin','core.hooksPath'], env=git_env(), \
   capture_output=True, text=True).returncode)"
```

Expect `1` — git finds no such key. Without the stripping this prints `0` and
the value.

```bash
bash scripts/sd-ai-command-pack-toolchain.sh run-python -- \
  -m unittest discover -s tests -p test_management.py
```

Same pass count as before the edit; this step changes no behavior.

## Step 2 — Migrate the call sites

Enumerate from the filesystem and reconcile against design D2's two tables:

```bash
bash scripts/sd-ai-command-pack-toolchain.sh run -- \
  git ls-files -z -- 'tests/*.py' | xargs -0 grep -n '"git"'
```

**Direct (13 sites):** add `env=git_env()`. The four inline calls in
`tests/test_release_gate.py` (`:151` `rev-parse`, `:349` `tag`, `:359`
`init --bare`, `:369` origin-side `tag`) are the ones a helper-only edit would
miss, and `tests/test_repo_tooling_ownership.py:67` is the conditional-argv one.

**Ambient (4 sites):** apply `hermetic_git_environment()` in `setUp` for
`tests/test_release_gate.py`'s `run_script` (`:42`) consumers,
`tests/test_trellis_provenance.py`'s `run_checker` class, and the unmocked
`_run_git` tests at `tests/test_management.py:972` and `:991`. These reach git
through a child script or through production code that passes no `env=`; an
`env=` keyword has nowhere to go at those call sites.

```bash
bash scripts/sd-ai-command-pack-toolchain.sh run-python -- \
  -m unittest discover -s tests -p 'test_*.py'
```

This step's real acceptance is measured against the hostile lane, not against
this run. Today's suite fails **61 tests** under the hostile ambient
configuration — `test_release_gate` 33, `test_trellis_provenance` 26,
`test_management` 2 — and those three modules are exactly the ones this step
touches. After the migration that count must be 0; anything left over is a call
site neither table found, and it belongs in the tables before continuing.

## Step 3 — `tests/test_test_hermeticity.py`, static guards (D3 + D6)

D3: AST scan for `subprocess.run`/`Popen`/`check_output`/`check_call`/`call`
whose argv begins with `"git"`, requiring an `env=` keyword. **Handle
`ast.IfExp` argv by examining both branches** — without it the scan finds 12
sites instead of 13 and `tests/test_repo_tooling_ownership.py:67` is invisible.
Enumerate modules from `git ls-files -z -- 'tests/*.py'`. Vacuity floor: 13.

D6: AST scan for maximal `PACK_ROOT / ...` chains; flag only paths that exist as
a file and are untracked; require each flagged path to appear in the reading
module's `HERMETICITY_UNTRACKED_PATHS`; assert every declared path is genuinely
untracked. Vacuity floor: **25 distinct literal paths** — not chain
occurrences, of which there are 59 (54 all-literal). Measured today: 28 distinct
(lexically deduped; 27 if `..` is normalized first, so dedupe lexically), 21
existing, **20 existing as a file** — the difference is the `templates`
directory — and 2 existing-as-a-file and untracked.

Then declare the two known entries:

- `HERMETICITY_UNTRACKED_PATHS = (".trellis/.template-hashes.json",)` in
  `tests/test_repo_tooling_ownership.py`
- `HERMETICITY_UNTRACKED_PATHS = ("docs/repomix-map.md",)` in
  `tests/test_repomix.py`

```bash
bash scripts/sd-ai-command-pack-toolchain.sh run-python -- \
  -m unittest discover -s tests -p test_test_hermeticity.py
```

### Probes for step 3 — run each, confirm the predicted failure, revert

| Probe | Change | Expected |
| --- | --- | --- |
| A | Drop `env=git_env()` from one migrated call site | D3 fails naming that file and line |
| B | Restrict the argv rule to list literals only | the 13-site vacuity floor fails (the scan finds 12) |
| C | Add `PACK_ROOT / ".trellis/.template-hashes.json"` + a read to another module | D6 fails naming that module |
| D | Add a tracked path to a `HERMETICITY_UNTRACKED_PATHS` tuple | D6 fails the genuinely-untracked assertion |

## Step 4 — Hostile-configuration pair (D4)

Same module. Build a hostile **home** directory — `.gitconfig` with
`core.hooksPath` pointing at a directory containing an executable `pre-commit`
that exits 1.

Both halves run **inside** `patch.dict(os.environ, {...}, clear=True)` over an
explicitly built environment — `PATH`, `HOME` set to that directory, and the
same `core.hooksPath` through
`GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_0`/`GIT_CONFIG_VALUE_0` at command scope.
`clear=True` is required: an inherited `GIT_DIR`, `GIT_INDEX_FILE`, or
`GIT_CONFIG_PARAMETERS` would otherwise be able to fail the negative half even
if the hook fixture were broken.

Inject through `HOME`, **not** through an ambient `GIT_CONFIG_GLOBAL`. `git_env`
strips every ambient `GIT_*` name, so a hostile `GIT_CONFIG_GLOBAL` is removed
whether or not the explicit `GIT_CONFIG_GLOBAL=os.devnull` assignment survives —
the pair would pass with that assignment deleted, proving nothing. `HOME` is not
a `GIT_*` name; it survives the strip, and only the assignment neutralizes it.

- Negative: `init`/`add`/`commit` with `env=None` (inheriting) must fail.
- Positive: the identical sequence with plain `git_env()` must succeed.
- Assert `git --version` ≥ 2.32.

Confirm the pair bites before moving on, by deleting one thing at a time from
`git_env` and re-running: without `GIT_CONFIG_GLOBAL=os.devnull` the positive
half must fail on the hostile `HOME`; without the `GIT_*` strip it must fail on
the command-scope triple. Revert each. Do not claim more: `GIT_CONFIG_SYSTEM`,
`GIT_CONFIG_NOSYSTEM`, and `GIT_TERMINAL_PROMPT` are not pinned by this pair and
design D1 records why.

Document the git floor in `CONTRIBUTING.md` in the same commit — the assertion
turns an undocumented assumption into a stated requirement, and the doc is what
makes it discoverable before a contributor hits the failure.

## Step 5 — The `install.py update` e2e (D5)

New `tests/test_update_e2e.py` — a dedicated module, not a class inside
`tests/test_management.py`, so the narrow verification command below actually
discovers it. Guard with `skipUnless(shutil.which("git"))`.

Build the origin from the **tracked working tree** (`git ls-files -z` copied into
a scratch directory, `git init`, commit, `git clone --bare`), never from a clone
of `PACK_ROOT` HEAD: the step-5 probe below edits `installer/management.py` in
the working tree, and a HEAD clone would run the unmodified committed file.

Call `make_home(base)` before installing, for parity with the rest of the suite
— not because of the anchor gate, which `--all` bypasses
(`installer/fileops.py:155`, and `tests/test_install.py:119-122` installs the
full set into a home with no anchors). Install with `--all`. Do not pass
`--confirm-source`; running `src/install.py` makes `source_root == ROOT`, and
passing the flag would mask a regression in that equality.

Pick the mutation target from `manifest.json` at the root of the `src` clone: a
`templates/**` row with a **`.md` source** whose `target` exists under the temp
home after the install. Not a `generated/**` row — it must also satisfy
generator parity — and not one of the three `templates/**` rows pointing at
`skill_review.py`, where a Markdown-body sentinel makes no sense. Append a
sentinel line to that row's `source` **body**, not its frontmatter. Commit and
push it from a separate scratch clone: `installer/management.py:464` refuses to
update from a source checkout with uncommitted changes.

Two assertions, both required: `src` HEAD equals `origin.git` HEAD, and the
installed copy under the temp home carries the sentinel.

```bash
bash scripts/sd-ai-command-pack-toolchain.sh run-python -- \
  -m unittest discover -s tests -p test_update_e2e.py
```

Check the run reports a nonzero test count — `Ran 0 tests ... OK` means the
pattern matched nothing and proves nothing.

### Probe for step 5

Comment out the final `_run_installer` call in `installer/management.py`
`update_pack` (`:510-521` — `:508-509` is the `if planned != 0` guard above it,
so comment the whole `:508-521` block and add a `return 0` to keep the return
type), rerun, and confirm the sentinel assertion fails while
the HEAD assertion still passes. Revert immediately. This probe is only
meaningful because the e2e sources from the working tree.

## Step 6 — The hermetic lane (D7)

Add `make test-hermetic`, in this order — the ordering is load-bearing:

1. resolve the interpreter with `$(abspath $(RUN_PYTHON))` — **not**
   `$(CURDIR)/$(VENV_PYTHON)`. `Makefile:4` defines `VENV_PYTHON` relative, so
   after changing directory it would resolve against the copy, which has no
   `.venv` (`.gitignore:12`); and CI has no `.venv` at all
   (`.github/workflows/tests.yml:34-39` installs the lockfile into the
   `setup-python` interpreter), so a hardcoded venv path fails there. `abspath`
   absolutizes the local venv and passes an already-absolute runner path
   through unchanged;
2. materialize `git ls-files -z` into a temp directory;
3. `git init`, `git add -A`, `git commit` there, **under a clean environment**;
4. only then run the suite with the hostile ambient configuration — hostile
   `HOME` plus the command-scope triple, the same injection D4 uses.

Step 3 is not optional. Measured on a copy without it: `FAILED (failures=1,
errors=12)`, every one of them `not a git repository` or
`git ls-files … exit status 128`. With it, **in a benign environment**:
`OK (skipped=2)`. That benign run is the criterion-3 evidence; it is not
criterion-1 evidence, and the pre-migration hostile run of the same copy still
reports `FAILED (failures=2, errors=59)`.

```bash
make test-hermetic
```

The lane runs the hostile form, so once steps 1–5 have landed it closes both
criteria at once — criterion 3 because the tree has no untracked files,
criterion 1 because the hostile configuration is live. Quote its final line as
the evidence. Expect exactly two skips — the two D6 entries — and treat a third
as a new untracked dependency, not as noise. If it fails, the failure is a real
ambient dependency: fix it rather than relaxing the lane.

Then wire the lane into CI. **Four edits, not two** — the lane set is
cross-checked, and `tests/test_aggregate_ci_result.py:159` fails the suite on a
partial edit:

1. the new job in `.github/workflows/tests.yml`;
2. that job added to `ci-result`'s `needs:` list (`.github/workflows/tests.yml:136`);
3. `REQUIRED_LANES` in `.github/scripts/aggregate-ci-result.py:20`;
4. the all-success fixture in `tests/test_aggregate_ci_result.py:42-45`, which
   otherwise reports the newly declared lane as missing and fails several tests
   that have nothing to do with it.

Do **not** add it to `make check`.

## Step 7 — Full gate

```bash
make check
```

Must report the unittest suite green, coverage at or above the floor, ruff and
mypy clean, generator parity clean, and `trellis-provenance check: ok`. The
release payload gate must report no version obligation, because no shipped
payload changed; if it demands a bump, stop — something under `templates/**` or
`installer/**` was touched and a non-goal was violated.

## Step 8 — Record and tick

Correct the PRD's drifted evidence lines and anchor by symbol as the previous
audit task did. Measured: the two `git init` fixtures in
`tests/test_skill_review.py` are at `:1059` and `:1393` (not `:904`/`:1238`, and
not `:1054`/`:1390` — those two lines are the `shutil.which()` guards above
them); `tests/test_management.py`'s `GIT_ENV` is at `:33`, not `:108`;
`tests/test_release_gate.py`'s `git()` helper is at `:33-39`, not `:17`.

Tick the three acceptance criteria with evidence: criterion 1 and 3 from the
`make test-hermetic` run, criterion 2 from the e2e plus its probe. Then ship.

## Rollback

Additive except the `env=` additions in step 2, the deletion of a module-level
constant in step 1, and the CI lane in step 6. Reverting the commit restores the
prior suite exactly; no shipped payload and no production code changes.
