# Design — se-propose-skills (packaged)

## Shape

A pack skill authored in this repo and installed into consumers. Deliverable is
**not** a single loose file anymore; it is:

1. `templates/skills/se-propose-skills/SKILL.md` — the canonical, framework-neutral
   skill (name+description frontmatter, five required sections).
2. `installer/registry.py` — one `SkillInfo` row + one runtime-profile assignment.
3. Regenerated committed artifacts from `make generate`: `manifest.json` (3 rows:
   agents/claude/codex), `generated/skills/claude/se-propose-skills/SKILL.md`
   (Claude overlay the generator synthesizes from the runtime profile), and the
   README catalog block.
4. `manifest.json` version bump + a dated `CHANGELOG.md` heading (release gate).

The Trellis task remains in-repo bookkeeping AND now owns real in-repo code — the
skill source and registry edit are committed to this repo.

## Why prompted, not scripted (D2)

The review — "what did this session teach that a mechanical skill would help" — is
irreducibly model judgement. A `scripts/*.py` could only manipulate text it cannot
evaluate. So SKILL.md carries the rubric and the note template; the model applies
them to its own context. `scripts/` is permitted by the pack but unnecessary here.

## The configurable target (D1) — resolution order

The skill resolves its write destination in this order, per invocation:

1. `profile=off` → **inline-only**. Never writes. Emits proposals in the report.
2. explicit `target=<path>` → write under `<path>/System/Databases/Skill Proposals/`.
3. `profile=auto` (default) → attempt to resolve a **private host-configured
   locator** (a path the user configures on their machine, kept OUT of the public
   pack files — e.g. a note the user places, an already-present vault path the
   skill is told about via the same private-locator convention `se-ask-me` /
   `se-paper` use). If it resolves, write there.
4. Nothing resolves → **do not write.** Emit the proposals inline and state
   exactly how to set `target=` or configure the locator.

This is the pack's established `profile=auto|off|<locator>` idiom
(`templates/skills/se-ask-me`, `se-paper`) and honors "locator details stay
private and outside the public installer" (`_shared/references/
personal-profile-contract.md`). No private path ships in the repo.

## Boundaries

- **In:** author SKILL.md to contract; register in registry.py; regenerate;
  version/changelog bump; the review rubric; the note template; target resolution;
  dedup; report.
- **Out:** no external ledger (D4/D6), no auto-file (D6), no `.base` edits, no new
  env/config mechanism (D1), no private path in-repo (D1), never a status other
  than `proposed`.

## Data flow

```
session context (in model)
  -> rubric scan (R4) -> candidates
  -> strict filter (D3) -> qualifying (may be empty)
  -> resolve destination (D1: off | target= | auto-locator | none)
  -> dedup <skill-name> vs (a) dest Skill Proposals notes, any status,
                          and (b) installed skill names (R5)
  -> render each note from canon template (D4/D5), status=proposed
  -> write to <dest>/System/Databases/Skill Proposals/<skill-name>.md  (only if a dest resolved)
  -> report written + skipped + inline-fallback (R7)
```

## Contract A: the pack SKILL.md (what we author)

Frontmatter — exactly two keys:
```yaml
---
name: se-propose-skills
description: Use when the user wants the current session reviewed for recurring friction, repeated steps, and hard-won gotchas, and high-bar skill proposals drafted into a configurable Obsidian Skill Proposals destination for later accept or decline.
---
```
`description` starts with `Use when`, single line, **no double quotes** (validator
line 210), ≤1024 chars, name == dir name. (The draft deliberately omits quotes
around "Skill Proposals".)

Body sections, in required order:
- `## When to use` — session-end harvest; when a pattern recurred; explicit triggers.
- `## Arguments` — `target=<path>`, `profile=auto|off|<locator>`, and the
  destination-neutral default (D1).
- `## Workflow` — review → strict-bar filter → resolve destination → dedup →
  render note(s) from the embedded template → write only `proposed` → report.
- `## Safety rules` — always `proposed`; no implicit write without a resolved
  target; never overwrite; no sensitive dumps; the note is the record.
- `## Final report` — written (paths), skipped (reasons), inline fallback / "zero".

No banned brand names anywhere in the body. `BANNED_PHRASE_PATTERN` (generator
line 94) is **case-sensitive** and bans `Claude|Cowork|Codex|Copilot|Gemini|
ChatGPT|OpenAI|Anthropic|Amp`. Consequences:
- Body prose refers to "the current session" / "the assistant" — never a
  capitalized product name.
- The embedded emitted-note template keeps `tags: - claude` (lowercase) — this
  does NOT match the case-sensitive pattern, so it is safe and stays consistent
  with existing vault notes. Do not capitalize it.

## Contract B: the emitted proposal note (unchanged canon, D4/D5)

```markdown
---
contexts:
  - <session repo/project slug>
area: Software Engineering
category:
  - Knowledge Management
content-type: skill-proposal
status: proposed
dateCreated: <YYYY-MM-DD today, unquoted>
description: <skill-name>
tags:
  - ai-generated
  - claude
  - se-propose-skills
skill-name: <skill-name>
---

# <skill-name>

**Status:** `INPUT[inlineSelect(option(proposed), option(accepted), option(declined), option(filed)):status]`

**What it would do.** <mechanical behavior; the one honest hard rule>

**Evidence.** <≥2 concrete instances from THIS session; pattern, not raw output>

**Why a skill and not a note.** <mechanical core vs one-time judgement>

**Cost of getting it wrong.** <over- vs under-reporting; the silent-failure case>

---

*This is a native note in this vault — the note itself is the record; there is no external ledger. Use the dropdown above rather than the frontmatter field — an off-vocabulary value is reported, not guessed at, so a typo reads as silence. Pick `accepted` to have `skill-proposal-accept` file it as a Trellis task in `se-ai-command-pack`, or `declined` to close it. `filed` is set by the routine, not by you.*
```
The `INPUT[inlineSelect(...)]` line is copied verbatim (Meta Bind control). The
note's `tags` include `se-propose-skills` as provenance; the note-body `# <name>`
is the PROPOSED skill's name, not `se-propose-skills`.

## Registry edit (Contract C)

- `installer/registry.py`: add `SkillInfo(name="se-propose-skills", family="improve")`
  to `SKILLS`. Verified: `improve` is a valid `FAMILY_LABELS` key and `se-retro`
  already uses `family="improve"` (registry line 134) — exact peer.
- Add `se-propose-skills` to the **same** `RUNTIME_PROFILE_ASSIGNMENTS` group that
  contains `se-retro` (registry line ~193). Mandatory or `validate_registry`
  raises. Confirm the group name by reading that block at implementation time.
- No `SHARED_REFERENCES` entry (the note template is embedded, not a shared ref).

## Key tradeoffs

- **Destination-neutral default (D1).** Safer than a hardcoded path and matches
  pack norms, at the cost of one extra step (pass `target=` or configure a
  locator) before the first write. Mitigated by a clear inline fallback message.
- **Registry + generate + gate overhead.** Real, but mandatory — skipping any of
  it fails CI (drift gate, release-payload gate, validate_registry).
- **Writing skill in a read-only-leaning pack.** Reconciled by making every write
  explicit and user-directed (no implicit external write), consistent with
  `se-capture`'s destination-neutral stance.

## Limitations

- **Context compaction.** Reviews from live context; a compacted session yields
  fewer citable instances. "Zero proposals" stays valid.
- **Sensitive evidence.** Evidence describes the pattern, never pastes raw output,
  secrets, or file contents into a note.
- **Locator privacy.** The auto-locator's path is host-local and never committed;
  a fresh consumer with no locator gets inline-only until they set `target=`.

## Rollback

Revert the `installer/registry.py` row + regenerated artifacts + manifest/CHANGELOG
bump (one commit), and delete `templates/skills/se-propose-skills/`. Notes already
written to a destination are independent files, individually removable.
