# Introduce the Vale prose gate

Parent: [`../08-26-adopt-claude-skills/`](../08-26-adopt-claude-skills/) — R3; parent AC3.

## Goal

Make prose quality deterministic for a product whose deliverable *is* prose:
a repo-local Vale configuration with committed `se-` styles, run over
`templates/skills/` and the top-level docs — advisory first, promoted into
`make check` and CI once tuned.

## Context

- Vale 3.18.0 is installed locally (verified 2026-08-26); no `~/.vale.ini`
  exists, so a repo-local config defines everything.
- Upstream's `prose-lint` skill assumed the author's personal ai-tells styles
  from dotfiles; those never shipped. This task builds the styles the pack
  actually owns.
- The re-authored `se-prose-lint` skill (sibling task) drives this gate;
  the gate must exist for that skill to be truthful, but the skill degrades
  gracefully where Vale is absent — the gate is repo-CI-side, the skill is
  fleet-side.

## Requirements

- R1. Repo-local `.vale.ini` plus committed styles under `styles/` (or the
  Vale-conventional path chosen in design), scoped to `templates/skills/**`
  and top-level `*.md` docs. Vendored platform dirs, `.trellis/`, and
  generated surfaces are excluded.
- R2. Initial style set is modest and tunable: ai-tell patterns (hedging,
  filler, "delve"-class vocabulary), banned weasel words, and any rules that
  encode this pack's documented prose conventions. RFC-2119 keywords get a
  suppress-with-justification carve-out (they are intentional in skill
  contract language).
- R3. `make prose-lint` runs Vale with the repo config; failure is advisory
  (target exists, is documented, but is not in `make check`) until tuning
  completes.
- R4. Promotion: once the alert rate on the existing corpus is signal — a
  tuning pass over current `templates/skills/` resolving every finding as
  fix-or-suppress — add `prose-lint` to `make check` and the CI workflow.
  Promotion may land in this task or as a recorded follow-up if tuning shows
  the corpus needs staged cleanup.
- R5. CI must not require a network install surprise: pin the Vale version
  expectation and fail with a clear message when the binary is absent.

## Non-goals

- Commit-message linting (maybe never — not in scope).
- Prose style enforcement on code comments or vendored content.

## Acceptance Criteria

- [ ] AC1. `.vale.ini` and committed styles exist; `vale ls-config` resolves
      them from the repo root.
- [ ] AC2. `make prose-lint` runs the scoped lint and exits nonzero on a
      seeded violation in a scratch file (falsification check), zero after
      removal.
- [ ] AC3. The tuning pass is recorded: every finding on the current corpus
      fixed or suppressed with justification, alert count at promotion time
      noted in the task.
- [ ] AC4. Either `prose-lint` is in `make check` + CI, or the promotion
      follow-up is recorded with the blocking finding count.

Medium task: PRD plus `design.md` (style inventory, scoping, promotion
criteria); `implement.md` only if design shows staged rollout.
