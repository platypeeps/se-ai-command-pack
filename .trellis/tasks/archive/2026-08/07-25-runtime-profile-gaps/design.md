# Fix fresh-session encoding and document runtime profiles — Design

## Overview

The RuntimeProfile layer (`installer/registry.py`) carries a portable
`context` axis with three values: `inline | forked | fresh-session`. The Claude
overlay renderer (`.github/scripts/generate-skill-surfaces.py`,
`claude_frontmatter`) translates `forked -> context: fork` but emits **nothing**
for `fresh-session`, so the only fresh-session skill (`se-red-team`, profile
`INDEPENDENT_RED_TEAM`) silently collapses to the host default. Its generated
overlay (`generated/skills/claude/se-red-team/SKILL.md`) has no marker of the
independent-run intent, and `tests/test_generate.py:330` currently asserts that
absence (`assertNotIn("context", ...)`), pinning the gap as if intended.

Two gaps, one PR: (R1) give `fresh-session` an explicit, honest encoding in the
generated Claude output; (R2) document the RuntimeProfile/overlay system in the
operator guide. R3: no behavior change for any skill other than se-red-team's
isolation expression.

## Proposal

### R1 — fresh-session encoding: in-body generated note

Claude skill frontmatter has no field for "independent run without inherited
conclusions." `CLAUDE_FRONTMATTER_KEYS` is exactly
`name, description, disable-model-invocation, user-invocable, context, model,
effort` and `claude_frontmatter` hard-rejects any other key (line 463-467). The
one isolation primitive, `context: fork`, is not fresh-session. Per the repo
contract (`templates/skills/se-review-skills/references/runtime-routing.md:26`):
`forked` = "a host-managed isolated subagent that returns to the caller";
`fresh-session` = "an independent run without inherited conclusions"; the two
"are not interchangeable." Mapping `fresh-session -> fork` would therefore
misrepresent intent — it advertises a bounded returning subagent where the
profile asks for an independent session — so `fork` is the wrong encoding.

Chosen encoding: when `profile.context == "fresh-session"`, `render_claude_skill`
appends a clearly-marked generated note to the **overlay body only** (canonical
`SKILL.md` body is untouched), stating the intent so it travels with the skill
wherever the profile applies. Frontmatter stays as today (no `context` key —
correct, because `fork` would be wrong).

Note text (single generated block, appended after the canonical body):

```
<!-- generated: runtime-profile fresh-session -->
> Runtime profile: **fresh-session**. Run this skill as an independent session —
> do not inherit conclusions, scratchpad state, or prior framing from the calling
> context. Start from the artifact and its evidence alone.
```

Rejected alternatives:
- `context: fork` frontmatter — wrong semantics (a returning isolated subagent,
  not an independent session; the two are "not interchangeable" per
  runtime-routing.md:26), and changes observable isolation for se-red-team
  (`contextIsolation` would flip to `forked`; violates the honesty of R1).
- New frontmatter field (e.g. `session: fresh`) — rejected by the
  `CLAUDE_FRONTMATTER_KEYS` guard; not a real Claude skill key.
- Doc-note-only (list fresh-session skills in the guide) — fails R1's "wherever
  the profile applies": the intent would not travel with the generated skill.

### R2 — documentation

In `docs/SE_AI_COMMAND_PACK.md`:
- add `generated/` to the layout table;
- explain the portable `context` vocabulary (`inline | forked | fresh-session`)
  and the Claude-only overlay translation (`forked -> context: fork`;
  `fresh-session -> in-body note`; `inline -> host default`);
- add runtime-profile steps to the "Adding a skill" and "Adding a platform"
  maintainer checklists.

## Boundaries And Non-Goals

- Only se-red-team's generated overlay gains the note (it is the sole
  fresh-session skill). All other overlays are byte-identical after this change.
- No change to canonical `SKILL.md` bodies (neutrality lint unaffected, R4).
- No change to Codex/other renderers — fresh-session encoding for non-Claude
  hosts is out of scope (no host currently maps it; documented as such).
- No change to the `context: fork` path or any model/effort/invocation mapping.

## Affected Files

- `.github/scripts/generate-skill-surfaces.py` — `render_claude_skill` (append
  generated note when `profile.context == "fresh-session"`).
- `generated/skills/claude/se-red-team/SKILL.md` — regenerated (body gains note).
- `docs/SE_AI_COMMAND_PACK.md` — layout row, runtime-profile section, two
  checklists.
- `tests/test_generate.py` — se-red-team case: keep `assertNotIn("context")`,
  add assertion that the generated body contains the fresh-session note marker;
  assert no other overlay body carries the marker.
- `tests/test_skill_review.py` — add a fresh-session fixture pinning that
  se-red-team's `contextIsolation` stays `inline-or-host-default` (the body note
  is advisory, NOT misreported as host-enforced fork/fresh isolation). The
  analyzer keys `contextIsolation` off frontmatter `context == "fork"` only
  (skill_review.py:1363), so the note must not flip it. This closes the PRD's
  named contextIsolation acceptance item.
- `CHANGELOG.md` + version bump per repo release rules.

## Data And Command Contracts

- No new config surface, no manifest/registry schema change. `context` axis
  values unchanged.
- Generator `--check` drift gate must pass with the regenerated overlay
  committed. Release-payload version gate requires the version bump + dated
  changelog entry.

## Risks And Edge Cases

- Drift gate: forgetting to commit the regenerated se-red-team overlay fails
  `--check`. Prevention: regenerate and commit in the same step.
- Version-ordering drift: the generated help/skill catalog embeds the manifest
  version (`rendered_help_catalog(metadata, version)`, generate-skill-surfaces.py
  :1055) and `--check` rejects a stale catalog (:1244). The manifest version bump
  MUST precede the final `make generate`, or the committed catalog carries the
  old version and the drift gate fails. Prevention: bump first, regenerate last,
  commit the regenerated catalog + overlay together.
- Over-broad note: appending to the wrong skills. Prevention: gate strictly on
  `profile.context == "fresh-session"`; test asserts exactly one overlay carries
  the marker.
- Body-mutation invariant: renderer docstring says "without changing its body."
  This change makes the generated body = canonical body + generated note for
  fresh-session only. Update the docstring to state the one deliberate exception
  so the invariant stays truthful.
- Idempotency: regeneration is deterministic; the marker comment lets `--check`
  compare stable output.

## Validation

- `make check` (= `test lint release-check`; `release-check` runs generator
  `--check` drift + `check-release-payload.py`) passes.
- Focused: `make test` (repo uses `unittest`, not pytest — no pytest in
  requirements-dev.txt), or targeted
  `<RUN_PYTHON> -m unittest tests.test_generate tests.test_skill_review`.
- Manual: regenerated `generated/skills/claude/se-red-team/SKILL.md` contains the
  note; the set of overlays carrying the marker equals exactly `{se-red-team}`;
  a non-fresh-session overlay (e.g. se-research) is byte-identical to its
  pre-change committed form.
