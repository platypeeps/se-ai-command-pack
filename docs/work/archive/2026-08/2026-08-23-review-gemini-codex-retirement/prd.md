---
title: Review the Gemini and Codex retirements and their impact on distribution/install
status: done
created: 2026-08-23
branch: docs/gemini-codex-retirement-inventory
---
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

## Acceptance criteria (original, SUPERSEDED 2026-08-26)

> Superseded by "Acceptance criteria (superseding, 2026-08-26)" at the end of
> this document. Kept for provenance; do not track progress here. The second
> criterion below is the one the inventory invalidated: it presumes a gemini
> platform exists in this repository to make a strategy decision about.

- [ ] Written inventory of gemini/codex-desktop touchpoints in this repo
- [ ] Gemini decision recorded (retarget / sunset / drop) with rationale
- [ ] Codex CLI path confirmed free of desktop-app assumptions
- [ ] Changes applied or follow-up tasks filed for each touchpoint

## Decisions (2026-08-26)

Recorded after the R1/R3 inventory
(`research/inventory-2026-08-26.md`). The Problem section above was written
before the inventory and overstates this repository's exposure; these
decisions correct it and take precedence.

**D1 — the Problem statement's premise is half wrong.** "This repo
distributes platform files for both ecosystems" holds for codex and does
**not** hold for gemini. `installer/registry.py:56-74` declares exactly three
platforms (`agents`, `claude`, `codex`); `manifest.json` contains zero gemini
strings; there is no `templates/.gemini/`. This repository's own pack has
never shipped a gemini surface.

**D2 — R2 is not applicable to this repository.** There is no gemini platform
here to retarget, sunset, or drop, so none of the three offered strategies has
a referent. The two real gemini surfaces both sit outside this repo's control:

- `.gemini/**` (nine tracked files) is Trellis-vendored per
  `CONTRIBUTING.md:45`. A local edit is reverted by the next `trellis update`,
  and all nine are hashed by the `release-payload-gate`
  (`.github/scripts/check-trellis-provenance.py:44`).
- The gemini command adapters belong to `sd-ai-command-pack` v0.71.51
  (`platforms = ["claude","gemini","github","opencode"]`) and install at user
  level (`~/.gemini/commands/sd`), not into this repository.

"What happens to already-installed users" is therefore also not this repo's
question to answer: no user has ever received a gemini file from this pack.

**D3 — R3 is confirmed clean; no change required.** The `codex` platform here
is the codex CLI, which is unaffected. The single desktop-app mention,
`.codex/config.toml:24`, exists to warn against a config form that breaks the
bundled CLI. It is a compatibility note, not a dependency.

**D4 — scope of the resulting change (R4).** Land the inventory, add a short
`CONTRIBUTING.md` note recording why gemini is not a platform of this pack so
the next reader does not re-investigate, and file a follow-up Trellis task
relaying the genuine gemini decision to `platypeeps/sd-ai-command-pack`. No
code, registry, manifest, or `.gemini/**` change is warranted here.

**D5 — two false positives are deliberately left untouched.** The
`gemini` hits in `.github/workflows/sd-review.yml` and
`.github/workflows/ai-review-router.yml` are the Gemini **API** as a PR-agent
model provider, unaffected by the CLI deprecation. The `gemini` rows in
`tests/test_skill_review.py` are a synthetic tmp fixture simulating an
SD-pack-shaped repo. Neither is a touchpoint.

## Acceptance criteria (superseding, 2026-08-26)

- [x] Written inventory of gemini/codex-desktop touchpoints in this repo
      (`research/inventory-2026-08-26.md`)
- [x] Gemini decision recorded: **not applicable to this repository**, with
      the evidence and the two out-of-scope owners named (D2)
- [x] Codex CLI path confirmed free of desktop-app assumptions (D3)
- [x] Changes applied or follow-up tasks filed for each touchpoint:
      `CONTRIBUTING.md` note landed, and the upstream gemini decision filed as
      `.trellis/tasks/08-25-relay-gemini-retirement-sd-pack`

## References

Research notes that lived beside this item's Trellis record and were not carried
into docs/work. Recover the bodies from git history under `.trellis/tasks/archive/2026-08/08-23-review-gemini-codex-retirement`:

- research/inventory-2026-08-26.md
- research/planning-review-2026-08-26.md
