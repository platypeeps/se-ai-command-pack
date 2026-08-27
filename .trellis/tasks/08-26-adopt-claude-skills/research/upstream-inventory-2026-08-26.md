# claude-skills / opencode-cfg inventory (2026-08-26)

Upstream: `Shearerbeard/claude-skills` @ `0e4fb48ed69d665fd1307a51cb126af915c6502b`
Local checkout: `~/repos/ai/claude-skills` (full clone, clean, tracks the GitHub remote).
History: 111 commits, 2025-11-05 through 2026-08-03. Actively maintained.

## Shipped skills (22 across 4 plugins)

| Plugin | Skills |
|---|---|
| `python` | python-quality, python-review |
| `rust` | rust-async, rust-design, rust-modules, rust-quality, rust-review, typed-holes |
| `docs` | adr-review, docs-bustest, humanizer, mermaid, prose-lint |
| `workflow` | codex-cli, collaborating-with-antigravity, gate-probes, git-commit, opencode-cli, plan-discipline, process-feedback, rebase-hygiene, skill-retro |

Two further plugins ship LSP config only, no skills: `vale-lsp`, `haskell-lsp`.

## Licensing (blocks redistribution, not use)

- No `LICENSE` or `COPYING` file at repo root.
- Exactly 1 of 22 `SKILL.md` files declares a license: `plugins/docs/skills/humanizer/SKILL.md` (`license: MIT`).
- The remaining 21 carry no license declaration and are all-rights-reserved by default.

Consequence: safe to install at user scope for personal use; NOT safe to vendor into this
pack, which redistributes payload through `manifest.json`, the provenance gate, and the
fleet registry. Vendoring is parked on a root LICENSE appearing upstream.

## opencode-cfg relationship

The local `opencode-cfg` checkout now lives at `~/repos/ai/opencode-cfg` and is tracked
locally from baseline commit `b37c6ec` (2026-08-26). That commit records receipt, not
provenance: the directory arrived with no git history, no upstream remote, and no license.
It ships 7 OpenCode
agents and zero skills, and routes to skills by name and by glob. It is the consumer layer for
this exact library.

Explicitly named skills (11 unique, across permission rules and `load` instructions):

| Name | In claude-skills? |
|---|---|
| gate-probes, humanizer, prose-lint, typed-holes, docs-bustest, python-quality, python-review, rust-review | yes (8) |
| codebase-design, domain-modeling, prose-corpus | no (3) |

Glob rules `docs-*`, `python-*`, and `rust-*` resolve to families the library does ship.

The 3 unresolved names are genuine gaps and point to a third source not present on this
machine. `board-hygiene` and `delegating-work` are NOT referenced rules: they appear only
inside a trailing comment on the `"*": deny` line of `agent/frontier-reviewer.md:21`, so they
require nothing.

Agent model pins target another party's accounts and are not portable:
`baseten/moonshotai/Kimi-K3`, `baseten/zai-org/GLM-5.2`, `baseten/moonshotai/Kimi-K2.7-Code`,
`baseten/deepseek-ai/DeepSeek-V4-Flash-0731`, `amazon-bedrock/deepseek.v3.2`.

The portable asset is the permission model, e.g. `skill: {"*": deny, "rust-*": allow}`.

## Install-safety verification

- Upstream installer prunes only entries listed in its own `.manifest.<marketplace-name>`
  (`bin/install-skills:214`). It never touches unmanifested directories.
- `~/.agents/skills/` currently holds **92 entries, all directories** — 91 visible plus the
  hidden `.people-profiles`. A plain `ls | wc -l` reports 91 and silently omits the hidden
  one; any before/after comparison must use `ls -A` or `find`.
- None carry a manifest, so every existing skill is classified third-party by this source and
  is not prunable by it.
- Name-collision check between the incoming 22 and the installed 92: zero collisions.
- **The default installer mode also mutates the Claude Code plugin registry**, not just
  `~/.agents/skills/`: `bin/install-skills:103` runs `claude plugin marketplace add` and
  `:108` runs `claude plugin install --scope user`. Per the upstream README, Claude Code
  reaches these skills through that marketplace, NOT through `~/.agents/skills/` — that path
  serves OpenCode, Codex, and Pi. `--agents-only` restricts the install to the latter.

## Per-skill relevance to this repo

Repo is Python + JavaScript today, documentation-heavy, and is itself a skill pack.
Rust is inbound, which promotes the rust skills and the Rust agents from out-of-scope to
in-scope.

- Adopt: gate-probes, plan-discipline, skill-retro, process-feedback, git-commit,
  rebase-hygiene, prose-lint, humanizer, docs-bustest, adr-review, python-quality,
  python-review.
- Adopt, repo-relevant as of 2026-08-26: the 6 rust skills. Rust is arriving in this repo,
  so `rust-design`, `rust-async`, `rust-quality`, `rust-review`, `rust-modules`, and
  `typed-holes` are first-class here rather than user-scope spillover.
- Not skills, no install surface: `haskell-lsp`, `vale-lsp`.
- Skip: `mermaid`. It shells out to `mermaid-view`, which its own SKILL.md states is
  installed from the author's dotfiles rather than the repo, so it arrives with a broken
  dependency. `archify` already owns diagram authoring here and is unaffected.
- Directly relevant to in-flight task 08-25: `collaborating-with-antigravity` is a worked
  example of the gemini-to-agy transition being relayed there.

## Unverified

- Whether python-quality / python-review conflict with this repo's ruff and mypy config.
- Whether plan-discipline's five gate types collide with
  `.claude/rules/sd-planning-adversarial-review.md`.
