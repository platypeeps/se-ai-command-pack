# Contributing

## Workflow

1. Branch from `main`; open a PR for every change.
2. Edit canonical skills under `templates/skills/` and canonical agents under
   `templates/agents/`, never the generated `manifest.json` rows or
   `generated/**` overlays by hand.
3. Run `make generate` after any skill, agent, or registry change so the
   manifest and generated overlays stay in sync (`make release-check` verifies
   this).
4. Run `make check` (tests, lint, release gates) before requesting review.

## Test coverage floor

`make test` and the CI `unittest` lane measure statement coverage of repo-own
Python and fail below a floor. Scope is `installer/`, `install.py`, and
`.github/scripts/` (vendored `scripts/` and `.trellis/` are out of scope). Much
of this code runs via subprocess under test, so `.coveragerc` enables
`parallel` mode and `tests/_coverage_subprocess/sitecustomize.py` (activated by
`COVERAGE_PROCESS_START`) measures those child processes; the run is
`coverage erase → run → combine → report --fail-under`.

- **Current floor: 80%.** It was introduced deliberately below the measured
  baseline (~88% on Python 3.13; the ubuntu-3.10 lane is lower because
  `tomllib`-gated tests skip there) so the gate lands green with margin.
- **Raising it:** read the real per-lane totals from a green CI `unittest` run,
  take the minimum across the 3.10/3.13 × ubuntu/macOS matrix, and raise
  `--fail-under` in both the `Makefile` `test` target and
  `.github/workflows/tests.yml` to just under that minimum.
- The gate compares `round(total, precision)` (`[report] precision = 1`) against
  the floor, so a value that rounds to the floor passes.

## Release discipline

Any change to the shipped payload (`templates/**`, `generated/**`, or
`manifest.json`) must:

- bump `version` in `manifest.json`, and
- add a matching top heading to `CHANGELOG.md` in the form
  `## <version> - YYYY-MM-DD`.

CI enforces this via the release payload gate. Merges to `main` are tagged
`v<version>` automatically when the version changes.

## Dependency updates

`.github/dependabot.yml` configures Dependabot to open weekly `pip` pull
requests for the pins in `requirements-dev.txt` (PyYAML, ruff, mypy, coverage),
one PR per package, with a `chore(deps)` commit prefix. Triage each with the
`sd-update-deps` workflow: it classifies the bump, merges the safe class through
the housekeeping gate, and parks the rest for review. Dependabot is the only
sanctioned source that hands a classified dependency PR to housekeeping.

Enablement: this repository is not a fork, so committing `dependabot.yml` to the
default branch is itself the enablement — version updates start automatically,
with no separate repo-level toggle. The only thing that can suppress them is an
org-level Dependabot disablement, which is observable after the config lands on
`main`.

Deliberately out of scope for now:

- **npm.** The root `package.json` declares no dependencies, and the only npm
  manifest with any (`.opencode/package.json`) is unused and slated for removal.
  Add an `npm` ecosystem block only if a real npm dependency is introduced.
- **A scheduled CVE / `pip-audit` lane.** The four dev-only pins have a small
  blast radius and Dependabot already surfaces version bumps. Revisit if the
  pack ever ships runtime (non-dev) Python dependencies.

## Dogfooding

`make sync` installs the pack into your own home directory (`install.py
--user`) so the skills you are editing are the skills you use.

### `.claude/` tracking policy

The sd-ai-command-pack Claude adapters under `.claude/` — `commands/sd/`,
`skills/sd-*/`, `rules/sd-*.md`, and `sd-ai-command-pack/` — are **tracked**, so a
fresh clone reproduces the dogfooded Claude surface. This mirrors the already
tracked `.gemini/commands/sd/*` twins. Everything else under `.claude/` (local
third-party skills, `agents/`, `hooks/`, `settings*.json`, `commands/trellis/`,
and all `.claude/**` local state) stays ignored. The allowlist lives in the top
block of `.gitignore`.

Do **not** re-assert a wholesale `.claude/` ignore. A trailing-slash `.claude/`
rule makes Git skip the whole directory, so the re-includes below it can no
longer surface the adapters. If you re-run `trellis init`, verify it did not put
`.claude/` back; the durable fix is an upstream `trellis init` change (emit
narrow `.claude/**` local-state rules like it already does for `.gemini`, no
wholesale ignore) — tracked as a separate follow-up task.
