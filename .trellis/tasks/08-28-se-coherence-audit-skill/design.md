# Design — se-coherence-audit

## Shape

One new authored skill directory plus registry wiring. No new code, no new
dependency, no generator change. The precedent is `se-brand-voice` (`47d1fb0`):
author under `templates/skills/`, add three registry lines, regenerate, document,
bump minor.

```
templates/skills/se-coherence-audit/
  SKILL.md
  references/
    detector-criteria.md      # the four classes: qualifies / near-miss / evidence required
    ledger-format.md          # finding schema, severity model, coverage block
    (argument-vocabulary.md)  # copied in by the generator, not authored here
```

## Frontmatter

Frontmatter carries exactly two keys, and the description is one physical
line beginning `Use when` (`generate-skill-surfaces.py:128,164`):

```yaml
name: se-coherence-audit
description: Use when a knowledge corpus — a note vault, agent-instruction files, or a docs tree — must be audited against itself for contradictions, vagueness, bandaid guidance, and redundancy, returning a read-only findings ledger with both sides quoted.
```

**Framework neutrality.** The generator's brand-name lint
(`generate-skill-surfaces.py:170`) rejects `Claude`, `Codex`, `Gemini`,
`Copilot`, and peers as words anywhere in the shipped text. The body therefore
names its targets by capability — "the root agent-instruction file",
"per-directory rule files", "a note vault" — never by product. Lowercase dotted
paths such as `.claude/rules/` remain allowed and are the one concrete form the
body may use.

Family `improve`; runtime profile `DEEP_ANALYSIS` (same tier as
`se-knowledge-gap`: cross-file reasoning over a whole corpus, not a bounded
single-artifact pass). Shared-reference consumer of
`_shared/references/argument-vocabulary.md` only — this skill verifies nothing
externally, so `verification-protocol.md` and `source-standards.md` do not apply.

## Arguments

Canonical names from the shared vocabulary wherever one exists.

- `input=` — corpus paths, globs, or a vault root. **Required.** Never inferred,
  never widened.
- `exclude=` — paths, globs, or file classes outside the audit boundary.
- `classes=` — comma list of detectors: `contradiction`, `vagueness`, `bandaid`,
  `redundancy`. Default all four; skill-owned name.
- `precedence=` — declared authority order over the corpus, most authoritative
  first (for example `CLAUDE.md,.claude/rules/,docs/`). Optional; when absent the
  skill looks for a precedence declaration inside the corpus and, failing that,
  treats missing precedence as reportable (R4).
- `depth=standard|brief|deep` — enforced ladder. `brief` reports blocking and
  high findings only; `deep` includes low-severity and near-miss observations.
- `min_severity=` — reporting floor, default `low`.
- `format=ledger|memo` — default `ledger`.

Unknown argument names are an error: stop and report before reading the corpus.

## Workflow (SKILL.md body)

1. **Resolve scope.** Expand `input=` minus `exclude=` into an explicit file
   list. State the count and the byte size. Stop if `input=` is absent or
   resolves to nothing. Do not read outside the resolved set.
2. **Resolve precedence.** Use `precedence=` if given; otherwise search the
   corpus for a declared ordering. Record which of the two happened, or record
   `precedence: undeclared` — that value is what makes step 5 report a missing
   precedence rather than a contradiction.
3. **Build the claim index.** Read each file and extract its *directives and
   assertions* — statements that tell a reader to do, prefer, forbid, or believe
   something — each with `path:line` and verbatim text. This index, not memory,
   is what later steps compare. Files too large to read in full are sampled and
   marked sampled.
4. **Run the detectors** in `references/detector-criteria.md`, each finding
   naming the criterion it satisfies. Compare index entries pairwise within and
   across files for contradiction and redundancy; scan individual entries for
   vagueness and bandaid.
5. **Classify each conflict** as `contradiction` (both sides live, no ordering
   resolves them), `resolved-by-precedence` (an ordering settles it — reported
   as an observation, not a defect), or `missing-precedence` (they conflict and
   nothing declares which wins).
6. **Score severity** by consequence (see below), then sort the ledger by
   severity, then by number of affected locations.
7. **Report** the coverage block first — files read in full, sampled, skipped
   with reason — then the ledger, then the proposed resolutions. A corpus that
   could not be audited in full is reported as partially audited with the
   remainder named.

## Finding schema (`references/ledger-format.md`)

| Field | Rule |
|---|---|
| `id` | `C-1`, `V-3`, `B-2`, `R-4` — class letter, stable within a report |
| `class` | contradiction \| vagueness \| bandaid \| redundancy |
| `severity` | blocking \| high \| medium \| low |
| `locations` | every `path:line`; contradiction and redundancy need ≥2 |
| `quotes` | verbatim text per location, never paraphrased |
| `criterion` | which named criterion from the detector reference it satisfies |
| `why` | what a reader acting on this would get wrong |
| `resolution` | the proposed fix, stated as a proposal — never applied |
| `confidence` | high \| medium; a low-confidence finding is not reported |

Severity is consequence-scored, not count-scored:

- **blocking** — a reader following the corpus would take a wrong, hard-to-undo
  action, or two passages demand opposite actions on the same trigger.
- **high** — load-bearing guidance that a competent reader will plausibly misread.
- **medium** — real defect, low blast radius or rarely-hit path.
- **low** — drift risk without a present-tense wrong outcome (a duplicate that
  currently agrees).

## Detector criteria (`references/detector-criteria.md`)

Each class states what **qualifies**, the **evidence required**, and at least one
**near-miss** that must not be reported:

- **Contradiction** — direct negation, incompatible thresholds or values,
  conflicting precedence or ordering, mutually exclusive triggers on the same
  condition. Near-miss: two rules with *different, non-overlapping* scopes that
  only look opposed.
- **Vagueness** — no measurable threshold, no named actor, unresolvable
  referent, undefined term used as a gate, missing failure branch, "etc." as a
  load-bearing list terminator. Near-miss: deliberate latitude that the passage
  itself marks as a judgment call.
- **Bandaid** — a workaround with no recorded root cause, "for now" / "until we
  fix" surviving past a stated date, an exception stacked on an exception, a
  retry-or-ignore instruction standing in for a fix, a TODO used as policy.
  Near-miss: a documented, owned, dated interim measure — that is a decision,
  not a bandaid.
- **Redundancy** — the same rule in ≥2 places verbatim or in paraphrase,
  overlapping scopes that both claim authority, a file restating another.
  Near-miss: an intentional summary that points at its canonical source.

## Boundary edits to existing skills

`se-knowledge-gap` gains one paragraph naming this skill as the owner of
inward corpus-defect audits; this skill's body names `se-knowledge-gap`,
`se-fact-check`, `se-prose-lint`, `se-docs-bustest`, and `se-red-team` as the
owners of what it does not do. No behavior change to any existing skill.

## Pack integration

Three edits in `installer/registry.py`:

1. `SKILLS` — `SkillInfo(name="se-coherence-audit", family="improve")`, appended
   (row order is manifest/install order; appending avoids reordering).
2. `RUNTIME_PROFILE_ASSIGNMENTS` — add to the `DEEP_ANALYSIS` tuple.
3. `SHARED_REFERENCES` — add to `_shared/references/argument-vocabulary.md`.

Two edits in the test suite, both of which the precedent commit also made and
neither of which the generator writes for you:

4. `tests/test_generate.py` — add the skill to the `EXPECTED_SHARED_SOURCES`
   golden snapshot; `test_registered_shared_sources_match_snapshot` iterates
   `SKILL_NAMES` and fails on any skill whose registered sources differ from
   the snapshot (`tests/test_generate.py:620-645`).
5. `tests/test_skills.py` — a test class for the new skill in the shape the
   file already uses for its neighbors (`47d1fb0` added 144 lines there).

Then `make generate` regenerates `manifest.json`,
`generated/skills/claude/se-coherence-audit/SKILL.md`,
`generated/references/skill-catalog.md`, and
`generated/registry-snapshot.json`. Only the `claude` overlay is committed
under `generated/skills/`; the other platform surfaces are produced at install
time. The skill catalog is **generated** output
(`installer/registry.py:530-532`) — never hand-edit it, unlike the pre-move
precedent commit, which edited it under `templates/skills/_shared/`.

Version is a hand edit: the generator's `DEFAULT_MANIFEST_HEADER` carries
`0.1.0` and the committed `manifest.json` carries the real value (`0.71.0` at
the time of writing), so the generator preserves whatever is committed. Bump
`manifest.json` `version` one minor **before** regenerating, so the regenerated
payload and the version land in one consistent tree.

Docs: `README.md`, `docs/SE_AI_COMMAND_PACK.md`, `CHANGELOG.md` (dated
heading).

## Risks

- **False contradictions.** The failure mode of this skill class is confident
  pairing of passages that are not actually opposed. Mitigated by the required
  near-miss rules, the ≥2-location evidence rule, and the `confidence` floor
  that drops low-confidence findings instead of reporting them.
- **Scope creep into fixing.** R5 is stated in the body as a safety rule, not
  only in the PRD.
- **Overlap drift with `se-knowledge-gap`.** Mitigated by the reciprocal
  boundary statements (A5).

## Rollback

Single-commit revert: the skill directory, three registry lines, regenerated
artifacts, and docs all land together. Nothing else depends on the new skill.
