# Review the Gemini and Codex retirements and their impact on distribution/install

## Problem

Two upstream retirements landed in Homebrew and were acted on locally on
2026-08-23; this repo distributes platform files for both ecosystems and has
not yet reacted:

- **Gemini CLI is going away.** The `gemini-cli` formula is deprecated
  ("not supported upstream") and will be **disabled on 2026-12-18**. Google
  folded the CLI into Antigravity; Homebrew's stated replacement is the
  `antigravity-cli` cask, which installs an `agy` binary — it does NOT
  provide a `gemini` command. Anything this repo installs or documents for
  the `gemini` CLI stops working for fresh installs after the disable date.
- **The Codex desktop app is discontinued.** The `codex-app` cask is
  deprecated ("discontinued upstream", disabled 2027-07-12) and has been
  uninstalled locally. The **codex CLI is unaffected** — the `codex` formula
  is alive and maintained. Only desktop-app assumptions are stale.

## Requirements

R1. Inventory every place this repo's distribution/install path targets the
    gemini CLI or the codex desktop app (configs shipped, manifests,
    registry/platform enumerations, install docs, CI).

R2. Decide the gemini strategy and record it: retarget to Antigravity
    (`agy`), keep-until-broken with a documented sunset, or drop the
    platform. Include what happens to already-installed users.

R3. Confirm the codex CLI path is desktop-app-free: nothing in install or
    docs should require or mention the retired `codex-app`.

R4. Apply the resulting changes (or file follow-up tasks per change) so a
    fresh install after 2026-12-18 does not reference a formula Homebrew
    refuses to install.

## Context

Pack-specific surfaces to review:
- `.gemini/settings.json` and `.codex/hooks.json` shipped in the repo — the
  gemini one loses its consumer when the gemini CLI is disabled; the codex
  one targets the still-supported codex CLI and should be confirmed, not
  removed.
- `generated/registry-snapshot.json`, `manifest.json`,
  `.sd-ai-command-pack/manifest.json` / `provenance.json` — platform
  enumerations to align with whatever is decided.
- `docs/repomix-map.md`, `CONTRIBUTING.md`, `.github/copilot-instructions.md`
  mention gemini — update wording once the decision lands.

## Acceptance criteria

- [ ] Written inventory of gemini/codex-desktop touchpoints in this repo
- [ ] Gemini decision recorded (retarget / sunset / drop) with rationale
- [ ] Codex CLI path confirmed free of desktop-app assumptions
- [ ] Changes applied or follow-up tasks filed for each touchpoint
