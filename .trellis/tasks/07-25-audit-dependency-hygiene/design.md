# Dependency hygiene for npm and transitive pins — Design

## Overview

Three audit findings share one theme — an un-deliberate third-party fetch — but
they do not share an owner. A-033 (floating Python transitives) and A-034
(`npx` lifecycle scripts) sit on repo-owned files and get real code changes.
A-032 (`@opencode-ai/plugin`) sits on an upstream-Trellis vendored file and
gets a record, not an edit. Establishing that split is the first design
decision, because getting it wrong produces an edit the next `trellis init`
silently reverts.

Ownership was resolved with the two lookups in
`.trellis/spec/backend/quality-guidelines.md:772-784`, run on 2026-08-10:

| File | Registry A | Registry B | Classification |
| --- | --- | --- | --- |
| `.opencode/package.json` | **hit** | absent | upstream-Trellis vendored — do not edit |
| `requirements-dev.txt` | absent | absent | repo-owned |
| `Makefile` | absent | absent | repo-owned |
| `.github/workflows/tests.yml` | absent | absent | repo-owned |
| `scripts/update_repomix` | absent | absent | repo-owned |
| `.sd-ai-command-pack/check.json` | absent | absent | repo-owned |
| `CONTRIBUTING.md` | absent | absent | repo-owned |

`.github/trellis-provenance.json` independently agrees on the first row:
`.opencode/package.json` appears in `templateReceipted`, not in `repoOwn` or
`files`.

## Proposal

### D1 — A-032: local-only record, no local edit

The spec requires the four-field record "in the task's disposition **and** in
whatever guidance section carries the constraint" (`quality-guidelines.md:857`)
— two locations, not one. So: an `## A-032 disposition` section in this task's
`prd.md`, and a matching record in
`.trellis/spec/backend/quality-guidelines.md`. Then fix `CONTRIBUTING.md:78`,
which currently reads as though this repository will do the removal.

No upstream pull request is opened, because the run-level authority excludes
upstream PRs (`quality-guidelines.md:850`) — not because the target is unknown.
The upstream is `mindfold-ai/Trellis`, already cited at
`quality-guidelines.md:651`. The relay is therefore a real, actionable
follow-up awaiting explicit per-PR approval, and is recorded as such rather
than written off.

The npm-out-of-scope decision in `CONTRIBUTING.md` stays — it is still correct,
just for a better reason: the only npm manifest with dependencies is not ours
to manage.

### D2 — A-033: universal hash-locked `requirements-dev.lock`

Generate `requirements-dev.lock` from `requirements-dev.txt` with:

```
uv pip compile --universal --python-version 3.10 --generate-hashes --no-header \
  --only-binary :all: requirements-dev.txt -o requirements-dev.lock
```

- `--universal` resolves one file valid for every CI environment. The matrix is
  ubuntu×3.10, ubuntu×3.13, macos×3.13 (`.github/workflows/tests.yml:23-28`), so
  a per-environment lock would mean three files; universal resolution emits one
  with environment markers pip evaluates at install time (probed 2026-08-10:
  `librt ; platform_python_implementation != 'PyPy'`,
  `tomli ; python_full_version < '3.11'`).
- `--python-version 3.10` sets the floor to the oldest supported lane.
- `--generate-hashes` gives every wheel on every platform a recorded hash, so
  installs run under `pip install --require-hashes`.
- `--no-header` keeps the file free of the uv version and command line, which
  would otherwise churn on every uv upgrade.
- `--only-binary :all:` restricts *resolution* to wheels, matching the install
  contract below. Without it, `make lock` itself can build a source
  distribution to read its metadata — executing exactly the build hooks this
  task is closing off. Probed 2026-08-10: adding the flag produced a
  byte-identical lock, so the stricter resolution costs nothing today and fails
  loudly the day a dependency stops shipping a wheel.

`requirements-dev.txt` stays the human-edited input and the Dependabot-managed
manifest; the lock is generated output. The extension is `.lock`, not `.txt`,
specifically so Dependabot's pip ecosystem does not adopt it as a second
manifest and open bumps against a generated file.

Consumers change to the lock: `make setup` (`Makefile:14`) and the three CI
`pip install` steps plus their `cache-dependency-path` keys
(`.github/workflows/tests.yml:38-39`, `:59-60`, `:79-80`).

### D3 — A-033 guard: offline consistency check, not a recompile lane

The failure mode this must catch is specific: Dependabot bumps a pin in
`requirements-dev.txt`, nothing regenerates the lock, and CI keeps installing
the old version while the PR looks merged and applied.

Two guards were considered:

1. **Recompile in CI and diff.** Catches everything, but needs `uv` installed in
   CI (a new action dependency) plus network access to a package index during
   the check — new supply-chain surface added by a supply-chain task.
2. **Offline consistency check** (chosen). A repo-own script
   `.github/scripts/check-dev-requirements-lock.py` parses both files and
   asserts (a) every direct pin in `requirements-dev.txt` appears in the lock at
   the identical version, (b) every lock entry carries at least one `--hash=`,
   and (c) the lock contains no unpinned entry. No network, no new tool, and it
   fails deterministically on exactly the Dependabot case, because the bumped
   direct pin is precisely what stops matching.

**What guard 2 provably does not catch**, stated so the acceptance criterion can
be written honestly rather than aspirationally: a removed direct pin whose lock
entry lingers, an orphaned transitive left behind by a shrunken dependency tree,
a hand-broadened marker, or a transitive pinned to a version the compiler would
not have chosen. All of those still install successfully, so no offline check
can distinguish them from a legitimate regeneration — that is precisely why the
recompile lane (guard 1) would be the only complete answer, and why its cost was
judged not worth paying here. What guard 2 does catch is the one failure mode
with a live source: Dependabot bumping a direct pin. "A new mypy release adds a
transitive" is also caught, because such a release changes the `mypy==` line
too.

Registration follows the existing generated-artifact pattern: a `lock-check`
Makefile target, wired into `check:` (`Makefile:56`), into
`.sd-ai-command-pack/check.json` as `repo.lockcheck` alongside the other
guard-safe entries, and into the CI `lint` job. Regeneration gets a `make lock`
target so the uv invocation lives in one place rather than in a doc.

### D4 — A-034: `NPM_CONFIG_IGNORE_SCRIPTS`

`scripts/update_repomix:24` runs `npx --yes repomix@1.16.1`, which executes any
lifecycle script the fetched package declares. The script already configures npm
through the environment (`export NPM_CONFIG_CACHE`, `:23`), so the in-style fix
is `export NPM_CONFIG_IGNORE_SCRIPTS=true` next to it rather than a new CLI flag.
The choice is stylistic consistency with the adjacent line, not a claim that
`npx --ignore-scripts` would fail; the env-var form also keeps the `exec npx`
invocation a single unbroken line.

Verified empirically on 2026-08-10 rather than assumed from npm's docs:

```
$ NPM_CONFIG_IGNORE_SCRIPTS=true npm config get ignore-scripts
true
$ npm config get ignore-scripts
false
```

## Boundaries And Non-Goals

- No edit to `.opencode/package.json` or any other Registry A file.
- No upstream pull request or issue against `mindfold-ai/Trellis` in this run —
  the target is known, the approval is not granted. Recorded as a follow-up.
- **No npm lockfile for the repomix fetch.** `npx --yes repomix@1.16.1` pins the
  tool but resolves its transitive tree fresh on every run. Vendoring a
  `package-lock.json` + `npm ci` for a docs-only, gitignored artifact
  (`docs/repomix-map.md`) is more machinery than the exposure warrants, so the
  residual risk is recorded as accepted where the pattern is documented — the
  third branch of the audit's own fix line (`report-2026-07-25.md:288`). This is
  the one place the task's goal is deliberately narrowed rather than met.
- No new Dependabot ecosystem block. npm stays out of scope (D1).
- No runtime (non-dev) dependency policy; the pack still ships zero runtime
  Python dependencies.
- No `pip-audit`/CVE lane — explicitly deferred by the archived
  `07-25-audit-dependabot-config` task and unchanged here.
- `uv` is not added as a required contributor tool for building or testing; it
  is required only to regenerate the lock (`make lock`), which contributors do
  only when they change a pin.

## Affected Files

| File | Change |
| --- | --- |
| `requirements-dev.lock` | **new**, generated |
| `.github/scripts/check-dev-requirements-lock.py` | **new**, repo-own checker |
| `.github/trellis-provenance.json` | regenerated — a new tracked `.github` file is an `uncovered:` finding until accepted into `repoOwn` |
| `tests/test_dev_requirements_lock.py` | **new**, unit tests for the checker |
| `requirements-dev.txt` | comment pointing at the lock and `make lock` |
| `README.md` | accepted-risk note for the unlocked `npx` transitive tree (`:290`) |
| `Makefile` | `setup` installs from lock; new `lock`, `lock-check`; `check` gains `lock-check` |
| `.github/workflows/tests.yml` | 3 × install + cache key switch to the lock; `lint` gains the check |
| `.sd-ai-command-pack/check.json` | new `repo.lockcheck` entry |
| `scripts/update_repomix` | `export NPM_CONFIG_IGNORE_SCRIPTS=true` |
| `tests/test_repomix.py` | assert the script sets that variable |
| `CONTRIBUTING.md` | lock workflow; corrected A-032 ownership wording |
| `.trellis/spec/backend/quality-guidelines.md` | A-032 local-only record |
| `.trellis/tasks/07-25-audit-dependency-hygiene/*` | task artifacts |

## Data And Command Contracts

- **Lock format**: `pip`-compatible requirements text. Each entry is
  `name==version[ ; marker] \` followed by one or more indented `--hash=sha256:…`
  continuation lines and a `# via …` comment. The checker parses only
  line-initial `name==version` and the presence of `--hash=` in the entry's
  continuation block; it does not attempt to model pip's grammar.
- **Checker CLI**: `check-dev-requirements-lock.py [--repo PATH]`. Exit 0 pass,
  1 findings (one `<class>: <detail>` line each, matching the
  `check-trellis-provenance.py` convention at `.github/scripts/check-trellis-provenance.py:11-14`),
  2 usage/environment error. Read-only; no `--write` mode, because regeneration
  belongs to `make lock`, which needs network.
- **Install contract**:
  `pip install --require-hashes --only-binary :all: -r requirements-dev.lock`.
  `--require-hashes` fails closed if an unhashed entry ever lands.
  `--only-binary :all:` is the load-bearing half: `--generate-hashes` hashes
  sdists too, so hash-checking mode alone would happily accept a source
  distribution, and a source build runs `setup.py`/PEP 517 hooks and resolves
  build requirements from the network — outside this lock entirely. Without
  `--only-binary :all:`, a future release that stops publishing a wheel for one
  lane would reintroduce exactly the un-reviewed-execution problem A-034
  addresses on the npm side.

## Risks And Edge Cases

1. **Dependabot PRs go red until the lock is regenerated.** Intended: a loud
   failure replaces a silent no-op. `CONTRIBUTING.md` documents the two-step
   (`make lock`, commit) and `sd-update-deps` triage already parks anything it
   cannot merge cleanly.
2. **`uv` unavailable on a contributor machine.** Only `make lock` needs it;
   `make setup`, `make test`, `make lint`, and every CI lane use plain pip.
   `make lock` fails with a plain "uv not found" from the shell.
3. **A missing wheel becomes a hard failure, by design.** `--require-hashes`
   alone would *not* stop a source build — uv hashes sdists as well — so
   `--only-binary :all:` is what makes the contract fail closed. Evidence for
   current wheel availability is the successful `--only-binary :all:` *compile*
   across the universal environment set, plus a macOS/CPython 3.13 install; the
   Linux 3.10 and 3.13 lanes are confirmed by CI on this PR, not by a local
   probe. If a future release drops a wheel, `make lock`, `make setup`, and CI
   all fail loudly rather than quietly running that package's build hooks.
4. **Universal resolution picks a version no single environment would.** uv's
   universal mode selects one version satisfying all environments, which can be
   older than a per-environment resolve. Accepted: identical inputs across the
   matrix is the property A-033 asks for.
5. **New platform/Python lane added later.** The floor lives in `make lock`
   (`--python-version 3.10`); adding a 3.9 lane without lowering it produces an
   install-time marker miss, not a silent wrong version.
6. **A new `.github` file is an automatic provenance failure until accepted.**
   `check-trellis-provenance.py` enumerates tracked files under `.github` with
   `git ls-files` (`:159`) and emits `uncovered: <path>` for anything absent
   from all three manifest keys (`:204`). The new checker therefore breaks
   `make trellis-provenance`, `make check`, and the CI `release-payload-gate`
   until it is absorbed with `--write --accept`. The trap is the ordering:
   discovery is `git ls-files`-based, so the gate *passes* while the file is
   still untracked and fails only after `git add`.
7. **Coverage floor.** `.github/scripts` is inside `.coveragerc`'s `source`, so
   an untested new script there drags the 80% floor down; hence
   `tests/test_dev_requirements_lock.py` ships in the same PR.
8. **The first lock is an upgrade, not a freeze.** Locking records today's
   resolution, which is not what every environment currently installs — this
   machine's `.venv` holds `ast_serialize==0.6.0` against a resolved
   `0.8.0` under an unchanged `mypy==2.3.0`. Merging the lock therefore *changes*
   what CI installs on the first run. The full `make check` gate must run after
   generation, not before, so a lint or type regression from the newly pinned
   transitive surfaces in this PR rather than the next one.
9. **repomix breakage from `--ignore-scripts`.** repomix is pure JavaScript with
   no postinstall step; if a future version needs one, `make repomix` fails
   visibly rather than silently producing a wrong map, and `docs/repomix-map.md`
   is gitignored and generated on demand (`tests/test_repomix.py:89-93`).

## Validation

Two load-bearing assumptions were proven during planning on 2026-08-10, not
deferred to implementation:

- The exact `make lock` command — including `--only-binary :all:` — compiles
  cleanly and emits 10 entries with the markers described above.
- `pip install --require-hashes --only-binary :all:` accepts that file. A
  throwaway venv on macOS/CPython 3.13 installed 9 of the 10 entries (`tomli`
  correctly skipped by its `python_full_version < '3.11'` marker) and exited 0.
  The 10-vs-9 gap is the marker working, not an inconsistency.

Both probes ran on macOS/CPython 3.13 only. The ubuntu 3.10 and 3.13 lanes are
verified by CI on the pull request; do not report them as locally proven.

Remaining checks, to run during implementation:

- `make lock` regenerates the lock byte-identically from a clean tree (proves
  the committed lock is the compiler's own output).
- `make lock-check` passes; mutating a pin in `requirements-dev.txt` without
  regenerating makes it fail with a mismatch finding.
- `make setup` in a scratch venv installs cleanly under `--require-hashes` —
  every entry whose marker matches the interpreter, so 9 on 3.11+ and 10 on
  3.10.
- `make test`, `make lint`, `make shell-syntax`, `make trellis-provenance`,
  `make release-check` — the full `make check` gate.
- `bash -n scripts/update_repomix` plus the new `tests/test_repomix.py`
  assertion; `make repomix` end-to-end when network is available, otherwise
  reported as unverified rather than claimed.
