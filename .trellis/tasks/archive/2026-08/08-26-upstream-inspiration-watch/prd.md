# Keep a lightweight upstream inspiration watch

Parent: [`../08-26-adopt-claude-skills/`](../08-26-adopt-claude-skills/) — R5; parent AC5.

## Goal

Record where the ideas came from and keep a cheap, reviewable ritual for
harvesting new upstream ideas — without any vendored files, digests, or drift
tooling (all dead with import mode).

## Deliverables

- D1. One new tracked file — `claude-skills.md` under a new `docs/inspiration/`
  directory (created by this task) — containing:
  - the pinned upstream identity: `Shearerbeard/claude-skills` @
    `0e4fb48ed69d665fd1307a51cb126af915c6502b`, plus the `opencode-cfg`
    local receipt `b37c6ec` (described as private/local; no remote URL,
    no hostnames — parent C4);
  - the inspiration map: one row per adopted surface — `se-*` name, upstream
    source skill/agent, and a one-line note on what was deliberately changed;
  - the non-adoption table copied from the parent PRD (upstream name +
    reason), so a future harvest does not re-litigate settled decisions;
  - the harvest ritual (D2).
- D2. Harvest ritual, documented in that file: on demand or roughly
  quarterly — fetch upstream, `git log --stat <pinned-sha>..origin/HEAD`,
  read new/changed skills, write a short harvest report (new ideas worth a
  task, changes affecting an `se-*` skill, nothing-of-note), then advance the
  pinned SHA in the same commit as the report. The ritual only ever produces
  Trellis tasks or nothing; it never edits `templates/` directly.

## Requirements

- R1. The upstream repo is inspiration, not a dependency: no submodule, no
  vendored copy, no CI job that fetches it.
- R2. The map covers all 13 skills, the agent trio, and the two folds
  (plan-discipline, python probes) from the sibling tasks.
- R3. Advancing the pin requires a harvest report in the same change.

## Acceptance Criteria

- [x] AC1. The inspiration file described in D1 exists with pin, map,
      non-adoption table, and ritual sections.
- [x] AC2. The map's `se-*` column matches the shipped roster exactly
      (checked by listing `templates/skills/se-*` and
      `templates/agents/se-rust-*` against the map rows).
- [x] AC3. No new CI job, Make target, script, or test references the
      upstream checkout; `grep -r 'claude-skills' Makefile .github/workflows/`
      stays clean of fetch/check steps.

Lightweight task: PRD-only. Runs after the authoring tasks so the map records
what actually shipped.
