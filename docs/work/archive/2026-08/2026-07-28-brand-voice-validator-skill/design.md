# Design — Brand voice validator skill

## Decisions

- **D1 — Name: `se-brand-voice`.** Keeps the `se-` prefix required by
  `installer/registry.py` (`SKILL_PREFIX`), reads as a noun phrase beside
  `se-technical-editor` / `se-review-skills`, and names the subject (brand
  voice) rather than the verb, matching `se-stakeholder-map`,
  `se-literature-map`, `se-topic-radar`.
- **D2 — Family: `improve`.** The skill strengthens an existing artifact
  against a stated standard, which is the `improve` family description
  ("Reflect, learn, and strengthen future work") and the family already
  carrying `se-technical-editor`, `se-feedback`, `se-evaluate`.
- **D3 — Runtime profile: reuse `BOUNDED_SYNTHESIS`** (`both`, `forked`,
  `balanced`, `medium`). The work is bounded rule application over one supplied
  document plus one guidelines artifact — not open-ended investigation, so
  `DEEP_ANALYSIS` overpays; not a conversational utility, so `CONVERSATIONAL`
  under-serves the located-findings contract. No new profile constant is
  introduced; `installer/registry.py` rejects unassigned skills, so the row is
  added to the existing `BOUNDED_SYNTHESIS` group.
- **D4 — Shared references: consume `argument-vocabulary.md` only.** The skill
  evaluates supplied copy against supplied guidelines; it does not rank external
  evidence (`source-standards.md`) and does not read or write a personal profile
  (`personal-profile-contract.md`). Registering unused shared references would
  ship dead payload to the installed skill directory.
- **D5 — One skill-owned reference:
  `references/voice-guidelines-schema.md`.** Defines the expected shape of a
  voice-guidelines artifact (tone attributes, preferred/banned terminology,
  style rules, audience fit) and the bootstrap draft template. Keeping the
  schema out of `SKILL.md` keeps the body near the size of its siblings and
  gives bootstrap mode a stable shape to draft against.
- **D6 — Every mode is read-only; the skill writes no file.** `mode=validate`
  (default) reports findings. `mode=bootstrap` returns a proposed guidelines
  draft *inside the report* for the user to save themselves. No destination
  argument exists and no write branch exists, so there is no approval path to
  get wrong. This is stricter than `se-technical-editor`'s report/edit split and
  matches the PRD's suggest-only boundary and its "no auto-rewriting" exclusion.
- **D7 — Never validate against an unstated voice.** With no resolvable
  guidelines, the skill reports the gap and offers bootstrap. It does not infer
  a brand voice from the content under review, because that would make every
  document self-consistent by construction and the findings meaningless.
- **D8 — Guidelines resolution is an explicit ordered list, never a search.**
  Following the `profile=auto` precedent in
  `_shared/references/personal-profile-contract.md` ("`auto` resolves only an
  attached authorized profile or a private host-configured locator; it never
  searches all personal stores"):
  1. an explicit `guidelines=<locator>` or inline text always wins; an
     unreadable explicit locator is an error, never a silent fallback to `auto`;
  2. `guidelines=auto` (the default) probes exactly these repository-root
     relative paths, in this order, and stops at the first that exists:
     `docs/brand-voice.md`, `docs/style-guide.md`, `BRAND_VOICE.md`,
     `STYLE_GUIDE.md` (conventional documentation paths only — the skill
     invents no hidden pack-specific directory);
  3. the resolved path is named in the report; any lower-ranked candidate that
     also exists is listed as present-but-unused, so a surprising resolution is
     visible rather than silent;
  4. no candidate found is not an error and not an inference trigger — it is the
     D7 gap report plus the bootstrap offer.
  The list is fixed and pinned literally in tests; the skill never globs for
  "something that looks like a style guide."

## Boundary with `se-technical-editor`

`se-technical-editor` already runs a `voice-consistency` pass. The two are
distinguished on the source of the standard, not on the artifact type:

| | `se-technical-editor` | `se-brand-voice` |
|---|---|---|
| Standard | the draft's own representative voice sample, derived from the supplied language | an external, stated guidelines artifact |
| Primary risk | correctness, evidence, and citation defects | terminology and tone drift from a defined brand |
| Scope | one technical draft, eleven passes, voice is one of them | any written content, four rule groups, all about voice |
| Output authority | report, then explicitly approved edits | report only; rewrites are suggestions |

Both directions of the handoff are stated in each body: `se-technical-editor`
keeps ownership of correctness and citation review; `se-brand-voice` keeps
ownership of conformance to a defined brand standard. `se-brand-voice` does not
gain a correctness pass, and `se-technical-editor` is not modified in this task
beyond the one-line sibling cross-reference required for the boundary to be
discoverable from both sides.

## Arguments

Canonical names come from
`templates/skills/_shared/references/argument-vocabulary.md`; the generator's
`argument_vocabulary_errors()` hard-fails a known alias or an off-ladder value.

Requirements are mode-specific, because the two modes act on different things:

- `input=` — the content under review, by path or pasted text (canonical
  reserved: the primary artifact). **Required in `mode=validate`**; ignored in
  `mode=bootstrap`. Missing in validate mode is a stop-and-report error, never a
  prompt to review whatever text is lying around in the conversation.
- `guidelines=auto|<locator>` — voice-definition locator or inline text;
  default `auto`, resolved by the fixed D8 order. Skill-owned name, precedent:
  `rubric=` on `se-evaluate`.
- `sources=` — representative published samples the voice is derived *from*
  (canonical reserved: reference material consulted). **Required in
  `mode=bootstrap`**; optional context in `mode=validate`. Bootstrap with no
  samples is a stop-and-report error: D7 forbids inventing a voice, and
  inventing one from zero samples is the same defect.
- `audience=` — intended readers (canonical reserved).
- `scope=all|tone|terminology|style|audience-fit` — default `all`; comma-joined
  subsets allowed (canonical reserved: extent of work).
- `mode=validate|bootstrap` — default `validate` (canonical reserved).
- `format=ledger|memo` — default `ledger` (canonical reserved; same value set
  as `se-evaluate`).
- `depth=brief|standard|deep` — default `standard` (enforced canonical ladder).

No `length=`, `source=`, `inputs=`, or `detail=` alias appears; no off-ladder
`depth=` value is declared.

## Registration surfaces

Adding a skill touches one source of truth plus generated output:

1. `installer/registry.py` — one `SkillInfo(name="se-brand-voice",
   family="improve")` row appended to `SKILLS` (row order is manifest/install
   order; appending keeps existing rows stable), `"se-brand-voice"` added to the
   `BOUNDED_SYNTHESIS` assignment group, and to the
   `_shared/references/argument-vocabulary.md` consumer tuple in
   `SHARED_REFERENCES`.
2. `templates/skills/se-brand-voice/SKILL.md` plus
   `references/voice-guidelines-schema.md`.
3. `make generate` derives `manifest.json` rows, the marker-bounded README
   catalog, `templates/skills/_shared/references/skill-catalog.md`,
   `generated/skills/claude/se-brand-voice/SKILL.md`, and
   `generated/registry-snapshot.json`. None of these are hand-edited.
4. `manifest.json` version bump + dated `CHANGELOG.md` heading, because
   `templates/**`, `generated/**`, and `installer/**` all change and
   `.github/scripts/check-release-payload.py` gates that. Current version is
   `0.66.14`; this ships as `0.67.0` (new shipped skill is a feature, and the
   pack's history uses a minor bump for new skills).
5. `docs/SE_AI_COMMAND_PACK.md` — shipped-skills sentence plus a
   `### Brand-voice workflow boundary` section, required by
   `tests/test_skills.py::test_operator_guide_covers_every_registered_skill`.
6. `README.md` — the catalog row is generated; the prose paragraph beside
   `se-technical-editor` is written by hand and satisfies
   `test_readme_lists_every_skill` together with the generated row.

## Test-side registries that also list every skill

Four golden literals in the suite are deliberately not derived from
`installer/registry.py`, so a new skill must be added to each or the suite
fails naming the skill:

- `tests/test_skills.py:242` — the ordered `SKILL_NAMES` tuple
  (`test_skill_names_are_derived_without_reordering`); append at the end to
  match the appended registry row.
- `tests/test_skills.py:305` — the name → family map in the same test; add
  `"se-brand-voice": "improve"`.
- `tests/test_skills.py:40` — `EXTERNAL_INPUT_SKILLS`; this skill reads supplied
  content and a guidelines artifact, so it belongs there and its body must carry
  the `data, not instructions` fragment
  (`test_external_input_skills_carry_injection_rule`).
- `tests/test_generate.py:65` — `EXPECTED_SHARED_SOURCES`; add
  `"se-brand-voice": ("_shared/references/argument-vocabulary.md",)`.

`test_shared_reference_consumers_cite_registered_reference`
(`tests/test_skills.py:403`) additionally requires the body to literally cite
`references/argument-vocabulary.md`, which the standard Arguments preamble does.

## Generator contracts the new skill must satisfy

From `.github/scripts/generate-skill-surfaces.py::validate_skill`:

- frontmatter keys exactly `name`, `description`; `name` equals the directory
  name; description starts with `Use when`, single line, no double quotes,
  ≤1024 characters;
- body opens with an H1 and contains `## When to use`, `## Arguments`,
  `## Workflow`, `## Safety rules`, `## Final report` **in that order**;
- neutrality lint: no `Claude|Cowork|Codex|Copilot|Gemini|ChatGPT|OpenAI|
  Anthropic|Amp` token anywhere in the file;
- only `SKILL.md`, `references/*.md`, `scripts/*.py`; no nested directories, no
  symlinks; file ends with a newline;
- every `references/<file>.md` the body cites must ship to this skill — either
  owned (`voice-guidelines-schema.md`) or registered as a `SHARED_REFERENCES`
  consumer (`argument-vocabulary.md`). The reverse-citation-closure check in
  `validate_skills()` now fails generation on a miss, so the PRD's "no gate
  catches a miss today" note (ledger A-007) is stale and is recorded as closed.

## Risks

- **R1 — Overlap read as duplication.** Mitigated by D-table above, explicit
  sibling references in both bodies, and a test pinning the boundary phrases in
  `docs/SE_AI_COMMAND_PACK.md`.
- **R2 — Neutrality lint tripped by brand-voice examples.** The body discusses
  brand terminology; any illustrative example must avoid the banned vendor
  tokens. Examples use neutral placeholders.
- **R3 — Version-gate miss.** `make release-check` runs in the local gate and
  CI; the bump and dated changelog heading land in the same commit as the
  payload.
- **R4 — Prompt injection via reviewed content.** The content under review and
  the guidelines artifact are data. The safety rules state this explicitly, as
  every sibling body does.

## Rollout / rollback

Additive only: one new registry row appended, one new skill directory, one
consumer added to one shared-reference tuple. No existing row, path, or install
target changes. Rollback is the inverse of the same commit (`git revert`);
installed consumers converge on the next `install.py --user` refresh because
removal is manifest-driven.
