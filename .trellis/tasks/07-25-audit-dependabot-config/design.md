# Design — Dependency bot and audit lane (A-031)

Base branch: `main`. Feature branch: `audit/dependabot-config`.

## Decisions

### D1 — Ecosystem scope: pip only (npm deferred)

Cover **pip** (`requirements-dev.txt` at repo root) and **not** npm.

- The goal (A-031) is that dependency-update PRs actually arrive so the
  dogfooded `sd-update-deps` triage stops being inert. pip coverage alone
  satisfies that: PyYAML, ruff, mypy, and coverage all get update PRs.
- Root `package.json` declares **no dependencies** (scripts only), so a npm
  ecosystem entry there would find nothing to update.
- The only npm manifest with deps, `.opencode/package.json`
  (`@opencode-ai/plugin` floating, no lockfile), is unused by any tracked code
  and is flagged for **removal** under A-032. Adding Dependabot coverage for it
  would generate PRs for a package nothing imports and become dead config once
  A-032 lands. Per the PRD's coordinate-with-A-032 note, npm coverage is
  deferred, not duplicated. (User-confirmed 2026-08-04.)

If A-032 keeps `.opencode` (pinned + lockfile) or a real npm runtime dep is
introduced, add a `npm` ecosystem block then.

### D2 — No scheduled pip-audit (CVE) lane

Do not add a pip-audit / osv CI lane in this task. (User-confirmed 2026-08-04.)

- Four pinned, dev-only dependencies with a small blast radius; Dependabot
  already surfaces version bumps.
- A recurring network CI lane over four dev tools is low value now.
- Revisit when the pack ships runtime (non-dev) Python deps or the dependency
  surface grows; recorded in CONTRIBUTING so the deferral is explicit, not lost.

### D3 — dependabot.yml shape

`version: 2`, one `updates` entry:

- `package-ecosystem: "pip"`, `directory: "/"` (requirements-dev.txt lives at
  root; Dependabot's pip ecosystem reads `requirements*.txt`). Root
  `pyproject.toml` is ruff/mypy config only — no `[project]`/PEP 621 or poetry
  dependency table — so Dependabot pulls nothing from it; requirements-dev.txt
  is the sole pip manifest.
- `schedule.interval: "weekly"` (a fixed day keeps PR arrival predictable).
- `open-pull-requests-limit: 5` (covers all four deps with headroom).
- `commit-message.prefix: "chore(deps)"` so bot commits match the repo's
  conventional-commit style and are easy to classify.
- **Ungrouped** (one PR per dependency): `sd-update-deps` classifies and merges
  per-package, so per-PR updates triage more cleanly than a grouped PR. Grouping
  can be introduced later if weekly PR volume becomes noisy.

### D4 — Validation strategy

No official Dependabot schema validator ships locally, so "schema-checked"
(AC1) is met by a **strict** offline assertion of every planned field and value,
not a subset:

- YAML parses (`yaml.safe_load`);
- top-level keys are exactly `{version, updates}` — any unknown top-level key
  fails (guards typos GitHub would silently ignore);
- `version == 2`;
- `updates` is a list of length exactly 1;
- the pip entry asserts every value the plan commits to:
  `package-ecosystem == "pip"`, `directory == "/"`,
  `schedule.interval == "weekly"`, `open-pull-requests-limit == 5`,
  `commit-message.prefix == "chore(deps)"`.

Asserting the two optional fields (`open-pull-requests-limit`,
`commit-message.prefix`) is deliberate: a subset check would pass a config that
dropped or corrupted them.

GitHub only reads `dependabot.yml` from the **default branch** and validates it
there — not on a feature-branch PR. So GitHub's own validation and Dependabot's
config pickup are a **post-merge** signal on `main` — the D6 post-archive
handoff, **not** acceptance evidence and not a pre-merge PR gate. The strict
offline check above is the pre-merge gate and the AC1 evidence.

### D5 — sd-update-deps triage documentation

Add a **Dependency updates** section to `CONTRIBUTING.md`: Dependabot opens
weekly pip PRs; triage them with `sd-update-deps` (classify, merge the safe
class under the housekeeping gate, park the rest). Record the npm and pip-audit
deferrals and the enablement model (D6: committing to the default branch enables
version updates on this non-fork; org-level disablement is the only blocker) in
the same section.

### D6 — Enablement model and post-archive handoff

Enablement facts (GitHub docs, verified 2026-08-04; repo is **not** a fork per
live `gh repo view` → `"isFork": false`):

- For a non-fork repository, **committing `dependabot.yml` to the default branch
  is itself the enablement** — version updates turn on automatically; there is
  no separate repo-level "enable version updates" toggle to flip.
- A separate manual enable step exists only for **forks**, and version updates
  can be suppressed by an **org-level** Dependabot disablement. Org-level policy
  is the only realistic blocker here, and it is observable only post-merge.

So the earlier "must be enabled in repo/org settings, unverifiable offline"
framing was wrong for this repo.

**AC1 is not gated on any post-merge observation.** Per the completion contract
(all acceptance criteria true before `task.py archive`; merge is post-archive),
AC1 is met pre-archive by the strictly-checked committed config (D4) plus the
CONTRIBUTING documentation. The following is the **post-archive handoff**, run
after housekeeping merges the PR, and is explicitly not acceptance evidence:

- Verify GitHub registered the config — the repo's
  Insights → Dependency graph → Dependabot tab lists it with no parse errors,
  and/or a `dependabot[bot]` pip PR appears
  (`gh pr list --repo platypeeps/se-ai-command-pack --author 'app/dependabot'`).
- If post-merge Dependabot instead reports a config error or an org policy
  suppresses updates, record that **actual observed** blocker as a follow-up
  task. Do not pre-document a hypothetical toggle.

## Scope / compatibility

- Additive only, and exactly two committed files change: a new
  `.github/dependabot.yml` and a CONTRIBUTING section.
- No shipped-payload change (`templates/**`, `generated/**`, `manifest.json`
  untouched) → no version bump; release gate stays green.
- No runtime/consumer surface change.

`.obsidian-kb` (a gitignored symlink to a local wiki outside the repo) is **not**
a task deliverable and is out of this task's committed scope and rollback. It
mirrors CONTRIBUTING.md automatically as a routine, local-only side effect of the
ship lifecycle's update-spec stage (which also keeps `sd-check`'s
`knowledge.obsidian-kb` current before review) and housekeeping's post-finish
refresh. This task adds no manual KB write of its own.

## Rollback

Delete `.github/dependabot.yml` and the CONTRIBUTING section — the only two
committed artifacts. Nothing else depends on them. No KB or external-path
accounting is needed because this task commits no such change.
