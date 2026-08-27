# Gemini / Codex-desktop touchpoint inventory

As-of 2026-08-26, against `main` at a clean tree. Satisfies PRD R1 and R3.

## Headline

This repository's own command pack **never targeted the gemini CLI**. The
gemini exposure here is entirely (a) vendored Trellis files this repo cannot
fix locally, and (b) a *different* pack installed as a consumer. The codex
surface is the **codex CLI**, which is unaffected by the desktop-cask
retirement.

## R1 — gemini touchpoints

### This repo's own pack: no gemini surface

| Evidence | Finding |
|---|---|
| `installer/registry.py:56-74` | `PLATFORM_REGISTRY` declares exactly three platforms: `agents`, `claude`, `codex`. No `gemini` row. |
| `manifest.json` | 0 occurrences of the string `gemini`. 185 `files[]` rows carry `platform: codex`, 183 of them targeting `.codex/skills/**` (the skill fan-out) and the remaining 2 targeting `.codex/agents/**` (`se-claim-verifier.toml`, `se-source-reader.toml`). |
| `templates/` | Contains only `agents/` and `skills/`. No `templates/.gemini/`. |

Adding or removing a platform is one registry row plus `make generate`
(`installer/registry.py:54-55`). Nothing gemini-shaped exists to remove.

### `.gemini/**` in-tree: vendored Trellis, not pack-shipped

Nine tracked files, all classified **Trellis-vendored** by
`CONTRIBUTING.md:45` (`.codex/**`, `.claude/{agents,hooks,settings.json}`,
`.gemini/{agents,hooks,settings.json}`, ... | Trellis | `mindfold-ai/Trellis`):

```
.gemini/agents/trellis-{check,implement,research}.md
.gemini/commands/trellis/{continue,finish-work}.toml
.gemini/hooks/{inject-shell-session-context,inject-workflow-state,session-start}.py
.gemini/settings.json
```

A local edit to any of these is reverted by the next `trellis update`. All
nine are hashed by the release gate:
`.github/scripts/check-trellis-provenance.py:44` sets
`PLATFORM_DIRS = (".agents", ".claude", ".codex", ".gemini", ".github", ".opencode")`
and `.github/trellis-provenance.json` records all nine paths. Removing them
locally would fail the `release-payload-gate` job as `uncovered:`/`drifted:`
until that manifest were regenerated — and would then be undone by the next
Trellis refresh anyway.

### SD pack (a separate pack, installed here as a consumer)

`.sd-ai-command-pack/provenance.json`: pack `sd-ai-command-pack`, version
`0.71.51`, mode `thin`, `platforms = ["claude", "gemini", "github", "opencode"]`.

Its gemini command adapters install at **user level** (`~/.gemini/commands/sd`),
not into this repository — `.gemini/commands/` here contains only `trellis/`.
The retarget/sunset/drop decision for those adapters belongs to
`platypeeps/sd-ai-command-pack`, not to this repo.

### Repo-own prose mentioning gemini

Only three lines, all DESCRIPTIVE ownership-table entries, none install-critical:

- `CONTRIBUTING.md:45` — vendored-ownership table row
- `CONTRIBUTING.md:252` — narrow local-state ignore rules "like the ones already emitted for `.gemini`"
- `CONTRIBUTING.md:265` — provenance gate's platform-dir list

`CHANGELOG.md` contains **0** gemini mentions. Every other `.md` hit lives in
vendored `trellis-meta` reference docs under `.agents/`, `.opencode/`, and
`.github/skills/`.

### False positives — deliberately excluded

- `.github/workflows/sd-review.yml:149,173` and
  `.github/workflows/ai-review-router.yml:77,101` reference `gemini` as an **AI
  model provider** (`PR_AGENT_MODEL_PROVIDER == 'gemini'`,
  `GOOGLE_AI_STUDIO__GEMINI_API_KEY`). That is the Gemini **API**, unaffected by
  the gemini **CLI** deprecation. Do not "fix" these.
- `tests/test_skill_review.py:149,159,225,1001` builds a **synthetic tmp
  fixture** (`root = self.base / "sd-pack"`) simulating an SD-pack-shaped repo
  with gemini adapters. `templates/.gemini/` does not exist in this repo. No
  test asserts a real gemini surface here.

### Tests that would go red if gemini were "dropped"

None. No test in `tests/` asserts a real gemini platform surface. The only
gate that touches `.gemini/**` is the vendored-provenance hash check described
above, which guards Trellis payload integrity, not pack platform membership.

## R3 — codex CLI path is desktop-app-free: CLEAN

Searches run (excluding `.git/`, `.venv/`, `node_modules/`), case-insensitive,
across `*.md,*.py,*.json,*.toml,*.yml,*.yaml,*.sh`:

```
codex-app | codex\.app | /Applications/Codex | codex desktop | brew install --cask
cask
```

Outside the task's own `prd.md` / `task.json`, exactly one hit:

- `.codex/config.toml:24` — a comment warning that the structured
  `[features.multi_agent_v2]` table form breaks on Codex 0.130 and earlier,
  "including the codex CLI bundled inside the Codex desktop app". This
  *mentions* the desktop app in order to avoid breaking it. It is a
  compatibility note, not a dependency.

No `brew install --cask` anywhere. No `.app` bundle path assumptions. Nothing
installs, requires, or instructs a user to obtain `codex-app`. The `codex`
platform in `installer/registry.py:68-73` is the CLI: its `skills_dir` and
`agents_dir` are home-relative install targets, not directories in this
repository.

**R3 verdict: confirmed clean. No change required.**
