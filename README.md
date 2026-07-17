# SE AI Command Pack

User-level knowledge-work skills for AI agent frameworks: deep research,
daily briefs, meeting prep, landscape scans, and document digests —
installed once per machine, centrally managed from this repository.

The pack borrows the installer architecture of its sibling
`sd-ai-command-pack` (manifest-driven payload, provenance receipts, vouched
removal, generated surfaces) but targets general knowledge work instead of
the software-delivery lifecycle, installs into **user-level** agent scopes
instead of per-repo adapters, and has no Trellis dependency.

## Skills

| Skill | Purpose |
|---|---|
| `se-research` | Deep multi-source research with verification and an explicit disconfirmation pass; produces a cited, confidence-labeled brief. |
| `se-brief` | Morning/daily/on-demand brief assembling the user's topics into one dated, scannable update. Read-only by design. |
| `se-meeting-prep` | One-page dossier on meeting participants, company, and context, plus goal-aligned talking points and questions. |
| `se-scan` | Competitive/market landscape scan: inventory the players, compare on consistent criteria, surface whitespace. |
| `se-digest` | Synthesize user-supplied documents/threads/links into one decision-ready brief with disagreements surfaced. |
| `se-pack` | Manage the pack itself from inside a session: status, update, refresh, remove. |

Research-family skills share one quality bar: a `source-standards.md`
reference (source tiers, independence, dating, confidence vocabulary) is
installed into each skill's `references/` directory.

## What gets installed where

Skills are plain `SKILL.md` directories, installed into every platform
whose anchor directory exists in your home directory:

| Platform | Skills directory | Gating anchor | Used by |
|---|---|---|---|
| `claude` | `~/.claude/skills/` | `~/.claude` | Claude Code / Cowork |
| `codex` | `~/.codex/skills/` | `~/.codex` | OpenAI Codex (honors `$CODEX_HOME`) |
| `agents` | `~/.config/agents/skills/` | `~/.config/agents` | Amp and compatible tools |

A platform whose anchor is missing is skipped with a hint; pass
`--platform <id>` or `--all` to install it anyway. Adding a platform is one
row in `installer/registry.py`.

## Install

```sh
git clone https://github.com/platypeeps/se-ai-command-pack.git
cd se-ai-command-pack
python3 install.py --user
```

Useful variants:

- `python3 install.py --user --dry-run` — show the plan without writing.
- `python3 install.py --user --platform codex` — one platform only.
- `python3 install.py --user --all` — install every platform, creating
  missing directories.

The installer is plan-before-apply: if any target file exists with
different content, it reports the conflicts and exits with code 2 without
writing anything. Re-run with `--force` to overwrite (add `--backup` to
keep `.bak` copies).

## Update

```sh
cd se-ai-command-pack
git pull --ff-only
python3 install.py --user
```

Or, from inside any session where the pack is installed, invoke `se-pack`
with `action=update` — it locates the checkout via the install receipts,
pulls fast-forward only, shows the dry-run plan, and reapplies.

## Remove

```sh
python3 install.py --remove            # add --dry-run to preview
```

Removal is vouched: a file is deleted only when its content matches the
recorded install hash or the current template. Files you have edited are
preserved and reported; `--remove --force` deletes them too. Empty parent
directories are pruned.

## How it works

- `templates/skills/<name>/` holds the canonical skill definitions — the
  only place skills are edited.
- `installer/registry.py` declares the platforms, the skill list, and the
  shared-reference fan-out; `make generate` regenerates `manifest.json`
  from it (one row per skill file per platform).
- `install.py` applies the manifest to your home directory (or `--root`
  elsewhere) and writes receipts under `~/.se-ai-command-pack/`:
  - `manifest.json` — copy of the installed manifest (version lookup);
  - `provenance.json` — sha256 per installed file plus `sourceRoot`, the
    checkout path updates run from;
  - `installed-targets.txt` — every installed path, the removal record.
- CI gates: the manifest must match the generated surfaces, and any payload
  change must bump the version with a dated `CHANGELOG.md` heading.

## Maintaining the pack

1. Edit or add skills under `templates/skills/` (see
   [docs/SE_AI_COMMAND_PACK.md](docs/SE_AI_COMMAND_PACK.md) for the
   add-a-skill checklist).
2. `make generate` to refresh the manifest.
3. Bump `version` in `manifest.json` and add the matching `CHANGELOG.md`
   heading.
4. `make check` (tests, lint, release gates), then PR.
5. `make sync` to dogfood the result into your own home directory.

## Non-goals in v0.1 (designed-for, not built)

- **Per-folder installs** — the manifest already carries a `scope` field
  and the installer a `--root`; a future `project` scope slots in without a
  schema break.
- **Plugin/marketplace packaging** — a build step can emit a plugin layout
  from the same `templates/skills/` source; that is the path to cloud
  sessions whose home directory is not this machine's.
- **Command surfaces** (per-platform command/prompt adapters) — the
  generator keeps the sd-pack fan-out pattern available if skills alone
  stop being enough.
- **A workflow backbone** — `preflight_checks()` in `install.py` is the
  single seam where a future backend prerequisite would land.

## License

MIT — see [LICENSE](LICENSE).
