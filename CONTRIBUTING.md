# Contributing

## Workflow

0. Run `make setup` once per fresh clone to create the virtualenv and install
   the dev dependencies (PyYAML, ruff, mypy, coverage); `make generate` and
   `make check` import PyYAML and crash without it.
0b. Install [Vale](https://vale.sh) once (`brew install vale`, or a packaged
   build of the same major as 3.18). `make check` runs the prose gate over the
   skill corpus and the root docs, and a missing binary is a hard failure
   rather than a silent pass — an environment without Vale must not be able to
   report a corpus it never linted.
1. Branch from `main`; open a PR for every change.
2. Edit canonical skills under `templates/skills/` and canonical agents under
   `templates/agents/`, never the generated `manifest.json` rows or
   `generated/**` overlays (including `generated/skills/`) by hand.
3. Run `make generate` after any skill, agent, or registry change so the
   manifest and generated overlays stay in sync (`make release-check` verifies
   this).
4. Run `make check` (tests, lint, release gates) before requesting review.

## Repo-own source vs vendored installs

There are no vendored installs any more. Every tracked file in this checkout is
this repository's own, so the ownership question this section used to answer no
longer has two answers: edit anything here and it stays edited.

What stood here was a do-not-edit table over `.github/prompts/sd-*.prompt.md`,
`.claude/rules/sd-*`, `.sd-ai-command-pack/**`, the Trellis platform trees and
`.trellis/**`, plus a two-registry lookup that decided ownership per path. The
framework removal deleted every family it named and the provenance gate that
enforced it, so keeping the table would have been a map of paths that are gone.

`git ls-files` is now the whole answer.

## Git version floor

**The suite requires git 2.32 or newer** (June 2021). Tests scrub the
machine's git configuration through `GIT_CONFIG_GLOBAL`, which older git
ignores — so on git < 2.32 the suite would silently run against your real
`~/.gitconfig` instead of failing. `tests/test_test_hermeticity.py` asserts the
version so that failure is loud rather than silent.

`make test-hermetic` goes further: it runs the whole suite against a
tracked-files-only copy of the repository under a deliberately hostile git
configuration. That lane is what proves the suite depends on neither your
configuration nor your untracked files; `make check` deliberately does not run
it, and CI does.

## Test coverage floor

`make test` and the CI `unittest` lane measure statement coverage of repo-own
Python and fail below a floor. Scope is `installer/`, `install.py`, and
`.github/scripts/`; every other tracked path is either not Python or not
executed by the suite. Much of this code runs via subprocess under
test, so `.coveragerc` enables `parallel` mode and
`tests/_coverage_subprocess/sitecustomize.py` (activated by
`COVERAGE_PROCESS_START`) measures those child processes; the run is
`coverage erase → run → combine → report --fail-under`.

- **Current floor: 88%.** It was 80 from introduction until 2026-08-30,
  deliberately below the measured baseline so the gate would land green with
  margin. That margin stopped being margin and became slack: the suite measures
  89.1% and could have lost nine points of coverage without the gate saying a
  word. Raised by the procedure below, off the run for #283:
  `unittest (ubuntu-latest, 3.10)` 89.0%, `(ubuntu-latest, 3.13)` 89.1%,
  `(macos-latest, 3.13)` 89.1% — minimum 89.0, floor set just under it. The
  3.10 lane is the low one because `tomllib`-gated tests skip there; the gap is
  currently 0.1 points, not the several the original note implied.
- **Raising it:** read the real per-lane totals from a green CI `unittest` run,
  take the minimum across the 3.10/3.13 × ubuntu/macOS matrix, and raise
  `--fail-under` in both the `Makefile` `test` target and
  `.github/workflows/tests.yml` to just under that minimum.
- The gate compares `round(total, precision)` (`[report] precision = 1`) against
  the floor, so a value that rounds to the floor passes.

## Release discipline

Any change to the shipped payload — `templates/**`, `generated/**`,
`installer/**`, `install.py`, or `manifest.json` — must:

- bump `version` in `manifest.json`, and
- add a matching top heading to `CHANGELOG.md` in the form
  `## <version> - YYYY-MM-DD`.

The gate is diff-based, so the carve-out is this: a change that leaves
every shipped payload path byte-identical (no git diff) needs no bump. Note that
`generated/registry-snapshot.json` is itself shipped payload, and family
descriptions now live in gated installer code (`installer/registry.py`), so a
family-description source edit does require a bump.

CI enforces this via the release payload gate against the real PR base and is
authoritative. Locally, `make release-check` passes `--base auto`, which
measures your branch against `origin/main` (not just uncommitted work); it is
best-effort — a stale `origin/main` can mask a missing bump, so `git fetch`
first if in doubt. Merges to `main` are tagged `v<version>` automatically when
the version changes.

### One version per pull request

A branch may add exactly one `## <version> - YYYY-MM-DD` heading, and the gate
fails the branch that adds more. A version bumped and then re-bumped on the same
branch never becomes a merge-base state, and the tagger that ran at the time
took its version from `manifest.json` alone, so the superseded heading was never
tagged. That is how `0.53.0` was written, superseded by `0.53.1` in PR #89, and
left permanently untagged — its changelog entry now carries that disposition,
and no `v0.53.0` will be backfilled.

Tagging no longer depends on that rule holding: a push to `main` tags every
changelog heading newer than the highest existing tag, so a push that somehow
carries two releases tags both. It still refuses to reach back below the highest
tag — a hole like `0.53.0` stays a hole rather than being pinned to a `HEAD` it
never shipped from.

If you have already bumped and need to bump again, rewrite the heading you
added rather than stacking a second one; ship genuinely separate releases as
separate pull requests.

### What earns a minor versus a patch

The pack is pre-1.0, so the leading `0.` is fixed and the minor position
carries the "something new or something gone" signal:

- **Minor** (`0.X.0`) — a new skill or agent, a new artifact kind, a new
  user-visible capability or argument, or a change in what an existing surface
  refuses or requires. Recent examples: `0.65.0` added `se-propose-skills`,
  `0.66.0` added `agent` as an artifact kind, `0.68.0` changed what
  `install.py update` refuses.
- **Patch** (`0.X.Y`) — everything else: fixes, refactors that keep behavior,
  documentation, and regenerated surfaces. Moving a generated file without
  changing an installed target is a patch (`0.68.3`).

Removals and breaking changes take a minor **and** lead their changelog bullet
with a bold marker, so a reader can find them without reading every entry:

```markdown
## 0.70.0 - 2026-08-11

- **Removed:** `se-pack`; refreshes now drop its vouched installed copies.
- **Breaking:** `install.py update` requires `--source` when provenance is absent.
```

Pre-1.0 means a minor may remove things. Anything relying on a surface should
pin a version rather than track `main`.

## Dependency updates

`.github/dependabot.yml` configures Dependabot to open weekly `pip` pull
requests for the pins in `requirements-dev.txt` (PyYAML, ruff, mypy, coverage),
with a `chore(deps)` commit prefix. Patch and minor bumps arrive batched as a
single grouped PR; majors arrive one per package, because `sd-update-deps`
always routes a major to manual review and grouping one in would block the safe
bumps behind it. Triage each with the `sd-update-deps` workflow: it classifies
the bump, merges the safe class through the housekeeping gate, and parks the
rest for review. Dependabot is the only sanctioned source that hands a
classified dependency PR to housekeeping.

**Lock regeneration.** Nothing installs from `requirements-dev.txt` directly.
`make lock` compiles it into `requirements-dev.lock` — fully pinned, hashed, and
wheel-only — and that lock is what CI and `make setup` install with
`--require-hashes --only-binary :all:`. Dependabot bumps the input file only, so
a dependency PR is incomplete until the maintainer runs `make lock` and commits
the regenerated lock in the same PR. `make lock-check` is what fails when they
drift apart; without it the merge would be a silent no-op that reinstalls the
version the PR claimed to replace.

`make relock-pr PR=<number>` is that step in one command: it checks out the bot
branch, regenerates the lock, and pushes it back, doing nothing if the lock
already matches. It refuses a PR that Dependabot did not author and refuses to
run against a dirty tree.

This stays a local helper on purpose. Doing it in CI means holding a writable
credential in a job triggered by a bot branch, and `GITHUB_TOKEN` cannot even
be that credential — GitHub suppresses workflow runs for events it generates,
so a lock pushed with it would never re-trigger `tests` and the PR would sit
permanently unmergeable. Grouped updates cap this at roughly one PR a week, and
that did not justify a standing write credential. The full comparison, including
the isolated `pull_request_target` design that was rejected, is archived at
`docs/work/archive/2026-08/2026-08-14-dependabot-lock-automation/design.md`.

Enablement: this repository is not a fork, so committing `dependabot.yml` to the
default branch is itself the enablement — version updates start automatically,
with no separate repo-level toggle needed to turn them on. They can still be
suppressed by disabling Dependabot at the repository or organization level
(Settings → Code security), which is observable only after the config lands on
`main`.

Deliberately out of scope for now:

- **npm.** The root `package.json` declares no dependencies, and the one
  manifest that did (`.opencode/package.json`) was deleted with the framework
  payload. Add an `npm` ecosystem block only if a real npm dependency is
  introduced into a repository-owned manifest.
- **A scheduled CVE / `pip-audit` lane.** The four dev-only pins have a small
  blast radius and Dependabot already surfaces version bumps. Revisit if the
  pack ever ships runtime (non-dev) Python dependencies.

## Dogfooding

`make sync` installs the pack into your own home directory (`install.py
--user`) so the skills you are editing are the skills you use.

### `.claude/` tracking policy

There is nothing left to track. The framework removal deleted every adapter,
agent, hook, command and settings file under `.claude/`, and the tracking
policy that kept them in a fresh clone went with them. `.gitignore` keeps one
rule for `settings.local.json`, because a local session still writes it.

Do **not** add a wholesale `.claude/` or `.claude/*` ignore even so. Git cannot
descend into a wholesale-ignored directory, so a rule like that would also
shadow any narrow re-include added later, and the failure is silent: the file
never appears in a fresh clone at all.

