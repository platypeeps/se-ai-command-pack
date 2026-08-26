# Relay the gemini-CLI retirement decision to sd-ai-command-pack

## Problem

The `gemini-cli` Homebrew formula is deprecated ("not supported upstream") and
is **disabled on 2026-12-18**. Google folded the CLI into Antigravity;
Homebrew's stated replacement is the `antigravity-cli` cask, which installs an
`agy` binary and does **not** provide a `gemini` command.

`sd-ai-command-pack` ships gemini command adapters. Its provenance receipt in
this repository records:

```
pack      = sd-ai-command-pack
version   = 0.71.51
mode      = thin
platforms = ["claude", "gemini", "github", "opencode"]
```

Those adapters install at **user level** (`~/.gemini/commands/sd`), not into
consumer repositories. After the disable date a fresh machine cannot install
the CLI that consumes them.

## Why this is a separate task

Task `08-23-review-gemini-codex-retirement` established that
`se-ai-command-pack` has no gemini surface of its own to change: its
`PLATFORM_REGISTRY` (`installer/registry.py:56-74`) declares only `agents`,
`claude`, and `codex`, and its `manifest.json` contains zero gemini strings.
The decision therefore belongs to `platypeeps/sd-ai-command-pack`, a different
repository.

Full evidence:
`.trellis/tasks/08-23-review-gemini-codex-retirement/research/inventory-2026-08-26.md`.

## Requirements

R1. Decide the gemini strategy for `sd-ai-command-pack` and record the
    rationale. The three options:
    - **Retarget to Antigravity.** Ship the adapters for `agy` instead. Note
      that `agy` is not a drop-in for `gemini`; the command surface and
      argument conventions need checking before this is costed.
    - **Keep until broken, with a documented sunset.** Leave the adapters,
      document the 2026-12-18 date, and stop claiming gemini support.
    - **Drop the platform.** Remove the gemini rows from the pack registry and
      manifest.

R2. Decide what happens to **already-installed users** — people who already
    have `~/.gemini/commands/sd/*.toml` on disk. Determine whether the
    installer orphans those files, removes them on refresh, or leaves them
    until an explicit uninstall, and whether existing provenance receipts stay
    valid. This is the half of the question most likely to be skipped.

R3. Relay the decision to `platypeeps/sd-ai-command-pack` as an issue or PR.
    This repository cannot land the change.

R4. Once the pack ships the decision, confirm no fleet consumer still installs
    a gemini adapter.

## Constraints

- Work happens in `platypeeps/sd-ai-command-pack`, not here. Opening a pull
  request there needs explicit per-PR approval.
- The Gemini **API** is unaffected. Do not conflate it with the CLI: the
  `gemini` references in `.github/workflows/sd-review.yml` and
  `ai-review-router.yml` are a PR-agent model provider and must stay.

## Acceptance criteria

- [ ] Gemini strategy for `sd-ai-command-pack` decided and recorded with rationale
- [ ] Already-installed-user behavior determined from installer code, not assumed
- [ ] Decision relayed upstream to `platypeeps/sd-ai-command-pack`
- [ ] After the pack ships it, fleet consumers confirmed free of gemini adapters

## Deadline

2026-12-18 — the `gemini-cli` formula disable date. After it, a fresh install
cannot obtain the CLI these adapters target.
