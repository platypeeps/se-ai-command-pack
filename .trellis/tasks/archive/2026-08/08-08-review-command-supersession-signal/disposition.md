# Disposition: supersession signal for superseded review commands

Recorded 2026-08-09. Route: **upstream proposal** (filed; URL below). This
file is the single authoritative record for the disposition, the proposal
text, the filing state, and the issue URL, per this task's PRD.

## The supersession claim

`.agents/skills/sd-review/SKILL.md:14-16` (vendored, sd-ai-command-pack
v0.64.32) states:

> This successor is self-contained. Never call, alias, or fall back to
> `sd-review-local`, `sd-review-pr`, a direct Copilot request, or a backend command
> found in configuration or a receipt.

## Surfaces where the superseded commands remain installed (v0.64.32)

Each command remains a first-class, unmarked peer at every command-palette
choice point. Verified 2026-08-09:

- `sd-review-local`: `.agents/skills/sd-review-local/SKILL.md`,
  `.claude/skills/sd-review-local/SKILL.md`, `.claude/commands/sd/review-local.md`,
  `.gemini/commands/sd/review-local.toml`, `.github/prompts/sd-review-local.prompt.md`,
  `.opencode/commands/sd-review-local.md`
- `sd-review-pr`: `.agents/skills/sd-review-pr/SKILL.md`,
  `.claude/skills/sd-review-pr/SKILL.md`, `.claude/commands/sd/review-pr.md`,
  `.gemini/commands/sd/review-pr.toml`, `.github/prompts/sd-review-pr.prompt.md`,
  `.opencode/commands/sd-review-pr.md`

Neither skill's frontmatter `description` — the text an agent or user sees
when choosing a command — mentions supersession. The only supersession notice
lives in the `sd-help` catalog
(`.claude/skills/sd-help/references/command-catalog.md`, rows 40 and 54:
"included in installed pack — transitional until 0.62.0; use sd-review"),
which reaches only users who invoke `/sd:help`.

## The expired transition promise

The catalog says "transitional until 0.62.0". The installed pack is 0.64.32.
The commands outlived their stated removal horizon by more than thirty
releases, and the 2026-08-09 refresh (v0.64.3 → v0.64.32) changed none of the
supersession signals. The promise is therefore stale on every installed copy.
This disposition reconciles it by proposing upstream that the transition
either complete (remove the commands) or be re-stated honestly at the choice
point (frontmatter notice plus a corrected or removed version horizon).
Accepting the expired promise as-is was rejected: a notice visible only in
`/sd:help` cannot govern a choice made in the command palette.

## Adjacent choice-point ambiguities (documented, not decided here)

Status of each: **deferred** — listed in the upstream proposal as observed
context, not included in its requested change.

1. `sd-full-check` / `sd-check`: the catalog (row 43) marks `sd-full-check`
   "transitional until 0.62.0; use sd-check", but `sd-full-check`'s own skill
   and adapter files never name `sd-check`. Succession per the catalog only;
   `sd-check` itself treats `sd-full-check` as an independent legacy surface
   it refuses to invoke.
2. `sd-create-pr` / `sd-ship`: `sd-create-pr` is a strict name prefix of the
   `sd-ship` lifecycle; no cross-reference at the choice point.
3. `sd-finish-work` / `sd-housekeeping`: both are named as "end of work"
   surfaces while one invokes the other; no disambiguation at the choice
   point.

## Upstream proposal (filed)

Proposal to sd-ai-command-pack: make the superseded review commands
self-describing at every choice point, or complete their removal. Exact
surfaces named in the issue: the frontmatter `description` of
`sd-review-local/SKILL.md` and `sd-review-pr/SKILL.md` (both `.agents` and
platform-mirrored copies), the four per-platform command adapters for each
command, and the `sd-help` catalog rows whose "transitional until 0.62.0"
horizon has expired.

- Filed: **platypeeps/sd-ai-command-pack#399**
  (https://github.com/platypeeps/sd-ai-command-pack/issues/399), 2026-08-09.

## Routing note

`08-07-vendored-artifact-upstream-route` has not yet landed its contract.
This task moved first and followed the existing relay precedent (issues #397
and #398, recorded in that task's relay log). Routing decision made here, for
the contract task to cite: vendored-payload defect → upstream GitHub issue on
platypeeps/sd-ai-command-pack, URL recorded in the originating task's
artifacts, brief relay entry appended to the 08-07 relay log. No local edits
to any provenance-tracked file.
