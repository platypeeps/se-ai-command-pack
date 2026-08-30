# Design — Fix .claude dogfood tracking conflict (A-001)

## Decision (owner: user, 2026-08-04)

**Option A — track the sd-ai-command-pack Claude adapters, reaching parity with
the tracked `.gemini/commands/sd/*` twins.** Local-only third-party skills under
`.claude/skills/` (caveman, claude-mem, buildpartner, …) stay ignored.

## Problem (verified 2026-08-04)

`.gitignore:27` `.claude/` (a wholesale directory ignore emitted by the external
`trellis init` binary) hides the entire `.claude/` tree. The external
`sd-ai-command-pack` installer records **59** `.claude/*` sd-adapter targets in
`.sd-ai-command-pack/installed-targets.txt`, none of which a fresh clone can
carry because line 27 ignores them. The parity partner `.gemini/commands/sd/*`
(21 `.toml` files) *is* tracked, because the top block never emits a wholesale
`.gemini/` rule — only narrow `.gemini/**` local-state rules.

`scripts/sd-ai-command-pack-install-audit.py` (audit_expected_targets, ~:474-511)
downgrades a claimed-but-gitignored-and-absent target to a *warning* instead of a
failure, so the conflict persists silently on every fresh clone.

### Why neither generator can be fixed in-repo

Both rule sources are external tools, not vendored here (verified by grep across
`installer/`, `scripts/`, `.trellis/scripts/`, root `*.py` — zero hits for the
block strings):

- Line 27 `.claude/` is written by the external **`trellis init`** binary.
- The `# sd-ai-command-pack trellis-gitignore start … end` managed block
  (`.gitignore:55-197`) is written by the external **`sd-ai-command-pack`
  installer**; its `.claude/**` rules (`:92-98`) are already narrow and
  symmetric with `.gemini` — they are **not** the conflict.

The managed block is already correct. The sole conflict is line 27. A fully
oscillation-proof fix therefore requires an upstream change to `trellis init`
(make it treat `.claude` like `.gemini`: narrow rules, no wholesale ignore).
That upstream change is out of scope for this repo-local task and is captured as
a follow-up.

## In-repo fix

Replace the wholesale `.claude/` (line 27, in the Trellis-owned top block) with a
descend-and-allowlist block. Git will not descend into a directory ignored with a
trailing-slash wholesale rule, so re-includes must ignore *contents* (`.claude/*`)
and re-include each parent level down to the pack subtrees:

```gitignore
# Claude Code adapters: ignore .claude by default, but keep the
# sd-ai-command-pack dogfood surfaces tracked (parity with .gemini/commands/sd
# twins). Local-only third-party skills stay ignored. Ownership + the required
# upstream `trellis init` change are documented in CONTRIBUTING.md.
.claude/*
!.claude/commands/
.claude/commands/*
!.claude/commands/sd/
!.claude/rules/
.claude/rules/*
!.claude/rules/sd-*.md
!.claude/sd-ai-command-pack/
!.claude/skills/
.claude/skills/*
!.claude/skills/sd-*/
```

Then `git add` the resulting sd-adapter files.

### Scope boundaries

- **Tracked (new):** `.claude/commands/sd/**`, `.claude/skills/sd-*/**`,
  `.claude/rules/sd-*.md`, `.claude/sd-ai-command-pack/**` — the receipt-claimed
  set (~59 files).
- **Still ignored (unchanged):** `.claude/commands/trellis/**` (not sd-pack
  claimed), `.claude/skills/<non-sd>/**` (local third-party), `.claude/agents/`,
  `.claude/hooks/`, `.claude/settings.json`, `.claude/settings.local.json`, and
  all `.claude/**` local-state matched by the later managed-block narrow rules.
- `sd-*/` glob is used instead of enumerating 21 dir names: compact and
  auto-covers future sd-* adapters. `sd-*` is the pack namespace; no local
  third-party skill uses it.

### Ordering note

The managed-block narrow rules (`.claude/**/*.local.*`, `.claude/**/.cache/`,
`.claude/**/*.log`, …) sit *after* this block, so local state inside tracked
sd-* dirs stays ignored. Correct by construction; sd-* dirs contain no local
state today regardless.

## Ownership record (PRD requirement: record the ownership decision)

Add a short "`.claude/` tracking policy" note to `CONTRIBUTING.md`: the
sd-ai-command-pack Claude adapters are tracked for dogfood reproducibility
(parity with `.gemini`), local skills are not, and anyone re-running
`trellis init` must not re-assert a wholesale `.claude/` ignore (the durable fix
is the upstream `trellis init` change tracked as a follow-up).

## Acceptance mapping

- **AC1** `git check-ignore .claude/commands/sd/start.md` no longer matches
  (tracked). Verified with `git check-ignore` on samples + a local-only skill
  (which must still be ignored).
- **AC2** `scripts/sd-ai-command-pack-install-audit.py` reports no
  missing-target failures/warnings for the `.claude/*` targets (they are now
  present + tracked). Run the audit.
- **AC3** *Partially in-repo.* This repo's `install.py` never touches
  `.gitignore` (verified), so the sd-pack side is stable. The `trellis init`
  side is documented + a follow-up filed; it cannot be enforced against an
  external binary. Reported honestly as a limitation, not a silent pass.

## Risks

- Committing ~59 primary-platform files. Reviewed: they are pack-shipped
  adapters, parity with already-tracked `.gemini` twins. Low risk.
- Glob over-capture: `!.claude/skills/sd-*/` could in principle catch a local
  skill named `sd-*`. Verified none exists today; the install-audit + a
  `git status` diff review before commit is the check.
- Oscillation from `trellis init` re-adding line 27: unavoidable in-repo;
  documented + follow-up.
