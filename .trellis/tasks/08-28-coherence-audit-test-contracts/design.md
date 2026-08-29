# Replace brittle prose pins in se-coherence-audit skill tests with contract assertions — Design

## Overview

`CoherenceAuditSkillTest` (`tests/test_skills.py:4124-4300`) holds eleven test
methods. Most assert that a full prose sentence appears in a named section of
`SKILL.md`, `references/detector-criteria.md`, or `references/ledger-format.md`.
The repository's own guidance already names the defect: *"Pin the shortest
phrase that carries the contract: long enough that deleting the contract breaks
it, short enough that rewording does not"*
(`.trellis/spec/backend/quality-guidelines.md:175-176`). This task is that rule
applied to the one class that violates it hardest; it is not a departure from
the prose-contract spec, and that spec's `grep`-before-pin and prove-the-pin
procedure still governs every pin that survives.

The most brittle assertion in the class pins a literal line break:

```python
self.assertIn(
    "its\n  proposed resolution, which is a proposal and is never applied",
    raw,
)
```

It reads unnormalized `skill_text()`, so re-wrapping the paragraph breaks it
while the contract stands untouched.

## Proposal

Assert against the **durable surfaces** the skill actually owns, in descending
order of preference. Reach for a prose token only when no structural surface
carries the contract.

### 1. Enumerated surfaces — parse, then compare sets

Three surfaces are enumerations that the documents already render structurally.
Parse each and assert the exact set, so both a deletion and an unannounced
addition fail:

| Surface | Source | Expected set |
|---|---|---|
| argument names | `SKILL.md` `## Arguments`, backticked head of each `-` bullet, truncated at the first `=` | `input`, `exclude`, `classes`, `precedence`, `depth`, `min_severity`, `sensitivity`, `format` |
| ledger field names | `ledger-format.md` `## Finding schema` table, column 1 | `id`, `class`, `severity`, `locations`, `quotes`, `precedence`, `criterion`, `why`, `resolution`, `confidence` |
| coverage sets | `ledger-format.md` `## Coverage block` table, column 1 | `read in full`, `sampled`, `skipped` |

### 2. Closed value sets — token presence inside the owning bullet or row

The document declares a value set in one of two shapes, and the assertion has to
handle both. Three arguments carry their values **inside** the backticked head —
`` `depth=standard|brief|deep` ``, `` `sensitivity=standard|restricted|minimal` ``,
`` `format=ledger|memo` `` — so the values are the pipe-separated tail of the
token. The remaining five have a bare head (`` `input=` ``, `` `classes=` ``, …)
and state their values in the bullet body. Read the tail when the token carries
one, the body otherwise; a naive `- \`name=\`` match finds only five of the eight
arguments and would report the other three as deleted.

Enum values are backticked identifiers, immune to rewording of the prose around
them. Scope each assertion to the bullet or table row that owns it, never the
whole file:

- `classes=` bullet holds `contradiction`, `vagueness`, `bandaid`, `redundancy`
- `depth=` bullet holds `standard`, `brief`, `deep`
- `sensitivity=` bullet holds `standard`, `restricted`, `minimal`
- `format=` bullet holds `ledger`, `memo`
- `severity` row and `## Severity` section hold `blocking`, `high`, `medium`, `low`

### 3. Detector classes and their criteria

`detector-criteria.md`'s `##` headings are the four detector classes; assert the
heading set exactly. Within each class section keep the three existing
structural markers (`**Qualifies**`, `**Evidence required**`, the near-miss
marker) — those are formatting contracts, not prose, and they did not break.

Add the criterion identifiers, which are a durable surface the current tests do
not cover at all. Each is a backticked slug opening its bullet, followed by an em
dash: `- \`slug\` — …`. That shape is what separates them from the near-miss
bullets in the same section, which are prose and open with no backticked token,
so one extraction rule over the whole class section yields the criteria and
nothing else:

- Contradiction: `direct-negation`, `incompatible-threshold`, `conflicting-order`, `exclusive-trigger`
- Vagueness: `no-threshold`, `no-actor`, `unresolvable-referent`, `undefined-gate`, `missing-failure-branch`, `open-list-terminator`
- Bandaid: `no-root-cause`, `expired-interim`, `stacked-exception`, `retry-as-fix`, `todo-as-policy`
- Redundancy: `verbatim-duplicate`, `paraphrase-duplicate`, `overlapping-authority`, `restating-file`

This is a net coverage increase: today, deleting `exclusive-trigger` breaks
nothing.

### 4. Cardinality rule

The multi-location requirement lives in two places and both must agree. Assert
the `locations` row of the finding schema names `contradiction`,
`missing-precedence`, and `redundancy`, and that `detector-criteria.md`'s
Contradiction and Redundancy sections each carry `at least two`. The existing
`"at least two \`path:line\` locations"` pin is short enough to keep; the
schema-row half is new.

### 5. The two contracts the PRD requires preserving

**Classification by settleable authority.** Two independent anchors, so a
rewording of either leaves the other standing:

1. In the `contradiction` bullet of `## Workflow` step 5 — scoped to that bullet,
   not the section — assert both `authority` and `block` appear. Deleting the
   block-level rule removes both; rewording "Authority is the block a passage
   lives in, not the file" keeps them.
2. In `ledger-format.md`'s Contradiction worked example, assert
   `precedence: irrelevant`. That token exists *only* because one authority
   leaves no ordering to invoke, so it fails if the rule is dropped from the
   model rather than merely from the sentence.

Also assert the three conflict-class tokens (`resolved-by-precedence`,
`missing-precedence`, `contradiction`) appear in step 5, and that
`missing-precedence` also appears in the schema's `class` row.

**Redaction carve-out.** One helper, applied to both files, asserting three
tokens co-occur in the owning region: `sensitivity`, `unquotable`, and a
retention marker. The marker must be one of the negated forms ("never dropped",
"not dropped", "neither drops", "rather than dropping/dropped"): a bare `dropp`
substring would also match a file asserting the finding *is* dropped, so it
accepts the inverted policy. Applied to `SKILL.md`'s `## Safety rules` and to
`ledger-format.md`'s `quotes` schema row. Dropping the carve-out from either
file fails; the two can no longer silently diverge on whether a withheld quote
survives as a finding.

### 6. Prose-only contracts — shortest distinctive token

Four safety rules have no structural carrier. Replace each full sentence with
the shortest token that dies with the contract, asserted within `## Safety
rules`: `read-only`, `never edit`, `never apply`, `never widen`,
`never invent`. Same for the partial-coverage rule (`partially audited`,
`never present a partial pass`) and the confidence floor
(`never report a low-confidence`, plus `dropped, not reported` in
`ledger-format.md`).

### 7. The resolution-is-a-field contract

Delete the line-break-sensitive pin. Replace it with the assertion that actually
states the contract: `resolution` is a field of every finding and there is no
separate resolutions section. Assert `resolution` is in the finding-schema field
set (already covered by §1) and that neither document contains a
`## Resolutions` heading nor a `**Resolutions**` report field.

### 8. What this cannot reach

The PRD's second acceptance criterion asks that rewording *any* single sentence
leave the suite green. That is achievable only where a structural surface
carries the contract. Four safety rules and the confidence floor have no
structural carrier at all, so their shortest token is the only guard left, and a
voice-inverting rewrite — "Never edit the corpus" to "The corpus is never
edited" — still breaks `never edit`.

That is the intended trade, not an oversight: the alternative is no assertion on
those rules. The criterion is therefore bounded to contracts with a structural
carrier, `prd.md` is amended to say so, and the worked rewording demonstrates
both halves — one sentence whose contract is structural (green), and one
prose-only safety sentence reworded within its token (also green), so the bound
is shown rather than asserted.

## Boundaries And Non-Goals

- Only `CoherenceAuditSkillTest` changes. No other test class, no skill file, no
  installer or template content.
- `EXTERNAL_INPUT_SKILLS`, the family map, and `SKILL_NAMES` ordering assertions
  are untouched — they pin identifiers, not prose, and did not break.
- Not a rewrite of the shared helpers. `section_body()`, `skill_section()`,
  `resource_section()`, `normalized*()` stay as they are; new parsing helpers are
  added beside them.
- The skill's Markdown is not edited by this task. If a parse helper cannot find
  a surface, the fix is the helper, not the document.

## Affected Files

| File | Change |
|---|---|
| `tests/test_skills.py` | rewrite `CoherenceAuditSkillTest`; add table/bullet parsing helpers |
| `.trellis/tasks/08-28-coherence-audit-test-contracts/research/rewording-proof-*.md` | new; records the worked rewording and the deletion probes |

No payload file changes, so no version bump and no `make generate` run.

## Data And Command Contracts

New module-level helpers in `tests/test_skills.py`, beside the existing ones:

```python
def markdown_table_column(text: str, heading: str, column: int = 0) -> list[str]:
    """Cells of one column of the first pipe table under ``heading``, header and
    separator rows dropped, backticks and bold markers stripped. Column 0 gives
    the field or set names; the ``locations`` cardinality rule and the severity
    tiers are read from column 1."""

def table_row(text: str, heading: str, key: str) -> str:
    """The row of the first pipe table under ``heading`` whose first cell is
    ``key``, joined and whitespace-collapsed. Sections 4 and 5 both assert
    against one named row — the ``locations`` cardinality rule and the ``quotes``
    redaction carve-out — so the lookup is by field name, never by row index.
    Raises when no row carries that key."""

def bullet_body(text: str, heading: str, token: str) -> str:
    """The one ``- `token`…`` bullet under ``heading``, including its
    continuation lines, whitespace-collapsed. Raises AssertionError when the
    bullet is absent, so a deleted argument fails loudly rather than
    vacuously."""

def argument_names(name: str) -> set[str]:
    """Argument identifiers declared as ``- `x=`` bullets under ``## Arguments``."""

def criterion_slugs(name: str, relative: str, heading: str) -> set[str]:
    """Backticked slugs introduced by ``- `slug` —`` bullets in one section."""
```

Every helper raises `AssertionError` on a missing surface. A helper that
returned an empty collection would let a deletion pass as "no members to check",
which is the same silent-pass failure mode the spec warns about for pins.

## Risks And Edge Cases

| Risk | Prevention |
|---|---|
| Parser silently returns empty and every set assertion trivially passes | Helpers raise on a missing heading, missing table, or empty result; the deletion probes in the validation plan exercise this directly |
| A set assertion makes adding a legitimate new argument fail | Intended. An added argument is a contract change and should require a test edit; the failure names the unexpected member |
| Bullet scoping too narrow, so a legitimate re-indent breaks the pin | `bullet_body()` collapses whitespace and follows continuation lines, matching the existing `normalized*()` behaviour |
| The redaction helper passes on a file that carries the tokens but states the opposite rule | Real bound, stated in the research notes: the assertion proves both files carry the carve-out's three parts, not that no other sentence contradicts it. Full contradiction detection is `se-coherence-audit`'s own job, not a unit test's |
| Lower-casing hides a case-carrying identifier | Assert identifiers against the un-lowered text; keep `.lower()` only for prose tokens |

## Validation

1. `make check` green — the deterministic gate, currently 773 tests.
2. **Rewording survives**, two probes, both expected green: reword a sentence
   whose contract is structural (an argument's description), and reword a
   prose-only safety sentence within its pinned token. Both recorded verbatim in
   the research notes, alongside the bound in section 8.
3. **Deletion fails**, four independent probes, each expected `FAILED`:
   delete the `format=` argument bullet; delete the `criterion` row from the
   finding schema; delete the `## Bandaid` heading and section; delete the
   redaction carve-out sentence from `ledger-format.md`'s `quotes` row.
4. Each probe restores from `HEAD` per
   `.trellis/spec/backend/quality-guidelines.md:152-161`, confirms `FAILED`,
   restores the file, and confirms `OK`.
