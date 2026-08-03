# Session-review skill that proposes new skills — packaged & installable

## Goal

Ship a **pack skill** (authored in this repo, installed into consumers) that
reviews the current session for recurring friction, repeated manual steps, and
hard-won gotchas, and drafts high-bar **skill proposals** into a
**user-configurable destination** — by default the same Obsidian "Skill
Proposals" collection, with the same approval/decline dropdown. The skill does
the judgement and drafting; the user decides via the dropdown; nothing is
auto-filed by this skill.

## Skill identity

- **Name:** `se-propose-skills` (the pack mandates the `se-` prefix;
  `propose-skills-from-session` is rejected by two gates).
- **Home:** `templates/skills/se-propose-skills/SKILL.md` in this repo; installed
  by `install.py` into the anchor-gated targets `~/.config/agents/skills/`,
  `~/.claude/skills/`, `~/.codex/skills/`.

## Confirmed facts (from inspection)

### The proposal notes (the skill's output artifact)
- One Markdown note per skill under the destination's
  `System/Databases/Skill Proposals/<skill-name>.md`; an Obsidian **Bases** view
  filters by `status` (proposed / accepted / filed / declined).
- The approval/decline control is an Obsidian **Meta Bind** inline select bound
  to `status`:
  `` `INPUT[inlineSelect(option(proposed), option(accepted), option(declined), option(filed)):status]` ``
- Migrated canon (2026-08-03): frontmatter carries `contexts`, `area`, `category`,
  `content-type: skill-proposal`, `status`, `dateCreated`, `description`, `tags`,
  `skill-name` — **no** `ledger`/`ledger-key`. Body: `# <name>` → `**Status:**
  <dropdown>` → four bold sections (**What it would do.** / **Evidence.** /
  **Why a skill and not a note.** / **Cost of getting it wrong.**) → `---` → the
  canon footer naming the `skill-proposal-accept` routine.

### The pack authoring contract (constrains the SKILL.md we write)
- Canonical `templates/skills/*/SKILL.md` frontmatter allows **only** `name` and
  `description`; `description` must start with `"Use when"`, single line, no
  double-quotes, ≤1024 chars; `name` must equal the directory name.
- Body must open with an H1 and contain, in order: `## When to use`,
  `## Arguments`, `## Workflow`, `## Safety rules`, `## Final report`.
- Brand/product names (the assistant's name, etc.) are **banned** in the body.
- Only `SKILL.md`, `references/*.md`, `scripts/*.py` may exist in the skill dir.
- Registration is **Python-registry driven**: add a `SkillInfo` row to
  `installer/registry.py` `SKILLS` and a `RUNTIME_PROFILE_ASSIGNMENTS` entry
  (mandatory), then `make generate` regenerates `manifest.json`, the Claude
  overlay `generated/skills/claude/<name>/SKILL.md`, and the README catalog.
- Release-payload gate: any change under `templates/**`, `generated/**`, or
  `manifest.json` requires a `manifest.json` version bump **and** a dated
  `## <version> - YYYY-MM-DD` CHANGELOG heading.
- **No env-var / config-file mechanism exists** (`ENV_PREFIX` is declared but
  never read). The only convention for a user-set value is a per-invocation
  argument; for a destination specifically, the `profile=auto|off|<locator>`
  idiom, where a **private host-configured locator** resolves the path and is
  kept out of the public pack files. SE skills are destination-neutral and forbid
  implicit external writes.

## Decisions

- **D1 — Configurable target via argument + private locator.** `target=<path>`
  sets the destination for one run. `profile=auto` resolves a private
  host-configured locator (e.g. the user's vault), kept **out** of the public
  pack files. `profile=off` forces inline-only. With neither a `target` nor a
  resolvable locator, the skill does **not** write — it prints the proposals
  inline and states how to configure a target. No hardcoded private path ships.
- **D2 — Prompted skill, not a script.** SKILL.md carries the rubric + the note
  template; the model produces proposals from its own session context. (A
  `scripts/*.py` helper is allowed but not required.)
- **D3 — Strict evidence bar.** A candidate qualifies only with ≥2 real instances
  (or a clearly recurring pattern), a mechanical core, and a real cost of getting
  it wrong. Judgement-only / one-off ideas are rejected. **Zero proposals is a
  valid, expected outcome.**
- **D4 — Output note = migrated canon.** Notes drop `ledger`/`ledger-key`, use
  the Meta Bind dropdown, the four bold sections, and the canon footer. `status`
  is **always** written as `proposed`.
- **D5 — Taxonomy.** `area: Software Engineering`, `category: [Knowledge
  Management]`, `contexts: [<session repo/project slug>]`.
- **D6 — Filing is not ours.** Accepted proposals are filed by the destination's
  own `skill-proposal-accept` routine (or by the user), never by this skill.
- **D7 — Supersede the prototype.** The interim personal skill
  `~/.claude/skills/propose-skills-from-session/` is removed; `se-propose-skills`
  replaces it.

## Requirements

- **R1** Author `templates/skills/se-propose-skills/SKILL.md` to the pack contract:
  `name`+`description` (`"Use when …"`) frontmatter; the five required sections in
  order; no banned brand names; H1 first.
- **R2** `## Arguments` documents `target=<path>`, `profile=auto|off|<locator>`,
  and the destination-neutral default (D1).
- **R3** `## Workflow` encodes: review the session (R-review), strict-bar filter
  (D3), dedup, resolve destination (D1), render each note from the canon template
  (D4/D5), write only `proposed`, report.
- **R4** Review the session for candidates — recurring friction, a step repeated
  across turns, a gotcha resolved the hard way, a pattern worth encoding once.
- **R5** Deduplicate `<skill-name>` before writing against (a) every note in the
  destination's Skill Proposals folder, any status, and (b) installed skill names
  under the platform skills dirs. Skip and report; never overwrite.
- **R6** `## Safety rules`: only ever write `status: proposed`; no implicit write
  without a resolved target; never overwrite; no sensitive session output copied
  into a note; the note is the record (no external ledger).
- **R7** `## Final report`: notes written (with paths), candidates skipped (with
  reason), and — when nothing cleared the bar or no target resolved — say so
  explicitly.
- **R8** Register the skill: `SkillInfo` row + runtime-profile assignment in
  `installer/registry.py`; run `make generate`; the drift/validation gates pass.
- **R9** Bump `manifest.json` version and add a dated CHANGELOG heading so the
  release-payload gate passes.

## Acceptance Criteria

- [ ] `templates/skills/se-propose-skills/SKILL.md` exists and passes
      `generate-skill-surfaces.py --check` (frontmatter, required sections order,
      no banned phrases, allowed files only).
- [ ] `installer/registry.py` lists `se-propose-skills` with a family and a
      runtime-profile assignment; `validate_registry()` passes at import.
- [ ] `make generate` produces `manifest.json` rows (agents/claude/codex) and the
      Claude overlay for the skill, with no drift (`--check` clean).
- [ ] `manifest.json` version bumped and a dated CHANGELOG heading present; the
      release-payload gate passes.
- [ ] `pytest` for the generator/skills/release-gate suites passes
      (`tests/test_generate.py`, `tests/test_skills.py`, `tests/test_release_gate.py`).
- [ ] With `target=<tmpdir>` the skill writes a canon note (dropdown verbatim,
      four sections, `status: proposed`, no ledger fields) into
      `<tmpdir>/System/Databases/Skill Proposals/`.
- [ ] With `profile=off` (or no resolvable target) the skill writes nothing and
      reports the proposals inline plus how to set a target.
- [ ] A candidate whose `skill-name` already exists (proposal note or installed
      skill) is skipped and reported, not overwritten.
- [ ] A session with no skill-worthy pattern produces zero notes and says so.

## Out of scope

- Writing any external ledger (the note is the record, D4).
- Auto-filing accepted proposals — the destination's `skill-proposal-accept`
  routine's job, not this skill's (D6).
- Editing the Bases `.base` view or its schema.
- Introducing an env-var/config-file mechanism to the pack (D1 uses arguments).
- Shipping any private vault path in the public pack (D1).

## Open questions (blocking)

None. Decisions D1–D7 resolved.
