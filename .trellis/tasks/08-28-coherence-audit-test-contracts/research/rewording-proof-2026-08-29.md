# Rewording and deletion proofs — 2026-08-29

Every run below is the focused lane:

```bash
.venv/bin/python -m unittest discover -s tests -p test_skills.py \
  -k CoherenceAudit -k MarkdownContractHelper
```

It covered 17 tests when this file was started and 46 by the last round; the
count is recorded per round rather than claimed once here, because each round
added cases. Every probe is the same procedure: copy the file to a `mktemp`,
apply the edit named in that round's entry, run the lane, restore the copy, run
it again. `git status --porcelain templates/` was empty after each round, which
is the evidence the restores happened. Probe numbers are unique per round and
never reused; where an earlier round's probe is re-run against later code, the
entry says so and keeps that probe's original number.

Note the inversion against the runnable block in
`.trellis/spec/backend/quality-guidelines.md:152-161`. That block restores the
*source* to `HEAD` to prove a new pin fails without the edit it guards. Here the
source is already correct and the tests are what changed, so the probe removes a
contract from the source instead. Same proof, opposite direction.

## Deletion probes — a dropped contract must fail

| Probe | Edit | Result |
|---|---|---|
| P1 | delete the `format=ledger\|memo` argument bullet from `SKILL.md` | `FAILED (failures=1)` |
| P2 | delete the `criterion` row from `ledger-format.md`'s finding schema | `FAILED (failures=1)` |
| P3 | delete the `## Bandaid` heading and section from `detector-criteria.md` | `FAILED (failures=3)` |
| P4 | replace the redaction carve-out in the `quotes` row with "Paraphrase is never acceptable" | `FAILED (failures=1)` |

Baseline before and after every probe: `OK`.

P3 failing three tests rather than one is the intended shape: the detector-class
heading set, the criterion slug set, and the near-miss structure are three
separate contracts that the same deletion breaks.

## Rewording probes — a preserved contract must stay green

Both reworded sentences are recorded verbatim.

### R1 — a contract with a structural carrier

Before:

```
- `classes=` — which detectors to run, as a comma list of `contradiction`,
  `vagueness`, `bandaid`, `redundancy`. Default all four.
```

After:

```
- `classes=` — the detectors to run: a comma-separated selection from
  `contradiction`, `vagueness`, `bandaid`, `redundancy`. All four run by default.
```

Result: `OK`.

The pin this replaced is present verbatim at `HEAD`:

```
"`contradiction`, `vagueness`, `bandaid`, `redundancy`. default all four"
```

R1 breaks it — the word order after the value list changed — while the contract
(four named detector classes, all four by default) did not. That is one of the
five PR #278 breakages reproduced deliberately.

### R2 — a prose-only contract, reworded within its token

Before:

```
- Never widen scope beyond the resolved file set, even when a corpus file points
  at material outside it.
```

After:

```
- Never widen scope past the resolved file set, even when a corpus file gestures
  at material outside it.
```

Result: `OK`. The `HEAD` pin
`"never widen scope beyond the resolved file set"` breaks under it; the surviving
token `never widen` does not.

## The bound on the rewording criterion

`prd.md`'s second acceptance criterion is stated against contracts that have a
structural carrier, and R1 is its demonstration. Five rules have no structural
carrier at all — the four read-only safety rules and the confidence floor — so
their guard is the shortest token that dies with them. R2 shows that a genuine
rewording of such a rule stays green, but a voice-inverting rewrite ("Never edit
the corpus" to "The corpus is never edited") would still break `never edit`.

That is the trade, taken deliberately: the alternative is no assertion on those
rules at all. The tokens chosen are the shortest that die with their contract.

## The bound on the redaction assertion

`test_redaction_carveout_agrees_across_skill_and_ledger` asserts that
`SKILL.md`'s `## Safety rules` and `ledger-format.md`'s `quotes` row each carry
all three parts of the carve-out: `sensitivity`, `unquotable`, and a retention
marker. The marker is one of the negated forms ("never dropped", "not dropped",
"neither drops", "rather than dropping/dropped"), not a bare `drop` substring —
review round 1 showed the bare token also matches a file asserting the finding
*is* dropped, so it accepted the inverted policy. P4 confirms removing the
carve-out from either side fails.

It proves each file carries the carve-out. It does not prove that no other
sentence in either file contradicts it. Detecting that is `se-coherence-audit`'s
own job — a `contradiction` finding at one authority — not a unit test's, and
claiming otherwise would be the same overreach the skill's own near-miss rules
exist to prevent.

## Round 2 — after the local review findings

The first review round returned ten local findings; all ten were verified true
against the checkout and fixed. Three changed an assertion, so each was
re-proved.

| Probe | Edit | Result |
|---|---|---|
| P4 | delete the redaction carve-out from the `quotes` row | `FAILED (failures=1)` |
| P5 | invert the ledger policy: "a withheld quote **drops** the finding" | `FAILED (failures=1)` |
| P6 | invert the same policy at `SKILL.md:155` only | `OK` |
| P6b | invert it at both `SKILL.md:155` **and** `:168` | `FAILED (failures=1)` |
| P7 | delete the empty-scope stop rule from the workflow | `FAILED (failures=1)` |

P5 is the finding gito and prism both raised: the first version of the
assertion looked for a bare `drop` token, which matches "dropped" and so passed
on a file stating the opposite policy. It now requires one of the negated forms
(`never dropped`, `not dropped`, `neither drops`, `rather than dropping`,
`rather than dropped`), and P5 turns it red.

P6 passing is correct, and it is the documented bound made concrete rather than
a gap. `SKILL.md` states the retention rule twice — at `:155` for the general
case and at `:168` for `sensitivity=minimal`. Inverting one leaves the section
carrying the contract *and* contradicting itself. A unit test asserting "this
file states X" cannot see that; a corpus audit for `contradiction` at one
authority can, which is what `se-coherence-audit` is for. P6b, which inverts
both, is red.

## Separator parsing

`markdown_table_column` originally detected the separator row by joining the
cells before cleaning, so `| --- | --- |` kept its inner spaces and was parsed as
data. Both reference files write `|---|---|`, so nothing was wrong today and
nothing would have been until someone reformatted a table. Cells are now cleaned
individually:

```
spaced separator -> ['id', 'class']
tight separator  -> ['id']
```

## Round 3: two coverage gaps the review found

Local review round 2 caught two contracts the rewrite dropped rather than
converted. Both were assertions the old prose pins had carried and the new
structural ones did not replace, because neither contract has a structural
carrier to parse.

`classes=` — the old pin `` `redundancy`. default all four `` asserted two
things at once: the accepted value set *and* what runs when the argument is
omitted. The set assertion replaced only the first half. A default is a
statement about absence, so there is nothing in the document to enumerate; it
keeps the shortest phrase that carries it.

`input=` — the old pin `comma-separated list of paths, globs, or a vault`
named the three accepted corpus forms. The replacement asserted only that the
argument is required and never inferred. Each form is restored as its own
token, so dropping one names which one.

Both probes:

```
P7  remove "Default all four." from SKILL.md
    -> FAILED: 'default all four' not found in '- `classes=` — ... `redundancy`.'
P8  drop "globs" from the input= bullet
    -> FAILED: 'globs' not found in '- `input=` ...' : input= no longer accepts globs
```

The general lesson, and the reason this is worth recording: converting a prose
pin to a structural one silently drops any *second* contract the sentence was
carrying. The set is the visible half; the default, the required-ness, the
accepted forms are not. Enumerate what a pin asserts before replacing it, not
what it looks like it asserts.

## Round 4: the sibling audit

Round 3 returned the same family again — five more contracts the conversion had
dropped. Patching the two from round 3 one at a time was the wrong move; the
right one was to enumerate every claim the old class made and check each against
the new one. That audit found all five the reviewer named plus one it did not
(the `total size` half of the scope announcement).

Every restored contract, probed by deleting it from the source:

```
P9   drop "comma-separated" from input=            -> FAILED
P10  drop "and total size" from the scope report   -> FAILED
P11  drop "say which emptiness it was"             -> FAILED
P12  drop "the passages themselves are the finding"-> FAILED
P13  drop "with the unaudited remainder named"     -> FAILED
P14  drop "scored by consequence" from Severity    -> FAILED
P15  add a "## Resolution" section to the ledger   -> FAILED (3)
P16  duplicate the `input=` argument bullet        -> FAILED
```

P16 is the one worth keeping in mind. `argument_names` and `criterion_slugs`
returned sets, so a document declaring the same argument twice parsed as one —
the set projection absorbed the defect instead of reporting it. Both helpers now
raise on a duplicate before projecting. This is the same failure the table
assertions guard with a length check, one layer further in: a set is the right
*answer* and the wrong *intermediate*.

Helper coverage. `MarkdownContractHelperTest` now fixes the parsing decisions the
contract assertions rest on — where a section ends, that both separator
spellings are structure, that a missing heading, a missing table, an absent
column, and an absent bullet each raise rather than return empty. A contract
assertion over a silently-wrong parse asserts nothing, and until this class
existed nothing proved the parse.

## Round 5: the three I talked myself out of

The round-4 sibling audit listed three dropped contracts and then dismissed each
one as "close enough": the five fields `never invent` enumerates, the `locations
intact` half of the redaction carve-out, and *what* coverage may not be inferred
from. The review returned all three. Worth recording as a process note rather
than a technical one — the audit found them, the judgement call lost them, and
the shortest-token rule answers each cleanly. A broad token that survives
deleting any one member of a list is not pinning the list.

```
P17  drop "quotation" from the never-invent list  -> FAILED
P18  drop "with its locations intact"             -> FAILED
P19  drop "from the number" in the coverage rule  -> FAILED
```

## Round 5: the parser findings

Two defects in the helpers added in round 4, both real:

`markdown_table_column` treated the first pipe-prefixed line as a header and
never required a separator after it, so any pipe-delimited prose parsed as a
table and supplied whatever cells it held. `table_row` then re-derived the rows
with a *different* rule and indexed by `+2`, so the two readers could disagree
about which row a name referred to. Both now read one `_table_rows` extractor
that requires header, separator, rows — and `table_row` matches by name against
the same list rather than computing an offset into a second parse.

`argument_values` had the P16 defect one level down: an inline enum written
`depth=standard|standard|deep` collapsed to two values in a set. It raises on a
repeat now, like the two projections fixed in round 4.

Also fixed: the focused validation command in `implement.md` excluded the helper
class, and `-k "A or B"` is not a thing — `unittest -k` takes patterns, and
multiple `-k` flags are what unions them.


## Round 6: the anchor that only looked like an anchor

The reviewer said the `authority` + `block` pin still breaks under a
contract-preserving rewording. It does. The obvious repair — drop `block`,
keep `authority`, lean on anchor 2 — was wrong, and the probe said so.

**P20 — delete the block-level rule from the `contradiction` bullet.** With
`authority` as the only anchor: **passed**. Deleting the rule leaves "the
passages sit at one authority" in the bullet, so the word survives its own
contract. Anchor 2 (`precedence: irrelevant`, in `ledger-format.md`) did not
catch it either: that token models "no ordering applies", not "authority is
sub-file". The contract was unguarded.

Adding a `{block, section}` vocabulary check did not fix it on the first try —
P20 still passed, because `bullet_body()` was returning the whole rest of the
section. The bullet is the *last* sub-bullet of step 5's nested list, and the
reader stopped only at the next `- `; with no sibling after it, the body ran on
through steps 6 and 7, where "Final report section" supplied the word
`section`. Every pin scoped to a trailing sub-bullet was reading the section,
not the bullet.

`bullet_body()` now ends a body at its own list level: a sibling bullet, a
de-indent, or the enclosing numbered step. `MarkdownContractHelperTest` covers
it with a nested fixture whose last sub-bullet is followed by an outer step.

With both fixes:

- **P20** (delete the rule) — **FAILED (failures=1)**, as required.
- **P21** (reword block/file to section/document throughout, contract intact) —
  **OK**.

The lesson generalizes past this bullet: a pin is only scoped as tightly as the
parser scopes it, and a parser that over-collects turns a bullet pin into a
section pin without changing a line of the test. The deletion probe is what
tells the two apart — the assertion itself reads the same either way.

### Round 6: the parser findings

- `_table_rows()` collected every pipe line in a section, so two tables under
  one heading merged into one and a name lookup could resolve against the wrong
  one. It now stops at the first non-pipe line after the table starts.
- `argument_names()` skipped a bullet head without `=`, reporting a malformed
  declaration as no declaration. It raises.
- `argument_values()` returned an empty set for an argument that declares no
  values, and its `[a-z_]+` charset hid any value with a digit or a hyphen. It
  raises on empty and reads `[a-z0-9_-]+`.
- Criterion slugs read `[a-z0-9-]+` for the same reason.

Each of these has a case in `MarkdownContractHelperTest` against a fixture
document, rather than being proven incidentally by a caller. Coverage is by
parse decision, not exhaustive: the cases fix the decisions that are not
obvious from reading the helper — which rows are structure, where a body ends,
what a fence means, and which inputs must raise.


## Round 7: what the parsers still accepted

Four more ways a parse could pass while meaning nothing, each fixed and each
given a case against the fixture document:

- A table drawn **inside a fenced block** parsed as a declaration. A fence
  shows a shape; the document is not declaring one. `_unfenced()` now strips
  fenced regions before every structural read — tables, bullet heads, bullet
  bodies, criterion slugs.
- `| : | :: |` passed as a separator, because the check was
  `set(cell) <= {"-", ":"}`. A separator cell is now dashes with optional
  alignment colons, so a malformed table fails instead of parsing.
- An **indented** `- \`x=\`` bullet counted as an argument declaration. Heads
  are read at column zero: a sub-point is part of the declaration above it.
- The value and slug regexes read `[a-z0-9_-]+`, so a declared value carrying
  any other character was invisible to the set assertion — the one change the
  assertion exists to catch. Both now read the whole backticked token, with the
  bullet's own head excluded from its values.

`skill_text()` is cached, since the contract assertions read one document from
several helpers.

Probes after the change: **P20** (delete the block-level rule) FAILED, **P22**
(delete the `precedence=` bullet) FAILED, **P23** (add a fifth value to
`classes=`) FAILED. Baseline OK, `make check` green at 795 tests.


## Round 8: fences, heads, and a cache that could lie

The review found a stronger version of the fence problem than round 7 fixed. It
is not only that a fenced table parsed as a declaration — a `#` line inside a
fence was read as a *heading*, so a sample document in an example both named
sections the document does not have and ended the real section it sat in. The
tail of that section then read as absent rather than as unmet. `section_lines()`
now tracks fences while locating the heading and while walking the body, and
`~~~` counts as a fence alongside ```` ``` ````.

Three more:

- `bullet_body()` matched its token as a line prefix, so a pin scoped to
  `` `beta=` `` was satisfied by the `betamax=` bullet — a deleted argument
  would keep passing against its neighbour. Lookup is against the parsed head:
  exact, except that a head stating its values inline is addressed by its name.
- Criterion slugs were read from the stripped line, so an indented example
  counted as a declaration. They are read at column zero, like argument heads.
- The detector-class heading set was read from raw lines, so a `## ` inside a
  worked example would have joined the set.

The `skill_text()` cache added in round 7 was keyed on the skill name alone,
which is a cache that can lie: a test rewriting a fixture inside one process
would read the text from before its own write. The key is now the path plus the
file's modification time, and the same reader serves the reference documents,
which several projections had been re-reading.

Probes after the change, each expected red and each red: **P20** (delete the
block-level rule), **P24** (delete the `## Bandaid` detector class), **P25**
(delete the `criterion` row from the ledger schema). Baseline OK, `make check`
green at 798 tests.

The PRD's goal and the design's anchor now state their own bounds. The goal
claimed rewording tolerance without qualification while an acceptance criterion
carved out the prose-only contracts; the anchor tolerates the unit noun
changing but not the word `authority` leaving the bullet, and says so.

## Round 9: three sentences that were never one rule

Round 8's remaining findings were all the same shape: an assertion that proved
the *parts* of a contract exist without proving they belong together.

**The carve-out was three unrelated searches.** `assert_states_redaction_carveout`
asserted `sensitivity`, `unquotable`, and a retention phrase each appeared
somewhere in the file. A document that described `sensitivity=` in its Arguments
section, used "unquotable" in a report example, and promised "not dropped" about
some other rule entirely would have passed — three true sentences, no carve-out.
Fixed with `statements()`, which splits a document into bullets, table rows, and
paragraphs; the assertion now requires one statement carrying all three. Probe
P26 deletes `, and neither drops the finding` from the ledger row: `FAILED`. Both
real documents state the rule inside a single bullet or cell, so the narrower
assertion needed no document change.

**The resolution prohibition matched four spellings of one thing.** It banned
`## Resolutions`, `## Resolution`, `**Resolutions**`, `**Resolution**` as
literals — so `### Resolution` or `## resolutions` was a section this test would
not see. Replaced with a heading read: every unfenced ATX heading is normalized
(strip `#`, strip emphasis, lower) and compared to the two words. Probe P27
appends `### Resolutions` to the ledger: `FAILED`.

**The criterion parser had no fixture.** `criterion_slugs()` ran only against the
real document, so its parse decisions — a near-miss bullet is prose, a fenced
bullet is an example, an empty class raises, a duplicate slug is not absorbed —
were assumptions. Split into `_criterion_slugs(text, heading)` and covered by
four cases against a fixture. Probe P28 deletes the criterion bullets from
`detector-criteria.md`: `FAILED`.

**"Closed value set" claimed more than the parser does.** The set is closed over
the declaration surface — the head's pipe tail, or the body's backticked tokens —
and `test_a_value_added_to_a_declaration_changes_the_set` proves an added value
reaches the `assertEqual` on both. It is not closed over the document, and it
cannot be: `depth=`'s body legitimately backticks `min_severity=` and `low`,
neither of which is one of its values. Recorded as a convention in `design.md`
rather than pretended away in the parser.

**Two anchors are not two chances.** The design claimed the classification
contract survived rewording because it had "two independent anchors"; both are
asserted, so defeating either fails the test. Independent in what they read, not
alternatives — and the tolerance is the rewording *within* an anchor (`block` or
`section` for the unit noun), never the loss of the word `authority`, which is
the contract's name. Corrected in `design.md` section 5.

Also this round: fence delimiters now follow the Markdown rule (three or more of
one character, closed by the same character at the same length or longer) instead
of treating any ``` or ~~~ prefix as a toggle — a tilde line inside a backtick
block used to invert the state and classify every following line backwards. A
table whose rows do not all carry the header's column count now raises instead of
projecting the wrong field past the short row. `ledger_text()` reads through the
shared cache rather than the disk. Gate: 804 tests, `make check` green,
prose-lint clean.

## Round 10: what "#" and "```" actually mean

Round 9's findings were about the parser believing its own shorthand.

**A `#` is not a heading.** `section_lines` ended a section at any stripped line
starting with `#`, so `#hashtag` in prose and a four-space-indented `#### note`
inside a code sample both truncated the section they sat in — and the contract
below the truncation read as *absent*, which is the failure mode this whole
class exists to remove. Replaced with the ATX rule: at most three spaces of
indent, one to six `#`, then whitespace or end of line. `## Not headings` in the
fixture carries both shapes above a table, and the table is still found.

**A fence with an info string is not a closer.** ` ```python ` inside a block
was read as closing it, so everything after it parsed as document structure.
`_fence` now returns the delimiter *and* its info string, and `_closes` requires
the info string to be empty. Fixture `## Reopened fence` puts a sample table
after such a line; reading it now raises instead of returning the example's rows.

**Deleting a fence joined what stood on either side.** `_unfenced` dropped the
block's lines outright, so a table, a fenced example, and a second table became
one table. It now leaves a blank line where the block was — the same separation
the document has. Fixture `## Split by a fence` proves the second table stays
separate.

**A delimiter row has one cell per header cell.** The separator was checked for
shape but not width, so `| --- | --- | --- |` under a two-column header parsed as
a table. It now raises. The separator is also read from the raw cells rather than
the cleaned ones, so `` | `---` | `` is no longer structure.

**The scope contract lost its ordering half.** The test asserted `file count`,
`total size`, and `before` all appeared in the workflow — but step 1 says
"before" about unresolved paths too, so the measurement could move after the read
and the test would still pass. Probe P29 rewrites the sentence to "state the
resulting file count and total size once the corpus has been read": with the
statement-wide search, `OK` — the contract was gone and nothing failed. Scoped to
the sentence, `FAILED`. Kept.

Also this round: the document cache keys on size as well as mtime, because a
filesystem whose timestamps are coarser than the write reports one mtime for two
revisions; the resolution prohibition reads `## Resolution ##` as the same
heading written closed. Round-9 regression probes: **P30** (rename the `format=`
argument) `FAILED`, **P31** (delete the `criterion` schema row) `FAILED`,
restored `OK`, `git status --porcelain templates/` empty. Gate: 808 tests,
`make check` green, prose-lint clean.
